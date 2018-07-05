from my_django.conf import settings
from my_django.utils.unittest import skipUnless

from .base import SitemapTestsBase

class FlatpagesSitemapTests(SitemapTestsBase):

    @skipUnless("my_django.contrib.flatpages" in settings.INSTALLED_APPS,
                "my_django.contrib.flatpages app not installed.")
    def test_flatpage_sitemap(self):
        "Basic FlatPage sitemap test"

        # Import FlatPage inside the test so that when my_django.contrib.flatpages
        # is not installed we don't get problems trying to delete Site
        # objects (FlatPage has an M2M to Site, Site.delete() tries to
        # delete related objects, but the M2M table doesn't exist.
        from my_django.contrib.flatpages.models import FlatPage

        public = FlatPage.objects.create(
            url=u'/public/',
            title=u'Public Page',
            enable_comments=True,
            registration_required=False,
        )
        public.sites.add(settings.SITE_ID)
        private = FlatPage.objects.create(
            url=u'/private/',
            title=u'Private Page',
            enable_comments=True,
            registration_required=True
        )
        private.sites.add(settings.SITE_ID)
        response = self.client.get('/flatpages/sitemap.xml')
        # Public flatpage should be in the sitemap
        self.assertContains(response, '<loc>%s%s</loc>' % (self.base_url, public.url))
        # Private flatpage should not be in the sitemap
        self.assertNotContains(response, '<loc>%s%s</loc>' % (self.base_url, private.url))
