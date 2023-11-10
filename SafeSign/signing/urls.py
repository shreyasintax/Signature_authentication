from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'homepage'),
    path('about', views.about, name = 'about'),
    path('clientsite', views.clientsite, name = 'clientsite'),
    path('signup', views.signup, name = 'signup'),
    path('signin', views.signin, name = 'signin'),
    path('signout', views.signout, name = 'signout'),
    path('signin_sign', views.signin_sign, name = 'signin_sign'),
    path('signin_pass', views.signin_pass, name = 'signin_pass'),
]