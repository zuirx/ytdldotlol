from django.db import models

class YtdlpVersion(models.Model):
    version = models.TextField(blank=True,null=True)