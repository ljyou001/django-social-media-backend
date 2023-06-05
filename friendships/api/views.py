from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    # FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User

class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    # GET /api/friendships/1/followers/
    @action(methods=['get'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({'followers': serializer.data}, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=True, permission_classes=[AllowAny])
    def following(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({'following': serializer.data}, status=status.HTTP_200_OK)
    
    # def list(self, request):
    #     """
    #     Only to enable the api access at GET /, which mean it will show this:
    #     "api/friendships": "<host>/api/friendships/"
    #     """
    #     return(Response({'message': 'This is friendship API'}))

    def list(self,request):
        """
        list function is for the GET function at the root endpoint of this API viewset
        Here I would like to provided a more restful API endpoint for following/follower
        """
        if request.query_params['type'] == 'followers':
            if 'to_user_id' not in request.query_params:
                return Response(status=400)
                # verify mandatory parameter must exist
            friendships = Friendship.objects.filter(to_user_id=request.query_params['to_user_id']).order_by('-created_at')
            serializer = FollowerSerializer(friendships, many=True)
            return Response({'followers': serializer.data}, status=status.HTTP_200_OK)
            # return followers of an account
        
        elif request.query_params['type'] == 'following':
            if 'from_user_id' not in request.query_params:
                return Response(status=400)
                # verify mandatory parameter must exist
            # check the following relationship between from_user_id and to_user_id
            friendships = Friendship.objects.filter(from_user_id=request.query_params['from_user_id']).order_by('-created_at')

            if 'to_user_id' in request.query_params:
                is_following = friendships.filter(to_user_id=request.query_params['to_user_id']).exists()
                return Response({'is_following': is_following}, status=status.HTTP_200_OK)
            
            serializer = FollowingSerializer(friendships, many=True)
            return Response({'following': serializer.data}, status=status.HTTP_200_OK)
            # return the following list of an account

        return Response(Response({'message': 'This is friendship API'}))
        # default return with no useful information
