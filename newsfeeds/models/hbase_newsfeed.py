from django.contrib.auth.models import User
from django_hbase import models
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


class HBaseNewsFeed(models.HBaseModel):
    user_id = models.IntegerField(reverse=True)  # who posted the tweet
    created_at = models.TimestampField()          # when posted the tweet
    tweet_id = models.IntegerField(column_family='cf') # which tweet

    class Meta:
        table_name = 'twitter_newsfeeds'
        row_key = ('user_id', 'created_at')

    def __str__(self):
        return f'{self.created_at} index of {self.user_id}: {self.tweet_id}'
    
    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)
    
    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)