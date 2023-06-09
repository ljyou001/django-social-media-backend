from testing.testcases import TestCase
from rest_framework.test import APIClient

COMMENT_URL = '/api/comments/'

class CommentAPITestCase(TestCase):
    def setUp(self):
        
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_create_comment(self):

        # Negative case: No anonymous user to create
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # Negative case: No Parm carried
        response = self.user1_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Negative case: Only with Tweet ID
        response = self.user2_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Please check your input')

        # Negative case: Only with content
        response = self.user2_client.post(COMMENT_URL, {'content': 'something'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Please check your input')

        # Negative case: Content is too long
        response = self.user2_client.post(COMMENT_URL, {
            'content': 'a' * 160,
            'tweet_id': self.tweet.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # Positive case
        response = self.user2_client.post(COMMENT_URL, {
            'content': 'a' * 10,
            'tweet_id': self.tweet.id
        }) 
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], 'a' * 10)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['user']['id'], self.user2.id)