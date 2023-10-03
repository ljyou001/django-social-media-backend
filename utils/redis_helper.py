from django.conf import settings
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer

class RedisHelper:

    @classmethod
    def _load_object_to_cache(cls, key, objects):
        connection = RedisClient.get_connection()

        serialized_list = []
        for obj in objects:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        if serialized_list:
            connection.rpush(key, *serialized_list)
            # rpush: append multiple values to the end of the list
            # *[]: expand the list
            connection.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            # Why expire?
            # For spare space, clean the dirty cache

    @classmethod
    def load_objects(cls, key, queryset):
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
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects

        # cache miss
        cls._load_object_to_cache(key, queryset)
        return list(queryset) 
    
    @classmethod
    def push_object(cls, key, obj, queryset):
        connection = RedisClient.get_connection()
        if not connection.exists(key):
            # Load from database
            cls._load_object_to_cache(key, queryset)
            return
        serialized_data = DjangoModelSerializer.serialize(obj)
        # Each piece of data in the Redis are serialized,
        # and stored in the list
        connection.lpush(key, serialized_data)
        # If key(name) does not exist and you implemented the lpush
        # It will insert the key-value into the DB and value type is list
        # If set(name), the value will be a string