from django.urls import path
from .views import *

# dashboards/
urlpatterns=[
    
    ## General settings ##
    path('', RedirectView.as_view(), name='video_first_page',kwargs={"url_name":"video_settings"}),
    path('videosettings/', VideoSettingsView.as_view(), name='videosettings'),
    path('editsetting/', EditSettingView.as_view(), name='new_setting'),
    path('editsetting/<int:setting_id>/', EditSettingView.as_view(), name='edit_setting'),
    path('deletesetting/<int:setting_id>/', DeleteSettingView.as_view(), name='delete_setting'),
    path('preview_image/<int:setting_id>/', PreviewImageView.as_view(), name='preview_image')
]
