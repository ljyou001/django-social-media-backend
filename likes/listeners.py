from utils.listeners import invalidate_object_cache
from utils.redis_helper import RedisHelper

def increase_likes_count(sender, instance, created, ** kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        # if this is only update, no need to deal with it
        return
    
    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # Only Tweet to process
        # TODO: use the similar method to add likes_count for comments
        return
    
    # Method 1:
    # tweet = instance.content_object
    # Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') + 1)
    #
    # 
    # # DO NOT: 
    # tweet = instance.content_object
    # tweet.likes_count += 1
    # # <---- if someone else liked at this point and current process is slow at here...
    # tweet.save()
    # 
    # Why: this is not atomic operation, could causing the wrong value.
    # Most of databses supports atmoic operation
    # 
    # Method 2: (same as method 1)
    Tweet.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') + 1
    )
    # SQL: UPDATE likes_count = likes_count + 1 FROM tweets_table WHERE id=<instance.object_id>
    # This is atmoic, using MySQL's row lock to ensure the linear operation of this line
    # F here is to pass the name string into the SQL query in raw
    # 
    # What if: Tweet.objects.filter(id=instance.object_id).update(likes_count=tweet.likes_count + 1)
    # SQL: UPDATE likes_count = 11 FROM tweets_table WHERE id=<instance.object_id>
    
    # Method 3:
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()
    # 
    # In this method, .save() will trigger the post_save listener, however, .update will not.

    # Cache part: more knowledge in comments.listeners.increase_comments_count()
    RedisHelper.increase_count(instance.content_object, 'likes_count')
    

def decrease_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return
    
    Tweet.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') - 1
    )
    RedisHelper.decrease_count(instance.content_object, 'likes_count')