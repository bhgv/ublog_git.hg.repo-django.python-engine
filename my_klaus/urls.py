# -*- coding: utf-8 -*-
from my_django.conf.urls import url

from my_klaus import views
from my_klaus.views_comment import post_comment,clone_repo,update_settings

# TODO: These regexps are probably not going to cover all the cases
repo = r'(?P<repo>[\w\.\-_]+)'
rev = r'(?P<rev>[\w\.\-_]+)'
path = r'(?P<path>.+)'
#app_name = 'klaus'

urlpatterns = [
    url(r'^add_repo/$', clone_repo, name='clone_repo'),
    url(r'^comment/$', post_comment, name='post_comment'),

    url(r'^$',
        views.repo_list, name=views.RepoListView.view_name),

    url(r'^' + repo + '/$',
        views.history, name=views.HistoryView.view_name),

    url(r'^' + repo + '/tree/' + rev + '/$',
        views.history, name=views.HistoryView.view_name),
    url(r'^' + repo + '/tree/' + rev + '/' + path + '/$',
        views.history, name=views.HistoryView.view_name),

    url(r'^' + repo + '/blob/' + rev + '/$',
        views.blob, name=views.BlobView.view_name),
    url(r'^' + repo + '/blob/' + rev + '/' + path + '/$',
        views.blob, name=views.BlobView.view_name),

    url(r'^' + repo + '/raw/' + rev + '/$',
        views.raw, name=views.RawView.view_name),
    url(r'^' + repo + '/raw/' + rev + '/' + path + '/$',
        views.raw, name=views.RawView.view_name),

    url(r'^' + repo + '/commit/' + rev + '/$',
        views.commit, name=views.CommitView.view_name),

    url(r'^' + repo + '/settings/$',
        views.settings, name=views.SettingsView.view_name),
    url(r'^' + repo + '/settings/update_settings/$', update_settings, name='update_settings'),

]
