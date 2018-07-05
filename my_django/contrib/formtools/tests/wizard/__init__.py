from my_django.contrib.formtools.tests.wizard.cookiestorage import TestCookieStorage
from my_django.contrib.formtools.tests.wizard.forms import FormTests, SessionFormTests, CookieFormTests
from my_django.contrib.formtools.tests.wizard.loadstorage import TestLoadStorage
from my_django.contrib.formtools.tests.wizard.namedwizardtests.tests import (
    NamedSessionWizardTests,
    NamedCookieWizardTests,
    TestNamedUrlSessionWizardView,
    TestNamedUrlCookieWizardView,
    NamedSessionFormTests,
    NamedCookieFormTests,
)
from my_django.contrib.formtools.tests.wizard.sessionstorage import TestSessionStorage
from my_django.contrib.formtools.tests.wizard.wizardtests.tests import (
    SessionWizardTests,
    CookieWizardTests,
    WizardTestKwargs,
    WizardTestGenericViewInterface,
    WizardFormKwargsOverrideTests,
)
