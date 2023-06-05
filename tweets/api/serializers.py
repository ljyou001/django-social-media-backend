from rest_framework import serializers
from tweets.models import Tweet
from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializerForTweets

class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweets()
    # If you don't import UserSerializer, the user is just a int, cannot get into it

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'content',
            'created_at',
        )

class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=5, max_length=160)

    class Meta:
        model = Tweet
        fields = (
            'content',
        )

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet