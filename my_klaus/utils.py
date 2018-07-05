# encoding: utf-8
import os
import re
import mimetypes
import locale
try:
    import chardet
except ImportError:
    chardet = None

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer, ClassNotFound
from pygments.formatters import HtmlFormatter

from my_klaus import markup


class KlausFormatter(HtmlFormatter):
    def __init__(self):
        HtmlFormatter.__init__(self, linenos='table', lineanchors='L',
                               anchorlinenos=True)

    def _format_lines(self, tokensource):
        for tag, line in HtmlFormatter._format_lines(self, tokensource):
            if tag == 1:
                # sourcecode line
                line = '<span class=line>%s</span>' % line
            yield tag, line

def guess_is_binary(dulwich_blob):
    return any(b'\0' in chunk for chunk in dulwich_blob.chunked)


def guess_is_image(filename):
    mime, _ = mimetypes.guess_type(filename)
    if mime is None:
        return False
    return mime.startswith('image/')


def extract_author_name(email):
    """
    Extracts the name from an email address...
    >>> extract_author_name("John <john@example.com>")
    "John"

    ... or returns the address if none is given.
    >>> extract_author_name("noname@example.com")
    "noname@example.com"
    """
    match = re.match('^(.*?)<.*?>$', email)
    if match:
        return match.group(1).strip()
    return email


def parent_directory(path):
    return os.path.split(path)[0]


def subpaths(path):
    """
    Yields a `(last part, subpath)` tuple for all possible sub-paths of `path`.

    >>> list(subpaths("foo/bar/spam"))
    [('foo', 'foo'), ('bar', 'foo/bar'), ('spam', 'foo/bar/spam')]
    """
    seen = []
    for part in path.split('/'):
        seen.append(part)
        yield part, '/'.join(seen)


try:
    from subprocess import check_output
except ImportError:
    # Python < 2.7 fallback, stolen from the 2.7 stdlib
    def check_output(*popenargs, **kwargs):
        from subprocess import Popen, PIPE, CalledProcessError
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output


def guess_git_revision():
    git_dir = os.path.join(os.path.dirname(__file__), '..', '.git')
    if os.path.exists(git_dir):
        return check_output(
            ['git', 'log', '--format=%h', '-n', '1'],
            cwd=git_dir
        ).strip()


KLAUS_VERSION = guess_git_revision() or '0.3'

def encode_for_git(s):
    # XXX This assumes everything to be UTF-8 encoded
    return s.encode()


def decode_from_git(b):
    # XXX This assumes everything to be UTF-8 encoded
    return b.decode('utf8')


def escape_html(s):
    return s.replace(b'&', b'&amp;').replace(b'<', b'&lt;') \
            .replace(b'>', b'&gt;').replace(b'"', b'&quot;')