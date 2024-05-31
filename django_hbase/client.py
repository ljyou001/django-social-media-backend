import happybase
from django.conf import settings


class HBaseClient:
    connection = None

    @classmethod
    def get_connection(cls):
        if cls.connection:
            return cls.connection
        cls.connection = happybase.Connection(settings.HBASE_HOST)
        # HBase normally have no username or password, thus, we will not provide public access in most of cases.
        return cls.connection