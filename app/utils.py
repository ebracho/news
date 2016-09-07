"""
Contains misc. useful functions.
"""
import newspaper
from app import db
from app.models import Domain


def add_domain(url):
    """Extract meta data about news source and add it to the database
    """
    src = newspaper.Source(url)
    if db.session.query(Domain).filter(Domain.url == src.url).first():
        print('Domain {} already exists'.format(url))
    else:
        src.download()
        src.parse()
        domain = Domain(url, src.brand, src.description)
        db.session.add(domain)
        db.session.commit()

