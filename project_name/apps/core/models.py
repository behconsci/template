import os
import codecs

from django.db import models


def create_default_hash(length=8):
    return codecs.encode(os.urandom(length), 'hex').decode()


class Base(models.Model):
    hash_id = models.CharField(
        default=create_default_hash,
        editable=False,
        max_length=30
    )
    idate = models.DateTimeField(auto_now_add=True, verbose_name='created at')
    udate = models.DateTimeField(auto_now=True, verbose_name='changed at')

    class Meta:
        abstract = True
