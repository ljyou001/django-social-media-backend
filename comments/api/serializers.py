from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from tweets.models import Tweet

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()
    # Remember: if you don't use UserSerializer() here
    # user will shown as its pid, rather than contain the fields in UserSerializer
    # 
    # Why only tweet_id rather tweet and import TweetSerializer?
    # Cuz in this case, we don't need to know the exact tweet.
    # 
    # PERFORMANCE ISSUE
    # Using UserSerializerForComment() could cause a bad performance issue:
    # Say there are n comments in a tweet, then django will sent n SQL queries for user info
    # To utilize this, you can use .prefetch_related('user') in the queryset
    # Go check it out in the views.py
    # Then you will see the debug log:
    # (0.000) SELECT `auth_user`.`id`, ... WHERE `auth_user`.`id` = 1 LIMIT 21; args=(1,)
    # (0.000) SELECT `auth_user`.`id`, ... WHERE `auth_user`.`id` = 1 LIMIT 21; args=(1,)
    # (0.000) SELECT `auth_user`.`id`, ... WHERE `auth_user`.`id` = 3 LIMIT 21; args=(3,)
    # was turned into the following:
    # (0.000) SELECT `auth_user`.`id`, ... WHERE `auth_user`.`id` IN (1, 3); args=(1, 3)

    class Meta:
        model = Comment
        fields = (
            'id', 
            'tweet_id', 
            'user', 
            'content', 
            'created_at', 
            'updated_at',
        )

class CommentSerializerForCreate(serializers.ModelSerializer):
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    # Why tweet_id and user_id?
    # ModelSerializer will only automatically contains user and tweet only
    # But not user_id and tweet_id
    # This is a problem of django rest framework

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError('This tweet does not exist')
        return data
    
    def create(self, validated_data):
        return Comment.objects.create(
            user_id = validated_data['user_id'],
            tweet_id = validated_data['tweet_id'],
            content = validated_data['content'],
        )
    
class CommentSerializerForUpdate(serializers.ModelSerializer):
    # This class also showing the advantage of seperate features need a standalone serializer
    # only "content" can be accessed through this serializer
    # If you use CommentSerializerForCreate, many unnecessary fields will be exposed for editing
    # which is dangerous

    class Meta:
        model = Comment
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance
    