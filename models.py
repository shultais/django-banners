# -*- coding: utf-8 -*-

from django.db import models
from datetime import datetime as dt

BANNER_TYPES = (
    ('g', u'графический баннер'),
    ('f', u'Flash-баннер'),
    ('h', u'HTML-баннер'),
)


class Zone(models.Model):
    name = models.CharField(u"название", max_length=255, blank=False, null=False)
    english_name = models.CharField(u"название по-английски", max_length=255, blank=False, null=False)
    html_pre_banner = models.CharField(u"HTML перед баннером", max_length=255, blank=True, default="")
    html_after_banner = models.CharField(u"HTML после баннера", max_length=255, blank=True, default="")

    class Meta(object):
        verbose_name = u"зона"
        verbose_name_plural = u"зоны"
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class Banner(models.Model):
    name = models.CharField(u"название", max_length=255, null=False, blank=False)
    banner_type = models.CharField(u"Тип баннера", max_length=1, choices=BANNER_TYPES)

    foreign_url = models.CharField(max_length=200, blank=True, verbose_name=u"URL перехода",default="") # Внешний URL куда ведет баннер
    width = models.CharField(u"Ширина", blank=True, default="", null=False, max_length=100, help_text=u"После значения указывайте единицы, например 100px или 30%")
    height = models.CharField(u"Высота", blank=True, null=False, default="", max_length=100, help_text=u"После значения указывайте единицы, например 100px или 30%")

    # Прорабатываем баннеры
    swf_file = models.FileField(u"SWF файл", upload_to="ibas/swf", blank=True, help_text=u"Только для Flash баннеров", null=True)
    img_file = models.FileField(u"Изображение", upload_to="ibas/img", blank=True, help_text=u"Использовать для графических баннеров", null=True)
    html_text = models.TextField(u"HTML текст", blank=True, null=False, default="")

    class Meta(object):
        verbose_name = u"баннер"
        verbose_name_plural = u"баннеры"
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class Placement(models.Model):
    banner = models.ForeignKey(Banner, verbose_name=u"баннер")
    zones = models.ManyToManyField(Zone, verbose_name=u"зоны", related_name="zones")
    frequency = models.PositiveIntegerField(u"частота", help_text="чем больше частота, тем чаще баннер будет показываться", blank=False, null=False, default=1)
    
    # Статистика
    clicks = models.PositiveIntegerField(u"Кликов", blank=True, default=0)
    shows = models.PositiveIntegerField(u"Показов", blank=True, default=0)
    # Ограничения
    max_clicks = models.PositiveIntegerField(u"Лимит кликов", blank=True, default=0, null=False, help_text=u"0 - лимит не ограничен")
    max_shows = models.PositiveIntegerField(u"Лимит показов", blank=True, default=0, null=False, help_text=u"0 - лимит не ограничен")
    begin_date = models.DateTimeField(u"Дата начала", null=True, blank=True)
    end_date = models.DateTimeField(u"Дата окончания", null=True, blank=True)

    class Meta(object):
        verbose_name = u"размещение"
        verbose_name_plural = u"размещения"
        ordering = ["banner__name"]

    def get_status(self):
        # Не активен
        if (self.max_clicks != 0 and self.max_clicks <= self.clicks) or \
           (self.max_shows != 0 and self.max_shows <= self.shows) or \
           (self.begin_date and self.begin_date > dt.now()) or \
           (self.end_date and self.end_date < dt.now()):
            return u"<span style=\"color:#ccc;\">Неактивен</span>"
        return u"<span style=\"color:green;\">Активен</span>"
    get_status.short_description = u"Статус"
    get_status.allow_tags = True

    def get_zones(self):
        zones = u"<ul>"
        for zone in self.zones.all():
            zones += u"<li>* %s</li>" % zone.name
        zones += "</ul>"
        return zones
    get_zones.short_description = u"Зоны"
    get_zones.allow_tags = True

    def __unicode__(self):
        return self.banner.name