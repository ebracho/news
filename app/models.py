"""
Database models for MyNews
Datetime columns use UTC
"""


from collections import Counter
from datetime import datetime
from app import db


class Domain(db.Model):
    __tablename__ = 'domain'
    url = db.Column(db.Unicode(256), primary_key=True)
    brand = db.Column(db.Unicode(128))
    description = db.Column(db.Unicode(2048))
    

    def __init__(self, url, brand, description):
        self.url = url
        self.brand = brand
        self.description = description

    def __repr__(self):
        return '<Domain {}>'.format(self.url)


class Article(db.Model):
    __tablename__ = 'article'
    url = db.Column(db.Unicode(512), primary_key=True)
    domain_url = db.Column(db.Unicode(256), db.ForeignKey('domain.url'))
    title = db.Column(db.Unicode(256))
    publish_date = db.Column(db.DateTime)
    text = db.Column(db.Unicode(256)) # First 256 characters of article text
    image_url = db.Column(db.Unicode(512))
    word_count = db.Column(db.PickleType)
    
    def __init__(self, url, domain_url, title, publish_date, text, image_url):
        self.url = url
        self.domain_url = domain_url
        self.title = title
        self.publish_date = publish_date or datetime.utcnow()
        self.text = text if len(text) < 256 else text[:256]
        self.image_url = image_url
        self.word_count = Counter(text.split())

    def __repr__(self):
        return '<Article {}>'.format(self.title)
        

class User(db.Model):
    __tablename__ = 'user'
    sub = db.Column(db.String(256), primary_key=True)
    join_date = db.Column(db.DateTime)

    def __init__(self, sub, join_date=None):
        self.sub = sub
        self.join_date = join_date or datetime.utcnow()
    
    
