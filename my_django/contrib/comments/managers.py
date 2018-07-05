from my_django.db import models
from my_django.contrib.contenttypes.models import ContentType
from my_django.utils.encoding import force_unicode

class CommentManager(models.Manager):

    def in_moderation(self):
        """
        QuerySet for all comments currently in the moderation queue.
        """
        return self.get_query_set().filter(is_public=False, is_removed=False)

    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_query_set().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_unicode(model._get_pk_val()))
        return qs
