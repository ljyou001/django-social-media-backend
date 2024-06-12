from django.utils import timezone
from rest_framework.test import APIClient

from comments.models import Comment
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'
TWEET_LIST_URL = '/api/tweets/'
TWEET_DETAIL_URL = '/api/tweets/{}/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'

class CommentAPITestCase(TestCase):
    def setUp(self):
        super(CommentAPITestCase, self).setUp()
        
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
        
    def test_list(self):
        # Negative case: Not providing tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Positive case: ask for comments of a 0 comment tweet
        response = self.user1_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # Positive case set up: 
        self.create_comment(self.user1, self.tweet, '1')
        self.create_comment(self.user2, self.tweet, '2')
        self.create_comment(self.user1, self.create_tweet(self.user2), '3')

        # Positive case CHECK: comments of a tweet -create_at order
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '2')
        self.assertEqual(response.data['comments'][1]['content'], '1')

        # Positive case CHECK: if other parms provided, say user_id
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.user2.id
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # Setup: Create a new tweet with no like/comment
        tweet = self.create_tweet(self.user1)
        url = TWEET_DETAIL_URL.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # test Tweet list api
        self.create_comment(self.user1, tweet)
        response = self.user2_client.get(TWEET_LIST_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeed list api
        self.create_comment(self.user2, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 2)


    def test_comments_count_with_cache(self):
        # Initialization: new tweet, no comments
        tweet_url = '/api/tweets/{}/'.format(self.tweet.id)
        response = self.user1_client.get(tweet_url)
        self.assertEqual(self.tweet.comments_count, 0)
        self.assertEqual(response.data['comments_count'], 0)

        # Add 2 comments to the tweet
        data = {'tweet_id': self.tweet.id, 'content': 'a comment'}
        for i in range(2):
            _, client = self.create_user_and_client('new_user{}'.format(i))
            client.post(COMMENT_URL, data)
            response = client.get(tweet_url)
            self.assertEqual(response.data['comments_count'], i + 1)
            self.tweet.refresh_from_db()
            self.assertEqual(self.tweet.comments_count, i + 1)
        
        comment_data = self.user2_client.post(COMMENT_URL, data).data
        response = self.user2_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # Update comment: should no count change
        comment_url = '{}{}/'.format(COMMENT_URL, comment_data['id'])
        response = self.user2_client.put(comment_url, {'content':'updated'})
        self.assertEqual(response.status_code, 200)
        response = self.user2_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # Delete comment: should count -1
        response = self.user2_client.delete(comment_url)
        self.assertEqual(response.status_code, 200)
        response = self.user1_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 2)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 2)