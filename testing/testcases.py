from comments.models import Comment
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.test import TestCase as DjangoTestCase
from django_hbase.models import HBaseModel
from friendships.models import Friendship
from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from likes.models import Like
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from rest_framework.test import APIClient
from tweets.models import Tweet
from utils.redis_client import RedisClient


class TestCase(DjangoTestCase):
    # HBase related functions
    hbase_tables_created = False

    def setUp(self):
        self.clear_cache()
        GateKeeper.turn_on('switch_friendship_to_hbase')
        GateKeeper.turn_on('switch_newsfeed_to_hbase')
        try:
            self.hbase_tables_created = True
            for hbase_model_class in HBaseModel.__subclasses__():
            # This is to obtain all the subclasses created with HBaseModel
                hbase_model_class.create_table()
        except Exception:
            self.tearDown()
            raise
        # raise: raise the exception, stop the test, then developer will see the error
        # If no raise, then there will be no exception thrown
        # `raise` equals `raise Exception` here, if no defined exception

        # remember to change the setUp functions in testcases
        # to execute this setUp functions of the subclasses
        # Otherwise, this setUp functions will not be executed in testcases

    def tearDown(self):
        if not self.hbase_tables_created:
            return
        for hbase_model_class in HBaseModel.__subclasses__():
            hbase_model_class.drop_table()

    # By checking the source code of django.test.TestCase we can see
    # Before the test starts, it will call the function setUp()
    # After the test ends, it will call the function tearDown()
    # Since TestCase did not implement both functions for HBase
    # We need to implement them manually

    def clear_cache(self):
        """
        This is to clean up the cache in memcached and create a clear testing env for tests.

        Why? 
        This is because django will not create new and reset the cache after each test.
        This is different from the purely DB related tests.
        """
        RedisClient.clear()
        caches['testing'].clear()

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
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            created_at = tweet.timestamp
        else:
            created_at = tweet.created_at
        return NewsFeedService.create(
            user_id=user.id, 
            tweet_id=tweet.id, 
            created_at=created_at,
        )

    def create_friendship(self, from_user, to_user):
        return FriendshipService.follow(from_user.id, to_user.id)