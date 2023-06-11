from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import(
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,
) 
from tweets.models import Tweet


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()

    def get_permissions(self):
        """
        Control whether client side need to login by action function
        """
        if self.action == 'list': # action can directly use the function name
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a tweet with comments
        GET /api/tweets/{pk}
        """
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    def list(self, request):
        """
        list tweets based on user id
        """
        if 'user_id' not in request.query_params:
            return Response(status=400)
        
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id'] 
        ).order_by('-created_at')         # -: reverse
        serializer = TweetSerializer(tweets, many=True) # many: a list of dict

        return Response({'tweets': serializer.data}) 
        # we normally will not directly return a list, that's why we warpped with a dict
    
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
        return Response(TweetSerializer(tweet).data, status=201)