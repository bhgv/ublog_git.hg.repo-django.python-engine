from my_django.contrib import admin
from my_django.contrib.sites.models import Site


class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name')
    search_fields = ('domain', 'name')

admin.site.register(Site, SiteAdmin)