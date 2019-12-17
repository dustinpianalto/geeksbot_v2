import discord
from discord.ext import commands
from datetime import datetime, timezone
import logging


message_logger = logging.getLogger('MessageEvents')


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_message_data(self, message: discord.Message):
        data = {
            'id': message.id,
            'author': message.author.id,
            'guild': message.guild.id,
            'channel': message.channel.id,
            'created_at': message.created_at.timestamp(),
            'tagged_everyone': message.mention_everyone,
            'content': message.content,
            'embeds': [e.to_dict() for e in message.embeds],
            'tagged_users': [user.id for user in message.mentions],
            'tagged_roles': [role.id for role in message.role_mentions],
            'tagged_channels': [channel.id for channel in message.channel_mentions],
        }
        return data

    @commands.Cog.listener(name='on_message')
    async def on_message(self, message):
        message_logger.info(f'Got Message')
        r = await self.bot.aio_session.get(f'{self.bot.api_base}/users/{message.author.id}/',
                                           headers=self.bot.auth_header)
        if r.status != 200:
            message_logger.warning(f'User not found: {message.author.id} Status: {r.status}')
            return

        user = await r.json()
        if user.get('logging_enabled'):
            message_data = self.get_message_data(message)
            r = await self.bot.aio_session.post(f'{self.bot.api_base}/messages/',
                                                headers=self.bot.auth_header,
                                                json=message_data)
            message_logger.info(f'Storing Message:\nStatus: {r.status}\n{await r.json()}')

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        data = {
            'deleted_at': datetime.utcnow().timestamp()
        }
        r = await self.bot.aio_session.put(f'{self.bot.api_base}/messages/{payload.message_id}',
                                           headers=self.bot.auth_header,
                                           json=data)
        message_logger.info(f'Deleting Message {payload.message_id}:\nStatus: {r.status}\n{await r.json()}')

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        data = {
            'deleted_at': datetime.utcnow().timestamp()
        }
        for id in payload.message_ids:
            r = await self.bot.aio_session.put(f'{self.bot.api_base}/messages/{id}',
                                               headers=self.bot.auth_header,
                                               json=data)
            message_logger.info(f'Deleting Message {id}:\nStatus: {r.status}\n{await r.json()}')

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if payload.data.get('mentions'):
            tagged_users = [user.id for user in payload.data.get('mentions')]
        else:
            tagged_users = None
        if payload.data.get('mention_roles'):
            tagged_roles = [role.id for role in payload.data.get('mention_roles')]
        else:
            tagged_roles = None
        if payload.data.get('mention_channels'):
            tagged_channels = [channel.id for channel in payload.data.get('mention_channels')]
        else:
            tagged_channels = None

        data = {
            'modified_at': datetime.utcnow().timestamp(),
            'content': payload.data.get('content'),
            'embeds': payload.data.get('embeds'),
            'tagged_everyone': payload.data.get('mention_everyone'),
            'tagged_users': tagged_users,
            'tagged_roles': tagged_roles,
            'tagged_channels': tagged_channels
        }
        r = await self.bot.aio_session.put(f'{self.bot.api_base}/messages/{payload.message_id}/',
                                           headers=self.bot.auth_header,
                                           json=data)
        message_logger.info(f'Editing Message {payload.message_id}\nStatus: {r.status}\n{await r.json()}')


def setup(bot):
    bot.add_cog(MessageEvents(bot))
