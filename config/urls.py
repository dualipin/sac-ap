from django.contrib import admin
from django.urls import path, include
from apps import api

urlpatterns = [
    path('api/', include(api.urlpatterns)),
]
