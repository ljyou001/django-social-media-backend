from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(self, tweet):
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
