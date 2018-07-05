# coding=utf-8
# The model is based on django_projectmgr
from my_mercurial import ui, hg
from datetime import datetime, date
import shutil, os
import mimetypes

from my_django.db import models
from my_django.contrib.auth.models import User
from my_django.db.models import Q
from my_django.utils.translation import ugettext_lazy as _
from my_django.core.urlresolvers import reverse
from my_django.conf import settings as global_settings

if "notification" in global_settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

# Bitwise permissions:
# 1 Read
# 2 Write
# 4 Owner (Doesn't imply read or write)
PERM_CHOICES = (
    (1, "Read"),
    (3, "Read/Write"),
    (7, "Owner")
)

class HgFile:
    def __init__(self, name, path, hg_view):
        self.name = name
        self.path = path + name

        if self.name.find('/')>-1:
            self.is_dir = True
        else:
            self.is_dir = False
            fctx = hg_view.ctx.filectx(self.path)
            self.size = fctx.size()
            mimetype = mimetypes.guess_type(self.path)
            if mimetype[0] is None:
                self.mimetype = 'application/octet-stream'
            else:
                self.mimetype = mimetype[0]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class HgContext:
    """A context view of a repository, i.e. a repository at a given rev"""
    def __init__(self, repo, hash=None) :
        if hash is None:
            hash = 'tip'
        # get a repo object for the current directory
        self.repository = hg.repository(ui.ui(),
                                        os.path.join(repo.repo_path))

        # get a context object for the "rev" revision
        self.ctx = self.repository[hash]
        self.user = self.ctx.user()
        self.description = self.ctx.description()
        self.time= datetime.fromtimestamp(self.ctx.date()[0]).time()
        self.date= date.fromtimestamp(self.ctx.date()[0])
        self.hash = self.ctx #hash
        self.rev = self.ctx.rev()
        self.files_count = len(self.ctx.files())

        self.revision = self.repository[self.rev]

    def __unicode__(self):
        return self.name

    def get_directory(self, path) :
        names = []
        dirs = []
        l = len(path)

        found = False
        for f in self.revision:
            if f[:l] != path:
                continue
            remain = f[l:]
            found = True
            if remain.count('/') == 0 :
                names.append(remain)
            else:
                d = remain.split('/')
                #print d[len(d)-1]
                #fctx = self.ctx.filectx(remain)
                #print fctx.size()

                if (d[0] not in dirs) :
                    dirs.append(d[0])
                    names.append(d[0] + '/')
        # sort the list of strings
        names.sort(key=str.lower)
        if found == False:
            return False
        else:
            # build the final list of objects
            self.files = []
            for f in names:
                self.files.append(HgFile(f, path, self))

            return self.files


class HgRepositoryManager(models.Manager):
    def filter_for_user(self, user, permission, **kwargs):
        qs = HgRepository.objects
        # search filtering
        for arg in kwargs:
            if arg == 'search' and kwargs[arg] != '' and kwargs[arg] is not None:
                for keyword in kwargs[arg].split(' '):
                    qs = qs.filter(Q(name__icontains=keyword) | Q(summary__icontains=keyword))
            if arg == 'display' and kwargs['display'] != 'all':
                if kwargs[arg] == 'only_member':
                    qs = qs.filter(repositoryuser__user__id = user.id,
                                   repositoryuser__permission__gte=1)
                elif kwargs[arg] == 'only_owner':
                    qs = qs.filter(repositoryuser__user__id = user.id,
                                   repositoryuser__permission=7)

        if user.is_authenticated():
            r = qs.distinct()
            r = r.extra(
                where=[('(anonymous_access=%d or '
                     + '(anonymous_access=%d '
                     + 'and django_hg_repositoryuser.user_id=%s '
                     + 'and django_hg_repositoryuser.source_repository_id=django_hg_hgrepository.id '
                     + 'and django_hg_repositoryuser.permission>=%s))') % (True, False, user.id, permission)],
                #params= [], #[user.id, permission],
                tables=['django_hg_repositoryuser']
                )
            return r
        else:
            return qs.filter(anonymous_access=True)

    def count_for_user(self, user, permission=3, **kwargs):
        """
        Return the total number of source repositories which the user has at
        least the given permission level
        """
        return self.filter_for_user(user, permission, **kwargs).count()


    def get_for_user(self, user, permission=3, **kwargs):
        """
        Return a list of source repositories which the user has at least the
        given permission level
        """
        return self.filter_for_user(user, permission, **kwargs).order_by('name')


class HgRepository(models.Model):
    """A version controlled source code repository"""
    name = models.SlugField(_("Name"), unique=True)
    summary = models.CharField(_('Summary'), max_length=255, blank=True, null=True)
    description = models.TextField(_('Description'), blank=True,null=True)
    anonymous_access = models.BooleanField(_("Allow Anonymous Viewing"), default=True)
    repo_path = models.CharField(editable=False, max_length=255)
    repo_url = models.CharField(editable=False, max_length=255)
    members = models.ManyToManyField(User, through='RepositoryUser', verbose_name="list of members")

    cmds  = ['between', 'branches', 'branchmap', 'capabilities', 'changegroupsubset', 'heads', 'unbundle', 'changegroup']

    class Meta:
        verbose_name = _("Repository")
        verbose_name_plural = _("Repositories")

    def __unicode__(self):
        return self.name

    objects = HgRepositoryManager()

    @models.permalink
    def get_absolute_url(self):
        """
        The path to the project page
        """
        return ("hg-repo", {}, {'name': self.name })

    def owners(self):
        """
        Get the project owners
        """
        return self.repositoryuser_set.filter(permission=7).order_by('user__username').select_related()

    def contributors(self):
        """
        Get the write users
        """
        return self.repositoryuser_set.filter(permission__gte = 3).order_by('-permission', 'user__username').select_related()

    def members(self):
        """
        Get all users involved in a project
        """
        return self.repositoryuser_set.filter(permission__gte = 1).order_by('-permission', 'user__username').select_related()


    def user_is_owner(self, userobj):
        """
        Is this user an owner of the project
        """
        try:
            repousr = self.repositoryuser_set.get(user=userobj)
        except:
            return False

        return repousr.permission > 4


    def user_can_write(self, userobj):
        """
        Does this user have write access to this repository
        """
        try:
            repousr = self.repositoryuser_set.get(user=userobj)
        except:
            return False

        return repousr.permission > 2


    def user_can_read(self, userobj):
        """
        Does the user have read access to this repository?
        """
        if self.anonymous_access:
            return True
        try:
            repousr = self.repositoryuser_set.get(user=userobj)
        except:
            return False

        return True # If we have a user, it must have at least read/write


    def move_to_public(self):
        """
        Move a repository from private to public
        """
        import os
        #os.umask(0)
        
        dest = os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['public'],
                                            self.name))
        source = self.repo_path
        shutil.move(source, dest)

    def move_to_private(self):
        """
        Move a repository from public to private
        """
        import os
        #os.umask(0)
        
        source = self.repo_path
        dest = os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['private'],
                                            self.name))
        shutil.move(source, dest)

    def get_size(self, directory=None):
        #The following is the code snippet to get the size of a directory in python:
        if directory is None:
            directory = self.repo_path

        dir_size = 0
        for (path, dirs, files) in os.walk(directory):
            for file in files:
                try:
                    filename = os.path.join(path, file)
                    dir_size += os.path.getsize(filename)
                except:
                    pass
        return dir_size

    def get_version_controller(self):
        if not controller: return
        return getattr(controller, VC_TYPE_CHOICES[self.vc_system-1][1])(self.repo_path)

    def create_repository(self):
        """
        Create a source code repository
        """
        import os
        #os.umask(0)

        u = ui.ui()
        if self.anonymous_access:
            hg.repository(u, os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['public'], self.repo_path), True)
        else:
            hg.repository(u, os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['public'], self.repo_path), True)

    def save(self, force_insert=False, force_update=False):
        """
        Do a little maintenence before doing the final save
        """
        new = self.id is None
        if self.anonymous_access:
            repo_path = os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['public'], self.name))
            repo_url = "%s%s/" % (global_settings.DJANGO_HG_REPOSITORIES_DIR['public'], self.name)
            if not new and repo_path != self.repo_path:
                self.move_to_public()
        else:
            repo_path = os.path.abspath(os.path.join(global_settings.DJANGO_HG_REPOSITORIES_DIR['private'], self.name))
            repo_url = "%s%s/" % (global_settings.DJANGO_HG_REPOSITORIES_DIR['private'], self.name)
            if not new and repo_path != self.repo_path:
                self.move_to_private()

        self.repo_path = repo_path
        self.repo_url = repo_url
        super(HgRepository, self).save(force_insert, force_update)
        # create the source repository here, if new
        if not os.path.isdir(self.repo_path):#new:
            self.create_repository()

    def get_hash(self):
        return self.get_context().ctx

    def get_context(self):
        return self.context

    def set_context(self, ctx):
        self.context = ctx

    def delete(self):
        # Delete the source repository here
        shutil.rmtree(self.repo_path)
        super(HgRepository, self).delete()


class RepositoryUser(models.Model):
    """A User of a repository"""
    source_repository = models.ForeignKey(HgRepository)
    user = models.ForeignKey(User)
    permission = models.IntegerField(_('Permission'), choices=PERM_CHOICES)

    def __unicode__(self):
        out = u"%s of %s with %s permission" % (self.user,
                self.source_repository, self.get_permission_display())

        return out

class ActiveManager(models.Manager):
    use_for_related_fields = True
    def active(self):
        qset = super(ActiveManager, self).get_query_set().filter(complete=False)
        if hasattr(self, 'core_filters'):
            return qset.filter(**self.core_filters)
        else:
            return qset

    def inactive(self):
        qset = super(ActiveManager, self).get_query_set().filter(complete=True)
        if hasattr(self, 'core_filters'):
            return qset.filter(**self.core_filters)
        else:
            return qset
