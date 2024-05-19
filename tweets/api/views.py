from django.utils.decorators import method_decorator
from newsfeeds.services import NewsFeedService
from ratelimit.decorators import ratelimit
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer, 
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from tweets.services import TweetService
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        """
        Control whether client side need to login by action function
        """
        if self.action in ['list', 'retrieve']: # action can directly use the function name
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @method_decorator(ratelimit(key='user_or_ip', rate='5/s', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a tweet with comments
        GET /api/tweets/{pk}
        """
        tweet = self.get_object()
        # MUST have queryset defined in the viewset
        return Response(TweetSerializerForDetail(
            tweet, 
            context={'request': request},
        ).data)
    
    @required_params(method='get', params=['user_id'])
    def list(self, request):
        """
        list tweets based on user id
        """
        # if 'user_id' not in request.query_params:
        #     return Response(status=400)
        user_id = request.query_params['user_id'] 
        cached_tweets = TweetService.get_cached_tweets(user_id=user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            # This queryset will be translated into:
            # SELECT * FROM twitter_tweets 
            # WHERE user_id = <user_id> 
            # ORDER BY created_at DESC
            # Using the joint index (user_id, created_at)
            # Only user_id indexed is not efficient enough 
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page, 
            many=True,              # many: a list of dict
            context={'request': request},
        ) 

        return self.get_paginated_response(serializer.data) 
    
    # In this case, 2 rate limiter will work together
    @method_decorator(ratelimit(key='user', rate='1/s', method='POST', block=True))
    @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True))
    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                'errors': serializer.errors
            }, status=400)
        tweet = serializer.save() # trigger create() in serializer
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request': request}).data, 
            status=201,
        )