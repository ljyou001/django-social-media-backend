from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()
    # Since NewsFeedSerializer used TweetSerializer, a context should be passed
    # NewsFeedSerializer cannot have the context directly, so we need to search it
    # and add the context to its viewsets
    # Then the context can be used in NewsFeedSerializer, 
    # and it will also be passed to the TweetSerializer

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')
        # 'user' was deleted in the fields since it is the current session user