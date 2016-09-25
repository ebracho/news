import random
from flask import request, session, render_template, jsonify, abort
from oauth2client import client, crypt
from app import app, db
from app.models import User, Article, ArticleView


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
def get_article():
    if not 'usersub' in session:
        abort(401)
    article = random.choice(db.session.query(Article).all())
    return jsonfiy(
        url=article.url, title=article.title, text=article.text, 
        image_url=article.image_url)
    

@app.route('/view-article', methods=['POST'])
def view_article():
    if not 'usersub' in session:
        abort(401)
    article_url = request.form.get('article_url', None)
    clicked = request.form.get('clicked', None)
    if not all([article_url, clicked]):
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
    db.session.commit()
    return ''
