from django.urls import path
from .views import *

urlpatterns=[
    path('triage/decodefiscalcode/', DecodeFiscalCodeView.as_view(), name='decode_fiscal_code'),

]