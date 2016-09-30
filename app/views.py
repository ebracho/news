import random
from functools import wraps
from flask import request, session, render_template, jsonify, abort
from oauth2client import client, crypt
from app import app, db
from app.models import User, Article, ArticleView


def requires_login(view):
    @wraps(view)
    def decorator(*args, **kwargs):
        if not 'usersub' in session:
            abort(401)
        user = db.session.query(User).filter(User.sub == session['usersub']).first()
        if not user:
            db.session.add(User(session['usersub']))
            db.session.commit()
        return view(*args, **kwargs)
    return decorator
    

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/google-signin', methods=['POST'])
def google_signin():
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

