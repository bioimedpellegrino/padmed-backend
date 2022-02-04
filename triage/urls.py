from django.urls import path
from django.conf.urls import url
from .views import *

#triage/
urlpatterns=[
    # Triage
    path('userconditions/', UserConditions.as_view(), name='user_conditions'),
    path('receptions/', ReceptionsView.as_view(), name='receptions'),
    path('accessreason/<int:access_id>', ReceptionsReasonsView.as_view(), name='accessreason'),
    path('recordvideo/<int:access_id>/', RecordVideoView.as_view(), name='record_video'),
    path('patientresults/', PatientResults.as_view(), name='patient_results'),
    
    #NFC and test Pages
    path('testnfc/', TestNFC.as_view(), name='test'),
    
    # DFXAPI
    path('testdfxapi/', TestDFXApiView.as_view(), name='test_dfx_api'),

]