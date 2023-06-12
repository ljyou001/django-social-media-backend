# from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
# This notification is from django-notification package

from comments.models import Comment
from tweets.models import Tweet


class NotificationService(object):
    """
    The service dealing with notifications


    LEARNING NOTE

    Why use service?
    The process is relatively complicated, we don't want to use too much space of serializer and viewset.
    serializer and viewset should not be too long, but servcice can be

    What is signal?
    Similar to service
    In Django, signals allow certain senders to inform a set of receivers that specific actions have occurred.
    Django signals are used to send and receive specific essential information whenever a data model is saved, changed, or even removed.
    Signal A:
        task 1
        task 2
        task 3
    When signal A is sent, it will allow the 3 task from different location executed, synchronously. 

    In production, we don't suggest to use it. 
    As the project goes more and more complex, we will have a lot of signal listener to receive the signals.
    However, there could be many listeners for each signal, we cannot trace them back about how many of them.
    Since there are too many listeners and can be located in different locations,
    it is very difficult to manage them.

    That's why we suggest to move all the tasks to Service, let them do it in one place,
    then you can clearly manage all the triggered tasks.
    """

    @classmethod
    def send_like_notification(cls, like):
        """
        This function is for sending notification when user likes a tweet or comment
        """
        target = like.content_object
        # like.content_object is a GenericForeignKey, here is to define what is the model of the object
        if like.user == target.user:
            return
            # Corner case: no notification is needed if you liked your own object
        if like.content_type.model == 'tweet':
            notify.send(
                like.user, 
                recipient=target.user, 
                verb='liked your tweet', 
                action_object=target
            )
        # You can also write this line in this way:
        # if like.content_type == ContentType.objects.get_for_model(Tweet):
        # Remember to import the ContentType model
        if like.content_type.model == 'comment':
            notify.send(
                like.user, 
                recipient=target.user, 
                verb='liked your comment', 
                action_object=target
            )

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.tweet.user:
            return
            # Corner case: no notification is needed if you commented your own object
        notify.send(
            comment.user,
            recipient=comment.tweet.user,
            verb='commented on your tweet',
            target=comment.tweet,
        )