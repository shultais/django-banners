# -*- coding: utf-8 -*-
from banners.models import Zone, Placement
from django.core.cache import cache
from django.db.models import F


class BannersMiddleware(object):
    def __init__(self):
        self.banners_zones = {}
        self.banners_zones_eng = {}

    def process_request(self, request):
        self.banners_zones, self.banners_zones_eng = cache.get('banners_zones'), cache.get('banners_zones_eng')
        if not self.banners_zones or not self.banners_zones_eng:
            self.banners_zones, self.banners_zones_eng = {}, {}
            zones = Zone.objects.all().values("id", "html_pre_banner", "html_after_banner", "english_name")
            for zone in zones:
                self.banners_zones[zone["id"]] = zone
                if zone.has_key("english_name") and zone["english_name"]:
                    self.banners_zones_eng[zone["english_name"]] = zone["id"]
            cache.set('banners_zones', self.banners_zones, 60 * 60 * 24 * 365)
            cache.set('banners_zones_eng', self.banners_zones_eng, 60 * 60 * 24 * 365)
        request.banners_zones = self.banners_zones
        request.banners_zones_eng = self.banners_zones_eng
        request.banners_placement_shows = []

    def process_response(self, request, response):
        # На больших нагрузках происходят факапы
        #if response.status_code == 200 and request.banners_placement_shows:
            #Placement.objects.filter(id__in=request.banners_placement_shows).update(shows=F("shows") + 1)
        return response
