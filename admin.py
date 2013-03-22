# -*- coding: utf-8 -*-
from django.contrib import admin
from banners.models import Zone, Banner,  Placement
from banners import clear_banners_cache


class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "english_name")
    list_per_page = 30

    def save_model(self, request, obj, form, change):
        clear_banners_cache()
        obj.save()


class BannerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'banner_type',)
        }),
        (u"Параметры", {
            'classes': ('wide',),
            'fields': ('foreign_url', 'width', 'height')
        }),
        (None, {
            'classes': ('wide',),
            'fields': ('swf_file', 'img_file', 'html_text')
        })
    )
    list_display = ("name", "banner_type", "width", "height")
    list_per_page = 30

    def save_model(self, request, obj, form, change):
        clear_banners_cache()
        obj.save()


class PlacementAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('banner', 'zones', 'frequency')
        }),
        (u"Клики", {
            'classes': ('wide',),
            'fields': ('clicks', 'max_clicks')
        }),
        (u"Показы", {
            'classes': ('wide',),
            'fields': ('shows', 'max_shows')
        }),
        (u"Период размещения", {
            'classes': ('wide',),
            'fields': ('begin_date', 'end_date')
        })
    )
    search_fields = ("banner__name",)
    list_display = ( "banner", "get_zones", "frequency", "clicks", "max_clicks", "shows", "max_shows", "begin_date", "end_date", "get_status")

    def save_model(self, request, obj, form, change):
        clear_banners_cache()
        obj.save()

admin.site.register(Banner, BannerAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Placement, PlacementAdmin)