from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import caches

from accounts.models import UserProfile
from twitter.cache import USER_PROFILE_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']

class UserService:

    @classmethod
    def get_profile_through_cache(cls, user_id):
        """
        Get user profile object via cache by user_id, not profile_id

        Why split this function?
        1. Both have a different id and but using the same user_id to find
        2. User and UserProfile model have a different change rate

        We did not merge this one to the utils.memcached_helper:
        1. Profile is not get through its own ID
        2. Profile should support get_or_create
        """
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        profile = cache.get(key)
        # Load from cache first
        if profile:
            # If the cache hit
            return profile
            # return the cache value
        # If cache miss
        profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, profile)
        return profile
    
    @classmethod
    def invalidate_profile(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)
        
    # After we finished all the User and UserProfile cache related function
    # We should globally search user foreign key or UserSerializer
    # to check which app used the User/UserProfile model
    # Say, in the likes.api.serializers, you can see the UserSerializerForLikes -> GO there and learn
    # Then, let go and check the friendships.api.serializers -> GO there and learn