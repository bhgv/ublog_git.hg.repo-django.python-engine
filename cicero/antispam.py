# -*- coding:utf-8 -*-
from my_django.core.urlresolvers import reverse
from my_django.utils.encoding import smart_str
#from scipio import antispam
#from scipio.antispam import akismet
#from scipio.models import Profile as ScipioProfile

from cicero import utils

class OldTopicHandler:
    def validate(self, request, article, **kwargs):
        if article and article.topic.old() and article.from_guest():
            return 'old_topic'

#class AkismetHandler(akismet.AkismetBaseHandler):
#    def get_params(self, request, article, **kwargs):
#        text = article.text
#        if article.topic.article_set.count() == 1: # new topic
#            text = article.topic.subject + '\n' + text
##        try:
##            openid = article.author.user.scipio_profile.openid
##        except ScipioProfile.DoesNotExist:
##            openid = ''
#        openid = ''
#        return {
#            'blog': utils.absolute_url(reverse('cicero_index')),
#            'user_ip': article.ip,
#            'permalink': utils.absolute_url(reverse(
#                'cicero.views.topic',
#                args=[article.topic.forum.slug, article.topic.id],
#            )),
#            'comment_type': 'post',
#            'comment_author': smart_str(article.from_guest() and article.guest_name or article.author),
#            'comment_author_url': smart_str(openid),
#            'comment_content': smart_str(text),
#        }

conveyor = None
#antispam.Conveyor([
#    antispam.WhitelistHandler(),
#    antispam.HoneyPotHandler(),
#    AkismetHandler(),
#    OldTopicHandler(),
#])