from datetime import datetime, timedelta, timezone
import newspaper
from newspaper import news_pool
from celery.utils.log import get_task_logger
from app import db, celery
from app.models import Domain, Article


# PST timezone for datetime functions
PST = timezone(-timedelta(hours=8))

# Task logger
logger = get_task_logger(__name__)


@celery.task(ignore_results=True)
def scrape_articles():
    """Retrieves and stores new articles from each domain in the database.
    """
    print('this is a test')

    # Open log file
    logger.info(datetime.now(PST).strftime('SCHEDULED SCRAPE %c\n'))

    # Build papers
    papers = [newspaper.build(d.url, memoize_articles=False) for d in db.session.query(Domain).all()]

    # Filter out seen articles to save bandwidth/cpu
    seen_articles = {a.url for a in db.session.query(Article).all()}
    for paper in papers:
        paper.articles = list(filter(lambda a: a.url not in seen_articles, paper.articles))

    # Download new articles from each domain concurrently
    news_pool.set(papers)
    news_pool.join()
    
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
            except Exception as e:
                logger.error('@@@@@@@@@@@@@@ SCRAPE_ARTICLES ERROR @@@@@@@@@@@@@@')
                logger.error('Error Downloading Article {}'.format(a.url))
                logger.error(e)
                logger.error('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            else:
                written_articles += 1

    logger.info('{} new articles written\n'.format(written_articles))
                

#
# Register scrape_articles as periodic task
#
CELERYBEAT_SCHEDULE = {
    'hourly_article_scrape': {
        'task': 'news.scrape_articles',
        'schedule': timedelta(hours=1),
    },
}


#
# Celery Settings
#
celery.conf.update(
    CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE,
    CELERYD_HIJACK_ROOT_LOGGER=True,
)

