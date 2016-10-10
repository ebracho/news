#
# Celery tasks
#

import logging
import newspaper
from newspaper import news_pool
from tldextract import extract
from .models import Article, DOMAINS

logger = logging.getLogger(__name__)

def parse_source(url):
    """Return stripped url containing only domain and suffix"""
    return '{0.domain}.{0.suffix}'.format(extract(url))

def scrape_articles(domains=DOMAINS):
    """Crawls domains and scrapes new web articles"""

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

