from django.contrib.auth.models import User
from notifications.models import Notification
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification
    """
    actor_content_type = serializers.SerializerMethodField()
    action_object_content_type = serializers.SerializerMethodField()
    target_content_type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )
        # actor: who
        # action: did what
        # target: to what object

        # For example: user1 followed you
        # actor: user1
        # verb: followed
        # action: N/A
        # target: N/A
        # recipient: you

        # Another example: user1 liked your tweet(tweet1)
        # actor: user1
        # verb: liked
        # action: N/A
        # target: tweet1
        # recipient: you

    def get_actor_content_type(self, obj):
        """
        Get actor content type
        """
        if obj.actor_content_type is None:
            return None
        return obj.actor_content_type.model

    def get_action_object_content_type(self, obj):
        """
        Get action object content type
        """
        if obj.action_object_content_type is None:
            return None
        return obj.action_object_content_type.model
    
    def get_target_content_type(self, obj):
        """
        Get target content type
        """
        if obj.target_content_type is None:
            return None
        return obj.target_content_type.model
    

class NotificationSerializerForUpdate(serializers.ModelSerializer):
    """
    Serializer for Notification Update
    Update here means change a notification to read or unread
    """
    unread = serializers.BooleanField()
    # BooleanField is similar to the True or False in Python
    # But it actually accepts true/True/1 as True, false/False/0 as False

    class Meta:
        model = Notification
        fields = (
            'unread',
        )

    def validate(self, data):
        """
        This is the validate method provided by DRF
        If you don't have any custom validation, just return the data like this

        In this case, serializer will only validate the BooleanField metioned above
        DRF validate will validate data in this order:
        1. field validation 2. run the validate method
        """
        return data

    def update(self, instance, validated_data):
        instance.unread = validated_data.get('unread')
        instance.save()
        return instance