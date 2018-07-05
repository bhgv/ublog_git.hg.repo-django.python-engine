from my_django.contrib import admin

from .models import Repo, Comment

admin.site.register(Repo)
admin.site.register(Comment)