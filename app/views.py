import random
from functools import wraps
import binascii
import requests
import os
from urllib.parse import urlencode, parse_qs
from flask import request, session, render_template, jsonify, abort, url_for, redirect
#from oauth2client import client, crypt
from app import app, db
from app.models import User, Article, ArticleView


def requires_login(view):
    @wraps(view)
    def decorator(*args, **kwargs):
        if not 'usersub' in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return decorator
    

def handle_github_login(session_code):
    data = {
        'client_id': app.config['GITHUB_CLIENT_ID'],
        'client_secret': app.config['GITHUB_CLIENT_SECRET'],
        'code': session_code,
        'state': session.get('state', '')
    }
    result = requests.post(
        'https://github.com/login/oauth/access_token', data=data)
    qs = parse_qs(result.text)
    access_token = qs['access_token']
    result = requests.get(
            'https://api.github.com/user', 
            params={'access_token': access_token})
    session['usersub'] = result.json()['login']

    # Create user if it doesn't exist
    user = db.session.query(User).filter(User.sub == session['usersub']).first()
    if not user:
        db.session.add(User(session['usersub']))
        db.session.commit()


@app.route('/', methods=['GET'])
def home():
    if 'code' in request.args:
        handle_github_login(request.args['code'])
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    state = binascii.hexlify(os.urandom(32)).decode('utf-8')
    session['state'] = state
    query = {
        'client_id': app.config['GITHUB_CLIENT_ID'],
        'state': state
    }
    return redirect(
        'https://github.com/login/oauth/authorize/?' + urlencode(query))


"""
@app.route('/google-signin', methods=['POST'])
def google_signin():
    print('google signin called')
    if 'idtoken' not in request.form:
        abort(400)
    token = request.form['idtoken']
    try:
        idinfo = client.verify_id_token(token, app.config['GOOGLE_CLIENT_ID'])
    except crypt.AppIdentityError:
        abort(401)
    if db.session.query(User).filter(User.sub == idinfo['sub']).first() == None:
        db.session.add(User(idinfo['sub']))
        db.session.commit()
    session['usersub'] = idinfo['sub']
    return ''
"""
        
    
@app.route('/get-article', methods=['POST'])
@requires_login
def get_article():
    article = random.choice(db.session.query(Article).all())
    return jsonify(
        url=article.url, title=article.title, text=article.text, 
        imageUrl=article.image_url)
    

@app.route('/view-article', methods=['POST'])
@requires_login
def view_article():
    article_url = request.form.get('articleUrl', None)
    clicked = request.form.get('clicked', None)
    article = db.session.query(Article).filter(Article.url == article_url).first()
    user = db.session.query(User).filter(User.sub == session['usersub']).first()
    if not all([article_url, clicked, article, user]):
        abort(400)
    av = (
        db.session.query(ArticleView)
        .filter(ArticleView.article_url == article_url)
        .filter(ArticleView.user_sub == session['usersub'])
        .first()
    )
    if av:
        av.clicked = clicked
    else:
        av = ArticleView(article_url, session['usersub'], clicked)
    db.session.add(av)

    # Add article to reading queue
    if clicked == 'true':
        user.append_reading_queue(article.url, article.title)
        db.session.add(user)

    db.session.commit()

    return ''



@app.route('/pop-reading-queue', methods=['POST'])
@requires_login
def pop_reading_queue():
    article_url = request.form.get('articleUrl', None)
    if article_url is None:
        abort(400)
    user = db.session.query(User).filter(User.sub == session['usersub']).first()
    user.remove_reading_queue(article_url)
    db.session.add(user)
    db.session.commit()
    return ''

@app.route('/get-reading-queue', methods=['GET'])
@requires_login
def get_reading_queue():
    user = db.session.query(User).filter(User.sub == session['usersub']).first()
    if user is None:
        abort(401)
    return jsonify([{'url': a[0], 'title': a[1] } for a in user.get_reading_queue()])

