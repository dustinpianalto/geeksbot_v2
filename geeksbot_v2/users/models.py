from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from geeksbot_v2.guilds.models import Guild


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    id = models.CharField(max_length=30, primary_key=True)
    discord_username = models.CharField(max_length=100, null=True)
    previous_discord_usernames = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    discriminator = models.IntegerField(null=True)
    previous_discriminators = ArrayField(models.IntegerField(), blank=True, null=True)
    guilds = models.ManyToManyField(Guild, blank=True, null=True)
    steam_id = models.CharField(max_length=30, blank=True, null=True)
    animated = models.BooleanField(blank=True, null=True)
    avatar = models.CharField(max_length=100, blank=True, null=True)
    bot = models.BooleanField(blank=True, null=True)
    banned = models.BooleanField(default=False)
    logging_enabled = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField()
    action = models.IntegerField()
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.time} | {self.user.id} | {self.action}"
