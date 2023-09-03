from testing.testcases import TestCase


# FYI: run the test before migrate database
# in case you need to modify the model, add more migration files, slow down the test
class CommentModelTest(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.tweet = self.create_tweet(self.user1)
        self.comment = self.create_comment(self.user1, self.tweet)

    def test_comment(self):
        """
        Model: create comment case
        """
        self.assertNotEqual((self.comment.__str__()), None)

    def test_like_comment(self):
        """
        Model test: users liked a comment
        """
        # Successfully like
        self.create_like(self.user1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)
        
        # Examine the unique_together
        self.create_like(self.user1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        # Another guy like this comment
        user2 = self.create_user('user2')
        self.create_like(user2, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
