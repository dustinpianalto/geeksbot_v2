import discord
from discord.ext import commands
from datetime import datetime
import logging


user_logger = logging.getLogger('UserEvents')


class UserEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        data = {
            'id': after.id,
            'username': after.name,
            'discriminator': after.discriminator,
            'animated': after.is_avatar_animated(),
            'avatar': after.avatar or str(after.default_avatar)
        }
        resp = await self.bot.aio_session.put(f'{self.bot.api_base}/users/{after.id}/',
                                              headers=self.bot.auth_header,
                                              json=data)
        msg = await resp.json()
        if resp.status == 400:
            data = {
                'id': after.id,
                'username': after.name,
                'discriminator': after.discriminator,
                'guilds': [f'{self.bot.api_base}/guilds/{after.guild.id}/'],
                'animated': after.is_avatar_animated(),
                'avatar': after.avatar or str(after.default_avatar),
                'bot': after.bot
            }
            resp = await self.bot.aio_session.post(f'{self.bot.api_base}/users/',
                                                   headers=self.bot.auth_header,
                                                   json=data)
            msg = await resp.json()
        user_logger.info(f'User Update Response:\n{msg}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = {
            'id': member.id,
            'username': member.name,
            'discriminator': member.discriminator,
            'guilds': [f'{self.bot.api_base}/guilds/{member.guild.id}/'],
            'animated': member.is_avatar_animated(),
            'avatar': member.avatar or str(member.default_avatar),
            'bot': member.bot
        }
        resp = await self.bot.aio_session.post(f'{self.bot.api_base}/users/',
                                               headers=self.bot.auth_header,
                                               json=data)
        msg = await resp.json()
        if resp.status == 400 and 'user with this id already exists.' \
                in msg.get('id', []):
            data = {
                'id': member.id,
                'guilds': [f'{self.bot.api_base}/guilds/{member.guild.id}/']
            }
            resp = await self.bot.aio_session.put(f'{self.bot.api_base}/users/{member.id}/',
                                                  headers=self.bot.auth_header,
                                                  json=data)
            msg = await resp.json()
        user_logger.info(f'User Joined: {msg}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = {
            'id': member.id,
            # Because this doesn't go through the serializer we just use the id for the guild
            'guilds': [str(member.guild.id)]
        }
        resp = await self.bot.aio_session.patch(f'{self.bot.api_base}/users/{member.id}/',
                                                headers=self.bot.auth_header,
                                                json=data)
        msg = await resp.json()
        user_logger.info(f'User Left {member.guild}: {msg}')


def setup(bot):
    bot.add_cog(UserEvents(bot))
