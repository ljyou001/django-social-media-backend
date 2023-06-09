from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
)

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
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]
        
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

    