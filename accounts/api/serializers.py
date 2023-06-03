from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class LoginSerializer(serializers.Serializer):
    # 仅用来帮助检测是否有这两项，CharField里面required默认为True
    username = serializers.CharField()
    password = serializers.CharField()