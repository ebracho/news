import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

# Flask configuration
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Google Signin configuration
#app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')

# GitHub Signin Config
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']

# SQLAlchemy configuration 
default_db_uri = 'sqlite:////tmp/news_test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Celery configuration
celery = Celery('news', backend='amqp://', broker='amqp://')

