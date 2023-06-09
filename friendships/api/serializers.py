from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    # source='' can directly access model field and property function
    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingsSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


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