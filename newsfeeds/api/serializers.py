from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    tweet = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id
    
    def get_tweet(self, obj):
        # This is not ModelSerializer:
        # 1. You must warp the tweet into a SerializerMethodField class
        # 2. You must manually pass the context
        return TweetSerializer(obj.cached_tweet, context=self.context).data
    
    def get_created_at(self, obj):
        return obj.created_at

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

# Depreciated after HBase Support

# class NewsFeedSerializer(serializers.ModelSerializer):
#     tweet = TweetSerializer(source='cached_tweet')
#     # Since NewsFeedSerializer used TweetSerializer, a context should be passed
#     # NewsFeedSerializer cannot have the context directly, so we need to search it
#     # and add the context to its viewsets
#     # Then the context can be used in NewsFeedSerializer, 
#     # and it will also be passed to the TweetSerializer

#     class Meta:
#         model = NewsFeed
#         fields = ('id', 'created_at', 'tweet')
#         # 'user' was deleted in the fields since it is the current session user