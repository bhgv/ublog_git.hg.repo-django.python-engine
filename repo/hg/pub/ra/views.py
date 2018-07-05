# coding=utf-8
import os.path, mimetypes, codecs, difflib
from datetime import datetime, date
from math import ceil

from my_django.http import HttpResponse, HttpResponseRedirect, Http404
from my_django.shortcuts import render_to_response, get_object_or_404
from my_django.contrib.auth import authenticate, login
from my_django.core.urlresolvers import reverse
from my_django.conf import settings as global_settings
from my_django.template import RequestContext
from django_hg.models import HgContext, HgRepository
from django_hg.decorators import logged_in_or_basicauth
from django_hg.forms import HgDiffForm, HgRepositoryForm

from cicero.views import _get_left_side_cont

from my_mercurial.error import RepoError

BINARY_MIMETYPES = ['image/png', 'image/jpeg', 'image/gif', 'application/pdf']

def __binary(request, repo, rev, path):
    """
    display the file itself at the given rev
    ``repo``
        the repository
    ``rev``
        the revision in the changesets history
    ``path``
        the file we want to display
    """
    ctx = repo.get_context().repository[rev]
    fctx = ctx.filectx(path)
    mimetype = mimetypes.guess_type(path)

    if mimetype[0] is None:
        mimetype = 'application/octet-stream'
    else:
        mimetype = mimetype[0]

    return HttpResponse(fctx.data(), mimetype)

def __browse(request, repo, rev, path):
    if rev == 'tip':
        rev = repo.get_context().rev
    files = repo.get_context().get_directory(path)
    if files == False:
        raise Http404

    return render_to_response('django_hg/browse.html', {
        'files': files,
        'hash': repo.get_context().repository[rev],
        'path': path,
        'repo': repo,
        'rev': rev,
            'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

def __changeset(request, repo, rev):
    """
    display the file history
    ``name``
        the name of the repository
    ``rev``
        the revision in the changesets history
    """
    ctx = repo.get_context().repository[rev]
    to_rev = rev 
    files = []
    for f in ctx.files():
        mimetype = mimetypes.guess_type(f)
        try:
            fc = ctx[f]
            if mimetype[0] is not None:
                if mimetype[0] not in BINARY_MIMETYPES:
                    data1 = fc.data().split('\n')
                    
                    from_rev = int(rev)-int(fc.filerev())
                    ctx2 = repo.get_context().repository[from_rev]
                    data2 = ctx2.filectx(f).data().split('\n')
    
                    diff = difflib.unified_diff(data1, data2, fromfile=f+'@'+ str(from_rev),
                                                tofile=f+'@'+str(to_rev))
                else:
                    diff = None
            else:
                diff = None
            
            files.append({'name': f,
                          'size': len(fc.data()),
                          'mimetype': mimetype[0],
                          'diff': diff
                         })
        except:
            files.append({'name': f, 'size': -1 })
    
    if 'HTTP_REFERER' in request.META:
        referer = request.META['HTTP_REFERER']
    else:
        referer = reverse('hg-repo-action', kwargs={'name': repo.name,
                                                    'action': 'changesets'})

    return render_to_response('django_hg/changeset.html', {
        'ctx' : {"user": ctx.user(),
                "description": ctx.description(),
                "time": datetime.fromtimestamp(ctx.date()[0]).time(),
                "date": date.fromtimestamp(ctx.date()[0]),
                "hash": ctx,
                "rev": rev,
                "files_count": len(ctx.files())
               },
        'files': files,
        'repo' : repo,
        'referer': referer,
        'rev' : rev,
            'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

def __changesets(request, repo):
    """
    display the changesets history of a repository
    """
    max = repo.get_context().rev
    page = int(request.GET.get('page', 1))
    # forbid a page to be greater than the max or to be lower than one
    if page > max/global_settings.DJANGO_HG_PAGER_ITEMS:
        page = max/global_settings.DJANGO_HG_PAGER_ITEMS+1
    elif page < 1:
        page = 1

    start = max-(page-1)*global_settings.DJANGO_HG_PAGER_ITEMS
    end = max-(page)*global_settings.DJANGO_HG_PAGER_ITEMS

    changelog = []
    c = start
    while c > end :
        ctx = repo.get_context().repository[c]
        # we pass a dict instead of the object because it's really, really
        # faster (from 12500 to 48 ms with the django repository ! )
        changelog.append({"user": ctx.user(),
                     "description": ctx.description(),
                     "time": datetime.fromtimestamp(ctx.date()[0]).time(),
                     "date": date.fromtimestamp(ctx.date()[0]),
                     "files_count": len(ctx.files()),
                     "hash": ctx,
                     "rev": c,
                    })
        c = c-1
        if c < 0:
            break

    return render_to_response('django_hg/changesets.html', {
        'changelog': changelog,
        'end': end > 0 and end+1 or 1,
        'items_per_page': global_settings.DJANGO_HG_PAGER_ITEMS,
        'max': max,
        'page': page,
        'repo': repo,
        'start': start,
            'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

def __diff(request, repo, rev, path):
    """
    display a diff of a file
    ``repo``
        the repository
    ``rev``
        the revision in the changesets history
    ``path``
        the file for which we want the log
    """
    ctx = repo.get_context().repository[rev]

    if request.GET.get('from_rev') and request.GET.get('to_rev') :
        # compare two given revs
        from_rev = request.GET.get('from_rev')
        to_rev = request.GET.get('to_rev')
    else:
        # Compare the rev given as parameter with the previous one the file has
        # been changed
        from_rev = rev
        to_rev = rev 
        ctx = repo.get_context().repository[rev]
        fctx = ctx.filectx(path)
        for fl in fctx.filelog():
            l = fctx.filectx(fl)
            if fl ==  fctx.filerev()-1:
                from_rev = l.rev()
                break
    
    ctx = repo.get_context().repository[from_rev]
    fctx = ctx.filectx(path)
    data1 = fctx.data().split('\n')
    
    ctx2 = repo.get_context().repository[to_rev]
    data2 = ctx2.filectx(path).data().split('\n')
    
    diff = difflib.unified_diff(data1, data2, fromfile=path+'@'+ str(from_rev),
                                tofile=path+'@'+str(to_rev))
    
    return render_to_response('django_hg/diff.html', {
        'diff': diff,
        'file': path,
        'from_rev': from_rev,
        'path': path,
        'repo': repo,
        'rev': rev,
        'to_rev': to_rev,
            'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

def __get_repo(request, name, rev):
    """
    this private function gets the repository object from the database and
    returns the context view of the repository
    """
    repo = get_object_or_404(HgRepository, name=name)
    try:
        repo.set_context(HgContext(repo, rev))
        repo.absolute_url = ''.join(['http',
                                    ('', 's')[request.is_secure()], '://',
                                    request.META['HTTP_HOST'],
                                    repo.get_absolute_url()])
    except RepoError  :
        raise Http404

    return repo

def __log(request, repo, rev, path):
    """
    display the file log
    ``repo``
        the repository
    ``rev``
        the revision in the changesets history
    ``path``
        the file for which we want the log
    """
    ctx = repo.get_context().repository[rev]
    fctx = ctx.filectx(path)
    filelog = []

    for fl in fctx.filelog():
        l = fctx.filectx(fl)
        filelog.append({
            'user': l.user(),
            "time": datetime.fromtimestamp(l.date()[0]).time(),
            "date": date.fromtimestamp(l.date()[0]),
            'description': l.description(),
            'branch': l.branch(),
            'hash': str(l)[str(l).rfind('@')+1:],
            'filesize': l.size(),
            'rev': l.rev(),
            'files_count': len(ctx.files())
        })
    filelog.reverse()
    
    from_rev = request.GET.get('from_rev', '')
    to_rev = request.GET.get('to_rev', '')
    form = HgDiffForm(filelog, {'from_rev': from_rev,
                                 'to_rev': to_rev})
    if '' != from_rev and '' != to_rev and form.is_valid():
        return HttpResponseRedirect(reverse('hg-repo-action-rev-path',
                                            kwargs={'name': repo.name,
                                                    'action': 'changesets',
                                                    'rev': from_rev,
                                                    'path': path})+'?from_rev=' + str(from_rev) + '&to_rev=' + str(to_rev))
    
    return render_to_response('django_hg/log.html', {
        'file': path,
        'filelog': filelog,
        'form': form,
        'from_rev': from_rev,
        'path': path,
        'repo': repo,
        'rev': rev,
        'to_rev': to_rev,
            'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

def __overview(request, repo, rev):
    ctx = repo.get_context().repository[rev]
    
    return render_to_response('django_hg/overview.html', {
            'ctx': {
                "user": ctx.user(),
                "description": ctx.description(),
                "time": datetime.fromtimestamp(ctx.date()[0]).time(),
                "date": date.fromtimestamp(ctx.date()[0]),
                "hash": ctx,
                "rev": repo.get_context().rev,
                "files_count": len(ctx.files())
            },
            'repo': repo,
            'rev': 'tip',
            'groups': _get_left_side_cont(),
        }, context_instance=RequestContext(request))

def __search(request, repo):
    """
    search in a repository 
    ``repo``
        the repository
    """
    if 'q' in request.GET:
        q = request.GET.get('q')
    else:
        q = None
    results = []
    if q is not None:
        max = repo.get_context().rev
        end = max-global_settings.DJANGO_HG_MAX_SEARCH_RESULTS
        c = max
        while c > end :
            ctx = repo.get_context().repository[c]
            files = []
            for f in ctx.files():
                if f.lower().find(q.lower()) > -1 :
                    files.append(f)
            if (codecs.decode(ctx.description(), 'utf8').lower().find(q.lower()) > -1
                or (codecs.decode(ctx.user(), 'utf8').lower().find(q.lower()) > -1)
                or (str(ctx).find(q) > -1)
                or (len(files) > 0)):
                results.append({"user": ctx.user(),
                                "description": ctx.description(),
                                "time": datetime.fromtimestamp(ctx.date()[0]).time(),
                                "date": date.fromtimestamp(ctx.date()[0]),
                                "files_count": len(ctx.files()),
                                "files": files,
                                "hash": str(ctx),
                                "rev": c,
                               })
            c = c-1
            if c < 0:
                break
    
    return render_to_response('django_hg/search.html', {
        'max': global_settings.DJANGO_HG_MAX_SEARCH_RESULTS,
        'q': q,
        'repo': repo,
        'results': results,
        'rev': 'tip',
            'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

def __show(request, repo, rev, path):
    """
    display the file informations at the given rev
    ``repo``
        the repository
    ``rev``
        the revision in the changesets history
    ``file``
        the file for which we want the history
    """
    ctx = repo.get_context().repository[rev]
    fctx = ctx.filectx(path)
    if 'raw' in request.GET:
        mimetype = ('text/plain', None)
    else:
        mimetype = mimetypes.guess_type(path)

    if 'download' in request.GET:
        response = HttpResponse(fctx.data(), mimetype[0])
        response['Content-Disposition'] = 'attachment; filename=' + path[path.rfind('/')+1:]
        return response
    else:
        return render_to_response('django_hg/show.html', {
            'DJANGO_HG_PYGMENT_STYLE': global_settings.DJANGO_HG_PYGMENT_STYLE,
            'fctx': fctx,
            'file': path,
            'host': request.META['HTTP_HOST'],
            'mimetype': mimetype,
            'path': path,
            'repo': repo,
            'rev': rev,
            'size': fctx.size(),
            'groups': _get_left_side_cont(),
        }, context_instance=RequestContext(request))


def list(request, tab):
    """
    display a paginated list of repositories. If the user is authenticated, the
    contains both public and private repositories. If not, the list contains
    only public repositories

    """
    if not request.user.is_authenticated():
        tab = 'all'
    if tab == 'all':
        form = HgRepositoryForm(request.user,
                                {'search': request.GET.get('search'),
                                 'display': 'all',
                                },
                                label_suffix='')
    else:
        form = HgRepositoryForm(request.user,
                                {'search': request.GET.get('search'),
                                 'display': request.GET.get('display'),
                                },
                                label_suffix='')
    if form.is_valid():
        search = form.data['search']
        display = form.data['display']
        if search != '' and search is not None:
            terms = search.split(' ')
        else:
            terms = None
    else:
        search = None
        display= 'all'
        terms = None

    page = int(request.GET.get('page', 1))
    if page <= 0 :
        page = 1
    max = HgRepository.objects.count_for_user(request.user, 1, search=search, display=display)
    if ceil(float(max)/float(global_settings.DJANGO_HG_PAGER_ITEMS))<page:
        page = int(ceil(float(max)/float(global_settings.DJANGO_HG_PAGER_ITEMS)))
    start = (page-1)*global_settings.DJANGO_HG_PAGER_ITEMS
    end = page*global_settings.DJANGO_HG_PAGER_ITEMS
    if end > max:
        end = max

    repositories = []
    if (max > 0):
        q = HgRepository.objects.get_for_user(request.user, 1, search=search, display=display)[start:end]
        for repo in q:
            try:
                repo.set_context(HgContext(repo, 'tip'))
                repo.absolute_url = ''.join(['http',
                                            ('', 's')[request.is_secure()], '://',
                                            request.META['HTTP_HOST'],
                                            repo.get_absolute_url()])
                repositories.append(repo)
            except:
                pass

    return render_to_response('django_hg/list.html', {
        'end': end,
        'host': request.META['HTTP_HOST'],
        'items_per_page': global_settings.DJANGO_HG_PAGER_ITEMS,
        'repositories': repositories,
        'page': page,
        'form': form.as_ul(),
        'start': start+1,
        'terms': terms,
        'max': int(max),
        'groups': _get_left_side_cont(),
    }, context_instance=RequestContext(request))

@logged_in_or_basicauth('Authentication django-hg')
def repo(request, name, action, rev, path='', display = None):
    """
    display a repository or handles the commands sended by an hg client
    (clone, pull, push) if a 'cmd' argument is given
    ``name``
        the name of the repository
    ``action``
        the action to display
    ``rev``
        the revision of the repository. By default, it's equal to ``tip``
    ``path``
        optional. A valid path within the repository. If not given, the root of
        the repository is returned
    """
    if request.GET.get('cmd') and request.GET.get('cmd') in HgRepository.cmds:
        # A clone/pull/push command from Mercurial
        from my_mercurial import hg, ui
        from my_mercurial.hgweb.request import wsgirequest
        from my_mercurial.hgweb import protocol

        repo = __get_repo(request, name, 'tip')
        req = wsgirequest(request.META, None)
        r = hg.repository(ui.ui(), repo.repo_path)

        try :
            resp = protocol.__getattribute__(request.GET.get('cmd'))(r, req)
            #update the repository size only after a push
            #if (request.GET.get('cmd') == 'unbundle'):
            #    print repo.get_size()
        except:
            from my_mercurial.hgweb.common import ErrorResponse, HTTP_OK
            resp = ErrorResponse(HTTP_OK, 'command unrecognized')

        return HttpResponse(resp, protocol.HGTYPE)
    else:
        # Display a view of a repository
        repo = __get_repo(request, name, rev)
        
        if not repo.user_can_read(request.user.username):
            return HttpResponseRedirect(global_settings.LOGIN_URL)
        
        # dispatcher
        if action == 'binary':
            return __binary(request, repo, rev, path)
        elif action == 'browse':
            if path.rfind('/') == len(path)-1:
                # browse the repo tree
                return __browse(request, repo, rev, path)
            else:
                # show a file
                return __show(request, repo, rev, path)
        elif action == 'changesets':
            if path == '' :
                if "q" in request.GET :
                    #perform a search
                    return __search(request, repo)
                # display changesets
                elif (rev=='tip'):
                    # pager of changesets
                    return __changesets(request, repo)
                else:
                    # show a changeset
                    return __changeset(request, repo, rev)
            else:
                if rev == 'tip':
                    # log of a file 
                    return __log(request, repo, rev, path)
                else:
                    return __diff(request, repo, rev, path)
        elif action == 'overview':
            return __overview(request, repo, rev)