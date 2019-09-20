from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from geeksbot_v2.guilds.models import Guild
from .utils import verify_user_data
from .utils import create_error_response
from .utils import create_log_success_response
from .utils import create_success_response


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
    )
    id = models.CharField(max_length=30, primary_key=True)
    discord_username = models.CharField(max_length=100, null=True)
    previous_discord_usernames = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    discriminator = models.CharField(max_length=4, null=True)
    previous_discriminators = ArrayField(models.CharField(max_length=4), blank=True, null=True)
    guilds = models.ManyToManyField(Guild, blank=True, null=True)
    steam_id = models.CharField(max_length=30, blank=True, null=True)
    animated = models.BooleanField(blank=True, null=True)
    avatar = models.CharField(max_length=100, blank=True, null=True)
    bot = models.BooleanField(blank=True, null=True)
    banned = models.BooleanField(default=False)
    logging_enabled = models.BooleanField(default=True)

    @classmethod
    def add_new_user(cls, data):
        if not verify_user_data(data):
            return create_error_response("Not all required fields are present.",
                                         status=status.HTTP_400_BAD_REQUEST)
        id = data.get('id')
        if id:
            if User.objects.filter(id=id).exists():
                return create_error_response("User Exists please update instead of create",
                                             status=status.HTTP_409_CONFLICT)
        discord_username = data.get('username')
        discriminator = data.get('discriminator')
        guild_id = data.get('guild')
        try:
            guild = Guild.objects.get(id=str(guild_id))
        except ObjectDoesNotExist:
            return create_error_response("That is not a valid Guild",
                                         status=status.HTTP_400_BAD_REQUEST)
        animated = data.get('animated')
        avatar = data.get('avatar')
        bot = data.get('bot')
        banned = data.get('banned')
        logging = data.get('logging')
        if not (avatar and (animated is not None) and (bot is not None)):
            return create_error_response("All required fields must contain a value",
                                         status.HTTP_400_BAD_REQUEST)

        user = User(
            id=id,
            discord_username=discord_username,
            discriminator=discriminator,
            animated=animated,
            avatar=avatar,
            bot=bot,
            banned=banned or False,
            logging_enabled=logging or True
        )
        user.save()
        user.guilds.add(guild)
        return create_success_response(user, status.HTTP_201_CREATED, many=False)

    def update_user(self, data):
        if data.get('username') and data.get('username') != self.discord_username:
            if isinstance(self.previous_discord_usernames, list):
                self.previous_discord_usernames.append(self.discord_username)
            else:
                self.previous_discord_usernames = [self.discord_username, ]
            self.discord_username = data.get('username')
        if data.get('discriminator') and data.get('discriminator') != self.discriminator:
            if isinstance(self.previous_discriminators, list):
                self.previous_discriminators.append(self.discriminator)
            else:
                self.previous_discriminators = [self.discriminator, ]
            self.discriminator = data.get('discriminator')
        if data.get('guild'):
            guild = Guild.get_guild_by_id(data.get('guild'))
            if not isinstance(guild, Guild):
                return create_error_response("That is not a valid Guild",
                                             status=status.HTTP_400_BAD_REQUEST)
            self.guilds.add(guild)
        if data.get('steam_id'):
            self.steam_id = data.get('steam_id')
        if data.get('animated'):
            self.animated = data.get('animated')
        if data.get('avatar'):
            self.avatar = data.get('avatar')
        if data.get('bot'):
            self.bot = data.get('bot')
        if data.get('banned'):
            self.banned = data.get('banned')
        if data.get('logging'):
            self.logging_enabled = data.get('logging')

        self.save()
        return create_success_response(self, status.HTTP_202_ACCEPTED, many=False)

    @classmethod
    def get_user_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    action = models.IntegerField()
    description = models.CharField(max_length=100, null=True, blank=True)

    @classmethod
    def add_new_log(cls, user, data):
        user_id = data.get('user')
        action = data.get('action')
        description = data.get('description')
        if not (user_id and action):
            return create_error_response("User and Action are required.",
                                         status=status.HTTP_400_BAD_REQUEST)
        user = User.get_user_by_id(user_id)
        if not isinstance(user, User):
            return create_error_response("User Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        try:
            action = int(action)
        except ValueError:
            return create_error_response("The Action must be a number",
                                         status=status.HTTP_400_BAD_REQUEST)
        log = cls(
            user=user,
            action=action,
            description=description
        )
        log.save()
        return create_log_success_response(log, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_log_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_logs_by_user(cls, user_id, count: int = None):
        user = User.get_user_by_id(user_id)
        if isinstance(user, User):
            user_logs = cls.objects.filter(user=user).order_by('-time')
            if count:
                user_logs = user_logs[:count]
            if len(user_logs) > 0:
                return user_logs
            else:
                return []
        else:
            return []

    @classmethod
    def get_logs_by_user_action(cls, user_id, action, count: int = None):
        user = User.get_user_by_id(user_id)
        if isinstance(user, User):
            user_logs = cls.objects.filter(user=user, action=action).order_by('-time')
            if count:
                user_logs = user_logs[:count]
            if len(user_logs) > 0:
                return user_logs
            else:
                return []
        else:
            return []

    def __str__(self):
        return f"{self.time} | {self.user.id} | {self.action}"
