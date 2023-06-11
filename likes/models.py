from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    """
    Model class for tweet like and comment like
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Check here: how to associate foreign key with two similar models
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    object_id = models.PositiveIntegerField()       # comment_id or tweet_id
    content_type = models.ForeignKey(               # model you selected
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True,
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    # Access the exact like record by calling like.content_object
    # content_object is not actually recorded in the database

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        index_together = (
            ('content_type', 'object_id', 'created_at'),
            ('user', 'content_type', 'created_at'),
        )
        ordering = ('-created_at',)

    def __str__(self):
        return '{} {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_object,
            self.object_id,
        )