# -*- coding: utf-8 -*-
import  random
from datetime import datetime as dt
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from banners.models import Zone, Placement, Banner
from django.core.urlresolvers import reverse
from django.core.cache import cache


def placement(request, placement_id):
   p = get_object_or_404(Placement, id=placement_id)
   p.clicks += 1
   p.save()
   return HttpResponseRedirect(p.banner.foreign_url)


def w_choice(lst):
    n = random.uniform(0, 1)
    for item, weight, plc in lst:
        if n < weight: break
        n = n - weight
    return item, plc


def normalize(lst):
    sum, new_lst = 0., []
    for item, weight, plc in lst:
        sum += weight
    for item, weight, plc in lst:
        new_lst.append([item, weight/sum, plc])
    return new_lst


def gen_banner_code(request, zone_id):
    zone, hbanner = None, u""

    zones = getattr(request, "banners_zones", None)
    zones_eng = getattr(request, "banners_zones_eng", None)

    if not request.META.has_key('banners.clients'): request.META['banners.clients'] = []

    # Поиск зоны
    zone_id = str(zones_eng[zone_id]) if (zones and zones_eng.has_key(zone_id)) else str(zone_id)
    try:
        if zone_id.isdigit():
            if zones and zones.has_key(int(zone_id)):
                zone = zones[int(zone_id)]
            else:
                zone = Zone.objects.get(id=zone_id).__dict__
        else:
            zone = Zone.objects.get(english_name=zone_id.lower()).__dict__
    except Exception:
        zone = None
        # Создание зоны и сайта если его еще не существует
        if not zone_id.isdigit():
            zone = Zone(
                english_name=zone_id.lower(),
                name=zone_id.lower()
            )
            zone.save()
            zone = zone.__dict__

    #try:
    #    if zone_id.isdigit(): zone = Zone.objects.get(id=zone_id)
    #    else: zone = Zone.objects.get(english_name=zone_id.lower())
    #except Exception:
    #    if not zone_id.isdigit():
    #        zone = Zone(english_name=zone_id.lower(), name=zone_id.lower())
    #        zone.save()

    if zone:
        placement = cache.get("banner_placement.%s" % zone["id"])
        if not placement:
            placement = Placement.objects.filter(
                (Q(begin_date__lte=dt.now()) | Q(begin_date__isnull=True)),
                (Q(end_date__gte=dt.now()) | Q(end_date__isnull=True)),
                (Q(max_clicks__gt=F('clicks')) | Q(max_clicks=0)),
                (Q(max_shows__gt=F('shows')) | Q(max_shows=0)), zones__id = zone["id"]).select_related().order_by('-id').values()
            cache.set("banner_placement.%s" % zone["id"], list(placement), 60*30)

        count = len(placement)

        banner, plc = False, False
        if count == 1:
            plc = placement[0]
            banner = placement[0]["banner_id"]
        elif count > 1:
            banners = [[t_p["banner_id"], t_p["frequency"], t_p] for t_p in placement]
            banner, plc = w_choice(normalize(banners))

        if banner:
            request.banners_placement_shows.append(plc["id"])

            # Кэшируем баннер
            hbanner = cache.get("hbanner.%s" % banner)
            if not hbanner:
                b = Banner.objects.get(id=banner)
                img_url = b.img_file.url if b.img_file else ""
                swf_url = b.swf_file.url if b.swf_file else ""

                code = u""

                # Flash-баннер
                if b.banner_type == 'f':
                    banner_href = reverse("banners:placement", kwargs={"placement_id":plc["id"]})
                    template = get_template("ibanners/gen_banner_code.html")
                    context = Context({
                        "banner_width":b.width,
                        "banner_height":b.height,
                        "data":u"%s?banner_href=%s" % (swf_url, banner_href),
                        "swf_url":swf_url,
                        "banner_href":banner_href,
                        "img_url":img_url,
                        "foreign_url":b.foreign_url,
                    })
                    code += template.render(context)
                # графические баннеры
                elif b.banner_type == 'g':
                    if b.foreign_url: code += u"<a href=\"%s\" target=\"_blank\" style=\"border-width:0;\">" % reverse("banners:placement", kwargs={"placement_id":plc["id"]})
                    code += u"""<img src="%s" width="%s" height="%s" style="border-width:0"/>""" % (img_url, b.width, b.height)
                    if b.foreign_url: code += u"""</a>"""
                # html баннеры
                elif b.banner_type == 'h':
                    code += b.html_text
                hbanner = code
            else:
                pass

            if hbanner:
                hbanner = u"%s%s%s" % (zone["html_pre_banner"], hbanner, zone["html_after_banner"])
            else:
                hbanner= u""
            cache.set("hbanner.%s" % banner, hbanner, 60*30)
        return hbanner
    # Если зона не найдена
    else:
        return u""
