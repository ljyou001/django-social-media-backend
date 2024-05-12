def push_newsfeed_to_cache(sender, instance, created, **kwargs):
    if not created:
        return
    # 1. Why if not created?
    # post_save signal will also be triggered when an object is got updated
    # we don't want to push the newsfeed to cache for that case
    # 
    # 2. You can also...
    # def push_newsfeed_to_cache(sender, instance, **kwargs):
    #     if kwargs.get('created', False):
    #         NewsFeedService.push_newsfeed_to_cache(instance)
    #     else: ...
    # 
    # 3. bulk_create in service.fanout_to_followers
    # This will not trigger the post_save signal

    from newsfeeds.services import NewsFeedService
    NewsFeedService.push_newsfeed_to_cache(instance)