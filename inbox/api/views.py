from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from notifications.models import Notification
from ratelimit.decorators import ratelimit
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.decorators import required_params


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """
    API Viewset for notifications

    What is ListModelMixin?
    https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-display/
    This is to list all the notifications of the defined queryset
    The queryset is defined by get_queryset function or queryset var in the viewset class
    You can check its source code then you will know it is just achieved a list method with pagination
    """
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',)
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
        # You can also use this way to return
        # return self.request.user.notifications.all()
        # Why use notifications here?
        # If you check the src of notification model(AbstractNotification)
        # you will find recipient field has definded related_name='notification'
        # related_name is defining the reverse list name of the related model
        
    # What is url_path in action?
    # This is to redefine the url path of the action
    # Why? Cuz we don't usually use _ in URL, but - is quite common
    @action(methods=['get'], detail=False, url_path='unread-count')
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def unread_count(self, request):
        """
        Get unread count
        GET /api/notifications/unread-count/
        """
        count = self.get_queryset().filter(unread=True).count()
        # count can also be defined as following:
        # Notification.objects.filter(recipient=self.request.user, unread=True).count()
        # Suggest to move the queryset part down here if the code is long 
        # 
        # You can do the concat operation for queryset. just like this one
        # it is same as .filter(recipient=self.request.user, unread=True)
        return Response({'unread_count': count}, status=status.HTTP_200_OK)
    
    @action(methods=['post'], detail=False, url_path='mark-all-as-read')
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def mark_all_as_read(self, request):
        """
        Mark all as read
        POST /api/notifications/mark-all-as-read/
        """
        updated_count = self.get_queryset().filter(unread=True).update(unread=False)
        # update() here is a method provided django models/queryset
        # it will be translated to the following SQL:
        # UPDATE notifications SET unread = false WHERE recipient = user FROM <table>
        # 
        # returned updated_count is an integer
        # indicating how many item has been updated
        # 
        # Why added ".filter(unread=True)" this part?
        # We don't want to update the whole table, which could cause performance issue
        # 
        # Luckly, there is a index_together = ('recipient', 'unread') in the Notification model
        # Before you write the queryset, you'd better to check whether the 3rd party model has revelent index provided
        return Response({'marked_count': updated_count}, status=status.HTTP_200_OK)
    
    @required_params(method='put', params=['unread'])
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request, *args, **kwargs):
        """
        Mark a notification as read or unread
        An updateoperation to the notification object
        PUT /api/notifications/<pk>/

        To achieve the same thing, you can also define two functions:
        mark_as_read() and mark_as_unread() with detail=True

        But here we use update() function since it is more restful

        *args and **kwargs can be used to receive the pk and more useful attribute
        DO NOT FORGET IT
        """
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        # Above, get_object is provided by DRF. 
        # Basically, it will run a queryset based on the detail(pk) in your URL
        # and obtain the object instance or return 404 error
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                'errors':serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        notification = serializer.save()
        # again: instance must be passed in the serializer
        # so .save() will call the .update() method in the serializer
        return Response(
            NotificationSerializer(notification).data, 
            status=status.HTTP_200_OK,
        )