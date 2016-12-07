#
# Article models
#

import math
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

redis_client = settings.REDIS_CLIENT

DOMAINS = [
    'http://pcmag.com',
    'http://vox.com',
    'http://theweek.com',
]

class Article(models.Model):
    """Stores information about a web article
    """
    url = models.CharField(max_length=256, primary_key=True)
    title = models.TextField()
    text = models.TextField()
    image = models.CharField(max_length=256)
    domain = models.CharField(max_length=256)
    published = models.DateTimeField(default=timezone.now)


class ArticleView(models.Model):
    """Stores information about a user's encounter with an Article
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clicked = models.BooleanField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('article', 'user')

    @staticmethod
    def get_clicked_articles(user):
        return ArticleView.objects.filter(user=user).filter(clicked=True).all()

    @staticmethod
    def get_skipped_articles(user):
        return ArticleView.objects.filter(user=user).filter(clicked=False).all()

class ArticleQueue(models.Model):
    """User model for MyNews.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    @property
    def id(self):
        return 'user:{.username}:articlequeue'.format(self.user)

    @property
    def size(self):
        return redis_client.zcard(self.id)

    def pop(self):
        """Pops the article with the highest click score and returns 
        the article, score
        """
        if self.size == 0:
            raise ValueError('Empty article queue cannot be popped from')
        article_url, score = redis_client.zrange(self.id, -1, -1, withscores=True)[0]
        redis_client.zrem(self.id, article_url)
        article = Article.objects.filter(url=article_url).first()
        return article, score

    def pop_random(self, subsection):
        """Pops a random article from the first `subsection` percent of the
        article queue, where 0 > `subsection` >= 1
        """
        if self.size == 0:
            raise IndexError('Empty article queue cannot be popped from')
        if not (0 <= subsection <= 1):
            raise ValueError('subsection must be greater and less than or equal to 1')
        end_index = math.ceil(self.size * subsection)
        articles = redis_client.zrevrange(self.id, 0, end_index, withscores=True)
        article_url, score = random.choice(articles)
        redis_client.zrem(self.id, article_url)
        article = Article.objects.filter(url=article_url).first()
        return article, score

    def update(self, article_scores):
        """Repopulates user's article queue with url-score pairs in 
        `article_scores` dict
        """
        redis_client.delete(self.id)
        redis_client.zadd(self.id, **article_scores)
        

