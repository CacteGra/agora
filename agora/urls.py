"""agora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings

from oikos import views as oikos_views


urlpatterns = [
    url(r'^$', oikos_views.home, name='home'),
    url(r'^bluetooth_primal_set/$', oikos_views.bluetooth_primal_set, name='bluetooth_primal_set'),
    url(r'^power_off/$', oikos_views.power_off, name='power_off'),
    url(r'^wifi_turn/(?P<wifi_device_id>\d+)/$', oikos_views.wifi_turn, name='wifi_turn'),
    url(r'^wifi_scan/$', oikos_views.wifi_scan, name='wifi_scan'),
    url(r'^wifi_connect/$', oikos_views.wifi_connect, name='wifi_connect'),
    url(r'^hotspot_turn/(?P<wifi_device_id>\d+)/$', oikos_views.hotspot_turn, name='hotspot_turn'),
    url(r'^hotspot_submit/$', oikos_views.hotspot_submit, name='hotspot_submit'),
    url(r'^bluetooth_turn/(?P<bluetooth_device_id>\d+)/$', oikos_views.bluetooth_turn, name='bluetooth_turn'),
    url(r'^bluetooth_scan/$', oikos_views.bluetooth_scan, name='bluetooth_scan'),
    url(r'^bluetooth_pair/$', oikos_views.bluetooth_pair, name='bluetooth_pair'),
]

