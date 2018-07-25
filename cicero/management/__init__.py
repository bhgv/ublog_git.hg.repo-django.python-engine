# -*- coding:utf-8 -*-
from my_django.db.models import signals
from cicero.models import Forum, Topic, Article, Profile

from datetime import datetime


def create_system_user(username):
    from my_django.contrib.auth.models import User
    from cicero.models import Profile
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        password = User.objects.make_random_password()
        user = User.objects.create_user(username, username + '@localhost', password)
        Profile(
            user=user, 
            # --
            max_posts = 0,
            today_posts = 0,
            # --
            max_topics = 0,
            today_topics = 0,
            # --
            max_edits = 0,
            today_edits = 0,
            # --
            total_posts = 0,
            # --
            carma = 0,
            today_change_carmas = 0,
            max_change_carmas = 0,
            # --
            last_post = datetime.now().date(),
            last_edit = datetime.now().date(),
            # --
            registered_date = datetime.now().date(),
            #registered_ip = request.META['REMOTE_ADDR']
            # --
            max_repos = 0,
            used_repos = 0,
        ).save()

def create_test_forum(slug, name, group):
    from cicero.models import Forum
    if Forum.objects.count() == 0:
        Forum.objects.create(slug=slug, name=name, group=group)

def init(sender, **kwargs):
    import cicero.models
    if kwargs['app'] == cicero.models:
        create_system_user('cicero_guest')
        create_system_user('cicero_search')
        create_test_forum('test', u'Тестовый форум', u'Тест')

signals.post_syncdb.connect(init)
