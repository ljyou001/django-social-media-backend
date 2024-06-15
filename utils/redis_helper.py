from django.conf import settings
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer, HBaseModelSerializer
from django_hbase.models import HBaseModel

class RedisHelper:

    @classmethod
    def _load_object_to_cache(cls, key, objects, serializer):
        """
        This function is to load objects that already obtained from DB to Redis.

        serializer is added to support multiple kinds of DB
        """
        connection = RedisClient.get_connection()

        serialized_list = []
        for obj in objects: 
            # Bug Fix: Removed the length limit here, this one did not actually limited the length
            serialized_data = serializer.serialize(obj)
            serialized_list.append(serialized_data)

        if serialized_list:
            connection.rpush(key, *serialized_list)
            # rpush: append multiple values to the end of the list
            # *[]: expand the list
            connection.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            # Why expire?
            # For spare space, clean the dirty cache

    @classmethod
    def load_objects(cls, key, lazy_load_objects, serializer=DjangoModelSerializer):
        """
        This function is to load objects from Redis or from DB directly if data is not in Redis

        lazy_load_objects and serializer is added to support HBase database
        lazy_load_objects: accept a lazy loading function for both HBase and SQL DB
        serializer: by default is DjangoModelSerializer since most of the components are still using SQL DB
                    But as for HBase models, you need to use approprate HBase serializer
        """
        connection = RedisClient.get_connection()

        # cache hit: check if key exists
        # If yes, load from cache directly
        if connection.exists(key):
            # load from cache
            serialized_list = connection.lrange(key, 0, -1)
            # Get all the objects in the Redis, from 0 to -1
            objects = []
            for serialized_data in serialized_list:
                # deserialize each tweet object in the Redis list one by one
                deserialized_obj = serializer.deserialize(serialized_data)
                # serializer: change to fit different kind of DB
                objects.append(deserialized_obj)
            return objects

        # cache miss
        # Redis will only cache REDIS_LIST_LENGTH_LIMIT objects to save space
        # When objects went beyond the limitation, then you need to obtain the objects from DB
        # There are not too many people really goes beyond the limitation
        objects = lazy_load_objects(settings.REDIS_LIST_LENGTH_LIMIT)
        cls._load_object_to_cache(key, objects, serializer)
        return list(objects) 
    
    @classmethod
    def push_object(cls, key, obj, lazy_load_objects):
        """
        This function is to push objects to Redis

        lazy_load_objects is newly added for both SQL and HBase DB
        """
        if isinstance(obj, HBaseModel):
            serializer = HBaseModelSerializer
        else:
            serializer = DjangoModelSerializer
        # This if-else is to choose to use which serializer since both are different
        connection = RedisClient.get_connection()
        
        if connection.exists(key):
            # If key is in the Redis
            serialized_data = serializer.serialize(obj)
            connection.lpush(key, serialized_data)
            # We put the object to the top of the "list" in cache
            connection.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)
            # Then trim the length 
            return
        # if key is not in the Cache
        # Then we need to call the lazy load function
        objects = lazy_load_objects(settings.REDIS_LIST_LENGTH_LIMIT)
        cls._load_object_to_cache(key, objects, serializer)
        return

    @classmethod
    def get_count_key(cls, obj, attr):
        """
        This class method is to compose the key for likes_count or comments_count ...
        Structure is {class/model name}.{attribute(which count)}:{object id}
        """
        return '{}.{}:{}'.format(obj.__class__.__name__, attr, obj.id)
    
    @classmethod
    def increase_count(cls, obj, attr):
        connection = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if connection.exists(key):
            return connection.incr(key) # An atmoic operation built-in in redis package
        # If we cannot find the key in the cache, we need to back fill cache from DB
        # No +1 operation will be implemented in this block
        # -> Because obj.attr has already +1 in DB, before call incr_count()
        obj.refresh_from_db() # reload the object from DB
        connection.set(key, getattr(obj, attr))
        # getattr: obtain certain attribute, say varible/function/etc., in the object
        # This is because all these things are a dictonary within the object managed by python
        # equals: obj.__dict__.get(attr)
        connection.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)
        
    
    @classmethod
    def decrease_count(cls, obj, attr):
        connection = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if connection.exists(key):
            return connection.decr(key)
        obj.refresh_from_db()
        connection.set(key, getattr(obj, attr))
        connection.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)
        
    @classmethod
    def get_count(cls, obj, attr):
        connection = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        count = connection.get(key)
        if count is not None:
            return int(count)
        obj.refresh_from_db()
        count = getattr(obj, attr)
        connection.set(key, count)
        return count