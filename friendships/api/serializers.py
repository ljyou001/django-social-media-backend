from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService


class FollowingUserIdSetMixin:
    """
    This Mixin to get the following user id set

    Mixin means a plugin
    """
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            # attr is a kind of cache in object level, in memory, but not memcached powered
            # it is because python can add or set attrbutes of class at anywhere and anytime
            return self._cached_following_user_id_set 
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set


class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_from_user')
    # source='' can directly access model field and property function
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        # As we said before, here is the implementation of cached version
        # following_user_id_set is extended from FollowingUserIdSetMixin
        return obj.from_user_id in self.following_user_id_set


class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        return obj.to_user_id in self.following_user_id_set


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()
    
    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, data):
        if data['from_user_id'] == data['to_user_id']:
            raise ValidationError('from_user_id and to_user_id should be different')
        if not User.objects.filter(id=data['to_user_id']).exists():
            raise ValidationError('You cannot follow a non-exist user')
        return data
    
    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id = validated_data['from_user_id'],
            to_user_id = validated_data['to_user_id'],
        )
    
        # Can you see the mistake of the following code?
        # 
        # return Friendship.objects.create({
        #     'from_user_id': validated_data['from_user_id'],
        #     'to_user_id': validated_data['to_user_id'],
        # })