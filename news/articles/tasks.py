#
# Celery tasks
#

import logging
import newspaper
from newspaper import news_pool
from tldextract import extract
from .models import Article, ArticleView, DOMAINS

logger = logging.getLogger(__name__)

#
# Article scraping
#

def parse_source(url):
    """Return stripped url containing only domain and suffix.
    """
    return '{0.domain}.{0.suffix}'.format(extract(url))


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

# Pipeline for processing and classifying text data.
nb_pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfdif', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

def build_training_set(user):
    """Build an NB classifier traning set for a given user's article views.
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

def get_unread_articles(user):
    """Return a list of Articles that have not been read by user
    """
    return Article.objects.exclude(articleview__user=user).all()
