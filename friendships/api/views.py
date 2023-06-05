from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User

class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate

    @action(methods=['get'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        """
        Get a list of followers based on to_user_id
        pk should be to_user_id
        GET /api/friendships/pk/followers/
        """
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({'followers': serializer.data}, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=True, permission_classes=[AllowAny])
    def following(self, request, pk):
        """
        Get a list of following user based on from_user_id
        pk should be from_user_id
        GET /api/friendships/pk/following/
        """
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({'following': serializer.data}, status=status.HTTP_200_OK)
    
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        """
        Create follow relationship between logged-in user (from_user_id) and some to_user_id
        pk should be to_user_id
        POST /api/friendships/pk/follow
        """
        if Friendship.objects.filter(from_user_id=request.user, to_user_id=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        # silent error handling: if doesn't matter if this is a duplicate

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        self.get_object()
        # if user(id=pk) not exist, 404 error will raise
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'error': 'you cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = Friendship.objects.filter(
            from_user = request.user,
            to_user=pk,
        ).delete()
        # .delete() will return (
        # how many elements you deleted,
        # how many elements per models you deleted 
        # )
        # This is because you might used on cascade delete
        # In prod, we normally use set null in case of domino effect.

        # Here we can know some don't while using SQL DB:
        # 1. Don't use JOIN: O(n^2) the whole step, mem is also big
        # 2. Don't use CASCADE
        # 3. Drop Foreign key constraint, use int/str id directly instead

        return Response({
            'success': True,
            'deleted': deleted,
        }, status=status.HTTP_200_OK)


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
                return Response({
                    'message': 'mandatory parameter must exist (to_user_id for this type)',
                    'error': 'lack of mandatory parameter',
                }, status=400)
                # verify mandatory parameter must exist
            friendships = Friendship.objects.filter(to_user_id=request.query_params['to_user_id']).order_by('-created_at')
            serializer = FollowerSerializer(friendships, many=True)
            return Response({'followers': serializer.data}, status=status.HTTP_200_OK)
            # return followers of an account
        
        elif request.query_params['type'] == 'following':
            if 'from_user_id' not in request.query_params:
                return Response({
                    'message': 'mandatory parameter must exist (from_user_id for this type)',
                    'error': 'lack of mandatory parameter',
                }, status=400)
                # verify mandatory parameter must exist
            friendships = Friendship.objects.filter(from_user_id=request.query_params['from_user_id']).order_by('-created_at')

            if 'to_user_id' in request.query_params:
                is_following = friendships.filter(to_user_id=request.query_params['to_user_id']).exists()
                return Response({'is_following': is_following}, status=status.HTTP_200_OK)
                # check the following relationship between from_user_id and to_user_id
            
            serializer = FollowingSerializer(friendships, many=True)
            return Response({'following': serializer.data}, status=status.HTTP_200_OK)
            # return the following list of an account

        return Response(Response({
            'message': 'This is friendship API, please define request type in get parm (followers/following)'
        }))
        # default return with no useful information
