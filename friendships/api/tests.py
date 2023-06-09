from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

class FriendshipApiTests(TestCase):

    def setUp(self):
        # self.anonymous_client = APIClient()

        self.youge = self.create_user('youge')
        self.youge_client = APIClient()
        self.youge_client.force_authenticate(self.youge)

        self.oliver = self.create_user('oliver')
        self.oliver_client = APIClient()
        self.oliver_client.force_authenticate(self.oliver)

        # Create followings and follower for oliver
        # always try some different numbers, in case of mess up
        for i in range(2):
            follower = self.create_user('oliver_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.oliver)
        for i in range(3):
            following = self.create_user('oliver_following{}'.format(i))
            Friendship.objects.create(from_user=self.oliver, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.youge.id)

        # Anonymous User should not access
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # User should not use get method
        response = self.oliver_client.get(url)
        self.assertEqual(response.status_code, 405)

        # User should not follow themselves
        response = self.youge_client.post(url)
        self.assertEqual(response.status_code, 400)

        # A normal case: oliver follow youge
        response = self.oliver_client.post(url)
        self.assertEqual(response.status_code, 201)

        # Repetance case: silent dealing
        response = self.oliver_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # Create new data in the DB, now try youge follow oliver
        count = Friendship.objects.count()
        response = self.youge_client.post(FOLLOW_URL.format(self.oliver.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.youge.id)

        # Anonymous User should not access
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # User should not use get method
        response = self.oliver_client.get(url)
        self.assertEqual(response.status_code, 405)

        # User should not unfollow themselves
        response = self.youge_client.post(url)
        self.assertEqual(response.status_code, 400)

        # A normal case: oliver unfollow youge, create this piece of data before you do it
        Friendship.objects.create(from_user=self.oliver, to_user=self.youge)
        count = Friendship.objects.count()
        response = self.oliver_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # Repetance case: silent dealing
        count = Friendship.objects.count() 
        response = self.oliver_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.oliver.id)

        # User should not use post method
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # A normal case: check oliver's followings
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # compare the time stamps order
        timestamp0 = response.data['followings'][0]['created_at']
        timestamp1 = response.data['followings'][1]['created_at']
        timestamp2 = response.data['followings'][2]['created_at']
        self.assertTrue(timestamp0 > timestamp1 > timestamp2)
        # check the content
        self.assertEqual(response.data['followings'][0]['user']['username'], 'oliver_following2')
        self.assertEqual(response.data['followings'][1]['user']['username'], 'oliver_following1')
        self.assertEqual(response.data['followings'][2]['user']['username'], 'oliver_following0')

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.oliver.id)

        # User should not use post method
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # A normal case: check oliver's followers
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # compare the time stamps order
        timestamp0 = response.data['followers'][0]['created_at']
        timestamp1 = response.data['followers'][1]['created_at']
        self.assertTrue(timestamp0 > timestamp1)
        # check the content
        self.assertEqual(response.data['followers'][0]['user']['username'], 'oliver_follower1')
        self.assertEqual(response.data['followers'][1]['user']['username'], 'oliver_follower0')