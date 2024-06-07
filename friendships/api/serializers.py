from accounts.api.serializers import UserSerializerForFriendship
from accounts.services import UserService
from django.contrib.auth.models import User
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class BaseFriendshipSerializer(serializers.Serializer): # Serializer is the most basic serializer in django-rest
    user = serializers.SerializerMethodField()
    # both can be to_user and from_user
    created_at = serializers.SerializerMethodField()
    has_followed = serializers.SerializerMethodField()
    # Above 3 are required attributes for Friendship

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
    # Above 2 function are required to have if super is serializers.Serializer
    # We will pass for both functions
    # This is to avoid potential data leak
    # Since we should not process data in this redenering class 

    def get_user_id(self, obj):
        raise NotImplementedError

    def _get_following_user_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set 
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set
    
    def get_has_followed(self, obj):
        return self.get_user_id(obj) in self._get_following_user_id_set()
    
    def get_user(self, obj):
        user = UserService.get_user_by_id(self.get_user_id(obj))
        return UserSerializerForFriendship(user).data
        # we need .data to transfer this to a dict
    
    def get_created_at(self, obj):
        return obj.created_at


class FollowerSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.from_user_id


class FollowingSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.to_user_id


class FriendshipSerializerForCreate(serializers.Serializer):
    # Originally, ModelSerializer also check the uniqueness and etc.
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()
    
    # No longer: class Meta
    # This is not a Django ORM

    def validate(self, data):
        if data['from_user_id'] == data['to_user_id']:
            raise ValidationError('from_user_id and to_user_id should be different')
        if not User.objects.filter(id=data['to_user_id']).exists():
            raise ValidationError('You cannot follow a non-exist user')
        return data
    
    def create(self, validated_data):
        return FriendshipService.follow(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
    
    def update(self, instance, validated_data):
        pass