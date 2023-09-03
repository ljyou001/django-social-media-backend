from rest_framework.test import APIClient

from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from testing.testcases import TestCase
from utils.paginations import EndlessPagination

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedTestCase(TestCase):

    def setUp(self):
        self.clear_cache()
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
        max_upside_paginate = EndlessPagination.max_upside_paginate
        
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user, f'tweet{i}')
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeeds.append(newsfeed)
        newsfeeds = newsfeeds[::-1]

        # Pull the 1st page
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'], 
            newsfeeds[page_size - 1].id,
        )

        # Pull the 2nd page
        response = self.user1_client.get(NEWSFEEDS_URL, {
            'created_at__lt': newsfeeds[page_size - 1].created_at
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], newsfeeds[2 * page_size - 1].id)

        # Upside pull the latest 
        response = self.user1_client.get(NEWSFEEDS_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(len(response.data['results']), 0)

        # One new newsfeed
        new_tweet = self.create_tweet(self.user1, 'a new tweet')
        new_newsfeed = self.create_newsfeed(self.user1, new_tweet)
        response = self.user1_client.get(NEWSFEEDS_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

        # Too many new newsfeeds
        new_newsfeeds = []
        for i in range(max_upside_paginate + 2):
            tweet = self.create_tweet(followed_user, f'tweet{i}')
            newsfeed = self.create_newsfeed(self.user1, tweet)
            new_newsfeeds.append(newsfeed)
        new_newsfeeds = new_newsfeeds[::-1]
        response = self.user1_client.get(NEWSFEEDS_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(response.data['beyond_upside_paginate'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], new_newsfeeds[1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], new_newsfeeds[page_size - 1].id)

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