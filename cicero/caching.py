# -*- coding:utf-8 -*-
'''
Вспомогательные методы для расчета и кеширования времени
последнего изменения страниц форума. Используются для
if_modified_since.
'''
import md5

from my_django.core.cache import cache
from my_django.conf import settings

from cicero.models import Forum, Article

def cached(key_func):
    '''
    Кеширующий декоратор.
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = str(key_func(*args, **kwargs))
            value = cache.get(key)
            if not value:
                value = func(*args, **kwargs)
                cache.set(key, value)
            return value
        return wrapper
    return decorator

@cached(lambda request, slug=None, topic_id=None, *args, **kwargs: 'alc-%s-%s' % (slug, topic_id))
def latest_change(request, slug=None, topic_id=None, *args, **kwargs):
    '''
    Запрос времени последнего обновления статей.
    '''
    if request.user.is_authenticated() and request.user.cicero_profile.moderator:
        return None
    def prepare(qs):
        if slug:
            qs = qs.filter(topic__forum__slug=slug)
        if topic_id:
            qs = qs.filter(topic__id=topic_id)
        return qs.order_by('-updated')

    updated_qs = prepare(Article.objects.all())
    deleted_qs = prepare(Article.deleted_objects.all())
    updated_time = len(updated_qs) and updated_qs[0].updated
    deleted_time = len(deleted_qs) and deleted_qs[0].deleted
    return (updated_time and deleted_time and max(updated_time, deleted_time)) or updated_time or deleted_time or None

@cached(lambda request, *args, **kwargs: 'ulc-%s' % request.COOKIES.get(settings.SESSION_COOKIE_NAME, None))
def user_etag(request, *args, **kwargs):
    '''
    Запрос поьзовательского etag'а.
    '''
    if (not request.user.is_authenticated()) :
        return '"None"'
    print "tst1 %s\n" % (str(request.user),)
    print "tst2 %s\n" % (request.user.cicero_profile,)
    print "tst3 %s\n" % (str(request.user.cicero_profile.read_articles),)
#    print "tst %s\n" % (str(request.user.cicero_profile.read_articles),)

    return md5.new(str(request.user.cicero_profile.read_articles)).hexdigest()
#    return md5.new(str(request.user)).hexdigest()

def invalidate_by_article(slug, topic_id):
    '''
    Инвалидация ключей кеша времени обновления статей.
    '''
    cache.delete(str('alc-%s-%s' % (None, None)))
    cache.delete(str('alc-%s-%s' % (slug, None)))
    cache.delete(str('alc-%s-%s' % (slug, topic_id)))

def invalidate_by_user(request):
    '''
    Инвалидация ключей кеша состояния пользователя.
    '''
    cache.delete(str('ulc-%s' % request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)))
