from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from comments.api.permissions import IsObjectOwner


class CommentViewSet(viewsets.GenericViewSet):
    """
    We will only implement the `list`, `create`, `update` and `destroy` actions.
    Since we don't need to check one single comment, so we will not provided `retrive` action.
    """
    # Learning Note:
    # Both ModelViewSet and GenericViewSet will provide the following default actions:
    # list, retrieve, create, partial_update, update and destroy
    # 
    # GET detail=True /api/comments/<pk>/ -> retrive
    # GET detail=False /api/comments/ -> list
    # POST detail=False /api/comments/ -> create
    # PATCH detail=True /api/comments/<pk>/ -> partial_update
    # PUT detail=True /api/comments/<pk>/ -> update
    # DELETE detail=True /api/comments/<pk>/ -> destroy
    # 
    # https://www.django-rest-framework.org/api-guide/viewsets/#default-actions
    # The problem is ModelViewSet will automatically expose all the actions to user
    # But for the security reason, we don't normally do that
    # So we normally use GenericViewSet instead
    # 
    # all the actions/functions are default provided, cannot user @action decorator
    # If you would like to add permission check for them, you need to user def permission_classes()
    # 

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    # queryset is providing the following API:
    # GET /api/comments/<pk>/

    filterset_fields = ('tweet_id',)
    # after you installed django-filter
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
            # The list means django will check IsAuthenticated(), then IsObjectOwner()
            # Only both are True, it will return True
            # 
            # Why this is better than return IsObjectOwner() only?
            # Because it will check IsAuthenticated() first, then IsObjectOwner()
            # 1. Speed up the processing
            # 2. Less misleading error message
        return [AllowAny()]
    
    def list(self, request, *args, **kwargs):
        """
        List all comments based on your tweet id
        GET /api/comments/?tweet_id=<tweet_id>

        AllowAny is OK, no need to change the get_permissions
        """
        if 'tweet_id' not in request.query_params:
            return Response({
                'success': False,
                'message': 'tweet_id is missing',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # BEFORE django filter
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id).order_by('-created_at')
        # # comments = Comment.objects.filter(tweet=tweet_id) is also OK
        
        # AFTER django filter
        queryset = self.get_queryset()
        # this get_queryset is using the `queryset = Comment.objects.all()` above
        comments = self.filter_queryset(queryset).\
                prefetch_related('user').\
                order_by('-created_at')
        # prefetch_related('user'): to utilize the massive amount of SQL query.
        # check serializer CommentSerializer class for more information
        # you can also user select_related('user'), it will use the JOIN query
        # But join has its limitation: 
        # 1. must within a same database 
        # 2. it will slow down the processing
        # 3. it will take up a lot of memory

        serializer = CommentSerializer(comments, many=True)
        # many=True means it will return a list of Comment objects

        return Response({
            'success': True, 
            'comments': serializer.data,
        }, status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs):
        """
        Create a new comment
        POST /api/comments
        post body: {content, tweet_id}
        """

        # Data Obtaining
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # This is another way to obtain the user id
        # You can also go to the tweets.api.views.TweetViewSet.create to check
        # how to use context for the user id

        # Learning note: Knowing the naming pattern
        # User: is name of Model
        # user: is a instance of User
        # user_id: is the primary key of User, by default it is a integer
        # users: is a list of users, or a queryset of User

        # Serializer validation 
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Data creation
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data, 
            status=status.HTTP_201_CREATED, 
        )
        # you can also make it status=201.
        # But it is always better to provide more explanation just like this one

    def update(self, request, *args, **kwargs):
        """
        Update an existing comment
        PUT /api/comments/<pk>
        """
        # Why not using the partial_update for this action?
        # In production, both mean update. 
        # To ease the pressure of the frontend, we all use PUT function

        comment = self.get_object()
        # get_object() here is provided by DRF, it will take the <pk> and find the object
        # If it cannot find the object, it will return 404
        serializer = CommentSerializerForUpdate(
            instance=comment,    
            data=request.data,
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        comment = serializer.save()
        # save() function here will trigger update() in the serializer, rather than create()
        # 
        # How to save() make its decision to call update() or create()?
        # It will check the instance parameter in the serializer. 
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing comment
        DELETE /api/comments/<pk>
        """
        comment = self.get_object()
        comment.delete()
        # DWF will return 204 by default for delete()
        # But I suggest to return 200 with some useful message
        return Response({'success': True}, status=status.HTTP_200_OK)
        