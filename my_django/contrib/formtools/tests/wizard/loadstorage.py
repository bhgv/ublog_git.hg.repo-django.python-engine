from my_django.test import TestCase

from my_django.contrib.formtools.wizard.storage import (get_storage,
                                                     MissingStorageModule,
                                                     MissingStorageClass)
from my_django.contrib.formtools.wizard.storage.base import BaseStorage


class TestLoadStorage(TestCase):
    def test_load_storage(self):
        self.assertEqual(
            type(get_storage('my_django.contrib.formtools.wizard.storage.base.BaseStorage', 'wizard1')),
            BaseStorage)

    def test_missing_module(self):
        self.assertRaises(MissingStorageModule, get_storage,
            'my_django.contrib.formtools.wizard.storage.idontexist.IDontExistStorage', 'wizard1')

    def test_missing_class(self):
        self.assertRaises(MissingStorageClass, get_storage,
            'my_django.contrib.formtools.wizard.storage.base.IDontExistStorage', 'wizard1')

