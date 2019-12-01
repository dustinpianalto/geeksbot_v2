# noinspection PyPackageRequirements
import discord


async def on_message(bot, message, user_info):
    if not user_info.get('disable_logging'):
        if message.guild:
            msg_data = {
                'author': str(message.author.id),
                'channel': str(message.channel.id),
                'mention_everyone': message.mention_everyone,
                'created_at': message.created_at
            }
            if message.mentions:
                msg_data['mentions'] = [str(user.id) for user in message.mentions]
            if message.channel_mentions:
                msg_data['channel_mentions'] = [str(channel.id) for channel in message.channel_mentions]
            if message.role_mentions:
                msg_data['role_mentions'] = [str(role.id) for role in message.role_mentions]
            if message.embeds:
                msg_data['embeds'] = [e.to_dict() for e in message.embeds]
            if message.content:
                msg_data['content'] = message.content
            if message.webhook_id:
                msg_data['webhook_id'] = message.webhook_id
            if message.tts:
                msg_data['tts'] = message.tts
            if message.attachments:
                msg_data['attachments'] = [{
                    'id': str(a.id),
                    'size': a.size,
                    'filename': a.filename,
                    'url': a.url
                } for a in message.attachments]

            bot.fs_db.document(f'guilds/{message.guild.id}/messages/{message.id}').set(msg_data)
        else:
            msg_data = {
                'author': str(message.author.id),
                'created_at': message.created_at
            }
            if message.mentions:
                msg_data['mentions'] = [str(user.id) for user in message.mentions]
            if message.embeds:
                msg_data['embeds'] = [e.to_dict() for e in message.embeds]
            if message.content:
                msg_data['content'] = message.content
            if message.webhook_id:
                msg_data['webhook_id'] = message.webhook_id
            if message.tts:
                msg_data['tts'] = message.tts
            if message.attachments:
                msg_data['attachments'] = [{
                    'id': str(a.id),
                    'size': a.size,
                    'filename': a.filename,
                    'url': a.url
                } for a in message.attachments]

            bot.fs_db.document(f'dm_channels/{message.channel.id}/messages/{message.id}').set(msg_data)


async def on_message_edit(bot, before: discord.Message, after: discord.Message, user_config):
    if not user_config.get('disable_logging'):
        if after.guild:
            msg_ref = bot.fs_db.document(f'guilds/{after.guild.id}/messages/{after.id}')
            msg_data = (await bot.loop.run_in_executor(bot.tpe, msg_ref.get)).to_dict()
            if before.content != after.content:
                if before.content:
                    if msg_data.get('previous_content') and isinstance(msg_data['previous_content'], list):
                        msg_data['previous_content'].append(before.content)
                    else:
                        msg_data['previous_content'] = [before.content, ]
                msg_data['content'] = after.content
            if before.embeds != after.embeds:
                if before.embeds:
                    if msg_data.get('previous_embeds') and isinstance(msg_data['previous_embeds'], list):
                        msg_data['previous_embeds'].append(before.embeds[0].to_dict())
                    else:
                        msg_data['previous_embeds'] = [before.embeds[0].to_dict(), ]
                msg_data['embeds'] = [e.to_dict() for e in after.embeds]
            if before.pinned != after.pinned:
                msg_data['pinned'] = after.pinned
            if before.mentions != after.mentions:
                msg_data['mentions'] = [str(user.id) for user in after.mentions]
            if before.channel_mentions != after.channel_mentions:
                msg_data['channel_mentions'] = [str(user.id) for user in after.channel_mentions]
            if before.role_mentions != after.role_mentions:
                msg_data['role_mentions'] = [str(user.id) for user in after.role_mentions]
            if before.attachments != after.attachments:
                if before.attachments:
                    if msg_data.get('previous_attachments') and isinstance(msg_data['previous_attachments'], list):
                        msg_data['previous_attachments'].append([{
                            'id': str(a.id),
                            'size': a.size,
                            'filename': a.filename,
                            'url': a.url
                        } for a in before.attachments])
                    else:
                        msg_data['previous_attachments'] = [[{
                            'id': a.id,
                            'size': a.size,
                            'filename': a.filename,
                            'url': a.url
                        } for a in before.attachments], ]
                msg_data['attachments'] = [{
                    'id': a.id,
                    'size': a.size,
                    'filename': a.filename,
                    'url': a.url
                } for a in after.attachments]

            bot.fs_db.document(f'guilds/{after.guild.id}/messages/{after.id}').set(msg_data)
        else:
            msg_ref = bot.fs_db.document(f'dm_channels/{after.channel.id}/messages/{after.id}')
            msg_data = (await bot.loop.run_in_executor(bot.tpe, msg_ref.get)).to_dict()
            if before.content != after.content:
                if before.content:
                    if msg_data.get('previous_content') and isinstance(msg_data['previous_content'], list):
                        msg_data['previous_content'].append(before.content)
                    else:
                        msg_data['previous_content'] = [before.content, ]
                msg_data['content'] = after.content
            if before.embeds != after.embeds:
                if before.embeds:
                    if msg_data.get('previous_embeds') and isinstance(msg_data['previous_embeds'], list):
                        msg_data['previous_embeds'].append(before.embeds[0].to_dict())
                    else:
                        msg_data['previous_embeds'] = [before.embeds[0].to_dict(), ]
                msg_data['embeds'] = [e.to_dict() for e in after.embeds]
            if before.pinned != after.pinned:
                msg_data['pinned'] = after.pinned
            if before.mentions != after.mentions:
                msg_data['mentions'] = [str(user.id) for user in after.mentions]
            if before.attachments != after.attachments:
                if before.attachments:
                    if msg_data.get('previous_attachments') and isinstance(msg_data['previous_attachments'], list):
                        msg_data['previous_attachments'].append([{
                            'id': str(a.id),
                            'size': a.size,
                            'filename': a.filename,
                            'url': a.url
                        } for a in before.attachments])
                    else:
                        msg_data['previous_attachments'] = [[{
                            'id': a.id,
                            'size': a.size,
                            'filename': a.filename,
                            'url': a.url
                        } for a in before.attachments], ]
                msg_data['attachments'] = [{
                    'id': a.id,
                    'size': a.size,
                    'filename': a.filename,
                    'url': a.url
                } for a in after.attachments]

            bot.fs_db.document(f'dm_channels/{after.channel.id}/messages/{after.id}').set(msg_data)
