from django.conf import settings
from friendships.models import Friendship
from gatekeeper.models import GateKeeper
from newsfeeds.models import HBaseNewsFeed, NewsFeed
from newsfeeds.services import NewsFeedService
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedTestCase(TestCase):

    def setUp(self):
        super(NewsFeedTestCase, self).setUp()
        # Always clear_cache before any test
        # Otherwise, it will be extremely difficult to debug if this fails

        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        for i in range(2):
            follower = self.create_user(f'user2_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user(f'user2_following{i}')
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_list(self):

        # Negative Case: login is required
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        # Negative Case: post method not accept
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        # Normal Case: nothing in the database
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # Normal Case: You can see your own tweets in the newsfeed
        self.user1_client.post(POST_TWEETS_URL, {'content': 'hello'})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # Normal Case: You can also see followings tweets
        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(POST_TWEETS_URL, {
            'content': 'hello from the other side',
        })
        posted_tweet_id = response.data['id']
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.user1, tweet=tweet)
            newsfeeds.append(newsfeed)
        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['created_at'], newsfeeds[0].created_at)
        self.assertEqual(results[1]['created_at'], newsfeeds[1].created_at)
        self.assertEqual(
            results[page_size - 1]['created_at'], 
            newsfeeds[page_size - 1].created_at,
        )
        # Change for HBase support: 1. ID to created_at
        # There is no incremental ID in HBase
        # If you don't want to change this part of code
        # You can also add a @property in HBaseNewsFeed adding user_id and created_at together
        # But emmm... normally not recommended, since this is not a front-end req
        # 
        # self.assertEqual(len(response.data['results']), page_size)
        # self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        # self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        # self.assertEqual(
        #     response.data['results'][page_size - 1]['id'],
        #     newsfeeds[page_size - 1].id,
        # )
        

        # pull the second page
        response = self.user1_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['created_at'], newsfeeds[page_size].created_at)
        self.assertEqual(results[1]['created_at'], newsfeeds[page_size + 1].created_at)
        self.assertEqual(
            results[page_size - 1]['created_at'],
            newsfeeds[2 * page_size - 1].created_at,
        )
        # ID to created_at, same as above

        # pull latest newsfeeds
        response = self.user1_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.user1, tweet=tweet)

        response = self.user1_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['created_at'], new_newsfeed.created_at)

    def test_user_cache(self):
        """
        The idea of this test is mainly to test the following chain:
        newsfeeds -> tweet -> user -> profile
        If profile has been changed, data through the chain can be updated
        """
        u2_profile = self.user2.profile
        u2_profile.nickname = 'user2 nickname'
        u2_profile.save()

        self.assertEqual(self.user2.username, 'user2')
        self.create_newsfeed(self.user2, self.create_tweet(self.user1))
        self.create_newsfeed(self.user2, self.create_tweet(self.user2))

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user2')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'user2 nickname')
        self.assertEqual(results[1]['tweet']['user']['username'], 'user1')

        self.user1.username = 'user1_new'
        self.user1.save()
        u2_profile.nickname = 'user2_new_nickname'
        u2_profile.save()

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user2')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'user2_new_nickname')
        self.assertEqual(results[1]['tweet']['user']['username'], 'user1_new')

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.user1, 'content1')
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user1')
        self.assertEqual(results[0]['tweet']['content'], 'content1')

        # Update username
        self.user1.username = 'user1_new'
        self.user1.save()
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user1_new')
        self.assertEqual(results[0]['tweet']['content'], 'content1')

        # Update tweet content
        tweet.content = 'content2'
        tweet.save()
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'user1_new')
        self.assertEqual(results[0]['tweet']['content'], 'content2')

    def _paginate_to_get_newsfeeds(self, client):
        """
        _ started function is a util function in the class
        will not be tested by Django
        """
        # paginate to the end
        response = client.get(NEWSFEEDS_URL)
        results = response.data['results']
        while response.data['has_next_page']:
            created_at__lt = response.data['results'][-1]['created_at']
            response = client.get(NEWSFEEDS_URL, {'created_at__lt': created_at__lt})
            results.extend(response.data['results'])
        return results
    
    def test_redis_list_limit(self):
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        page_size = EndlessPagination.page_size
        users = [self.create_user('redis_user{}'.format(i)) for i in range(5)]
        newsfeeds = []
        for i in range(list_limit + page_size):
            tweet = self.create_tweet(user=users[i % 5], content='feed{}'.format(i))
            feed = self.create_newsfeed(user=self.user1, tweet=tweet)
            newsfeeds.append(feed)
        newsfeeds = newsfeeds[::-1]

        # only cached list_limit objects
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_newsfeeds), list_limit)
        self.assertEqual(NewsFeedService.count(self.user1.id), list_limit + page_size)
        # Change for HBase support: 2. count, since no built in count function
        # 
        # There is no built in count function in HBaseModel
        # queryset = NewsFeed.objects.filter(user=self.user1)
        # self.assertEqual(queryset.count(), list_limit + page_size)

        results = self._paginate_to_get_newsfeeds(self.user1_client)
        self.assertEqual(len(results), list_limit + page_size)
        for i in range(list_limit + page_size):
            self.assertEqual(results[i]['created_at'], newsfeeds[i].created_at)
        
        # a followed user create a new tweet
        self.create_friendship(self.user1, self.user2)
        new_tweet = self.create_tweet(self.user2, 'a new tweet')
        NewsFeedService.fanout_to_followers(new_tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeeds(self.user1_client)
            self.assertEqual(len(results), list_limit + page_size + 1)
            self.assertEqual(results[0]['tweet']['id'], new_tweet.id)
            for i in range(list_limit + page_size):
                self.assertEqual(results[i + 1]['created_at'], newsfeeds[i].created_at)

        _test_newsfeeds_after_new_feed_pushed()
        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()