from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete

from accounts.services import UserService
from friendships.listeners import invalidate_following_cache


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
        ordering = ('-created_at',)
        # this is to avoid duplicate entries for this pair of relation, 
        # say operate too fast in frontend and leads to call two async operations in backend

    def __str__(self):
        return f'{self.from_user} follows {self.to_user}'
    
    @property
    def cached_from_user(self):
        return UserService.get_user_through_cache(self.from_user_id)
    @property
    def cached_to_user(self):
        return UserService.get_user_through_cache(self.to_user_id)
    
# Hook up with listeners to invalidate cache
pre_delete.connect(invalidate_following_cache, sender=Friendship)
post_save.connect(invalidate_following_cache, sender=Friendship)
# event.connect(<function name you would like to proceed>, sender=<who triggered this event>)
