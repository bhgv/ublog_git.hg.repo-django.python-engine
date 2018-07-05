from __future__ import absolute_import

from my_django.test import TestCase
from my_django.contrib.gis import admin

from .models import City


class GeoAdminTest(TestCase):
    urls = 'my_django.contrib.gis.tests.geoadmin.urls'

    def test01_ensure_geographic_media(self):
        geoadmin = admin.site._registry[City]
        admin_js = geoadmin.media.render_js()
        self.assertTrue(any([geoadmin.openlayers_url in js for js in admin_js]))

