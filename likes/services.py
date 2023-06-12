from django.contrib.contenttypes.models import ContentType

from likes.models import Like


class LikeService(object):
    """
    LikeService class

    Methods:
        has_liked
    
    Learning note: Why the service not under the api directory?
    Cuz service could used by components more than api, say an async task
    """

    @classmethod
    def has_liked(cls, user, target):
        """
        Check if the user has liked the tweet or comment
        """
        if user.is_anonymous:
            return False
        return Like.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
        ).exists()