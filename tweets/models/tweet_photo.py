from django.contrib.auth.models import User
from django.db import models
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus

from .tweet import Tweet
# You can only use reletive reference in this case to avoid circular import
# This is a style requirement


class TweetPhoto(models.Model):
    """
    TweetPhoto model: Allow Tweets to have photos
    """
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # The photo file belongs to which tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # You can directly use tweet.user to know who the photo belongs to
    # Here we provided a better way to query
    # We can know who sent this photo directly rather than join two tables which could causing performance issue

    file = models.FileField()
    # Image file
    order = models.IntegerField(default=0)
    # The order of photo in a tweet

    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES, 
        # Why choices?
        # It means you can only choose the status defined by developer in TWEET_PHOTO_STATUS_CHOICES
    )
    # The status of the photo, 
    # In censorship use case, it could be 0: pending, 1: approved, 2: rejected
    # Why IntegerField?
    # Because we did not match the number to a certain string, 
    # If you want to change your expected status, it will be very convenient

    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    # soft delete mark: when a image is deleted, it will only be marked as deleted
    # It will only be removed from the bucket after a certain time
    # Why?
    # 1. Immediate delete will causing performance issue, 
    #    here we can use some async tasks to delete in the background,
    #    rather than slowing down the production service
    # 2. Recycle mechanism, admins can still see the file

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('tweet', 'order'),
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('has_deleted', 'deleted_at'),
            ('status', 'created_at'),
        )

    def __str__(self):
        return f'{self.created_at} {self.tweet_id}: {self.user} {self.file}'