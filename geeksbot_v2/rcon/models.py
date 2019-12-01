from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.dmessages.models import Message
from geeksbot_v2.users.models import User
from geeksbot_v2.channels.models import Channel
from .utils import create_error_response
from .utils import create_success_response

# Create your models here.


class RconServer(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    password = models.CharField(max_length=50)
    monitor_chat = models.BooleanField()
    monitor_chat_channel = models.ForeignKey(
        Channel, on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True, default=None
    )
    alerts_channel = models.ForeignKey(
        Channel, on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True, default=None
    )
    info_channel = models.ForeignKey(
        Channel, on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True, default=None
    )
    info_message = models.ForeignKey(
        Message, on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True, default=None
    )
    settings_message = models.ForeignKey(
        Message, on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True, default=None
    )
    whitelist = models.ManyToManyField(User, blank=True)

    def update_server(self, data):
        if data.get('name'):
            self.name = data.get('name')
        if data.get('ip'):
            self.ip = data.get('ip')
        if data.get('port'):
            self.port = data.get('port')
        if data.get('password'):
            self.password = data.get('password')
        if data.get('monitor_chat'):
            self.monitor_chat = data.get('monitor_chat')
        if 'monitor_chat_channel' in data.keys():
            self.monitor_chat_channel = Channel.get_channel_by_id(data.get('monitor_chat_channel'))
        if 'alerts_channel' in data.keys():
            self.alerts_channel = Channel.get_channel_by_id(data.get('alerts_channel'))
        if 'info_channel' in data.keys():
            self.alerts_channel = Channel.get_channel_by_id(data.get('info_channel'))
        if 'info_message' in data.keys():
            self.info_message = Message.get_message_by_id(data.get('info_message'))
        if 'settings_message' in data.keys():
            self.settings_message = Message.get_message_by_id(data.get('settings_message'))

        self.save()
        return create_success_response(self, status.HTTP_202_ACCEPTED, many=False)

    def add_whitelist(self, user_id):
        user = User.get_user_by_id(user_id)
        if not isinstance(user, User):
            return create_error_response("User Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        if not user.steam_id:
            return create_error_response("User does not have a Steam 64ID attached to their account",
                                         status=status.HTTP_406_NOT_ACCEPTABLE)
        self.whitelist.add(user)
        return create_error_response("User has been added to the whitelist",
                                     status=status.HTTP_200_OK)

    def remove_from_whitelist(self, user_id):
        user = User.get_user_by_id(user_id)
        if not isinstance(user, User):
            return create_error_response("User Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        self.whitelist.remove(user)
        return create_error_response("User has been removed from the whitelist",
                                     status=status.HTTP_200_OK)

    @classmethod
    def add_new_server(cls, data):
        guild_id = data.get('guild')
        name = data.get('name')
        ip = data.get('ip')
        port = data.get('port')
        password = data.get('password')
        if not (guild_id and name and ip and port and password):
            return create_error_response("One or more of the required fields are missing",
                                         status=status.HTTP_400_BAD_REQUEST)
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return create_error_response("Guild Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        server = cls(
            guild=guild,
            name=name,
            ip=ip,
            port=port,
            password=password,
            monitor_chat=data.get('monitor_chat', False)
        )
        server.save()
        return create_success_response(server, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_server(cls, guild_id, name):
        guild_servers = cls.get_guild_servers(guild_id)
        if guild_servers:
            try:
                return guild_servers.get(name=name)
            except ObjectDoesNotExist:
                return None
        return None

    @classmethod
    def get_guild_servers(cls, guild_id):
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return None
        return cls.objects.filter(guild=guild)

    def __str__(self):
        return f"{self.guild.id} | {self.name}"
