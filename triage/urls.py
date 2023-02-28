from django.urls import path
from django.conf.urls import url
from .views import *

#triage/
urlpatterns=[
    # Triage
    path('', RedirectView.as_view(), name='triage_first_page',kwargs={"url_name":"user_conditions"}),
    path('splash/', SplashView.as_view(), name='splash'),
    path('userconditions/', UserConditions.as_view(), name='user_conditions'),
    path('receptions/', ReceptionsView.as_view(), name='receptions'),
    path('accessanagrafica/<int:access_id>', AnagraficaView.as_view(), name='access_anagrafica'),
    path('accessreason/<int:access_id>', ReceptionsReasonsView.as_view(), name='accessreason'),
    path('preparevideomeasure/<int:access_id>', PrepareVideoMeasureView.as_view(), name='prepare_video_measure'),
    path('recordvideo/<int:access_id>/', RecordVideoView.as_view(), name='record_video'),
    path('patientresults/', PatientResults.as_view(), name='patient_results'),
    path('patientresultsmock/', ResultsMock.as_view(), name='patient_results_mock'),
    path('patientresults_error/', PatientResultsError.as_view(), name='patient_results_error'),
    path('endpage/', EndPageView.as_view(), name='end_page'),
    #NFC and test Pages
    path('testnfc/', TestNFC.as_view(), name='test'),
    path('videoselecting/', VideoSelecting.as_view(), name='videoselecting'),
    # DFXAPI
    path('testdfxapi/', TestDFXApiView.as_view(), name='test_dfx_api'),
    
    ## AJAX GET
    path('get_access_status/', GetAccessStatusView.as_view(), name='get_access_status'),

]