from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweets
from tweets.models import Tweet
from comments.api.serializers import CommentSerializer


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


class TweetSerializerWithComments(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    
    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'content',
            'created_at',
            'comments',
        )

    # Another way to define is to use the serializer method:
    # comments = serializers.SerializerMethodField()
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set, many=True).data


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