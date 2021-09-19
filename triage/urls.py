from django.urls import path
from .views import *

urlpatterns=[
    path('decodefiscalcode/', DecodeFiscalCodeView.as_view(), name='decode_fiscal_code'),
    path('testdfxapi/', TestDFXApiView.as_view(), name='test_dfx_api'),
    path('receptions/', ReceptionsView.as_view(), name='receptions'),

]