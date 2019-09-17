from rest_framework import serializers

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.guilds.models import Role


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "guild", "type"]
