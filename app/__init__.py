import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Flask configuration
app = Flask(__name__)

# SQLAlchemy configuration 
default_db_uri = 'sqlite:////tmp/news_test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

