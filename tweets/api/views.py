from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet

class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        """
        Control whether client side need to login by action function
        """
        if self.action == 'list': # action can directly use the function name
            return [AllowAny()]
        return [IsAuthenticated()]

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
        return Response(TweetSerializer(tweet).data, status=201)