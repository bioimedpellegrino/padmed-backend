from django.urls import path
from django.conf.urls import url
from .views import *

#triage/
urlpatterns=[
    # Triage
    path('decodefiscalcode/', DecodeFiscalCodeView.as_view(), name='decode_fiscal_code'),
    path('receptions/', ReceptionsView.as_view(), name='receptions'),
    path('receptions_accessreason/<int:access_id>/<int:reason_id>/', ReceptionsReasonsView.as_view(), name='receptions_accessreason'),
    path('recordvideo/<int:access_id>/', RecordVideoView.as_view(), name='record_video'),
    path('patientresults/', PatientResults.as_view(), name='patient_results'),
    
    # DFXAPI
    path('testdfxapi/', TestDFXApiView.as_view(), name='test_dfx_api'),

]