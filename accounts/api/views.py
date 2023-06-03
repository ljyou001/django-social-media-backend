from django.contrib.auth.models import User
from rest_framework import viewsets 
from rest_framework import permissions
from accounts.api.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    # 从哪里去获取数据
    serializer_class = UserSerializer
    # 确认数据+转换json+默认表单
    permission_classes = [permissions.IsAuthenticated]

# ModelViewSet: 一般是model一一对应
# /api/users/<id> 访问用户详情