from django.db import models


class Thumb(models.Model):
    s3url = models.TextField(blank=False, null=False)
    md5sum = models.CharField(max_length=255, blank=False, )
    thumb_path = models.TextField(blank=False, null=False)

