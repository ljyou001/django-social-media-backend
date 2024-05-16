from utils.listeners import invalidate_object_cache
from utils.redis_helper import RedisHelper

def increase_comments_count(sender, instance, created, ** kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return
    
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') + 1
    )
    
    # Then, how about cache?
    # If you don't update cache, the likes and comments count will be highly different compare to the source of truth
    #
    # We will use the increase and decrease portol provided by the Cache providors
    # -> likes and comments count should be stripping from tweet in cache, so we can use the protols
    # -> otherwise, every click will cause a cache invalidate for the whole tweet
    RedisHelper.increase_count(instance.tweet, 'comments_count')

def decrease_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') - 1
    )
    RedisHelper.decrease_count(instance.tweet, 'comments_count')

