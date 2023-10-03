def push_tweet_to_cache(sender, instance, created, **kwargs):
    """
    Push a tweet to the cache
    """
    from tweets.services import TweetService
    TweetService.push_tweet_to_cache(instance)