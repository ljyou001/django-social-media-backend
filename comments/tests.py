from testing.testcases import TestCase

# FYI: run the test before migrate database
# in case you need to modify the model, add more migration files, slow down the test
class CommentModelTest(TestCase):

    def test_comment(self):
        user = self.create_user('oliver')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual((comment.__str__()), None)
