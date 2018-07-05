"""
Django Unit Test and Doctest framework.
"""

from my_django.test.client import Client, RequestFactory
from my_django.test.testcases import (TestCase, TransactionTestCase,
    SimpleTestCase, LiveServerTestCase, skipIfDBFeature,
    skipUnlessDBFeature)
from my_django.test.utils import Approximate
