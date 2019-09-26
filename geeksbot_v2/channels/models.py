from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from geeksbot_v2.guilds.models import Guild
from .utils import create_error_response
from .utils import create_success_response

# Create your models here.


class Channel(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    default = models.BooleanField(default=False)
    new_patron = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    def update_channel(self, data):
        if data.get('default'):
            try:
                existing_default = self.get_guild_channels(self.guild).get(default=True)
            except ObjectDoesNotExist:
                pass
            else:
                existing_default.default = False
                existing_default.save()
            finally:
                self.default = data.get('default')
        if data.get('new_patron'):
            self.new_patron = data.get('new_patron')
        if data.get('admin'):
            self.admin = data.get('admin')
        
        self.save()
        return self

    @classmethod
    def add_new_channel(cls, data):
        id = data.get('id')
        if id and cls.get_channel_by_id(id):
            return create_error_response('Channel Already Exists',
                                         status=status.HTTP_409_CONFLICT)
        guild_id = data.get('guild')
        if not (id and guild_id):
            return create_error_response('ID and Guild are required',
                                         status=status.HTTP_400_BAD_REQUEST)
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return create_error_response('Guild Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)

        channel = cls(
            id=id,
            guild=guild,
            default=data.get('default', False),
            new_patron=data.get('new_patron', False),
            admin=data.get('admin', False)
        )
        channel.save()
        return create_success_response(channel, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_channel_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None
    
    @classmethod
    def get_guild_channels(cls, guild):
        if isinstance(guild, Guild):
            return cls.objects.filter(guild=guild)

    def __str__(self):
        return str(id)
