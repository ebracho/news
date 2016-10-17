from .models import Article, ArticleView

def get_unread_articles(user):
    """Return a list of Articles that have not been read by user
    """
    return Article.objects.exclude(articleview__user=user).all()


def news_cli(user):
    """Command line interface for clicking/skipping articles
    """
    unread = get_unread_articles(user)
    for article in unread:
        inp = input('{} (c/s) '.format(article.title))
        if inp == 'c':
            ArticleView(article=article, user=user, clicked=True).save()
        elif inp == 's':
            ArticleView(article=article, user=user, clicked=False).save()
        elif inp == 'q':
            break
        else:
            print('unrecognized input')

