from gatekeeper.models import GateKeeper
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        super(NewsFeedServiceTests, self).setUp()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_get_user_newsfeeds(self):
        newsfeed_timestamps = []
        for i in range(3):
            tweet = self.create_tweet(self.user2)
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeed_timestamps.append(newsfeed.created_at)
        newsfeed_timestamps = newsfeed_timestamps[::-1]
        # Change for HBase support: 1. ID to created_at

        # cache miss
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.created_at for f in newsfeeds], newsfeed_timestamps)

        # cache hit
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.created_at for f in newsfeeds], newsfeed_timestamps)

        # cache updated
        tweet = self.create_tweet(self.user1)
        new_newsfeed = self.create_newsfeed(self.user1, tweet)
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        newsfeed_timestamps.insert(0, new_newsfeed.created_at)
        self.assertEqual([f.created_at for f in newsfeeds], newsfeed_timestamps)

    def test_create_new_newsfeed_before_get_cached_newsfeeds(self):
        feed1 = self.create_newsfeed(self.user1, self.create_tweet(self.user1))

        RedisClient.clear()
        connection = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(connection.exists(key), False)
        feed2 = self.create_newsfeed(self.user1, self.create_tweet(self.user1))
        self.assertEqual(connection.exists(key), True)

        feeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(
            [f.created_at for f in feeds], 
            [feed2.created_at, feed1.created_at],
        )


class NewsFeedTaskTests(TestCase):

    def setUp(self):
        super(NewsFeedTaskTests, self).setUp()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.user1, 'tweet 1')
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            created_at = tweet.timestamp
        else:
            created_at = tweet.created_at
        self.create_friendship(self.user2, self.user1)
        msg = fanout_newsfeeds_main_task(tweet.id, created_at, self.user1.id)
        self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batches created')
        self.assertEqual(1 + 1, NewsFeedService.count())
        # Change for HBase support: 2. count, since no built in count function
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 1)

        for i in range(2):
            user = self.create_user('newuser{}'.format(i))
            self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet 2')
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            created_at = tweet.timestamp
        else:
            created_at = tweet.created_at
        msg = fanout_newsfeeds_main_task(tweet.id, created_at, self.user1.id)
        self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batches created')
        self.assertEqual(4 + 2, NewsFeedService.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 2)

        user = self.create_user('anotheruser')
        self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet 3')
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            created_at = tweet.timestamp
        else:
            created_at = tweet.created_at
        msg = fanout_newsfeeds_main_task(tweet.id, created_at, self.user1.id)
        self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batches created')
        self.assertEqual(8 + 3, NewsFeedService.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual(len(cached_list), 3)