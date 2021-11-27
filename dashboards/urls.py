from django.urls import path
from .views import *

# dashboards/
urlpatterns=[
    path('live', LiveView.as_view(), name='live_dash'),
    path('storico', StoricoView.as_view(), name='storico_dash'),
    path('icons', IconsView.as_view(), name='icons'),
    path('maps', MapsView.as_view(), name='maps'),
    path('user-profile', UserProfileView.as_view(), name='user_profile'),
    
    ## AJAX Views
    
    path('lot_table', GetStoricoData.as_view(), name='get_storico_data'),
]