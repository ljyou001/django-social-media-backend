from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.api.serializers import (
    LoginSerializer, 
    SignupSerializer,
    UserProfileSerializerForUpdate,
    UserSerializer,
    UserSerializerWithProfile,
)
from accounts.models import UserProfile
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    # 从哪里去获取数据
    serializer_class = UserSerializerWithProfile
    # 确认数据+转换json+默认表单
    permission_classes = (permissions.IsAdminUser, )
                          

# ModelViewSet: 一般是model一一对应，默认支持增删查改(list,retrive,put,patch,delete)
# 如果不想要这么全的话，可以用ReadOnlyModelViewSet
# /api/users/<id> 访问用户详情
# permission_classes：针对是否登录之后进行检测

class AccountViewSet(viewsets.ViewSet):
    # 这里所用的viewset是一个空的viewset，全部自己定义想要的东西
    serializer_class = SignupSerializer
    # You can define a default serializer for this class

    @action(methods=['get'], detail=False)
    # 自定义了一个动作来操作
    # detail=False：意味着这是定义在整体资源上的一个动作，不需要写objectID
    def login_status(self, request):
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR']
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)
    
    @action(methods=['post'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})
    
    @action(methods=['post'], detail=False)
    def login(self, request):
        # get username and passwrod from request
        # normally from request.data['username'], but this one could be void
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "manage": "Please check your input",
                "errors": serializer.errors
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        # You can obtain data directly from serializer, and it will help you with some essential transformations

        # If you would like to know how the sql query executed in the BG:
        # queryset = User.objects.filter(username=username)
        # print(queryset.query)
        # if not User.objects.filter(username=username.lower()).exists():
        #     return Response({
        #         "success": False,
        #         "manage": "User does not exist"
        #     }, status=400)
        # Normally we will not user this though
        # >> now above code validation steps has been moved to the serializer

        user = django_authenticate(username=username.lower(), password=password)
        # django_login only accept the user gone through the django_authenticate
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "manage": "Invalid username or password"
            }, status=400)
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        }, status=200)
    
    @action(methods=['post'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        # If SignupSerializer(instance=user, data=request.data), it is updating data rather than create a new one
        if not serializer.is_valid():
            return Response({
                "success": False,
                "manage": "Please check your input",
                "errors": serializer.errors
            }, status=400)
        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)
    
class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin, # PUT /api/profiles/<id>
):
    """
    API endpoint that allows users profile to be viewed or edited.
    """
    queryset = UserProfile
    permission_classes = (permissions.IsAuthenticated, IsObjectOwner)
    serializer_class = UserProfileSerializerForUpdate