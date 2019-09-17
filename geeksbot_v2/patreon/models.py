from django.db import models

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.guilds.models import Role

# Create your models here.


class PatreonCreator(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, null=False)
    creator = models.CharField(max_length=50, null=False)
    link = models.CharField(max_length=100, null=False)

    def __str__(self):
        return f"{self.guild.id} | {self.creator}"


class PatreonTier(models.Model):
    creator = models.ForeignKey(PatreonCreator, on_delete=models.CASCADE)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.guild.id} | {self.creator.creator} | {self.name}"
