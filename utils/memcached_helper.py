from django.conf import settings
from django.core.cache import caches

cache = caches['testing'] if settings.TESTING else caches['default']

class MemcachedHelper:
    """
    This Helper is derived from accounts.services.UserService in the previous commit.
    Therefore, we can use the similar functions for different models.

    To apply this Helper, you need to change the following:
    1. accounts.listeners, rewrite one in the utils
    2. accounts.models, update the listeners
    3. check and updatemodels used UserServices in the code repo
    """

    @classmethod
    def get_keys(cls, model_class, object_id):
        return '{}:{}'.format(model_class.__name__, object_id)
    
    @classmethod
    def get_object_through_cache(cls, model_class, object_id):
        # key = USER_PATTERN.format(user_id=user_id)
        key = cls.get_keys(model_class, object_id)
        object = cache.get(key)
        # Load from cache first
        if object:
            # If the cache hit
            return object
            # return the cache value
        # If cache miss
        object = model_class.objects.get(id=object_id)
        # Load from database second
        cache.set(key, object)
        # try:
        #     object = model_class.objects.get(id=object_id)
        #     # id=object_id NOT object_id=object_id
        #     cache.set(key, object)
        # except model_class.DoesNotExist:
        #     object = None
        # If you don't want to see the None return
        # You should delete the try except block
        # Since we don't expect the object_id to be None here, so...
        # A 5xx error will be reported here if None returned
        return object
    
    @classmethod
    def invalidate_object(cls, model_class, object_id):
        key = cls.get_keys(model_class, object_id)
        cache.delete(key)