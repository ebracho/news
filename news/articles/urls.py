from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_article/$', views.get_article, name='get_article'),
    url(r'^view_article/$', views.view_article, name='view_article'),
    url(r'^get_reading_queue/$', views.get_reading_queue, name='get_reading_queue'),
    url(r'^read_article/$', views.read_article, name='read_article'),
]

