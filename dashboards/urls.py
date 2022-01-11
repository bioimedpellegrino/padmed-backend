from django.urls import path
from .views import *

# dashboards/
urlpatterns=[
    
    ## Dashboard ## 
    path('live', LiveView.as_view(), name='live_dash'),
    path('access/<int:id>', AccessView.as_view(), name='access'),
    path('storico', StoricoView.as_view(), name='storico_dash'),
    path('post_live_access_status', SetLiveAccessStatus.as_view(), name='post_live_access_status'),
    path('post_storico_access_status', SetStoricoAccessStatus.as_view(), name='post_storico_access_status'),
    
    ## User ## 
    path('user-profile', UserProfileView.as_view(), name='user_profile'),
    
    ## Hospitals ## 
    path('hospitals', HospitalsView.as_view(), name='hospitals'),
    path('hospital/<int:id>', HospitalEditView.as_view(), name='hospital_edit'),
    
    ## Patients ## 
    path('patients', PatientsView.as_view(), name='patients'),
    path('patient/<int:id>', PatientView.as_view(), name='patient'),
    path('patient/<int:id>/edit', PatientEditView.as_view(), name='patient_edit'),
    
    ## Totems ## 
    path('totem/<int:id>', TotemEditView.as_view(), name='totem'),
    
    ## AJAX VIEWS ##
    path('lot_table', GetStoricoData.as_view(), name='get_storico_data'),
]
