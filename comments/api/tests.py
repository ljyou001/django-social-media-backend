from django.utils import timezone
from rest_framework.test import APIClient

from comments.models import Comment
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'

class CommentAPITestCase(TestCase):
    def setUp(self):
        
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_create(self):

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

    def test_destory(self):
        comment = self.create_comment(self.user1, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # Negative case: No anonymous user to delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # Negative case: Only object owner can delete
        response = self.user2_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # Positive case
        count = Comment.objects.count()
        response = self.user1_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.user1, self.tweet)
        tweet2 = self.create_tweet(self.user2)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # Negative case: No anonymous user to update
        response = self.anonymous_client.put(url, {'content': 'somethingelse'})
        self.assertEqual(response.status_code, 403)

        # Negative case: Only object owner can update
        response = self.user2_client.put(url, {'content': 'somethingelse'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        # In case the content is changed in DB but not in test memory
        # Update manually from the DB
        self.assertNotEqual(comment.content, 'somethingelse')

        # Mixed case: Only content can be updated
        before_created_at = comment.created_at
        before_updated_at = comment.updated_at
        now = timezone.now()
        response = self.user1_client.put(url, {
            'content': 'somethingelse',
            'created_at': now,
            'updated_at': now,
            'tweet_id': tweet2.id,
            'user_id': self.user2.id,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'somethingelse')
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.updated_at, before_updated_at)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.user, self.user1)
        
