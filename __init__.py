# -*- coding: utf-8 -*-
from django.core.cache import cache

def clear_banners_cache():
    from banners.models import Banner, Zone, Placement

    cache.delete("banners_zones")
    cache.delete("banners_zones_eng")

    for zone in Zone.objects.all():
        cache.delete("banner_placement.%s" % zone.id)

    for banner in Banner.objects.all():
        cache.delete("hbanner.%s" % banner.id)