from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from newsfeeds.constants import FANOUT_BATCH_SIZE
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


# What does routing_key do? go check twitter.settings.CELERY_QUEUE
@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    """
    fanout newsfeed task that to be executed in the worker side.

    Basically, the following are just copied from original fanout function.
    But just re-obtained the tweet using tweet_id, because worker have no access to web server's object 

    ### Robust version
    - Adding `follower_ids` to decrease DB calls
    - No need to create current user's newsfeed
    - No need to get the tweet and follower list from friendship_services to decrease DB calls
    """
    # To avoid circulated dependency, import should be in the function
    from newsfeeds.services import NewsFeedService
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in follower_ids
    ]
    NewsFeed.objects.bulk_create(newsfeeds)

    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    # To do: more utilization
    # If you got 10 million followers, this is still very slow.

    return "{} newsfeeds created".format(len(newsfeeds))
    # Async tasks are allow to return values, which will be printed into the Celery log page in terminal


@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    """
    This function is to split large fanout task into small fanout tasks.

    Considering, there are 1 million follower in once's follow list:
    - Use only one fanout task will take extremely long time and the executing process could be dangerous.
      Say abruptly crash, causing some of the data not updated in DB and you cannot local from where
    Therefore, you need to split a large task into small tasks

    This spliting job should only be executed in an another async task:
    - Not the main business logic
    - Do not cause more waiting time to user
    - Programmers in chage of business logic may not be understand the split logic
    """
    # Business Logic: Create its own newsfeed asap, ensure user can see the newsfeed themselves first
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    follower_ids = FriendshipService.get_following_user_ids(tweet_user_id) # Obtain all the follower ids
    index = 0
    while index < len(follower_ids):
        # Call batch tasks, using index to follow task * batch size
        batch_follower_ids = follower_ids[index: index + FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, batch_follower_ids)
        index += FANOUT_BATCH_SIZE

    return '{} newsfeeds going to fanout, {} batches created'.format(
        len(follower_ids),
        (len(follower_ids) - 1) // FANOUT_BATCH_SIZE + 1
    )


