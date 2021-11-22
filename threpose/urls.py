"""threpose URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from users import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views
from django.views.static import serve
from theme import views as homepage

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('admin', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('trip.urls', namespace="trip")),
    path('search/', include('search.urls', namespace="search")),
    path('planner/', include('planner.urls', namespace="planner")),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('profile', views.profile, name='profile'),
    path('editprofile/', views.edit_profile, name='editprofile'),
    path('ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
    path('about-us/', homepage.about_us, name='about-us'),
    path('feedback/', homepage.feedback, name='feedback'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
