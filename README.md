Your own github!
================
* uBlog/uForum (multiple text/table/image formatters. stylized to [cat-v.org](http://cat-v.org/)),
* full functional Public and Private Git multi-repo (colorised/structured Web Wiew, remote Clone, Commit, Authentication etc),
* Mercurial (Hg) (currently in the work),
* may be used as locally and as on a server in the internet,
* 100% python django code.


Before the first use:
---------------------
run from the root of the project
```
python manage.py syncdb
```


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
You need any server supporting Python 2.7 (2.74) and WSGI (example: pythonanywhere.com). 

Also, you may use your own home web-server.

copy this project to your server as a new WSGI app. in your WSGI starter script import and use bhgv WSGI application
```python
from bhgv.wsgi import application
```

(will add screenshots/write better in the future)
