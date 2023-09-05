from django.conf import settings
import redis

class RedisClient:
    connection = None
    # variable here will be shared by the whole class

    @classmethod
    def get_connection(cls):
        if cls.connection:
            return cls.connection
        # singleton style: only one "instance" for the whole class
        # 
        # Why singleton?
        # Our normal request is like: request -> web server 1 process -> response to client
        # inside the 1 web server process, there are many redis get/set
        # So, most of the remote service will use singleton to reuse the connection within the process
        cls.connection = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.connection
    
    @classmethod
    def clear(cls):
        """
        Clear all the keys in the redis database, for TESTING.

        DO NOT use it in PRODUCTION, otherwise, high cache miss rate.
        """
        if not settings.TESTING:
            raise Exception("You can not flush redis in production environment")
        connection = cls.get_connection()
        connection.flushdb()