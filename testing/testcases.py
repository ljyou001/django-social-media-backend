from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from comments.models import Comment
from tweets.models import Tweet


class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        if hasattr(self,'_anonymous_client'):
            # check whether the instance has _anonymous_client created, if yes, return it
            return self._anonymous_client
        # if not, create a new _anonymous_client using APIClient
        self._anonymous_client = APIClient()
        return self._anonymous_client
        # therefore, only one _anonymous_client within one class
    
    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'a-generic-password'
        if email is None:
            email = f'{username}@twitter.com'
        return User.objects.create_user(username=username, email=email, password=password)
    
    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default content'
        return Tweet.objects.create(user=user, content=content)
    
    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)