from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    if request.user.is_authenticated:
        return HttpResponse('Hello {}!'.format(request.user.username))
    return HttpResponse('Hello Stranger!')
    
