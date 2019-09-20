from rest_framework import serializers

from .models import Message
from .models import GuildInfo
from .models import AdminRequest
from .models import AdminComment


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class GuildInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuildInfo
        fields = "__all__"


class AdminRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminRequest
        fields = "__all__"


class AdminCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminComment
        fields = "__all__"
