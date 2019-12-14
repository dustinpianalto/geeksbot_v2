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
        user_logger.info(f'User Update Response:\n{await resp.json()}')


def setup(bot):
    bot.add_cog(UserEvents(bot))
