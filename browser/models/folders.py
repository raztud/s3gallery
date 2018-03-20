# coding: utf-8
from django.db import models


class Folders(models.Model):
    s3url = models.CharField(db_index=True,
                             primary_key=True,
                             max_length=500,
                             blank=False,
                             null=False,
                             unique=True)

    description = models.TextField(default='', max_length=255, blank=True, )
    name = models.TextField(default='', blank=True, max_length=255,)
    preview_thumb = models.CharField(default='', max_length=255, blank=True, null=False)

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description
