# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('banners.views',
   url(regex=r'^(?P<placement_id>\d+)/$', view='placement', name='placement'),
)