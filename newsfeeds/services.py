from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from utils.redis_helper import RedisHelper
from twitter.cache import USER_NEWSFEEDS_PATTERN

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # # Mistake in Production: for + SQL query
        # # Causing the executing time extremely long
        # followers = FriendshipService.get_followers(tweet.user)
        # for follower in followers:
        #     NewsFeed.objects.create(
        #         user=follower,
        #         tweet=tweet,
        #     )
        # 
        # # Normally, there is a big (ms level) latency between web server and db
        # # n SQL queries means n times of overhead, say data back and forth, authentication, etc.

        # Correct way: bulk_create, merge all inserts into one query
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

        # bulk_create will not trigger the post_save signal, so we should push the newsfeed to cache here
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

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