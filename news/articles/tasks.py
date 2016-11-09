#
# Celery tasks
#

import itertools
import logging
import newspaper
from newspaper import news_pool
from tldextract import extract
from celery import shared_task
from .models import Article, ArticleView, DOMAINS

logger = logging.getLogger(__name__)

#
# Article scraping
#

def parse_source(url):
    """Return stripped url containing only domain and suffix.
    """
    return '{0.domain}.{0.suffix}'.format(extract(url))


@shared_task
def scrape_articles(domains=DOMAINS):
    """Crawls domains and scrapes new web articles.
    """
    papers = [newspaper.build(s, memoize_articles=False) for s in domains]
    news_pool.set(papers, threads_per_source=1)
    news_pool.join()

    for domain, paper in zip(domains, papers):
        paper_source = parse_source(domain)
        for article in paper.articles:
            article_source = parse_source(article.url)
            if article_source != paper_source:
                continue
            article.parse()
            a = Article(url=article.url, 
                        title=article.title,
                        text=article.text, 
                        image=article.top_image,
                        domain=domain)
            a.save()

    n_articles = sum(map(lambda p: len(p.articles), papers))
    logmsg = '{} articles crawled'.format(n_articles)
    logger.info(logmsg)


#
# Article classification
#

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from django.conf import settings
from .util import get_unread_articles

redis_client = settings.REDIS_CLIENT

# Pipeline for processing and classifying text data.
nb_pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfdif', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

def build_training_set(user):
    """Build NB classifier traning set for a given user's article views.
    """
    article_views = ArticleView.objects.filter(user=user).all()
    data = [av.article.text for av in article_views]
    labels = ['clicked' if av.clicked else 'skipped' for av in article_views]
    return (data, labels)


def build_classifier(user):
    """Create and fit an NB classifier for a given user's article views.
    """
    data, labels = build_training_set(user)
    return nb_pipeline.fit(data, labels)


@shared_task
def build_article_queue(user):
    """Repopulate user's article queue with unread articles ordered by 
    click probability. Does nothing if user has less than 5 clicked and
    5 skipped articles.
    """
    clicked = ArticleView.get_clicked_articles(user)
    skipped = ArticleView.get_skipped_articles(user)
    if len(clicked) < 5 or len(skipped) < 5:
        return
    clf = build_classifier(user)
    unread_articles = get_unread_articles(user)
    probs = clf.predict_proba(a.text for a in unread_articles)
    scores = { a.url: p[0] for a, p in zip(unread_articles, probs) }
    user.articlequeue.update(scores)

