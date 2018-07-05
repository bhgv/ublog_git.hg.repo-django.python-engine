from my_django.db.backends.mysql.base import *
from my_django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from my_django.contrib.gis.db.backends.mysql.creation import MySQLCreation
from my_django.contrib.gis.db.backends.mysql.introspection import MySQLIntrospection
from my_django.contrib.gis.db.backends.mysql.operations import MySQLOperations

class DatabaseWrapper(MySQLDatabaseWrapper):

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = MySQLCreation(self)
        self.ops = MySQLOperations(self)
        self.introspection = MySQLIntrospection(self)
