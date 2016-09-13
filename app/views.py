from flask import request, session, render_template
from oauth2client import client, crypt
from app import app


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
        print(idinfo)
    except crypt.AppIdentityError:
        abort(401)
    session['userid'] = idinfo['sub']
    return ''
        
    
