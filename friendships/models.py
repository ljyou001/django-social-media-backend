from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
        help_text='The user who followed someone',
    )
    # about reverse lookup: user.tweets_set equal to Tweet.objects.filter(user=user)
    # the reason why we need to rename the reverse lookup set by related_name
    # is because we need to clearly know the direction of the operation of the site
    # here: user.following_friendship_set = Friendship.objects.filter(user=user).from_user

    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
        help_text='The user who were followed by someone',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (
            ('from_user', 'created_at'),
            ('to_user', 'created_at'),
        )
        unique_together = (
            ('from_user', 'to_user'),
        ) 
        # this is to avoid duplicate entries for this pair of relation, 
        # say operate too fast in frontend and leads to call two async operations in backend

    def __str__(self):
        return f'{self.from_user} follows {self.to_user}'