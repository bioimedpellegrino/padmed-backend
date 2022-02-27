from django.urls import path
from django.conf.urls import url
from .views import *

#triage/
urlpatterns=[
    # Triage
    path('', RedirectView.as_view(), name='triage_first_page',kwargs={"url_name":"user_conditions"}),
    path('userconditions/', UserConditions.as_view(), name='user_conditions'),
    path('receptions/', ReceptionsView.as_view(), name='receptions'),
    path('accessreason/<int:access_id>', ReceptionsReasonsView.as_view(), name='accessreason'),
    path('recordvideo/<int:access_id>/', RecordVideoView.as_view(), name='record_video'),
    path('patientresults/', PatientResults.as_view(), name='patient_results'),
    path('patientresults_error/', PatientResultsError.as_view(), name='patient_results_error'),
    
    #NFC and test Pages
    path('testnfc/', TestNFC.as_view(), name='test'),
    path('videoselecting/', VideoSelecting.as_view(), name='videoselecting'),
    # DFXAPI
    path('testdfxapi/', TestDFXApiView.as_view(), name='test_dfx_api'),
    
    ## AJAX GET
    path('get_access_status/', GetAccessStatusView.as_view(), name='get_access_status'),

]