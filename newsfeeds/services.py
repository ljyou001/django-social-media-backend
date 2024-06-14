from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from newsfeeds.models import HBaseNewsFeed, NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_main_task
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


def lazy_load_newsfeeds(user_id):
    """
    This is to support lazy loading for HBaseNewsFeed model

    Why this structure?
    This is because if you define
    `lazy_load_func = lazy_load_newsfeeds(user_id=1)` will not actually run the DB queries.
    Only you have given an actualy parameter to lazy_load_func just like `lazy_load_func(10)`,
    Then the function will be actually executed as well as the SQL access.
    """
    def _lazy_load(limit):
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            return HBaseNewsFeed.filter(prefix=(user_id,), limit=limit, reverse=True)
        return NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')[:limit]
    return _lazy_load


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        """
        This function is to fanout the tweet into follower's newslist

        Details:
        Create a fanout task in message queue managed by Celery
        parameter is `tweet`, all listening workers could take this task
        Task processing worker will execute codes asynchronously in fanout_newsfeeds_task
        If this task need 10s to finish, then the 10s will be spent by worker in backend rather than user 
        """
        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id) # <- adding tweet.user_id to -1 DB call
        # The line only put the task into the message queue rather than execute the function to make the user wait
        # 
        # NOTE: parameter in .delay() should be values that can be serialized by celery
        # This is because workers are independent, they won't know the value in the memory of web server
        # Thus, we can only pass tweet.id rather than tweet. Cuz Celery don't know how to serialize tweet.

        # fanout_newsfeeds_task(tweet.id)
        # This is a synchronous task, user need to wait until the task finish

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, lazy_load_newsfeeds(user_id))

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, lazy_load_newsfeeds(newsfeed.user_id))

    @classmethod
    def batch_create(cls, batch_params):
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            newsfeeds = HBaseNewsFeed.batch_create(batch_params)
        else:
            newsfeeds = [NewsFeed(**params) for params in batch_params]
            NewsFeed.objects.bulk_create(newsfeeds)
        
        # bulk_create or batch_create will not trigger post_save signal, 
        # you need to manually create them into the cache
        for newsfeed in newsfeeds:
            NewsFeedService.push_newsfeed_to_cache(newsfeed)

        return newsfeeds