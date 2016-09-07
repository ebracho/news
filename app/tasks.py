from datetime import datetime, timedelta, timezone
import newspaper
from newspaper import news_pool
from app import db, celery
from app.models import Domain, Article


# PST timezone for datetime functions
PST = timezone(-timedelta(hours=8))


@celery.task(ignore_results=True)
def scrape_articles():
    """Retrieves and stores new articles from each domain in the database.
    """
    # Open log file
    logfile = open('news.tasks.log', 'a')
    logfile.write(datetime.now(PST).strftime('SCHEDULED SCRAPE %c\n'))

    # Build papers
    logfile.write('Building papers...\n')
    papers = [newspaper.build(d.url) for d in db.session.query(Domain).all()]

    # Filter out seen articles to save bandwidth/cpu
    logfile.write('Filtering seen articles...\n')
    seen_articles = {a.url for a in db.session.query(Article).all()}
    for paper in papers:
        paper.articles = list(filter(lambda a: a.url not in seen_articles, paper.articles))

    # Download new articles from each domain concurrently
    n_articles = sum(map(lambda p: len(p.articles), papers))
    logfile.write('Downloading {} articles...\n'.format(n_articles))
    news_pool.set(papers)
    news_pool.join()
    
    # Parse and store new articles
    for paper in papers:
        domain_url = paper.url
        logfile.write('Parsing articles from {}\n'.format(domain_url))
        for a in paper.articles:
            try:
                a.parse()
                if not a.title or not a.text or a.meta_lang != 'en':
                    continue
                entry = Article(a.url, domain_url, a.title, a.publish_date, a.text, a.top_image)
                db.session.add(entry)
                db.session.commit()
            except Exception as e:
                logfile.write('===============ERROR===============')
                logfile.write(e)
                logfile.write('===================================')
            else:
                logfile.write('Article written: {}\n'.format(a.url))

    # Close log file
    logfile.write('\n')
    logfile.close()
                
            
# Register scrape_articles as periodic task

CELERYBEAT_SCHEDULE = {
    'hourly_article_scrape': {
        'task': 'news.scrape_articles',
        'schedule': timedelta(hours=1),
    },
}

celery.conf.update(
    CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE,
)

