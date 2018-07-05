"""Main entry point"""

import sys
if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "unittest2"

__unittest = True

from my_django.utils.unittest.main import main_
main_()
