from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForLikes
from comments.models import Comment
from likes.models import Like
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLikes()
    class Meta:
        model = Like
        fields = ('id', 'user', 'created_at')


class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    """
    A parental class for LikeSerializerForCreate and LikeSerializerForCancel
    with some common fields and functions

    Serializer can be extended, but this doesn't works for models
    """
    content_type = serializers.ChoiceField(choices=['tweet', 'comment'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, data):
        if data['content_type'] == 'tweet':
            return Tweet
        if data['content_type'] == 'comment':
            return Comment
        else:
            return None
        
    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({'content_type': 'Invalid content type'})
        liked_object = model_class.objects.filter(id=data['object_id']).first()
        # Why user filter() rather than get()?
        # if the object doesn't exist, .get() will return a 5xx error.
        # Normally, we will take serious look for all kinds of 5xx error
        # 
        # queryset.first(): return the first data obtained by queryset
        # The following also works
        # if model_class.objects.filter(id=data['object_id']).exists()
        if liked_object is None:
            raise ValidationError({'object_id': 'Object could not found'})
        return data


class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):

    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        instance, _ = Like.objects.get_or_create(
            user=self.context['request'].user,
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
        )
        return instance


class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):
    
    def cancel(self):
        """
        Self defined function to cancel a like, 
        So it will not be called by django just like serializer.save()
        We need to directly call the serializer.cancel() in this case

        No validated_date passed?
        validated_data is required for create(), but for self defined functions
        you can directly use self.validated_data 
        as long as you called is_valid() function before
        """
        model_class = self._get_model_class(self.validated_data)
        deleted, rows_count = Like.objects.filter(
            user=self.context['request'].user,
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
        ).delete()
        return deleted, rows_count
        # delete() doesn't return any error even if nothing was deleted
        # However, deleted will return False in this case, since nothing was found and deleted