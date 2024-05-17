from friendships.services import FriendshipService
from newsfeeds.tasks import fanout_newsfeeds_task
from newsfeeds.models import NewsFeed
from utils.redis_helper import RedisHelper
from twitter.cache import USER_NEWSFEEDS_PATTERN

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
        fanout_newsfeeds_task.delay(tweet.id)
        # The line only put the task into the message queue rather than execute the function to make the user wait
        # 
        # NOTE: parameter in .delay() should be values that can be serialized by celery
        # This is because workers are independent, they won't know the value in the memory of web server
        # Thus, we can only pass tweet.id rather than tweet. Cuz Celery don't know how to serialize tweet.

        # fanout_newsfeeds_task(tweet.id)
        # This is a synchronous task, user need to wait until the task finish

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)