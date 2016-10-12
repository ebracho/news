from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', auth_views.logout, {'next': '/'}, name='logout'),
    url('^register/', views.register, name='register'),
]

