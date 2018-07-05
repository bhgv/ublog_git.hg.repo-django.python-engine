from my_django.test import TestCase

from my_django.contrib.formtools.tests.wizard.storage import TestStorage
from my_django.contrib.formtools.wizard.storage.session import SessionStorage


class TestSessionStorage(TestStorage, TestCase):
    def get_storage(self):
        return SessionStorage
