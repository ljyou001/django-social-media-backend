from notifications.models import Notification

from inbox.services import NotificationService
from testing.testcases import TestCase


class NotificationTest(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')
        self.user1_tweet = self.create_tweet(self.user1)

    def test_send_comment_notification(self):
        # do not send notification to yourself
        comment = self.create_comment(self.user1, self.user1_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # send notification if tweet user != comment user
        comment = self.create_comment(self.user2, self.user1_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # do not send notification to yourself
        like = self.create_like(self.user1, self.user1_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # send notification if tweet user != like user
        like = self.create_like(self.user2, self.user1_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)