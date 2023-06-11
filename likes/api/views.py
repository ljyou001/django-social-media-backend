from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCreate,
)
from likes.models import Like
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    """
    ViewSet for likes of tweet or comments
    """
    queryset = Like.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = LikeSerializerForCreate

    @required_params(request_attr='data', params=['content_type', 'object_id'])
    def create(self, request, *args, **kwargs):
        """
        Create a new like
        """
        serializer = LikeSerializerForCreate(
            data=request.data, 
            context={'request': request},
        )
        # Why we are still using serializer, even though we have content_type and object_id?
        # This is because we want to match the common usage of Django
        # We hope all, at least most of, the validation errors will be raised by serializer
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(
            LikeSerializer(instance).data, 
            status=status.HTTP_201_CREATED
        )