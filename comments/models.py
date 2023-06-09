from django.contrib.auth.models import User
from django.db import models

from tweets.models import Tweet


class Comment(models.Model):
    """
    In this version, we only archieve a easy comment feature:
    You can only comment one's tweet, but you cannot comment one's comment.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'),)
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return '{} - {} commented {} on {}'.format(
            self.created_at, 
            self.user, 
            self.content,
            self.tweet_id,
        )