from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from likes.models import Like
from tweets.listeners import push_tweet_to_cache
from utils.listeners import invalidate_object_cache
from utils.memcached_helper import MemcachedHelper
from utils.time_helper import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # In production, always use set_null for on delete
        null=True, 
        help_text='The user who posted this tweet',
    )
    # too long for one line? one line one parm, "," in the last line
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True) # auto_now_add only update while creating
    updated_at = models.DateTimeField(auto_now=True) # auto_now: update every time

    likes_count = models.IntegerField(default=0, null=True)
    comments_count = models.IntegerField(default=0, null=True)
    # NOTE: these two columns are newly added in this version, always add "null=True"
    # Otherwise: default = 0 will update all the data in the DB table
    # causing table LOCKED, the whole table, user unable to use the software.
    # 
    # Then how about the likes_count and comments_count for existing tweets?
    # We need to have an another script to fill the number one by one to avoid table lock.

    class Meta:
        index_together = (('user', 'created_at'),)
        # This way to create a compound index
        # There could be multiple compound indcies, so it is a tuple in a tuple
        # it is actually created a sorted table in DB with fields: ['user', 'created_at', 'id']
        # you need to make migration for the index
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        """
        return (datetime.datetime.now() - self.created_at).seconds / 3600
        """
        # TypeError: can't subtract offset-naive and offset-aware datetimes
        # This is because now() have no time zone. but created_at has time zone. 
        return (utc_now() - self.created_at).seconds / 3600
    
    # @property
    # def comments(self):
    #     """
    #     Obtain the comments of a tweet
    #     """
    #     return self.comment_set.all()
    #     # return Comment.objects.filter(tweet=self)

    @property
    def like_set(self):
        """
        Obtain all the like of a tweet
        """
        return Like.objects.filter(
            content_type = ContentType.objects.get_for_model(Tweet),
            object_id = self.id,
        ).order_by('-created_at')
    
    def __str__(self):
        """
        This function define the string representation while you print the instance
        """
        return f'{self.created_at} {self.user}: {self.content}'
    
    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)
    
    
post_save.connect(invalidate_object_cache, sender=Tweet)
pre_delete.connect(invalidate_object_cache, sender=Tweet)
# For a typical signal handler, we got the folowing parts:
# 1. The signal type, here is post_save, which is the ModelSignal name
# 2. The sender, here is Tweet, who send the signal
# 3. The receiver, here is invalidate_object_cache, which is the listener function who handling the signal
# 4. connect function, connect the signal and listener 
post_save.connect(push_tweet_to_cache, sender=Tweet)
