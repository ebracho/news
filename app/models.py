from collections import Counter
from app import db


class Domain(db.Model):
    __tablename__ = 'domain'
    url = db.Column(db.Unicode(256), primary_key=True)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return '<Domain {}>'.format(self.url)


class Article(db.Model):
    __tablename__ = 'article'
    url = db.Column(db.Unicode(2048), primary_key=True)
    domain_url = db.Column(db.Unicode(256), db.ForeignKey('domain.url'))
    title = db.Column(db.Unicode(256))
    publish_date = db.Column(db.DateTime)
    text = db.Column(db.Unicode(200)) # First 200 characters of article text
    image_url = db.Column(db.Unicode(2048))
    word_count = db.Column(db.PickleType)
    
    def __init__(self, url, domain_url, title, publish_date, text, image_url):
        self.url = url
        self.domain_url = domain_url
        self.title = title
        self.publish_date = publish_date
        self.text = text if len(text) < 200 else text[:200]
        self.image_url = image_url
        self.word_count = Counter(text.split())

    def __repr__(self):
        return '<Article {}>'.format(self.title)
        

