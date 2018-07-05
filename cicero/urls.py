# -*- coding:utf-8 -*-
from my_django.conf.urls.defaults import *
from my_django.conf import settings

from my_django.views.generic.list_detail import object_list, object_detail
from my_django.contrib.syndication.views import Feed as feed
from cicero import views
from cicero import feeds
from cicero.models import Forum, Topic, Article, Profile
from cicero.context import default

info = views.generic_info

urlpatterns = patterns('',
    (r'^(.*/)?cauth/login/$', views.login),
    (r'^(.*/)?cauth/logout/$', views.logout),
    (r'^(.*/)?cauth/newuser/$', views.newuser),
#    (r'^users/', include('scipio.urls')),
    url(r'^users/(?P<object_id>\d+)/$', object_detail, {
        'queryset': Profile.objects.all(),
        'context_processors': [default],
        'extra_context': {'page_id': 'profile', 'groups': views._get_left_side_cont()},
    }, name='profile'),
    (r'^users/(\d+)/topics/$', views.user_topics),
    (r'^users/self/$', views.edit_profile),
    (r'^users/self/openid/$', views.change_openid),
    (r'^users/self/(personal|settings)/$', views.post_profile),
    url(r'^$', views.index, {
        'queryset': Forum.objects.filter(is_forum=True).all(),
        'context_processors': [default],
        'extra_context': {'page_id': 'index', 'groups': views._get_left_side_cont()},
    }, name='cicero_index'),
    url(r'^articles_list/$', views.articles_list, {
        'queryset': Forum.objects.filter(is_forum=False).all(),
        'context_processors': [default],
        'extra_context': {'page_id': 'index', 'groups': views._get_left_side_cont()},
    }, name='cicero_articles_list'),
    url(r'^users/self/deleted_articles/$', views.deleted_articles, {'user_only': True}, name='deleted_articles'),
    (r'^mark_read/$', views.mark_read),
    (r'^([a-z0-9-]+)/mark_read/$', views.mark_read),
    url(r'^deleted_articles/$', views.deleted_articles, {'user_only': False}, name='all_deleted_articles'),
    (r'^article_preview/$', views.article_preview),
    (r'^article_edit/(\d+)/$', views.article_edit),
    (r'^article_delete/(\d+)/$', views.article_delete),
    (r'^article_undelete/(\d+)/$', views.article_undelete),
    (r'^spam_queue/$', views.spam_queue),
    (r'^article_publish/(\d+)/$', views.article_publish),
    (r'^article_spam/(\d+)/$', views.article_spam),
    (r'^delete_spam/$', views.delete_spam),
    (r'^topic_edit/(\d+)/$', views.topic_edit),
    (r'^topic_spawn/(\d+)/$', views.topic_spawn),
    (r'^to_article/(\d+)/$', views.topic_to_article),
    url(r'^feeds/(?P<url>.*)/$', feed, {'feed_dict': {
        'articles': feeds.Article,
    }}, name='cicero_feeds'),
    
    (r'^carma/([_A-Za-z0-9-]+)/([id][ne]c)/$', views.carma, info),
    
    (r'^([a-z0-9-]+)/$', views.forum, info),
    (r'^([a-z0-9-]+)/(\d+)/$', views.topic, info),
    (r'^([a-z0-9-]+)/search/$', views.search),
)
