from datetime import timedelta

from django.test import TestCase

from testing.testcases import TestCase
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
from tweets.services import TweetService
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from utils.time_helper import utc_now


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.tweet = self.create_tweet(user=self.user1, content='hello world')
    
    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)
        # DO NOT use hours_to_now(), property should use no ()

    def test_like_tweet(self):
        """
        Model test: users liked a comment
        """
        # Successfully like
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)
        
        # Examine the unique_together
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        # Another guy like this comment
        user2 = self.create_user('user2')
        self.create_like(user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            user=self.user1, 
            tweet=self.tweet,
        )
        self.assertEqual(photo.user, self.user1)
        self.assertEqual(photo.tweet, self.tweet)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)
        # reverse query: lowercase of the table name plus _set

    def test_cache_tweet_in_redis(self):
        """
        This function is testing the basic usage of get a tweet from Redis 
        """
        tweet = self.create_tweet(self.user1)
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set('tweets:{}'.format(tweet.id), serialized_data)
        # tweets:<id> is defined by our self
        # In redis, the key "tweets:<id>" is called "name"
        # This is because redis supports dict as value, it will call the dict's key as key

        data = conn.get('tweets:not_exists')
        self.assertEqual(data, None)

        data = conn.get('tweets:{}'.format(tweet.id))
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)
        # assertEqual will compare the content of tweet and cached_tweet
        # tweet and cached_tweet is not sharing the same memory address

class TweetServiceTests(TestCase):
    
    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')

    def test_get_user_tweets(self):
        tweet_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.user1, 'tweet {}'.format(i))
            tweet_ids.append(tweet.id)
        tweets_ids = tweet_ids[::-1]

        RedisClient.clear()
        connection = RedisClient.get_connection()

        # cache miss
        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([t.id for t in tweets], tweets_ids)

        # cache hit
        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([t.id for t in tweets], tweets_ids)

        # cache updated
        new_tweet = self.create_tweet(self.user1, 'new tweet')
        tweets = TweetService.get_cached_tweets(self.user1.id)
        tweets_ids.insert(0, new_tweet.id)
        self.assertEqual([t.id for t in tweets], tweets_ids)

    def test_create_new_tweet_before_get_cached_tweets(self):
        tweet1 = self.create_tweet(self.user1, 'tweet1')

        RedisClient.clear()
        connection = RedisClient.get_connection()

        key = USER_TWEETS_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(connection.exists(key), False)
        tweet2 = self.create_tweet(self.user1, 'tweet2')
        self.assertEqual(connection.exists(key), True)

        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([t.id for t in tweets], [tweet2.id, tweet1.id])
