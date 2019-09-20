import os

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from .utils import create_error_response
from .utils import create_success_response
from .utils import create_role_success_response


# Create your models here.


class Guild(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    admin_chat = models.CharField(max_length=30, blank=True, null=True)
    new_patron_message = models.TextField(max_length=1000, blank=True, null=True)
    default_channel = models.CharField(max_length=30)
    new_patron_channel = models.CharField(max_length=30, blank=True, null=True)
    prefixes = ArrayField(models.CharField(max_length=10))

    def __str__(self):
        return self.id

    def update_guild(self, data):
        if data.get('admin_chat'):
            self.admin_chat = data.get('admin_chat')
        if data.get('new_patron_message'):
            self.new_patron_message = data.get('new_patron_message')
        if data.get('default_channel'):
            self.default_channel = data.get('default_channel')
        if data.get('new_patron_channel'):
            self.new_patron_channel = data.get('new_patron_channel')
        if data.get('add_prefix'):
            if data.get('add_prefix') not in self.prefixes:
                self.prefixes.append(data.get('add_prefix'))
        if data.get('remove_prefix'):
            if data.get('remove_prefix') in self.prefixes:
                self.prefixes.remove(data.get('remove_prefix'))
            if len(self.prefixes) <= 0:
                self.prefixes = [os.environ['DISCORD_DEFAULT_PREFIX'], ]

        self.save()
        return self

    @classmethod
    def get_guild_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def create_guild(cls, data):
        id = data.get('id')
        default_channel = data.get('default_channel')
        if not (id and default_channel):
            return create_error_response('id and default_channel are required',
                                         status=status.HTTP_400_BAD_REQUEST)

        if cls.get_guild_by_id(id):
            return create_error_response('That Guild already exists',
                                         status.HTTP_409_CONFLICT)

        guild = cls(
            id=id,
            default_channel=default_channel,
            prefixes=data.get('prefixes'),
            admin_chat=data.get('admin_chat'),
            new_patron_message=data.get('new_patron_message'),
            new_patron_channel=data.get('new_patron_channel')
        )
        guild.save()
        return create_success_response(guild, status.HTTP_201_CREATED, many=False)


class Role(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, null=False)
    role_type = models.PositiveSmallIntegerField()

    def update_role(self, data):
        if data.get('role_type'):
            self.role_type = data.get('role_type')

        self.save()
        return create_role_success_response(self, status=status.HTTP_202_ACCEPTED, many=False)

    @classmethod
    def add_new_role(cls, data):
        id = data.get('id')
        guild_id = data.get('guild')
        role_type = data.get('role_type')
        if not (id and guild_id and role_type):
            return create_error_response("The Role ID, Guild, and Role Type are required",
                                         status=status.HTTP_400_BAD_REQUEST)

        if cls.get_role_by_id(id):
            return create_error_response("That Role Already Exists",
                                         status=status.HTTP_409_CONFLICT)
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return create_error_response("Guild Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)

        try:
            role_type = int(role_type)
        except ValueError:
            return create_error_response("Role Type must be a positive number",
                                         status=status.HTTP_400_BAD_REQUEST)
        if role_type < 0:
            return create_error_response("Role Type must be a positive number",
                                         status=status.HTTP_400_BAD_REQUEST)
        elif 1000 < role_type:
            return create_error_response("Role Type must be less than 1000",
                                         status=status.HTTP_400_BAD_REQUEST)

        role = cls(
            id=id,
            guild=guild,
            role_type=role_type
        )
        role.save()
        return create_role_success_response(role, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_role_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return f"{self.guild.id} | {self.id}"
