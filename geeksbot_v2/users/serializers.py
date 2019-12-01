from rest_framework import serializers

from geeksbot_v2.users.models import User
from geeksbot_v2.users.models import UserLog


class UserSerializer(serializers.HyperlinkedModelSerializer):
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
            'logging_enabled',
            'is_staff',
            'is_superuser',
            'url'
        ]
        extra_kwargs = {
            'url': {
                'view_name': 'users_api:detail',
                'lookup_field': 'id'
            },
            'guilds': {
                'view_name': 'guilds_api:detail',
                'lookup_field': 'id'
            }
        }


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = [
            'user',
            'time',
            'action',
            'description',
            'url'
        ]
        extra_fields = {
            'url': {
                'view_name': 'users_api:log_detail',
                'lookup_field': 'id',
                'lookup_url_kwarg': 'log'
            }
        }
