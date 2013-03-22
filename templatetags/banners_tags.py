# -*- coding: utf-8 -*-

from django import template
from banners.views import gen_banner_code

class BannerNode(template.Node):
    def __init__(self, request, zone_id):
        self.request = template.Variable(request)
        self.zone_id = int(zone_id) if zone_id.isdigit() else zone_id

    def render(self, context):
        return gen_banner_code(self.request.resolve(context), self.zone_id)

def do_banner(parser, token):
    try:
        tokens = token.split_contents()
        if tokens.__len__() == 3:
            tag_name, request, zone_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a 2 arguments" % token.contents.split()[0]
    return BannerNode(request, zone_id)

register = template.Library()
register.tag('banner', do_banner)
