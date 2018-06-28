"""card_db URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^runs/', include('qie_cards.runs_urls', namespace='runs')),
    url(r'^cards/', include('qie_cards.card_urls', namespace='cards')),
    url(r'^rm/', include('qie_cards.rm_urls')),
    url(r'^cu/', include('qie_cards.cu_urls')),
    url(r'^sipm/', include('qie_cards.sipm_urls')),
    url(r'^$', RedirectView.as_view(pattern_name='cards:catalog',permanent=False)),
    url(r'^admin/', admin.site.urls),
]

