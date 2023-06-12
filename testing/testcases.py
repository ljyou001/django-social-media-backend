from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from comments.models import Comment
from likes.models import Like
from newsfeeds.models import NewsFeed
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
    
    def create_like(self, user, target):
        """
        A test help to create like for tweet or comments

        :param target:
        a comment or tweet object
        """
        instance, _ = Like.objects.get_or_create(
            user=user, 
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id
        )
        return instance
        # instance, _
        # _ is a boolean indicate whether the instance is created or not
        # 
        # Why get_or_create()?
        # To avoid SQL error since the unique_together limitation in like.models
        # 
        # In side the return, __class__ is to obtain model's class name
        # model's class name have no record in database
        # Therefore, we need to use get_for_model()  to find the record in db according to the name
        # Then, you will find the correct ContentType in DB

    def create_user_and_client(self, *args, **kwargs):
        """
        This function will create user and client at the same time using the create_user fucntion above

        :param args and kwargs:
        same as create_user function
        :return:
        a user model object and a APIClient logged in with the user
        """
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client
    
    def create_newsfeed(self, user, tweet):
        """
        This function will create newsfeed using the model create 
        """
        return NewsFeed.objects.create(user=user, tweet=tweet)