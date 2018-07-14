Your own github!
================

Features:
---------
* uBlog/uForum (multiple text/table/image formatters. stylized to [cat-v.org](http://cat-v.org/)),
* full functional Public and Private Git multi-repo (colorised/structured Web Wiew, remote Clone, Commit, Authentication etc),
* Mercurial (Hg) (currently in the work),
* may be used as locally and as on a server in the internet,
* Git based update of the code of the engine (`[this-site-url]/git/.self`),
* 100% python django code.


Before the first use:
---------------------
run from the root of the project
```
python manage.py syncdb
```

first start may take a longer time because it will create the git self-repo.


To run locally:
---------------
run from the root of the project
```
python manage.py runserver
```
you may see/edit your Articles/Repos by `127.0.0.1:8000` url. 

also you may work (clone/push/pull) with your Git repos in a regular way using repo-url `127.0.0.1:8000/git/[your-repo-name]`.


To run on a Web-server:
-----------------------
you need any server supporting Python 2.7 (2.74) and WSGI (example: pythonanywhere.com). 

also, you may use your own home web-server.

copy this project to your server as a new WSGI app. in your WSGI starter script import and use bhgv WSGI application
```python
from bhgv.wsgi import application
```

you may work (clone/push/pull) with your Git repos in a regular way using repo-url `[url-of-your-site]/git/[your-repo-name]`.

and read/write/edit articles


To work with the site's git self-repo:
--------------------------------------
* to create a self-repo you should run the engine as minimum one time after installing. the engine automatically creates the repo,
* **NOTE:** self-repo is accessible only for admin (superuser) of this site,
* after, clone it locally:
```
git clone [url-of-the-site]/git/.self
```
* change/test/run it locally,
* after, add, commit and push it back to the origin master as a regular git repo.


(will add screenshots/write better in the future)
