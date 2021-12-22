# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from django.conf import settings

from app import views

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
]

# if settings.DEBUG:
#     urlpatterns.extend([
#         # Matches any html file
#         # re_path(r'^.*\.*', views.pages, name='pages'),
#         # re_path('', views.pages, name='pages'),
#     ])