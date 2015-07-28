from django.db import models
from django.conf import settings


class PrefixField(models.CharField):
    description = "Prefix module field for searching"

    def __init__(self, *args, **kwargs):
        super(PrefixField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        if 'postgres' in settings.DATABASES['default']['ENGINE']:
            return 'prefix_range'
        return super(PrefixField, self).db_type(connection)

