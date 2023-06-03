from django.contrib.auth.models import User
from rest_framework import viewsets 
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    # 从哪里去获取数据
    serializer_class = UserSerializer
    # 确认数据+转换json+默认表单
    permission_classes = [permissions.IsAuthenticated]

# ModelViewSet: 一般是model一一对应，默认支持增删查改(list,retrive,put,patch,delete)
# 如果不想要这么全的话，可以用ReadOnlyModelViewSet
# /api/users/<id> 访问用户详情
# permission_classes：针对是否登录之后进行检测

class AccountViewSet(viewsets.ViewSet):
    
    @action(methods=['get'], detail=False)
    # 自定义了一个动作来操作
    # detail=False：意味着这是定义在整体资源上的一个动作，不需要写objectID
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)
    

# 这里所用的viewset是一个空的viewset，全部自己定义想要的东西