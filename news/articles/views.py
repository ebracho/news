import random
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from articles.models import Article

#
# Site views
#

@login_required(login_url='/login/')
def index(request):
    return render(request, 'articles/index.html', {})
    

#
# Web API
#

@login_required(login_url='/login/')
def article(request):
    """Returns an unread article that best matches the user's history
    """
    aq = request.user.articlequeue
    if aq.size > 0:
        article = aq.pop()
    else:
        article = random.choice(Article.objects.all())
    data = {
        'articleUrl': article.url,
        'title': article.title,
        'text': article.text[:500],
        'imageUrl': article.image,
        'domain': article.domain,
        'published': article.published
    }
    return JsonResponse(data)

