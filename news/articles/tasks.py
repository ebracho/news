#
# Celery tasks
#

import newspaper
from newspaper import news_pool
import tldextract
from .models import Article

def parse_source(url):
    """Return stripped url containing only domain and suffix"""
    return '{0.domain}.{0.suffix}'.format(tldextract.extract(url))

def scrape_articles(sources=[]):
    """Crawls domains in sources and scrapes new web articles"""

    papers = [newspaper.build(s, memoize_articles=False) for s in sources]
    news_pool.set(papers, threads_per_source=1)
    news_pool.join()

    for paper in papers:
        paper_source = parse_source(paper.url)
        for article in paper.articles:
            article_source = parse_source(article.url)
            if article_source != paper_source:
                continue
            article.parse()
            a = Article(url=article.url, 
                        title=article.title,
                        text=article.text, 
                        image=article.top_image,
                        source=article_source)
            a.save()

