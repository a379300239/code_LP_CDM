import imp
from django.contrib import admin
from django.urls import include, path
from lp import views

urlpatterns = [
    path('', views.lp,name='lp'),
    path('lp/', views.lp,name='lp'),
    path('dcm', views.dcm,name='dcn'),
    path('submitLp', views.submitLp,name='submitLp'),
]