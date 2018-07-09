import os, sys

from my_django.conf import settings

from my_dulwich.errors import (
    ApplyDeltaError,
    ChecksumMismatch,
    GitProtocolError,
    NotGitRepository,
    UnexpectedCommandError,
    ObjectFormatException,
    )
from my_dulwich.repo import (
    Repo,
    )

from my_dulwich import log_utils
logger = log_utils.getLogger(__name__)

from my_dulwich.server import Backend


repo_home = settings.REPO_HOME
def test_repo_path(path):
    abspath = os.path.normcase(os.path.abspath(path))
    dir_list = os.listdir(repo_home)
    for one in dir_list:
        repo_path = os.path.normcase(os.path.abspath(repo_home + os.sep + one + os.sep))
        if os.path.isdir(repo_path) and abspath == repo_path:
            return True
    return False


class MyGitFileSystemBackend(Backend):
    """Simple backend looking up Git repositories in the local file system."""
    def __init__(self, root=os.sep):
        super(MyGitFileSystemBackend, self).__init__()
        self.root = (os.path.abspath(root) + os.sep).replace(
                os.sep * 2, os.sep)

    def open_repository(self, path):
        logger.debug('opening repository at %s', path)
        #abspath = os.path.abspath(os.path.join(self.root, path)) + os.sep
        abspath = os.path.abspath(self.root + path) + os.sep
        #normcase_abspath = os.path.normcase(abspath)
        #normcase_root = os.path.normcase(self.root)
        if not test_repo_path(abspath): #normcase_abspath.startswith(normcase_root):
            raise NotGitRepository(
                    "Path %r not inside root %r" %
                    (path, self.root))
        return Repo(abspath)

