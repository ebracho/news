#
# Article models
#

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

redis_client = settings.REDIS_CLIENT

DOMAINS = [
    'http://pcmag.com',
    'https://www.yahoo.com/news',
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


class ArticleQueue(models.Model):
    """User model for MyNews.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    @property
    def id(self):
        return 'user:{.username}:articlequeue'.format(self.user)

    @property
    def size():
        return redis_client.zcard(self.article_queue_id)

    def pop():
        article_url = redis_client.zrange(self.article_queue_id, 0, -1)
        redis_client.zrem(self.article_queue_id, article_url)
        return article_url

    def update(self, article_scores):
        """Populates user's article queue with url-score pairs in 
        `article_scores` dict
        """
        redis_client.zadd(**article_scores)
        

