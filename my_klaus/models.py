from my_django.db import models


class Repo(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    users_owner = models.CharField(max_length=50)
    users_read = models.CharField(max_length=700)
    users_write = models.CharField(max_length=700)


class Comment(models.Model):
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    rev = models.CharField(max_length=200)#tag
    file_path = models.CharField(max_length=200)#tag
    line = models.IntegerField()
    content = models.CharField(max_length=200)
    
