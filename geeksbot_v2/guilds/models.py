from django.db import models
from django.contrib.postgres.fields import ArrayField

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


class Role(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, null=False)
    type = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.guild.id} | {self.id}"
