import random
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from articles.models import Article, ArticleView
from articles.tasks import build_article_queue

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
@csrf_exempt
def get_article(request):
    """Returns an unread article that best matches the user's history
    """
    aq = request.user.articlequeue
    if aq.size > 0:
        article, score = aq.pop_random(0.4)
    else:
        article = random.choice(Article.objects.all())
        score = 0.666
    data = {
        'articleUrl': article.url,
        'title': article.title,
        'text': article.text[:500],
        'imageUrl': article.image,
        'domain': article.domain,
        'published': article.published,
        'score': score
    }
    return JsonResponse(data)


@login_required(login_url='/login/')
@csrf_exempt
def view_article(request):
    """Registeres a viewed article as 'clicked' or 'skipped'
    """
    article_url = request.POST.get('articleUrl', None)
    clicked = request.POST.get('clicked', None)
    if not article_url and clicked:
        return HttpResponseBadRequest('Missing Parameters')
    clicked = clicked == 'true'
    article = Article.objects.filter(url=article_url).first()
    if not article:
        return HttpResponseBadRequest('Article not found')
    av = ArticleView.objects.filter(article=article, user=request.user).first()
    if av is None:
        av = ArticleView(article=article, user=request.user, clicked=clicked)
    else:
        av.clicked = clicked
    av.save()
    # Rebuild user's article queue
    build_article_queue.delay(request.user)
    return HttpResponse('')


@login_required(login_url='/login/')
@csrf_exempt
def get_reading_queue(request):
    """Returns a list of articles that were clicked but are not yet read 
    by the user
    """
    rq = (
        ArticleView.objects
        .filter(user=request.user)
        .filter(clicked=True)
        .filter(read=False)
        .order_by('timestamp')
        .all()
    )
    data = [{
        'url': av.article.url,
        'title': av.article.title,
    } for av in rq]
    return JsonResponse({ 'readingQueue': data })


@login_required(login_url='/login/')
@csrf_exempt
def read_article(request):
    article_url = request.POST.get('articleUrl', None)
    if not article_url:
        return HttpResponseBadRequest()
    article = Article.objects.filter(url=article_url).first()
    if not article:
        return HttpResponseBadRequest()
    av = ArticleView.objects.filter(article=article, user=request.user).first()
    if not av:
        return HttpResponseBadRequest()
    av.read = True
    av.save()
    return HttpResponse('')

