from django.db import models

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.dmessages.models import Message
from geeksbot_v2.users.models import User

# Create your models here.


class RconServer(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    password = models.CharField(max_length=50)
    monitor_chat = models.BooleanField()
    monitor_chat_channel = models.CharField(max_length=30, blank=True)
    alerts_channel = models.CharField(max_length=30, blank=True)
    info_channel = models.CharField(max_length=30, blank=True)
    info_message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="+", blank=True
    )
    settings_message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="+", blank=True
    )
    whitelist = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.guild.id} | {self.name}"
