# coding=utf-8
#!/usr/bin/env python
if __name__ == '__main__':
    import os.path, sys
    try:
        from my_django.core.management import setup_environ
    except:
        print "Unable to import setup_environ"
        sys.exit(1)
    # define PROJECT_PATH to a django project that use
    PROJECT_PATH = os.path.abspath('../../../Sites/chaptrz/projects/core/')
    sys.path.append(PROJECT_PATH)
    try:
        import settings
    except ImportError:
        print "Unable to import settings. You need to define PROJECT_PATH to a"
        + "django project that use django_hg"
        sys.exit(1)
    setup_environ(settings)

import os

from my_django.test import TestCase
from my_django.test.client import Client
from my_django.core.urlresolvers import reverse
from my_django.conf import settings as global_settings

from django_hg.models import HgRepository


class CommandsTest(TestCase):
    '''
    Test the commands view when an Hg client requests a clone/pull/push throught
    django_hg
    '''
    fixtures = ['djangohgauth.json','repositories.json']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_unknown_repository_returns_404(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'foo'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_repository_in_db_but_not_in_FS(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'bar'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'})
        self.failUnlessEqual(response.status_code, 404)


    def test_commands_auth_not_required(self):
        '''
        no authentication is needed as anonymous access to the repository is
        allowed
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'},
                                   follow= False,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)

    def test_commands_unknown_command(self):
        '''
        pass an unknown command
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django'}),
                                   {'cmd': 'foo'},
                                   follow= False,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)

    def test_commands_known_command_but_no_required_params(self):
        '''
        pass a known command
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django'}),
                                   {'cmd': 'between'},
                                   follow= False,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)

    def test_commands_auth_required_but_not_provided(self):
        '''
        an authentication is needed to access to the repository but no user is
        provided
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django_hg'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'
                                   },
                                   follow= False,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 401)

    def test_commands_auth_required_with_a_valid_user_(self):
        '''
        an authentication is needed, a valid user is provided
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django_hg'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'
                                   },
                                   follow= True,
                                   **{'HTTP_AUTHORIZATION': 'Basic b3duZXI6cGFzc3dvcmQ=',
                                      'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)

    def test_commands_auth_required_with_an_invalid_user(self):
        '''
        an authentication is needed, an invalid (unknown user or bad password)
        user is provided
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django_hg'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'
                                   },
                                   follow= True,
                                   **{'HTTP_AUTHORIZATION': 'Basic Z291bHdlbjphVGgjMjJOQA==',
                                      'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 401)

    def test_commands_auth_required_with_a_valid_user_but_not_contributor(self):
        '''
        an authentication is needed, a valid user is provided but he doesn't
        belong to the contributors
        '''
        response = self.client.get(reverse('hg-repo',
                                           None,
                                           None,
                                           {'name': 'django_hg'}),
                                   {'cmd': 'between',
                                    'pairs': '0000000000000000000000000000000000000000-0000000000000000000000000000000000000000'
                                   },
                                   follow= True,
                                   **{'HTTP_AUTHORIZATION': 'Basic cmVhZGVyOnBhc3N3b3Jk',
                                      'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 401)


class BrowseTest(TestCase):
    fixtures = ['djangohgauth.json', 'repositories.json']
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    
    def test_unknown_repository_returns_404(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'foo', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_repository_in_db_but_not_in_FS(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'foo', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_required_elements_in_context(self):
        """
        tests the presence of required elements in the context passed to the
        template
        """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failIfEqual(ctx['repo'], None)
        self.failIfEqual(ctx['rev'], None)

    def test_browse_anonymous_access(self):
        """ the repository is accessible without authentication"""
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].anonymous_access, True)

    def test_browse_login_required(self):
        """
        the repository is not accessible without authentication, no user
        given, so we get a redirection to login page
        """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django_hg', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])
    
    def test_browse_login_required_owner_given(self):
        """
        the repository is not accessible without authentication, the owner of
        the repository is given, we get the detail page
        """
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django_hg', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].user_can_read(ctx['user']), True)

    def test_browse_login_required_not_member_given(self):
        """
        the repository is not accessible without authentication, a user that
        doesn't belongs to members is given, we get a redirection to login page
        """
        self.client.login(username='no_permission', password='password')
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django_hg', 'action': 'browse'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])

class ChangesetsTest(TestCase):
    fixtures = ['djangohgauth.json', 'repositories.json']
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_unknown_repository_returns_404(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'foo', 'action': 'changesets'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_repository_in_db_but_not_in_FS(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'foo', 'action': 'changesets'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_changesets_anonymous_access(self):
        """ the repository is accessible without authentication"""
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django', 'action': 'changesets'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].anonymous_access, True)

    def test_changesets_login_required(self):
        """
        the repository is not accessible without authentication, no user
        given, so we get a redirection to login page
        """
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django_hg', 'action': 'changesets'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])
    
    def test_changesets_login_required_owner_given(self):
        """
        the repository is not accessible without authentication, the owner of
        the repository is given, we get the detail page
        """
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django_hg', 'action': 'changesets'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].user_can_read(ctx['user']), True)

    def test_changesets_login_required_not_member_given(self):
        """
        the repository is not accessible without authentication, a user that
        doesn't belongs to members is given, we get a redirection to login page
        """
        self.client.login(username='no_permission', password='password')
        response = self.client.get(reverse('hg-repo-action',
                                           None,
                                           None,
                                           {'name': 'django_hg', 'action': 'changesets'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])

class ChangesetTest(TestCase):
    fixtures = ['djangohgauth.json', 'repositories.json']
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_unknown_repository_returns_404(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'foo',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_repository_in_db_but_not_in_FS(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'foo',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_required_elements_in_context(self):
        """
        tests the presence of required elements in the context passed to the
        template
        """
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'django',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failIfEqual(ctx['repo'], None)
        self.failIfEqual(ctx['rev'], None)

    def test_changesets_anonymous_access(self):
        """ the repository is accessible without authentication"""
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'django',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].anonymous_access, True)


    def test_changesets_login_required(self):
        """
        the repository is not accessible without authentication, no user
        given, so we get a redirection to login page
        """
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])

    def test_changesets_login_required_owner_given(self):
        """
        the repository is not accessible without authentication, the owner of
        the repository is given, we get the detail page
        """
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].user_can_read(ctx['user']), True)

    def test_changesets_login_required_not_member_given(self):
        """
        the repository is not accessible without authentication, a user that
        doesn't belongs to members is given, we get a redirection to login page
        """
        self.client.login(username='no_permission', password='password')
        response = self.client.get(reverse('hg-repo-action-rev',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 1}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])


class DiffTest(TestCase):
    fixtures = ['djangohgauth.json', 'repositories.json']
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    
    def test_unknown_repository_returns_404(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'foo',
                                            'action': 'changesets',
                                            'rev': 1,
                                            'path': 'bar'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_repository_in_db_but_not_in_FS(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'bar',
                                            'action': 'changesets',
                                            'rev': 1,
                                            'path': 'bar'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_required_elements_in_context(self):
        """
        tests the presence of required elements in the context passed to the
        template
        """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django',
                                            'action': 'changesets',
                                            'rev': 10000,
                                            'path': 'django/trunk/AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failIfEqual(ctx['repo'], None)
        self.failIfEqual(ctx['rev'], None)
    
    def test_browse_anonymous_access(self):
        """ the repository is accessible without authentication"""
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django',
                                            'action': 'changesets',
                                            'rev': 10000,
                                            'path': 'django/trunk/AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].anonymous_access, True)

    def test_browse_login_required(self):
        """
        the repository is not accessible without authentication, no user
        given, so we get a redirection to login page
        """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 1,
                                            'path': 'AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])

    def test_browse_login_required_owner_given(self):
        """
        the repository is not accessible without authentication, the owner of
        the repository is given, we get the detail page
        """
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 1,
                                            'path': 'urls.py'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].user_can_read(ctx['user']), True)

    def test_browse_login_required_not_member_given(self):
        """
        the repository is not accessible without authentication, a user that
        doesn't belongs to members is given, we get a redirection to login page
        """
        self.client.login(username='no_permission', password='password')
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 1,
                                            'path': 'AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])


class FilelogTest(TestCase):
    fixtures = ['djangohgauth.json', 'repositories.json']
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_unknown_repository_returns_404(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'foo',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'foo/bar/baz'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_repository_in_db_but_not_in_FS(self):
        """ test thats passing an unknown repository returns a 404 page """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'bar',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'foo/bar/baz'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 404)

    def test_required_elements_in_context(self):
        """
        tests the presence of required elements in the context passed to the
        template
        """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'django/trunk/AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failIfEqual(ctx['repo'], None)
        self.failIfEqual(ctx['rev'], None)

    def test_filelog_anonymous_access(self):
        """ the repository is accessible without authentication"""
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'django/trunk/AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].anonymous_access, True)

    def test_filelog_login_required(self):
        """
        the repository is not accessible without authentication, no user
        given, so we get a redirection to login page
        """
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])
    
    def test_filelog_login_required_owner_given(self):
        """
        the repository is not accessible without authentication, the owner of
        the repository is given, we get the detail page
        """
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        self.failUnlessEqual(ctx['repo'].user_can_read(ctx['user']), True)

    def test_filelog_login_required_not_member_given(self):
        """
        the repository is not accessible without authentication, a user that
        doesn't belongs to members is given, we get a redirection to login page
        """
        self.client.login(username='no_permission', password='password')
        response = self.client.get(reverse('hg-repo-action-rev-path',
                                           None,
                                           None,
                                           {'name': 'django_hg',
                                            'action': 'changesets',
                                            'rev': 'tip',
                                            'path': 'AUTHORS'}),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.redirect_chain, [('http://localhost:8000/signin/', 302)])


class ListTest(TestCase):
    fixtures = ['authtestdata.json', 'repositories.json']
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_list(self):
        response = self.client.get(reverse('hg-list'),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        # 3 = number of items per page. We have 9 items in the fixtures
        self.failUnlessEqual(len(ctx['repositories']), 2)
        is_public = 0
        # check with an anonymous user: all viewable repositories must be
        # public
        for repo in ctx['repositories']:
            if repo.anonymous_access == True:
                is_public += 1
        self.failUnlessEqual(is_public, 2)
        # authenticate the user
        auth= self.client.login(username='testclient', password='password')
        self.assertTrue(auth)
        #reload the list page
        response = self.client.get(reverse('hg-list'),
                                   {},
                                   follow = True,
                                   **{'HTTP_HOST': 'localhost:8000'})
        self.failUnlessEqual(response.status_code, 200)
        ctx = response.context[0]
        # 3 = number of items per page. We have 9 items in the fixtures
        self.failUnlessEqual(len(ctx['repositories']), 2)
        is_public = 0
        is_private = 0
        # check with an authenticated user: one of the viewable repositories
        # is a private one
        for repo in ctx['repositories']:
            if repo.anonymous_access == True:
                is_public += 1
            else:
                is_private += 1
        self.failUnlessEqual(is_public, 1)
        self.failUnlessEqual(is_private, 1)



class HgRepositoryTest(TestCase):
    def setUp(self):
        self.client = Client()
        src_repo = HgRepository(name="public-repo", anonymous_access=True)
        src_repo.save()
        src_repo = HgRepository(name="private-repo", anonymous_access=False)
        src_repo.save()
    
    def tearDown(self):
        objs = HgRepository.objects.all()
        for obj in objs:
            obj.delete()
    
    def testNewPublicRepo(self):
        """
        Creating a new HgRepository object should create a new repository
        """
        src_repo = HgRepository.objects.get(name="public-repo")
        self.assertEquals(src_repo.repo_path,
                          os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['public'],
                                                       'public-repo')))
        self.assertTrue(os.path.exists(src_repo.repo_path))
    
    def testNewPrivateRepo(self):
        """
        Creating a new HgRepository object should create a new repository
        """
        src_repo = HgRepository.objects.get(name="private-repo")
        self.assertEquals(src_repo.repo_path,
                          os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['private'],
                                                       'private-repo')))
        self.assertTrue(os.path.exists(src_repo.repo_path))

    def testMovePrivateToPublic(self):
        """
        Switching the anonymous_access flag should change the location of the 
        repository
        """
        src_repo = HgRepository.objects.get(name="private-repo")
        src_repo.anonymous_access = True
        src_repo.save()
        self.assertEquals(src_repo.repo_path,
                          os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['public'],
                                                       'private-repo')))
        self.assertTrue(os.path.exists(src_repo.repo_path))

    def testMovePublicToPrivate(self):
        """
        Switching the anonymous_access flag should change the location of the 
        repository
        """
        src_repo = HgRepository.objects.get(name="public-repo")
        src_repo.anonymous_access = False
        src_repo.save()
        self.assertEquals(src_repo.repo_path,
                          os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['private'],
                                                       'public-repo')))
        self.assertTrue(os.path.exists(src_repo.repo_path))

    def testDeletePublicRemovesRepo(self):
        """
        Deleting the repository should remove the repository
        """
        src_repo = HgRepository.objects.get(anonymous_access=True)
        repo_path = src_repo.repo_path
        src_repo.delete()
        self.assertFalse(os.path.exists(repo_path))

    def testDeletePrivateRemovesRepo(self):
        """
        Deleting the repository should remove the repository
        """
        src_repo = HgRepository.objects.get(anonymous_access=False)
        repo_path = src_repo.repo_path
        src_repo.delete()
        self.assertFalse(os.path.exists(repo_path))

if __name__ == '__main__':
    unittest.main()
