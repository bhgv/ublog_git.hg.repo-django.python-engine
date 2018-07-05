from my_django.contrib import admin
from django_hg.models import HgRepository, RepositoryUser

class UserInline(admin.TabularInline):
    model=RepositoryUser

class HgRepositoryAdmin(admin.ModelAdmin):
    inlines=[UserInline,]

admin.site.register(HgRepository, HgRepositoryAdmin)
