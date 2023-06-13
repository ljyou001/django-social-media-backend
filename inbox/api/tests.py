from notifications.models import Notification

from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'
NOTIFICATION_DETAIL_URL = '/api/notifications/{}/'


class NotificationTests(TestCase):

    def setUp(self) -> None:
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')
        self.user2_tweet = self.create_tweet(self.user2)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user1_client.post(COMMENT_URL, {
            'tweet_id': self.user2_tweet.id, 
            'content': 'comment',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        response = self.user1_client.post(LIKE_URL, {
            'object_id': self.user2_tweet.id, 
            'content_type': 'tweet',
        })
        self.assertEqual(Notification.objects.count(), 1)


class NotificationsAPITests(TestCase):

    def setUp(self) -> None:
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')
        self.user1_tweet = self.create_tweet(self.user1)

    def test_unread_count(self):
        url = NOTIFICATION_URL + 'unread-count/'

        self.user2_client.post(LIKE_URL, {
            'object_id': self.user1_tweet.id,
            'content_type': 'tweet',
        })
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'object_id': comment.id,
            'content_type': 'comment',
        })
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        unread_count_url = NOTIFICATION_URL + 'unread-count/'
        mark_all_as_read_url = NOTIFICATION_URL + 'mark-all-as-read/'

        self.user2_client.post(LIKE_URL, {
            'object_id': self.user1_tweet.id,
            'content_type': 'tweet',
        })
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'object_id': comment.id,
            'content_type': 'comment',
        })

        response = self.user1_client.get(unread_count_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)

        # GET method not allowed
        response = self.user1_client.get(mark_all_as_read_url)
        self.assertEqual(response.status_code, 405)
        # Client can only mark their own notifications
        response = self.user2_client.post(mark_all_as_read_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)
        response = self.user1_client.get(unread_count_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)
        # Client successfully marked their notifications read
        response = self.user1_client.post(mark_all_as_read_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.user1_client.get(unread_count_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.user2_client.post(LIKE_URL, {
            'object_id': self.user1_tweet.id,
            'content_type': 'tweet',
        })
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'object_id': comment.id,
            'content_type': 'comment',
        })

        # Anonymous user cannot get list notifications
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # User2 don't have any notifications
        response = self.user2_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # User1 have 2 notifications
        response = self.user1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # User1 only have 1 notification after one of them is marked as read
        notification = Notification.objects.filter(recipient=self.user1).first()
        notification.unread = False
        notification.save()
        response = self.user1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        response = self.user1_client.get(NOTIFICATION_URL, data={'unread': True})
        # {'unread': True} is powered by the DEFAULT_FILTER_BACKENDS
        # called by filterset_fields and ListModelMixin in the viewset 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        response = self.user1_client.get(NOTIFICATION_URL, data={'unread': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.user2_client.post(LIKE_URL, {
            'object_id': self.user1_tweet.id,
            'content_type': 'tweet',
        })
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'object_id': comment.id,
            'content_type': 'comment',
        })
        notification = self.user1.notifications.first()
        url = NOTIFICATION_DETAIL_URL.format(notification.id)
        unread_url = NOTIFICATION_URL + 'unread-count/'
        
        # Negative Case: Anonymous user cannot update notification
        response = self.anonymous_client.patch(url, {'unread': False})
        self.assertEqual(response.status_code, 403)

        # Negative Case: Only PUT method
        response = self.user1_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)

        # Negative Case: user2 cannot update user1's notification
        response = self.user2_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        # Why 404?
        # Because Notification model's queryset is based on logged-in user's id
        # rather than use a permission class IsObjectOwner -> 403

        # Positive case: user1 mark the notification as read
        response = self.user1_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # Positive case: user1 mark the notification as unread
        response = self.user1_client.put(url, {'unread': True})
        self.assertEqual(response.status_code, 200)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # Negative case: unread is a mandatory field
        response = self.user1_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)
        
        # Negative case: no other information can be changed
        response = self.user1_client.put(url, {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')