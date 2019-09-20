from rest_framework import serializers

from geeksbot_v2.users.models import User
from geeksbot_v2.users.models import UserLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'name',
            'discord_username',
            'previous_discord_usernames',
            'discriminator',
            'previous_discriminators',
            'guilds',
            'steam_id',
            'animated',
            'avatar',
            'bot',
            'banned',
            'logging_enabled'
        ]


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = "__all__"
