from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from tweets.models import Tweet
from utils.time_helper import utc_now


class TweetTests(TestCase):
    
    def test_hours_to_now(self):
        youge = User.objects.create(username='niyouge')
        tweet = Tweet.objects.create(
            user=youge,
            content='hello world',
        )
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
        # DO NOT use hours_to_now(), property should use no ()