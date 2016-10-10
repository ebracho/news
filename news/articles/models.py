#
# Article models
#

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Article(models.Model):
    """Stores information about a web article"""

    url = models.CharField(max_length=256, primary_key=True)
    title = models.TextField()
    text = models.TextField()
    image = models.CharField(max_length=256)
    source = models.CharField(max_length=256)
    published = models.DateTimeField(default=timezone.now)


class ArticleView(models.Model):
    """Stores information about a user's encounter with an Article"""

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clicked = models.BooleanField()
    read = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('article', 'user')

