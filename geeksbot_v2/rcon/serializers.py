from rest_framework import serializers

from geeksbot_v2.rcon.models import RconServer


class RconServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RconServer
        fields = "__all__"
