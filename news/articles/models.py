from django.db import models
from django.contrib.auth.models import User
from urllib.parse import urlparse
from django.utils import timezone

class Article(models.Model):
    """Stores information about a web article"""

    url = models.CharField(max_length=256, primary_key=True)
    text = models.TextField()
    source = models.CharField(max_length=256)
    image = models.CharField(max_length=256)
    published = models.DateTimeField(default=timezone.now)

    def __init__(self, url, text, image, published=None):
        self.url = url
        self.text = text
        self.source = urlparse(url).netloc
        self.image = image
        if published:
            self.published = published

class ArticleView(models.Model):
    """Stores information about a user's encounter with an Article"""

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clicked = models.BooleanField()
    read = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('article', 'user')

    def __init__(self, article, user, clicked, read=False):
        self.article = article
        self.user = user
        self.clicked = clicked
        self.read = read

