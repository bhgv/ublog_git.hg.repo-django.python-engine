# -*- coding:utf-8 -*-
from my_django.contrib.admin import site, ModelAdmin

import models

site.register(models.Forum,
    list_display = ['name', 'ordering', 'group'],
    list_editable = ['ordering', 'group'],
)

site.register(models.Topic,
    list_display = ['subject', 'created', 'forum'],
    list_filter = ['forum'],
)

site.register(models.Article)

site.register(models.Profile,
    list_display = ['user', 'moderator',
    
    'is_banned',
    # --
    'last_post',
    'last_edit',
    # --
    'max_posts',
    'today_posts',
    # --
    'max_topics',
    'today_topics',
    # --
    'max_edits',
    'today_edits',
    # --
    'total_posts',
    'carma',
    ],
#    list_filter = ['moderator'],
    search_fields = ['user__username'],
)
