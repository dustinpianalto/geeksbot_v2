from django.db import models
from django.contrib.postgres.fields import ArrayField

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.users.models import User

# Create your models here.


class Message(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    channel = models.CharField(max_length=30)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    content = models.CharField(max_length=2000)
    previous_content = ArrayField(models.CharField(max_length=2000))
    tagged_users = ArrayField(models.CharField(max_length=30))
    tagged_channels = ArrayField(models.CharField(max_length=30))
    tagged_roles = ArrayField(models.CharField(max_length=30))
    tagged_everyone = models.BooleanField()
    embeds = ArrayField(models.TextField())
    previous_embeds = ArrayField(ArrayField(models.TextField()))

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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    completed = models.BooleanField()
    requested_at = models.DateTimeField()
    completed_at = models.DateTimeField()

    def __str__(self):
        return f"{self.guild.id} | {self.requested_at} | By {self.author.id}"
