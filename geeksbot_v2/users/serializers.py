from rest_framework import serializers

from geeksbot_v2.users.models import User
from geeksbot_v2.users.models import UserLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = "__all__"
