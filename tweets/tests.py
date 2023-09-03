from datetime import timedelta

from django.test import TestCase

from testing.testcases import TestCase
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
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