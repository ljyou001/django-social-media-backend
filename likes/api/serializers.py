from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForLikes
from comments.models import Comment
from likes.models import Like
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLikes
    class Meta:
        model = Like
        fields = ('id', 'user', 'created_at')

class LikeSerializerForCreate(serializers.ModelSerializer):
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
    
    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        instance, _ = Like.objects.get_or_create(
            user=self.context['request'].user,
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
        )
        return instance