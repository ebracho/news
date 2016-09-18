from flask import request, session, render_template
from oauth2client import client, crypt
from app import app, db
from app.models import User


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
    session['userid'] = idinfo['sub']
    return ''
        
    
