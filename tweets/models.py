from django.db import models
from django.contrib.auth.models import User
# import datetime
from utils.time_helper import utc_now
# Create your models here.

class Tweet(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # In production, always use set_null for on delete
        null=True, 
        help_text='The user who posted this tweet',
    )
    # too long for one line? one line one parm, "," in the last line
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True) # auto_now_add only update while creating
    updated_at = models.DateTimeField(auto_now=True) # auto_now: update every time

    class Meta:
        index_together = (('user', 'created_at'),)
        # This way to create a compound index
        # There could be multiple compound indcies, so it is a tuple in a tuple
        # it is actually created a sorted table in DB with fields: ['user', 'created_at', 'id']
        # you need to make migration for the index
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # return (datetime.datetime.now() - self.created_at).seconds / 3600
        # TypeError: can't subtract offset-naive and offset-aware datetimes
        # This is because now() have no time zone. but created_at has time zone. 
        return (utc_now() - self.created_at).seconds / 3600
    
    def __str__(self):
        # This function define the string representation while you print the instance
        return f'{self.created_at} {self.user}: {self.content}'