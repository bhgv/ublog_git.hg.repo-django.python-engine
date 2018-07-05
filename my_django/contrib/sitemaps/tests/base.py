import os

from my_django.conf import settings
from my_django.contrib.auth.models import User
from my_django.contrib.sites.models import Site
from my_django.test import TestCase


class SitemapTestsBase(TestCase):
    protocol = 'http'
    domain = 'example.com' if Site._meta.installed else 'testserver'
    urls = 'my_django.contrib.sitemaps.tests.urls.http'

    def setUp(self):
        self.base_url = '%s://%s' % (self.protocol, self.domain)
        self.old_USE_L10N = settings.USE_L10N
        self.old_TEMPLATE_DIRS = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = (
            os.path.join(os.path.dirname(__file__), 'templates'),
        )
        self.old_Site_meta_installed = Site._meta.installed
        # Create a user that will double as sitemap content
        User.objects.create_user('testuser', 'test@example.com', 's3krit')

    def tearDown(self):
        settings.USE_L10N = self.old_USE_L10N
        settings.TEMPLATE_DIRS = self.old_TEMPLATE_DIRS
        Site._meta.installed = self.old_Site_meta_installed
