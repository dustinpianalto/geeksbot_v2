from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from geeksbot_v2.guilds.models import Guild
from geeksbot_v2.guilds.models import Role
from .utils import create_error_response
from .utils import create_success_creator_response
from .utils import create_success_tier_response

# Create your models here.


class PatreonCreator(models.Model):
    guilds = models.ManyToManyField(Guild)
    creator = models.CharField(max_length=50, null=False, primary_key=True)
    link = models.CharField(max_length=100, null=False, unique=True)

    def update_creator(self, data):
        if data.get('guild'):
            guild = Guild.get_guild_by_id(data.get('guild'))
            if not isinstance(guild, Guild):
                return create_error_response('Guild Does Not Exist',
                                             status=status.HTTP_404_NOT_FOUND)
            self.guilds.add(guild)
        if data.get('link'):
            self.link = data.get('link')

        self.save()
        return create_success_creator_response(self, status.HTTP_202_ACCEPTED, many=False)

    @classmethod
    def add_new_creator(cls, data):
        creator = data.get('creator')
        if PatreonCreator.get_creator_by_name(creator):
            return create_error_response('That Creator already exists',
                                         status=status.HTTP_409_CONFLICT)
        link = data.get('link')
        if not (creator and link):
            return create_error_response('Creator and Link are both required fields',
                                         status=status.HTTP_400_BAD_REQUEST)
        guild = Guild.get_guild_by_id(data.get('guild'))
        if not guild:
            return create_error_response('A Valid Guild is required',
                                         status=status.HTTP_400_BAD_REQUEST)

        new_creator = cls(
            creator=creator,
            link=link
        )
        new_creator.save()
        new_creator.guilds.add(guild)
        return create_success_creator_response(new_creator, status.HTTP_201_CREATED, many=False)

    @classmethod
    def get_creator_by_name(cls, name):
        try:
            return cls.objects.get(creator=name)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return f"{self.guild.id} | {self.creator}"


class PatreonTier(models.Model):
    creator = models.ForeignKey(PatreonCreator, on_delete=models.CASCADE)
    guild = models.ManyToManyField(Guild)
    name = models.CharField(max_length=50)
    description = models.TextField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)
    next_lower_tier = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def update_tier(self, data):
        if data.get('guild'):
            guild = Guild.get_guild_by_id(data.get('guild'))
            if not isinstance(guild, Guild):
                return create_error_response('Guild Does Not Exist',
                                             status=status.HTTP_404_NOT_FOUND)
            self.guilds.add(guild)
        if data.get('name'):
            self.name = data.get('name')
        if data.get('description'):
            self.description = data.get('description')
        if data.get('role'):
            role = Role.get_role_by_id(data.get('role'))
            if not isinstance(role, Role):
                return create_error_response('Role Does Not Exist',
                                             status=status.HTTP_404_NOT_FOUND)
            self.role = role
        if data.get('amount'):
            self.amount = data.get('amount')
        if data.get('next_lower_tier'):
            tier = self.get_tier_by_id(data.get('next_lower_tier'))
            if not isinstance(tier, self.__class__):
                return create_error_response('Next Lower Tier Does Not Exist',
                                             status=status.HTTP_404_NOT_FOUND)
            self.next_lower_tier = tier

        self.save()
        return create_success_tier_response(tier, status.HTTP_202_ACCEPTED, many=False)

    @classmethod
    def get_tier_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def add_new_tier(cls, data):
        creator_str = data.get('creator')
        guild_id = data.get('guild')
        name = data.get('name')
        description = data.get('description')
        role_id = data.get('role')
        next_lower_tier_id = data.get('next_lower_tier')
        if not (creator_str and guild_id and name and description and role_id):
            return create_error_response("The Creator's name, Guild, Tier name, Description, "
                                         "and Discord Role are all required.",
                                         status=status.HTTP_400_BAD_REQUEST)
        creator = PatreonCreator.get_creator_by_name(creator_str)
        if not isinstance(creator, PatreonCreator):
            return create_error_response("Creator Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        guild = Guild.get_guild_by_id(guild_id)
        if not isinstance(guild, Guild):
            return create_error_response("Guild Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        role = Role.get_role_by_id(role_id)
        if not isinstance(role, Role):
            return create_error_response("Role Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)
        if next_lower_tier_id:
            next_lower_tier = cls.get_tier_by_id(next_lower_tier_id)
            if not isinstance(next_lower_tier, cls):
                return create_error_response("Next Lower Tier Does Not Exist",
                                             status=status.HTTP_404_NOT_FOUND)
            if next_lower_tier.guild != guild:
                return create_error_response("The given next lower tier is not for the same guild.",
                                             status=status.HTTP_400_BAD_REQUEST)
            if next_lower_tier.creator != creator:
                return create_error_response("The given next lower tier is not for the same creator.",
                                             status=status.HTTP_400_BAD_REQUEST)
        try:
            PatreonTier.objects.filter(creator=creator, guilds__id=guild.id).get(name=name)
        except ObjectDoesNotExist:
            tier = cls(
                creator=creator,
                name=name,
                description=description,
                role=role,
                amount=data.get('amount'),
                next_lower_tier=next_lower_tier if next_lower_tier_id else None
            )
            tier.save()
            return create_success_tier_response(tier, status.HTTP_201_CREATED, many=False)
        else:
            return create_error_response("A Tier with that name already exists for that creator in this guild.",
                                         status=status.HTTP_409_CONFLICT)

    def __str__(self):
        return f"{self.guild.id} | {self.creator.creator} | {self.name}"
