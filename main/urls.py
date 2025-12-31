from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views 

urlpatterns = [
    path('', views.home_yt, name='home_yt'),
    path('get_info/', views.get_info, name='get_info'),
    path('dl_from_opt/', views.dl_from_opt, name='dl_from_opt'),
    path('user_def_cookie/', views.user_def_cookie, name='user_def_cookie'),
    path('<path:subpath>/', views.home_yt, name='home_yt'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)