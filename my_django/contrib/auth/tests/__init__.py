from my_django.contrib.auth.tests.auth_backends import (BackendTest,
    RowlevelBackendTest, AnonymousUserBackendTest, NoBackendsTest,
    InActiveUserBackendTest, NoInActiveUserBackendTest)
from my_django.contrib.auth.tests.basic import BasicTestCase
from my_django.contrib.auth.tests.context_processors import AuthContextProcessorTests
from my_django.contrib.auth.tests.decorators import LoginRequiredTestCase
from my_django.contrib.auth.tests.forms import (UserCreationFormTest,
    AuthenticationFormTest, SetPasswordFormTest, PasswordChangeFormTest,
    UserChangeFormTest, PasswordResetFormTest)
from my_django.contrib.auth.tests.remote_user import (RemoteUserTest,
    RemoteUserNoCreateTest, RemoteUserCustomTest)
from my_django.contrib.auth.tests.management import (
    GetDefaultUsernameTestCase,
    ChangepasswordManagementCommandTestCase,
)
from my_django.contrib.auth.tests.models import (ProfileTestCase, NaturalKeysTestCase,
    LoadDataWithoutNaturalKeysTestCase, LoadDataWithNaturalKeysTestCase,
    UserManagerTestCase)
from my_django.contrib.auth.tests.hashers import TestUtilsHashPass
from my_django.contrib.auth.tests.signals import SignalTestCase
from my_django.contrib.auth.tests.tokens import TokenGeneratorTest
from my_django.contrib.auth.tests.views import (AuthViewNamedURLTests,
    PasswordResetTest, ChangePasswordTest, LoginTest, LogoutTest,
    LoginURLSettings)

# The password for the fixture data users is 'password'
