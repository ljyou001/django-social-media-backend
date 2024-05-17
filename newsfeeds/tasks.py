from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR

@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    """
    fanout newsfeed task that to be executed in the worker side.

    Basically, the following are just copied from original fanout function.
    But just re-obtained the tweet using tweet_id, because worker have no access to web server's object 
    """
    # To avoid circulated dependency, import should be in the function
    from newsfeeds.services import NewsFeedService

    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    # To do: more utilization
    # If you got 10 million followers, this is still very slow.

    # return ...
    # Async tasks are allow to return values, which will be printed into the Celery log page in terminal