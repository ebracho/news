from collections import Counter
from datetime import datetime
from functools import partial
from app import db


# MySQL defaults to 3-byte unicode encodings for some strange reason.
# This column type will collate to 4-byte unicode encoding.
Unicode9 = partial(db.Unicode, collation='utf8mb4_unicode_ci')


class Domain(db.Model):
    __tablename__ = 'domain'
    url = db.Column(Unicode9(256), primary_key=True)
    brand = db.Column(Unicode9(128))
    description = db.Column(Unicode9(2048))
    

    def __init__(self, url, brand, description):
        self.url = url
        self.brand = brand
        self.description = description

    def __repr__(self):
        return '<Domain {}>'.format(self.url)


class Article(db.Model):
    __tablename__ = 'article'
    url = db.Column(Unicode9(512), primary_key=True)
    domain_url = db.Column(Unicode9(256), db.ForeignKey('domain.url'))
    title = db.Column(Unicode9(256))
    publish_date = db.Column(db.DateTime)
    text = db.Column(Unicode9(256)) # First 256 characters of article text
    image_url = db.Column(Unicode9(512))
    word_count = db.Column(db.PickleType)
    
    def __init__(self, url, domain_url, title, publish_date, text, image_url):
        self.url = url
        self.domain_url = domain_url
        self.title = title
        self.publish_date = publish_date or datetime.now()
        self.text = text if len(text) < 256 else text[:256]
        self.image_url = image_url
        self.word_count = Counter(text.split())

    def __repr__(self):
        return '<Article {}>'.format(self.title)
        

