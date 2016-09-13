import os
import logging
from datetime import timedelta
import newspaper
from newspaper import news_pool
from app import db, celery
from app.models import Domain, Article


# Task logger
logfile = os.environ.get('CELERY_LOGFILE', './celery.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(logfile)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


@celery.task(ignore_results=True)
def scrape_articles():
    """Retrieves and stores new articles from each domain in the database.
    """
    # Open log file
    logger.info('Beginning Schedule Scrape')

    # Build papers
    try:
        papers = [newspaper.build(d.url, memoize_articles=False) for d in db.session.query(Domain).all()]
    except Exception as e:
        logger.error('Error loading papers. Aborting')
        logger.error(e)
        return

    # Filter out seen articles to save bandwidth/cpu
    seen_articles = {a.url for a in db.session.query(Article).all()}
    for paper in papers:
        paper.articles = list(filter(lambda a: a.url not in seen_articles, paper.articles))

    # Download new articles from each domain concurrently
    try:
        news_pool.set(papers)
        news_pool.join()
    except Exception as e:
        logger.error('Error downloading papers. Aborting') 
        logger.error(e)
        return
    
    # Parse and store new articles
    written_articles = 0
    for paper in papers:
        domain_url = paper.url
        for a in paper.articles:
            try:
                a.parse()
                if not a.title or not a.text or a.meta_lang != 'en':
                    continue
                entry = Article(a.url, domain_url, a.title, a.publish_date, a.text, a.top_image)
                db.session.add(entry)
                db.session.commit()
                logger.info('Article written: {}'.format(a.url))
            except Exception as e:
                logger.error('Error parsing article {}'.format(a.url))
                logger.error(e)
            else:
                written_articles += 1

    logger.info('{} new articles written\n'.format(written_articles))
                

@celery.task
def add(x, y):
    return x + y

#
# Register scrape_articles as periodic task
#
CELERYBEAT_SCHEDULE = {
    'hourly_article_scrape': {
        'task': 'app.tasks.scrape_articles',
        'schedule': timedelta(hours=1),
    },
}


#
# Celery Settings
#
celery.conf.update(
    CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE,
)

