from django.db import models


class Thumb(models.Model):
    s3url = models.CharField(db_index=True, max_length=500, blank=False, null=False)
    md5sum = models.CharField(db_index=True, unique=True,
                              max_length=255,
                              blank=False, null=False)
    thumb_path = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.thumb_path

    def __repr__(self):
        return self.thumb_path
