from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        super(FriendshipApiTests, self).setUp()
        # self.anonymous_client = APIClient()

        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # Create followings and follower for user2
        # always try some different numbers, in case of mess up
        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            self.create_friendship(follower, self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            self.create_friendship(self.user2, following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.user1.id)

        # Anonymous User should not access
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # User should not use get method
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 405)

        # User should not follow themselves
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)

        # A normal case: user2 follow user1
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)

        # Repetance case: silent dealing
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # Create new data in the DB, now try user1 follow user2
        before_count = FriendshipService.get_following_count(self.user1.id)
        response = self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        self.assertEqual(response.status_code, 201)
        after_count = FriendshipService.get_following_count(self.user1.id)
        self.assertEqual(after_count, before_count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.user1.id)

        # Anonymous User should not access
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # User should not use get method
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 405)

        # User should not unfollow themselves
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)

        # A normal case: user2 unfollow user1, create this piece of data before you do it
        self.create_friendship(from_user=self.user2, to_user=self.user1)
        before_count = FriendshipService.get_following_count(self.user2.id)
        response = self.user2_client.post(url)
        after_count = FriendshipService.get_following_count(self.user2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(after_count, before_count - 1)

        # Repetance case: silent dealing
        before_count = FriendshipService.get_following_count(self.user2.id)
        response = self.user2_client.post(url)
        after_count = FriendshipService.get_following_count(self.user2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(after_count, before_count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user2.id)

        # User should not use post method
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # A normal case: check user2's followings
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        # compare the time stamps order
        timestamp0 = response.data['results'][0]['created_at']
        timestamp1 = response.data['results'][1]['created_at']
        timestamp2 = response.data['results'][2]['created_at']
        self.assertTrue(timestamp0 > timestamp1 > timestamp2)
        # check the content
        self.assertEqual(response.data['results'][0]['user']['username'], 'user2_following2')
        self.assertEqual(response.data['results'][1]['user']['username'], 'user2_following1')
        self.assertEqual(response.data['results'][2]['user']['username'], 'user2_following0')

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user2.id)

        # User should not use post method
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # A normal case: check user2's followers
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        # compare the time stamps order
        timestamp0 = response.data['results'][0]['created_at']
        timestamp1 = response.data['results'][1]['created_at']
        self.assertTrue(timestamp0 > timestamp1)
        # check the content
        self.assertEqual(response.data['results'][0]['user']['username'], 'user2_follower1')
        self.assertEqual(response.data['results'][1]['user']['username'], 'user2_follower0')

    def _paginate_until_the_end(self, url, expect_pages, friendships):
        """
        This is a function to test pagination
        Protected function

        This is changed from _test_friendship_pagination function which was for page-by-page test
        New Pagination is Endless
        """
        results, pages = [], 0
        response = self.anonymous_client.get(url)
        results.extend(response.data['results'])
        pages += 1
        while response.data['has_next_page']:
            self.assertEqual(response.status_code, 200)
            last_item = response.data['results'][-1]
            response = self.anonymous_client.get(url,{
                'created_at__lt': last_item['created_at'],
            })
            results.extend(response.data['results'])
            pages += 1
        self.assertEqual(len(results), len(friendships))
        self.assertEqual(pages, expect_pages)
        for result, friendship in zip(results, friendships[::-1]):
            self.assertEqual(result['created_at'], friendship.created_at)

    def test_following_pagination(self):
        """
        This test function will test pagination and our new added "has_followed" field
        =====
        In the new version, we have changed the page number pagination to endless pagination
        """
        # Know the pagination configurations
        page_size = EndlessPagination.page_size

        # Set ups for the test
        friendships = []
        for i in range(page_size * 2):
            following = self.create_user('user1_following{}'.format(i))
            friendship = self.create_friendship(from_user=self.user1, to_user=following)
            friendships.append(friendship)
            if following.id % 2 == 0:
                self.create_friendship(from_user=self.user2, to_user=following)

        url = FOLLOWINGS_URL.format(self.user1.id)
        # Test pagination using this protected function
        self._paginate_until_the_end(url, 2, friendships)

        # Anonymous User have no one following
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # User2 follows id with even number
        response = self.user2_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)
        
        # User1 can see all following
        response = self.user1_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

        # Test pull new friendships
        last_created_at = friendships[-1].created_at
        response = self.user1_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        new_friends = [self.create_user('celebrity_{}'.format(i)) for i in range(3)]
        new_friendships = []
        for friend in new_friends:
            new_friendships.append(self.create_friendship(from_user=self.user1, to_user=friend))
        response = self.user1_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(len(response.data['results']), 3)
        for result, friendship in zip(response.data['results'], reversed(new_friendships)):
            self.assertEqual(result['created_at'], friendship.created_at)

    def test_follower_pagination(self):
        """
        This test function will test pagination and our new added "has_followed" field
        =====
        In the new version, we have changed the page number pagination to endless pagination
        """
        # Know the pagination configurations
        page_size = EndlessPagination.page_size

        # Set ups for the test
        friendships = []
        for i in range(page_size * 2):
            follower = self.create_user('user1_follower{}'.format(i))
            friendship = self.create_friendship(from_user=follower, to_user=self.user1)
            friendships.append(friendship)
            if follower.id % 2 == 0:
                self.create_friendship(from_user=self.user2, to_user=follower)

        url = FOLLOWERS_URL.format(self.user1.id)
        self._paginate_until_the_end(url, 2, friendships)

        # anonymous have none following
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # User2 follows id with even number
        response = self.user2_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)
