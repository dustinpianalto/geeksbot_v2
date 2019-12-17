import discord
from discord.ext import commands
import logging
import json

guild_logger = logging.getLogger('guilds')


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        default_config = {
            'prefixes': [self.bot.default_prefix],
            'id': guild.id
        }
        admin_role = guild.roles[-1] if len(guild.roles) > 1 else 0
        resp = await self.bot.aio_session.post(f'{self.bot.api_base}/guilds/',
                                               headers=self.bot.auth_header,
                                               json=default_config)
        guild_logger.info(f'Guild Joined {guild.name}: {await resp.json()}')
        if resp.status == 201:
            for role in guild.roles:
                role_dict = {
                    'id': str(role.id),
                    'role_type': 100 if role == admin_role else 0
                }
                role_resp = await self.bot.aio_session.post(f'{self.bot.api_base}/guilds/{guild.id}/roles',
                                                            headers=self.bot.auth_header,
                                                            json=role_dict)
                guild_logger.info(f'Role Added {role.name}: {await role_resp.json()}')
            for channel in guild.channels:
                channel_dict = {
                    'id': channel.id,
                    'guild': guild.id,
                    'default': False,
                    'new_patron': False,
                    'admin': False
                }
                channel_resp = await self.bot.aio_session.post(f'{self.bot.api_base}/channels/',
                                                               headers=self.bot.auth_header,
                                                               json=channel_dict)
                guild_logger.info(f'Channel Added {channel.name}: {await channel_resp.json()}')
        guild_logger.info(f'All Entries Created for {guild.name}')
        await guild.me.edit(nick=f'[{self.bot.default_prefix}] Geeksbot')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        resp = await self.bot.aio_session.delete(f'{self.bot.api_base}/guilds/{guild.id}/',
                                                 headers=self.bot.auth_header)
        if resp.status == 200:
            guild_logger.info(f'Left Guild {guild.name}: {await resp.json()}')
        else:
            guild_logger.error(f'Error Deleting Guild {guild.name}: {await resp.json()}')


def setup(bot):
    bot.add_cog(GuildEvents(bot))
