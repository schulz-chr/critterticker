from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('seacreatures', views.sea_creatures, name="seacreatures"),
    path('fish', views.fish, name="fish"),
    path('bugs', views.bugs, name="bugs"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
