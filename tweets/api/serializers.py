from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForTweets
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService
from tweets.api.services import TweetSerivce
from tweets.constants import TWEET_PHOTOS_UPLOAD_LIMIT
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweets(source='cached_user')
    # If you don't import UserSerializer, the user is just a int, cannot get into it
    # Also, this must be instancelized using the ()
    # Otherwise, django will not render output in the UserSerializerForTweets's way
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    # What is SerializerMethodField?
    # This is a class provided by DRF
    # It will automatically detect and use get_varname() functions below 
    # It allows you to define you own method to obtain certain data
    # Such data generally not saved in the model and require some computing
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'content',
            'created_at',
            'has_liked',
            'likes_count',
            'comments_count',
            'photo_urls',
        )

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_likes_count(self, obj):
        return obj.like_set.count()
    
    def get_comments_count(self, obj):
        return obj.comment_set.count()
        # What is comment_set?
        # This is a reverse query mechanism provided by Django
        # Triggered by: Comment have the foreign key of Tweet 
        # It will return a queryset of Comment that associated to this particular tweet object

    def get_photo_urls(self, obj):
        photo_urls = []
        for photo in obj.tweetphoto_set.all().order_by('order'):
            photo_urls.append(photo.file.url)
        return photo_urls


class TweetSerializerForDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)
    
    class Meta:
        """
        Although TweetSerializerForDetail extends TweetSerializer
        But this class Meta still need to be rewrited
        This will not extends from TweetSerializer as the values has changed
        """
        model = Tweet
        fields = (
            'id',
            'user',
            'content',
            'created_at',
            'comments',
            'likes',
            'has_liked',
            'likes_count',
            'comments_count',
            'photo_urls',
        )

    # Another way to define is to use the serializer method:
    # comments = serializers.SerializerMethodField()
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set, many=True).data


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=5, max_length=160)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,  # element value can be empty
        required=False, # POST request can have no "files" attribute
    )
    # files is a ListField, which means FE should give a list of File binary
    # child here means the type of each element of this list 


    class Meta:
        model = Tweet
        fields = (
            'content',
            'files',
        )
    
    def validate(self, data):
        if len(data.get('files', [])) > TWEET_PHOTOS_UPLOAD_LIMIT:
            # You can also use the max_length attribute of ListField
            # To limit TWEET_PHOTOS_UPLOAD_LIMIT
            raise ValidationError({
                'message':'You can only upload {} files at most'\
                          .format(TWEET_PHOTOS_UPLOAD_LIMIT)
            })
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        # First: create the tweet
        if validated_data.get('files'):
            TweetSerivce.create_photos_from_files(
                tweet, 
                validated_data['files'],
            )
        # Second: create the file, so we can associate it to the tweet
        return tweet