from django.urls import path
from django.conf.urls import url
from .views import *

# dashboards/
urlpatterns=[
    path('', LiveView.as_view(), name='live_view'),
]