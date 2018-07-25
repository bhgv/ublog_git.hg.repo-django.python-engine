# -*- coding:utf-8 -*-
import cPickle as pickle

from my_django.db import models
#from my_django.db.models.fields.related import SingleRelatedObjectDescriptor
try:
    from my_django.db.models.fields.related import SingleRelatedObjectDescriptor
except ImportError:
    from my_django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor as SingleRelatedObjectDescriptor

class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor): # this line just can't be too long, right?
    def __get__(self, instance, instance_type=None):
        cached_name = '_cached_' + self.related.get_accessor_name()
        if not hasattr(instance, cached_name):
            try:
                obj = super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
            except self.related.model.DoesNotExist:
                obj = self.related.model(**{self.related.field.name: instance})
                obj.save()
            setattr(instance, cached_name, obj)
        return getattr(instance, cached_name)

class AutoOneToOneField(models.OneToOneField):
    '''
    OneToOneField, которое создает зависимый объект при первом обращении
    из родительского, если он еще не создан.
    '''
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))

class RangesField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if not value:
            return [(0, 0)]
        return pickle.loads(str(value))

    def get_db_prep_value(self, value, connection, prepared=False):
        return unicode(pickle.dumps(value))
