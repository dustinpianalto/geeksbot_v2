from datetime import datetime

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.fields import ArrayField
from rest_framework import status

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.guilds.models import Role
from geeksbot_v2.users.models import User
from geeksbot_v2.channels.models import Channel
from .utils import create_error_response
from .utils import create_success_response
from .utils import create_request_success_response
from .utils import create_comment_success_response

# Create your models here.


class Message(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    author = models.ForeignKey(User, related_name="+", on_delete=models.CASCADE)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name="+", on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    content = models.CharField(max_length=2000, null=True, blank=True)
    previous_content = ArrayField(models.CharField(max_length=2000), default=list)
    tagged_users = models.ManyToManyField(User, related_name="+")
    tagged_channels = models.ManyToManyField(Channel, related_name="+")
    tagged_roles = models.ManyToManyField(Role)
    tagged_everyone = models.BooleanField()
    embeds = ArrayField(models.TextField(), default=list)
    previous_embeds = ArrayField(ArrayField(models.TextField()), default=list)

    @classmethod
    def add_new_message(cls, data):
        id = data.get('id')
        if id and cls.get_message_by_id(id):
            return create_error_response("Message Already Exists",
                                         status=status.HTTP_409_CONFLICT)
        author_id = data.get('author')
        guild_id = data.get('guild')
        channel_id = data.get('channel')
        created_at = data.get('created_at')
        content = data.get('content')
        tagged_everyone = data.get('tagged_everyone')
        if not (id and author_id and guild_id and channel_id and created_at and (tagged_everyone is not None)):
            return create_error_response("One or more required fields are missing.",
                                         status=status.HTTP_400_BAD_REQUEST)
        author = User.get_user_by_id(author_id)
        if not isinstance(author, User):
            return create_error_response("Author Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return create_error_response("Guild Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        channel = Channel.get_channel_by_id(guild_id, channel_id)
        if not isinstance(channel, Channel):
            return create_error_response("Channel Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        created_at = datetime.fromtimestamp(created_at)

        message = cls(
            id=id,
            author=author,
            guild=guild,
            channel=channel,
            created_at=created_at,
            tagged_everyone=tagged_everyone or False,
            content=content or '',
            embeds=data.get('embeds') or []
        )
        message.save()
        if data.get('tagged_users'):
            tagged_users = data.get('tagged_users')
            for user_id in tagged_users:
                user = User.get_user_by_id(user_id)
                if user:
                    message.tagged_users.add(user)
        if data.get('tagged_roles'):
            tagged_roles = data.get('tagged_roles')
            for role_id in tagged_roles:
                role = Role.get_role_by_id(role_id)
                if role:
                    message.tagged_roles.add(role)
        if data.get('tagged_channels'):
            tagged_channels = data.get('tagged_channels')
            for channel_id in tagged_channels:
                channel = Channel.get_channel_by_id(guild_id, channel_id)
                if channel:
                    message.tagged_channels.add(channel)

        return create_success_response(message, status.HTTP_201_CREATED, many=False)

    def update_message(self, data):
        if data.get('modified_at'):
            self.modified_at = datetime.fromtimestamp(int(data.get('modified_at')))
        if data.get('deleted_at'):
            self.deleted_at = datetime.fromtimestamp(int(data.get('deleted_at')))
        if data.get('content'):
            content = data.get('content')
            if content != self.content:
                self.previous_content.append(self.content)
                self.content = content
        if data.get('embeds'):
            embeds = data.get('embeds')
            if embeds != self.embeds:
                self.previous_embeds.append(self.embeds)
                self.embeds = embeds
        if data.get('tagged_everyone'):
            tagged_everyone = data.get('tagged_everyone')
            if self.tagged_everyone or tagged_everyone:
                self.tagged_everyone = True
        if data.get('tagged_users'):
            tagged_users = data.get('tagged_users')
            for user in tagged_users:
                if user not in self.tagged_users:
                    self.tagged_users.append(user)
        if data.get('tagged_roles'):
            tagged_roles = data.get('tagged_roles')
            for role in tagged_roles:
                if role not in self.tagged_roles:
                    self.tagged_roles.append(role)
        if data.get('tagged_channels'):
            tagged_channels = data.get('tagged_channels')
            for channel in tagged_channels:
                if channel not in self.tagged_channels:
                    self.tagged_channels.append(channel)

        self.save()
        return create_success_response(self, status.HTTP_202_ACCEPTED, many=False)

    @classmethod
    def get_message_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return (f'{self.created_at} | '
                f'{self.author.id}'
                f'{" | Modified" if self.modified_at else ""}'
                f'{" | Deleted" if self.deleted_at else ""}')


class GuildInfo(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, blank=True, null=True
    )
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField()
    text = models.TextField(max_length=1980)
    format = models.PositiveSmallIntegerField()
    channel = models.CharField(max_length=30)
    message_number = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.guild.id} | {self.text[:25]}"


class AdminRequest(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="+", on_delete=models.DO_NOTHING)
    message = models.ForeignKey(Message, on_delete=models.DO_NOTHING)
    channel = models.ForeignKey(Channel, on_delete=models.DO_NOTHING, null=True)
    completed = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, default=None)
    completed_by = models.ForeignKey(
        User, related_name="+", on_delete=models.DO_NOTHING, null=True, blank=True, default=None
    )
    completed_message = models.CharField(max_length=1000, null=True, blank=True, default=None)
    content = models.CharField(max_length=2000)

    def update_request(self, data):
        completed = data.get('completed', False)
        completed_by_id = data.get('completed_by')
        completed_message = data.get('message', '')
        if not self.completed and completed:
            self.completed = completed
            self.completed_at = datetime.utcnow()
            self.completed_message = completed_message
            user = User.get_user_by_id(completed_by_id)
            if not isinstance(user, User):
                return create_error_response('User Does Not Exist',
                                             status=status.HTTP_404_NOT_FOUND)
            self.completed_by = user
        self.save()
        return create_request_success_response(self, status.HTTP_202_ACCEPTED)

    @classmethod
    def add_new_request(cls, guild_id, data):
        author_id = data.get('author')
        message_id = data.get('message')
        channel_id = data.get('channel')
        content = data.get('content')
        if not (guild_id and author_id and message_id and channel_id and content):
            return create_error_response("One or more of the required fields are missing.",
                                         status=status.HTTP_400_BAD_REQUEST)
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return create_error_response('Guild Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
        author = User.get_user_by_id(author_id)
        if not isinstance(author, User):
            return create_error_response('Author Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
        message = Message.get_message_by_id(message_id)
        if not isinstance(message, Message):
            return create_error_response('Message Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
        channel = Channel.get_channel_by_id(guild_id, channel_id)
        if not isinstance(channel, Channel):
            return create_error_response('Channel Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)

        print('test')

        request = cls(
            guild=guild,
            author=author,
            message=message,
            channel=channel,
            content=content
        )
        request.save()
        return create_request_success_response(request, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_open_requests_by_guild(cls, guild_id):
        return cls.objects.filter(guild__id=guild_id).filter(completed=False)

    @classmethod
    def get_open_request_by_id(cls, guild_id, request_id):
        try:
            return cls.get_open_requests_by_guild(guild_id).get(id=request_id)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return f"{self.guild.id} | {self.requested_at} | By {self.author.id}"

    @classmethod
    def get_open_requests_by_guild_author(cls, guild_id, author_id):
        return cls.get_open_requests_by_guild(guild_id).filter(author__id=author_id)


class AdminComment(models.Model):
    request = models.ForeignKey(AdminRequest, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=1000)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)

    @classmethod
    def add_new_comment(cls, data, guild_id, request_id):
        author_id = data.get('author')
        content = data.get('content')
        if not (request_id and author_id and content):
            return create_error_response('Request, Author, and Content are required fields',
                                         status=status.HTTP_400_BAD_REQUEST)
        request = AdminRequest.get_open_request_by_id(guild_id, request_id)
        if not isinstance(request, AdminRequest):
            return create_error_response("Admin Request Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        author = User.get_user_by_id(author_id)
        if not isinstance(author, User):
            return create_error_response("Author Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)

        comment = cls(
            request=request,
            author=author,
            content=content
        )
        comment.save()
        return create_comment_success_response(comment, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_comment_by_id(cls, comment_id):
        try:
            return cls.objects.get(id=comment_id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_comments_by_request(cls, request):
        return cls.objects.filter(request=request).order_by('updated_at')
