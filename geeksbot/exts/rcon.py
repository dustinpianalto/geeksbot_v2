import discord
from discord.ext import commands
from discord.ext.commands import Greedy
import logging
from datetime import datetime
import asyncio
from typing import Union
from geeksbot.imports import arcon
from geeksbot.imports import utils
from geeksbot.imports import checks

rcon_log = logging.getLogger('rcon')


class Rcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @staticmethod
    # async def admin(bot, guild, msg, server_name, server_con: arcon.ARKServer, guild_config: dict):
    #     player = msg.split(' ||| ')[1].split(' (')[0]
    #     rcon_log.info(f'{player} requested admin assistance')
    #     admin_roles = guild_config.get('admin_roles')
    #     if admin_roles:
    #         for role in admin_roles:
    #             msg = '{0} {1}'.format(msg, discord.utils.get(guild.roles, id=admin_roles[role]).mention)
    #     await server_con.server_chat_to_player_name(player, 'GeeksBot: Admin Geeks have been notified you need '
    #                                                         'assistance. Please be patient.')
    #     return msg
    #
    # async def dinowipe(self, bot, guild, msg, server_name, server_con: arcon.ARKServer, guild_config: dict):
    #     player = msg.split(' ||| ')[1].split(' (')[0]
    #     steam_ref = self.bot.fs_db.collection(f'users').where('steam_name', '==', player)
    #     user_info = await self.bot.loop.run_in_executor(self.bot.tpe, steam_ref.get)
    #     steamid = None
    #     user = None
    #     for user in user_info:
    #         if user:
    #             steamid = user.to_dict().get('steam_id')
    #             break
    #     if steamid:
    #         if not self.bot.dino_wipe_request.get(server_name):
    #             if user:
    #                 player = await patron.Patron.from_id(bot, steamid, discord_id=int(user.id))
    #                 rcon_log.info(f'{player.steam_name} requested a wild dino wipe')
    #                 member = guild.get_member(player.discord_id)
    #                 self.bot.loop.create_task(self.request_dinowipe(member, server_name, server_con))
    #             else:
    #                 await server_con.server_chat_to_player_name(player,
    #                                                             'Sorry, an error has occurred please try again.')
    #         else:
    #             await server_con.server_chat_to_player_name(player, 'A Wild Dino Wipe request is already in progress.')
    #     else:
    #         await server_con.server_chat_to_player_name(player, 'Sorry. You are not registered to run commands via the '
    #                                                             'in-game chat. Please send a chat message in-game '
    #                                                             '$register steamid=your_steam_id and follow the '
    #                                                             'instructions so I can link your character with your '
    #                                                             'Discord account. Thanks')
    #     return msg
    #
    # @staticmethod
    # async def delaywipe(bot, guild: discord.Guild, msg, server_name, server_con: arcon.ARKServer, guild_config: dict):
    #     player = msg.split(' ||| ')[1].split(' (')[0]
    #     if bot.dino_wipe_request.get(server_name):
    #         bot.dino_wipe_request[server_name] = False
    #         await server_con.broadcast(f'Wild Dino Wipe has been delayed by {player}. '
    #                                    f'Please watch chat for timing updates')
    #     elif bot.dino_wipe_request.get(server_name) is None:
    #         await server_con.server_chat_to_player_name(player, 'There are no Wild Dino Wipes pending.')
    #     else:
    #         await server_con.server_chat_to_player_name(player, 'The dino wipe has already been delayed.')
    #     return msg
    #
    # @staticmethod
    # async def register(bot, guild, msg, server_name, server_con: arcon.ARKServer, guild_config: dict):
    #     player = msg.split(' ||| ')[1].split(' (')[0]
    #     steamid = msg.split(' ||| ')[1].split('steamid=')[1].split(' ')[0].replace('`', '').replace("'", '').strip()
    #     rcon_log.info(f'{player} - {steamid}')
    #     try:
    #         int(steamid)
    #     except ValueError:
    #         await server_con.server_chat_to_player_name(player, 'That is not a valid SteamID')
    #         return msg
    #     else:
    #         identifier = randint(10000, 99999)
    #         prefix = guild_config.get("prefixes", bot.default_prefix)
    #         await server_con.server_chat_to_player_name(player,
    #                                                     'Your SteamID has been noted, to finish registering '
    #                                                     'please run the following command in the discord '
    #                                                     f'channel. You will not be able to run commands '
    #                                                     f'in-game until your registration is completed... '
    #                                                     f'{prefix[0] if isinstance(prefix, list) else prefix}'
    #                                                     f'register {identifier}')
    #         bot.pending_registrations[identifier] = (player, steamid)
    #     return msg
    #
    # @commands.command(name='register')
    # async def register_discord_account(self, ctx, identifier: int=None):
    #     user_ref = self.bot.fs_db.document(f'users/{ctx.author.id}')
    #     user_info = (await self.bot.loop.run_in_executor(self.bot.tpe, user_ref.get)).to_dict()
    #     if user_info.get('steam_id') and user_info.get('steam_name'):
    #         await ctx.send('You are already registered to run commands in-game')
    #         return
    #
    #     if identifier not in self.bot.pending_registrations.keys():
    #         await ctx.send('That identifier is not in the pending registrations')
    #         return
    #
    #     steam_info = self.bot.pending_registrations[identifier]
    #
    #     await self.bot.loop.run_in_executor(self.bot.tpe, user_ref.update, {
    #         'steam_name': steam_info[0],
    #         'steam_id': steam_info[1]
    #     })
    #     await ctx.send('Registration complete. You are now authorized to run commands in-game on the ARK servers.')
    #     del self.bot.pending_registrations[identifier]
    #
    # async def create_server_chat_chan(self, guild: discord.Guild, server_name: str,
    #                                   server_con: arcon.ARKServer, guild_config: dict):
    #     rcon_log.info(f'Creating channel for {server_name}')
    #     category = discord.utils.get(guild.categories, name='Server Chats')
    #     if category is None:
    #         overrides = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}
    #         category = await guild.create_category('Server Chats', overwrites=overrides)
    #     rcon_log.info(category)
    #     channels = guild.channels
    #     if category:
    #         for channel in category.channels:
    #             if server_con.server_chat_channel == channel.id:
    #                 return channel
    #         else:
    #             rcon_log.info(f'Creating {server_name}')
    #             chan = await guild.create_text_channel(f'{server_name}', category=category)
    #             server_con.server_chat_channel = chan.id
    #             if guild_config.get('rcon_connections'):
    #                 guild_config['rcon_connections'][server_name]['game_chat_chan_id'] = chan.id
    #                 guild_ref = self.bot.fs_db.document(f'guilds/{guild.id}')
    #                 await self.bot.loop.run_in_executor(self.bot.tpe, guild_ref.update, guild_config)
    #             return chan
    #
    # async def _monitor_chat(self, guild, server_name, server_con, guild_config: dict):
    #     # noinspection PyShadowingNames
    #     async def start_monitor_chat(bot, guild, *, server_name: str,
    #                                  server_con: arcon.ARKServer, guild_config: dict):
    #         while server_con.monitor_chat:
    #             messages = await server_con.getchat()
    #             rcon_log.debug('Got chat from {0}.'.format(server_name))
    #             for message in [msg.strip() for msg in messages.split('\n')
    #                             if msg.strip() != 'Server received, But no response!!']:
    #                 rcon_log.info(message)
    #                 message_out = f'```{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ||| {message}```'
    #                 for command in self.bot.game_commands:
    #                     prefix_command = '{0}{1}'.format(self.bot.game_prefix, command)
    #                     if message.split('): ')[-1].startswith(prefix_command):
    #                         try:
    #                             func = getattr(self, command)
    #                         except AttributeError:
    #                             rcon_log.warning('Function not found "{0}"'.format(command))
    #                         else:
    #                             rcon_log.info(f'Sending to {command}')
    #                             message_out = await func(bot, guild, message_out, server_name, server_con, guild_config)
    #
    #                 await guild.get_channel(server_con.server_chat_channel).send(message_out)
    #             await asyncio.sleep(1)
    #         await guild.get_channel(server_con.server_chat_channel).send('Monitoring Stopped')
    #
    #     rcon_log.info(server_con.server_chat_channel)
    #     if server_con.server_chat_channel:
    #         channel = self.bot.get_channel(server_con.server_chat_channel)
    #         if not channel:
    #             channel = await self.create_server_chat_chan(guild, server_name, server_con, guild_config)
    #     else:
    #         channel = await self.create_server_chat_chan(guild, server_name, server_con, guild_config)
    #     rcon_log.info(channel)
    #     self.bot.loop.create_task(start_monitor_chat(self.bot, guild, server_name=server_name,
    #                                                  server_con=server_con, guild_config=guild_config))
    #     await channel.send('Started monitoring on the {0} server.'.format(server_name))
    #     rcon_log.debug('Started monitoring on the {0} server.'.format(server_name))
    #
    # @commands.command()
    # @commands.guild_only()
    # async def monitor_chat(self, ctx, *, server=None):
    #     """Begins monitoring the specified ARK server for chat messages and other events.
    #     The specified server must already be in the current guild\'s configuration.
    #     To add and remove ARK servers from the guild see add_rcon_server and remove_rcon_server.
    #     The server argument is not case sensitive and if the server name has two
    #         words it can be in one of the following forms:
    #     first last
    #     first_last
    #     "first last"
    #     To view all the valid ARK servers for this guild see list_ark_servers."""
    #
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         if server is not None:
    #             server = server.replace('_', ' ').title()
    #             server_con: arcon.ARKServer = await self.get_rcon_server_by_name(guild_config=ctx.guild_config,
    #                                                                              name=server)
    #             if server_con:
    #                 server_con.monitor_chat = True
    #                 ctx.guild_config['rcon_connections'][server]["monitoring_chat"] = 1
    #                 guild_ref = self.bot.fs_db.document(f'guilds/{ctx.guild.id}')
    #                 await self.bot.loop.run_in_executor(self.bot.tpe, guild_ref.update, ctx.guild_config)
    #                 await self._monitor_chat(ctx.guild, server, server_con, ctx.guild_config)
    #                 await ctx.message.add_reaction('✅')
    #             else:
    #                 await ctx.send(f'Server not found: {server}')
    #         else:
    #             await ctx.send(f'You must include a server in this command.')
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')
    #
    # @commands.command()
    # @commands.guild_only()
    # async def end_monitor_chat(self, ctx, *, server=None):
    #     """Ends chat monitoring on the specified server.
    #     Context is the same as monitor_chat"""
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         if server is not None:
    #             server = server.replace('_', ' ').title()
    #             server_con: arcon.ARKServer = await self.get_rcon_server_by_name(guild_config=ctx.guild_config,
    #                                                                              name=server)
    #             if server_con:
    #                 server_con.monitor_chat = False
    #             else:
    #                 await ctx.send(f'{server} is not connected currently.')
    #             if server in ctx.guild_config.get('rcon_connections', []):
    #                 ctx.guild_config['rcon_connections'][server]["monitoring_chat"] = 0
    #                 guild_ref = self.bot.fs_db.document(f'guilds/{ctx.guild.id}')
    #                 await self.bot.loop.run_in_executor(self.bot.tpe, guild_ref.update, ctx.guild_config)
    #             else:
    #                 await ctx.send(f'Server not found in config: {server}')
    #         else:
    #             await ctx.send(f'You must include a server in this command.')
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')

    @commands.command()
    @commands.guild_only()
    @checks.is_moderator()
    async def listplayers(self, ctx, *, server_name=None):
        """Lists the players currently connected to the specified ARK server.
        The specified server must already be in the current guild\'s configuration.
        To add and remove ARK servers from the guild see add_rcon_server and remove_rcon_server.
        The server argument is not case sensitive and if the server name has two
            words it can be in one of the following forms:
        first last
        first_last
        "first last"
        To view all the valid ARK servers for this guild see list_ark_servers."""
        if server_name:
            server_name = server_name.replace('_', ' ').title()
            msg = await ctx.send(f'**Getting Data for the {server_name} server**')
            await ctx.channel.trigger_typing()
            resp = await self.bot.aio_session.get(
                f'{self.bot.api_base}/rcon/{ctx.guild.id}/{server_name}/listplayers/',
                headers=self.bot.auth_header
            )
            if resp.status == 200:
                message = '\n'.join(await resp.json())
                await ctx.channel.trigger_typing()
                await msg.delete()
                await ctx.send(f'**Players currently on the {server_name} server:**\n{message}')
                return
            elif resp.status < 500:
                message = (await resp.json()).get('details', 'There was a problem. Please try again')
            else:
                message = "There was an error on my server. I have notified the maintainers."
            await ctx.send(message)
        else:
            futures = []
            resp = await self.bot.aio_session.get(
                f'{self.bot.api_base}/rcon/{ctx.guild.id}/',
                headers=self.bot.auth_header
            )
            if resp.status != 200:
                await ctx.send('There was a problem getting the servers for this guild.')
                return
            guild_servers = await resp.json()
            for server in guild_servers:
                msg = await ctx.send(f'**Getting Data for the {server["name"]} server**')

                # noinspection PyShadowingNames
                async def _listplayers(server_name: str, msg: discord.Message):
                    resp = await self.bot.aio_session.get(
                        f'{self.bot.api_base}/rcon/{ctx.guild.id}/{server_name}/listplayers/',
                        headers=self.bot.auth_header
                    )
                    if resp.status == 200:
                        message = '\n'.join(await resp.json())
                        await ctx.channel.trigger_typing()
                        await msg.delete()
                        await ctx.send(f'**Players currently on the {server_name} server:**\n{message}')
                        return
                    elif resp.status < 500:
                        message = f'Error getting data for {server_name}' + \
                                  (await resp.json()).get('details', 'Please try again')
                    else:
                        message = "There was an error on my server. I have notified the maintainers."
                    await ctx.send(message)

                futures.append(_listplayers(msg=msg, server_name=server['name']))
            if futures:
                asyncio.ensure_future(asyncio.gather(*futures))
            else:
                await ctx.send('There are no available servers for this guild.')

    # @commands.command()
    # @commands.guild_only()
    # async def add_rcon_server(self, ctx, server, ip, port, password):
    #     """Adds the specified server to the current guild\'s rcon config.
    #     All multi-word strings (<server>, <ip>, <password>) must be contained inside double quotes."""
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         server = server.replace('_', ' ').title()
    #         if ctx.guild_config.get('rcon_connections'):
    #             if server not in ctx.guild_config['rcon_connections']:
    #                 ctx.guild_config['rcon_connections'][server] = {
    #                     'ip': ip,
    #                     'port': port,
    #                     'password': password,
    #                     'game_chat_chan_id': 0,
    #                     'msg_chan_id': 0,
    #                     'monitoring_chat': 0
    #                 }
    #                 guild_ref = self.bot.fs_db.document(f'guilds/{ctx.guild.id}')
    #                 await self.bot.loop.run_in_executor(self.bot.tpe, guild_ref.update, ctx.guild_config)
    #                 await ctx.send('{0} server has been added to my configuration.'.format(server))
    #             else:
    #                 await ctx.send('This server name is already in my configuration. Please choose another.')
    #         else:
    #             ctx.guild_config['rcon_connections'] = {server: {
    #                 'ip': ip,
    #                 'port': port,
    #                 'password': password,
    #                 'game_chat_chan_id': 0,
    #                 'msg_chan_id': 0,
    #                 'monitoring_chat': 0
    #             }}
    #             guild_ref = self.bot.fs_db.document(f'guilds/{ctx.guild.id}')
    #             await self.bot.loop.run_in_executor(self.bot.tpe, guild_ref.update, ctx.guild_config)
    #             await ctx.send('{0} server has been added to my configuration.'.format(server))
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')
    #     await ctx.message.delete()
    #     await ctx.send('Command deleted to prevent password leak.')
    #
    # @commands.command()
    # @commands.guild_only()
    # async def remove_rcon_server(self, ctx, *, server: str):
    #     """removes the specified server from the current guild\'s rcon config."""
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         server = server.replace('_', ' ').title()
    #         if server in ctx.guild_config.get('rcon_connections', []):
    #             del ctx.guild_config['rcon_connections'][server]
    #             guild_ref = self.bot.fs_db.document(f'guilds/{ctx.guild.id}')
    #             await self.bot.loop.run_in_executor(self.bot.tpe, guild_ref.update, ctx.guild_config)
    #             await ctx.send('{0} has been removed from my configuration.'.format(server))
    #         else:
    #             await ctx.send('{0} is not in my configuration.'.format(server))
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')

    @staticmethod
    async def _whitelist(ctx, *, server_name: str, discord_id: str):
        data = {
            'discord_id': discord_id
        }
        resp = await ctx.bot.aio_session.post(f'{ctx.bot.api_base}/rcon/{ctx.guild.id}/{server_name}/whitelist/',
                                              headers=ctx.bot.auth_header,
                                              json=data)
        return resp

    @commands.command(name='add_whitelist')
    @commands.guild_only()
    @checks.is_admin()
    async def add_whitelist(self, ctx, members: Greedy[discord.Member] = None):
        if members:
            resp = await self.bot.aio_session.get(
                f'{self.bot.api_base}/rcon/{ctx.guild.id}/',
                headers=self.bot.auth_header
            )
            if resp.status != 200:
                await ctx.send('There was a problem getting the servers for this guild.')
                return
            guild_servers = await resp.json()
            for member in members:
                await ctx.send(f'Whitelisting {member.display_name} on all servers:')
                e = False
                for server in guild_servers:
                    suc = await self._whitelist(ctx,
                                                server_name=server["name"],
                                                discord_id=str(member.id)
                                                )
                    if suc.status == 400:
                        error = (await suc.json())['details']
                        await ctx.send(error)
                        e = True
                        break
                    elif suc.status in (404, 408):
                        msg = (await suc.json())['details']
                        e = True
                    else:
                        msg = '\n'.join(await suc.json())
                    await ctx.send(f'{server["name"]}: {msg}')
                if e:
                    await ctx.send(f'{ctx.author.mention} There were errors processing {member.display_name}.')
                else:
                    await ctx.send(f'{member.display_name} Done.')

        else:
            await ctx.send('I need a list of members to whitelist.')

    @commands.command(name="add_steamid", aliases=['steamid'])
    @checks.is_moderator()
    async def _add_steam_id_to_user(self, ctx, member: discord.Member, steam_id: int):
        if isinstance(member, discord.Member):
            resp = await self.bot.aio_session.patch(f'{self.bot.api_base}/users/{member.id}/',
                                                    headers=self.bot.auth_header,
                                                    json={'steam_id': steam_id})
            if resp.status == 200:
                await ctx.message.add_reaction(self.bot.success_emoji)
                return
            await ctx.send('I couldn\'t update that user for some reason.')
            return
        await ctx.send('Are you sure that is a valid user?')
    #
    # @commands.command(name='new_patron')
    # @commands.guild_only()
    # async def register_new_patron(self, ctx, *, members: str=None):
    #     """Adds the included Steam 64 IDs to the running whitelist on all the ARK servers in the current guild\'s rcon config.
    #     Steam 64 IDs should be a comma separated list of IDs.
    #     Example: 76561198024193239,76561198024193239,76561198024193239"""
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         if members is not None:
    #             async with ctx.typing():
    #                 members = members.replace(', ', ',').split(',')
    #                 converter = commands.MemberConverter()
    #                 members = [await converter.convert(ctx, m) for m in members]
    #                 futures = []
    #                 patrons = []
    #                 rcon_connections: dict = await self.get_rcon_server_by_name(guild_config=ctx.guild_config,
    #                                                                             name='*')
    #
    #                 if not isinstance(members, list):
    #                     members = [members, ]
    #                 for member in members:
    #                     member: discord.Member
    #                     player = await patron.Patron.from_name(self.bot, discord_name=member)
    #                     if player == -1:
    #                         await ctx.send(f'{ctx.author.mention} I Cannot find a player with a discord name of '
    #                                        f'{member.display_name} in the current whitelist sheet. Did you forget to '
    #                                        f'move them to the correct sheet?')
    #                     else:
    #                         if rcon_connections:
    #                             msg = await ctx.send(f'**Whitelisting {player.discord_name} on all servers**')
    #                             lock = asyncio.Lock()
    #                             for server_name, server_con in rcon_connections.items():
    #                                 futures.append(self._whitelist(server_name=server_name, server_con=server_con,
    #                                                                player=player, message=msg, message_lock=lock))
    #
    #                         roles = []
    #                         patron_roles = ctx.guild_config.get('patreon_tiers')
    #                         creator_roles = ctx.guild_config.get('patreon_creators')
    #                         if creator_roles:
    #                             rcon_log.info(f'patron_of {player.patron_of}')
    #                             if 'both' in player.patron_of.casefold():
    #                                 rcon_log.info('found both')
    #                                 for role_id in creator_roles.values():
    #
    #                                     roles.append(ctx.guild.get_role(int(role_id)))
    #                             else:
    #                                 roles.append(ctx.guild.get_role(
    #                                     int(creator_roles[player.patron_of + '_Patron'])
    #                                 ))
    #                         if patron_roles:
    #                             roles.append(ctx.guild.get_role(
    #                                 int(patron_roles[player.patreon_tier.strip().title()])
    #                             ))
    #                         if roles:
    #                             role_str = '\n'.join([role.name for role in roles])
    #                             await ctx.send(f'Adding {player.discord_name} to the following roles:\n'
    #                                            f'{role_str}')
    #                             await ctx.guild.get_member(int(player.discord_id)).add_roles(*roles)
    #
    #                         patrons.append(player)
    #
    #                 if futures:
    #                     asyncio.ensure_future(asyncio.gather(*futures), loop=self.bot.loop)
    #                 else:
    #                     await ctx.send('Nothing for me to do')
    #                     return
    #
    #                 if patrons:
    #                     new_patron_message = ctx.guild_config.get('new_patron_message')
    #                     new_patron_channel = ctx.guild_config.get('new_patron_channel')
    #                     if new_patron_message and new_patron_channel:
    #                         channel = ctx.guild.get_channel(int(new_patron_channel))
    #                         if channel:
    #                             patron_mentions = []
    #                             for p in patrons:
    #                                 member = ctx.guild.get_member(int(p.discord_id))
    #                                 patron_mentions.append(member.mention)
    #                             prelude = new_patron_message.get('prelude')
    #                             message = ''
    #                             if prelude:
    #                                 if len(patron_mentions) > 1:
    #                                     message = prelude.get('plural')
    #                                 else:
    #                                     message = prelude.get('singular')
    #                             body = new_patron_message.get('body')
    #                             if body:
    #                                 server_info_channel = ctx.guild.get_channel(int(
    #                                     ctx.guild_config.get('server_info')
    #                                 ))
    #                                 message += ' ' + body.format(users=', '.join(patron_mentions),
    #                                                              server_info=server_info_channel.mention if
    #                                                              server_info_channel else "server_info")
    #                             await channel.send(message)
    #         else:
    #             await ctx.send('I need a list of members to add roles to and whitelist.')
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')
    #
    # @commands.command()
    # @commands.guild_only()
    # async def saveworld(self, ctx, *, server=None):
    #     """Runs SaveWorld on the specified ARK server.
    #     If a server is not specified it will default to running saveworld on all servers in the guild\'s config.
    #     Will print out "World Saved" for each server when the command completes successfully."""
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #
    #         # noinspection PyShadowingNames
    #         async def _saveworld(ctx, server_name: str, server_con: arcon.ARKServer):
    #             response = await server_con.saveworld()
    #             if response == 'World Saved':
    #                 await ctx.send(f'{server_name} Saved')
    #             else:
    #                 await ctx.send(f'Failed to save {server_name}')
    #
    #         futures = []
    #         async with ctx.typing():
    #             if server is None:
    #                 rcon_connections: dict = await self.get_rcon_server_by_name(guild_config=ctx.guild_config,
    #                                                                             name='*')
    #                 if rcon_connections:
    #                     for server_name, server_con in rcon_connections.items():
    #                         futures.append(_saveworld(ctx, server_name, server_con))
    #                     self.bot.loop.create_task(asyncio.gather(*futures))
    #                 else:
    #                     await ctx.send('There are no available servers for this guild.')
    #             else:
    #                 server = server.replace('_', ' ').title()
    #                 server_con: arcon.ARKServer = await self.get_rcon_server_by_name(
    #                     guild_config=ctx.guild_config, name=server
    #                 )
    #                 if server_con:
    #                     # noinspection PyTypeChecker
    #                     await _saveworld(ctx, server, server_con)
    #                 else:
    #                     await ctx.send(f'{server} is not currently in the configuration for this guild.')
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')

    async def _broadcast(self, *, message: str, server_name: str,
                         msg: discord.Message, message_lock: asyncio.Lock):
        suc = await self.bot.aio_session.get(
                    f'{self.bot.api_base}/rcon/{msg.guild.id}/{server_name}/broadcast/',
                    headers=self.bot.auth_header,
                    json={'message': message}
                )
        if suc.status == 400:
            resp = (await suc.json())['details']
        elif suc.status in (404, 408):
            resp = (await suc.json())['details']
        else:
            resp = '\n'.join(await suc.json())
        if resp == 'Server received, But no response!!':
            with await message_lock:
                msg = await msg.channel.fetch_message(msg.id)
                await msg.edit(content=f'{msg.content}\n{server_name} Success')
        else:
            with await message_lock:
                msg = await msg.channel.fetch_message(msg.id)
                await msg.edit(content=f'{msg.content}\n{server_name} Failed\n{resp}')

    @commands.group(case_insensitive=True)
    @commands.guild_only()
    @checks.is_moderator()
    async def broadcast(self, ctx, server_name, *, message=None):
        """Sends a broadcast message to all servers in the guild config.
        The message will be prefixed with the Discord name of the person running the command.
        Will print "Success" for each server once the broadcast is sent."""
        if message is not None:
            resp = await self.bot.aio_session.get(
                f'{self.bot.api_base}/rcon/{ctx.guild.id}/',
                headers=self.bot.auth_header
            )
            if resp.status != 200:
                await ctx.send('There was a problem getting the servers for this guild.')
                return
            guild_servers = await resp.json()
            # noinspection PyShadowingNames

            futures = []
            error = False
            if server_name == 'all':
                message = ''.join(i for i in f'{ctx.author.display_name}: {message}' if ord(i) < 128)
                msg = await ctx.send(f'Broadcasting "{message}" to all servers.')
                lock = asyncio.Lock()
                for server in guild_servers:
                    futures.append(self._broadcast(message=message, server_name=server["name"],
                                                   msg=msg, message_lock=lock))
            else:
                for server in guild_servers:
                    if server["name"].lower().replace(" ", "_") == server_name.lower():
                        msg = await ctx.send(f'Broadcasting "{message}" to {server["name"]}.')
                        lock = asyncio.Lock()
                        futures.append(self._broadcast(message=message, server_name=server["name"],
                                                       msg=msg, message_lock=lock))
                        break
                else:
                    await ctx.send('That server is not configured in this guild.')
                    error = True
            if not error:
                await asyncio.gather(*futures, loop=self.bot.loop)
                await ctx.message.add_reaction('✅')

        else:
            await ctx.send('You must include a message with this command.')
    #
    # @commands.command(aliases=['servers', 'list_servers'])
    # @commands.guild_only()
    # @commands.check(checks.is_restricted_chan)
    # async def list_ark_servers(self, ctx):
    #     """Returns a list of all the ARK servers in the current guild\'s config."""
    #     servers = ctx.guild_config.get('rcon_connections', [])
    #     em = discord.Embed(style='rich',
    #                        title=f'__**There are currently {len(servers)} ARK servers in my config:**__',
    #                        color=discord.Colour.green()
    #                        )
    #     if ctx.guild.icon:
    #         em.set_thumbnail(url=f'{ctx.guild.icon_url}')
    #     for server in servers:
    #         description = f"""
    #         ឵          **IP:** {servers[server]['ip']}:{servers[server]['port']}
    #         ឵          **Steam Connect:** [steam://connect/{servers[server]['ip']}:{servers[server]['port']}]\
    #         (steam://connect/{servers[server]['ip']}:{servers[server]['port']})"""
    #         em.add_field(name=f'__***{server}***__', value=description, inline=False)
    #     await ctx.send(embed=em)
    #
    # @commands.command(name='server_chat')
    # @commands.guild_only()
    # async def send_chat_to_server(self, ctx, server: str=None, *, message: str=None):
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         if server is not None:
    #             server = server.replace('_', ' ').title()
    #             server_con: arcon.ARKServer = await self.get_rcon_server_by_name(guild_config=ctx.guild_config,
    #                                                                              name=server)
    #             if server_con:
    #                 if message is not None:
    #                     message = ''.join(i for i in f'{ctx.author.display_name}: {message}' if ord(i) < 128)
    #                     msg = await ctx.send(f'Sending "{message}" to {server}\'s chat')
    #                     response = await server_con.serverchat(message)
    #                     if response == 'Server received, But no response!!':
    #                         await msg.add_reaction(self.bot.unicode_emojis['y'])
    #                     else:
    #                         await msg.add_reaction(self.bot.unicode_emojis['x'])
    #                 else:
    #                     await ctx.send('You must include a message with this command.')
    #             else:
    #                 await ctx.send(f'That server is not in my configuration.\nPlease add it via !add_rcon_server '
    #                                f'"{server}" "ip" port "password" if you would like to get info from it.')
    #         else:
    #             await ctx.send('You must include a server with this command')
    #     else:
    #         await ctx.send('You are not authorized to run this command.')
    #
    # @commands.command(name='restart_server', aliases=['restart'])
    # @commands.guild_only()
    # async def restart_rcon_server(self, ctx, message: str, server_name: str=None,
    #                               delay_time: int=15, sleep_time: int=60):
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #
    #         if server_name is None or server_name == 'all':
    #             futures = []
    #             rcon_servers: dict = await self.get_rcon_server_by_name(
    #                 guild_config=ctx.guild_config, name='*'
    #             )
    #             for server_name, server_con in rcon_servers.items():
    #                 message = ''.join(i for i in f'{ctx.author.display_name}: {message}' if ord(i) < 128)
    #                 futures.append(utils.restart_rcon_server(ctx, server_name=server_name, server_con=server_con,
    #                                                          message=message, delay=delay_time, sleep=sleep_time))
    #             self.bot.loop.create_task(asyncio.gather(*futures))
    #
    #         elif server_name.startswith('exclude='):
    #             futures = []
    #             exclude_servers = server_name.split('exclude=')[1].replace('_', ' ').title().split(',')
    #             rcon_servers: dict = await self.get_rcon_server_by_name(
    #                 guild_config=ctx.guild_config, name='*'
    #             )
    #             for server_name, server_con in rcon_servers.items():
    #                 if server_name not in exclude_servers:
    #                     message = ''.join(i for i in f'{ctx.author.display_name}: {message}' if ord(i) < 128)
    #                     futures.append(utils.restart_rcon_server(ctx, server_name=server_name, server_con=server_con,
    #                                                              message=message, delay=delay_time, sleep=sleep_time))
    #             self.bot.loop.create_task(asyncio.gather(*futures))
    #
    #         else:
    #             async with ctx.typing():
    #                 server_name = server_name.replace('_', ' ').title()
    #                 server_con: arcon.ARKServer = await self.get_rcon_server_by_name(
    #                     guild_config=ctx.guild_config, name=server_name
    #                 )
    #                 if server_con:
    #                     message = ''.join(i for i in f'{ctx.author.display_name}: {message}' if ord(i) < 128)
    #                     await utils.restart_rcon_server(ctx, server_name=server_name, server_con=server_con,
    #                                                     message=message, delay=delay_time, sleep=sleep_time)
    #                 else:
    #                     await ctx.send(f'That server is not in my configuration.\nPlease add it via !add_rcon_server '
    #                                    f'"{server_name}" "ip" port "password" if you would like to get info from it.')
    #     else:
    #         await ctx.send('You are not authorized to run this command.')
    #
    # # noinspection PyShadowingNames
    # @staticmethod
    # async def start_dinowipe(channel, server_name: str, server_con: arcon.ARKServer):
    #     msg = await channel.send(f'Wild dinos will be wiped on {server_name} in 2 minutes.')
    #     await server_con.broadcast(f'Wild dino wipe incoming in 2 minutes, expect a small amount of lag while '
    #                                f'the dinos repopulate.')
    #     await asyncio.sleep(90)
    #     await server_con.serverchat(f'Wild Dino Wipe in 30 seconds')
    #     await asyncio.sleep(26)
    #     await server_con.serverchat(f'Wild Dino Wipe in 3')
    #     await asyncio.sleep(1)
    #     await server_con.serverchat(f'Wild Dino Wipe in 2')
    #     await asyncio.sleep(1)
    #     await server_con.serverchat(f'Wild Dino Wipe in 1')
    #     await asyncio.sleep(1)
    #     response = await server_con.destroy_wild_dinos()
    #     if response == 'All Wild Dinos Destroyed':
    #         await msg.edit(content=f'Wild Dinos Wiped on {server_name}')
    #         await server_con.serverchat(f'Wild dinos have been wiped.')
    #     else:
    #         await msg.edit(content=f'Failed to wipe wild dinos on {server_name}')
    #         await server_con.serverchat(f'Wild Dino Wipe failed, Please let the Admin know of this issue')
    #
    # # noinspection PyShadowingNames,PyUnresolvedReferences
    # async def request_dinowipe(self, requester, server_name: str, server_con: arcon.ARKServer):
    #     self.bot.dino_wipe_request[server_name] = True
    #     if server_con.server_messages_channel and self.bot.get_channel(int(server_con.server_messages_channel)):
    #         channel = self.bot.get_channel(int(server_con.server_messages_channel))
    #     else:
    #         channel = self.bot.get_channel(server_con.server_chat_channel)
    #     msg = False
    #     if channel:
    #         msg = await channel.send(f'@here {requester.mention} has requested wild dinos be wiped on the '
    #                                  f'{server_name} server\n'
    #                                  f'If you are in the middle of taming or have some other reason to '
    #                                  f'delay the wipe please react to this message with '
    #                                  f'{self.bot.unicode_emojis["x"]}.\n'
    #                                  f'Doing so will delay the wipe for 10 minutes.')
    #     await server_con.broadcast(f'{requester.display_name} has requested wild dinos be wiped.\n'
    #                                f'if you are in the middle of taming or have some other reason to delay the wipe '
    #                                f'please send a chat message containing "$delaywipe" here in-game.\n'
    #                                f'Doing so will delay the wipe for 10 minutes.')
    #     await asyncio.sleep(5)
    #     await server_con.serverchat('The wipe will continue in 2 minutes if there are no requests to delay. '
    #                                 'Send a message containing $delaywipe to delay for 10 minutes.')
    #     rcon_log.info('Dino Wipe messages sent')
    #     if msg:
    #         def check(reaction, user):
    #             return str(reaction.emoji) == self.bot.unicode_emojis['x'] and reaction.message.id == msg.id and \
    #                    user != self.bot.user
    #
    #         user = None
    #         await msg.add_reaction(self.bot.unicode_emojis['x'])
    #         try:
    #             reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
    #         except asyncio.TimeoutError:
    #             rcon_log.info('Message timed out...')
    #             if self.bot.dino_wipe_request.get(server_name):
    #                 rcon_log.info('Starting dino wipe')
    #                 await self.start_dinowipe(channel, server_name, server_con)
    #                 rcon_log.info('Wild Dino Wipe Completed')
    #                 return
    #         else:
    #             rcon_log.info('Dino Wipe Delayed.')
    #             await server_con.broadcast(f'Wild Dino Wipe has been delayed by {user.display_name}. '
    #                                        f'Please watch chat for timing updates')
    #         await channel.send(f'Dino wipe has been delayed by {user.mention if user else "Game Chat"}...')
    #         for i in range(10):
    #             await asyncio.sleep(60)
    #             if i >= 5 or i == 0:
    #                 await server_con.serverchat(f'The Wild Dino Wipe process will continue in {9 - i} '
    #                                             f'{"minute" if 9 - i == 1 else "minutes"}')
    #         await self.request_dinowipe(requester, server_name, server_con)
    #     else:
    #         rcon_log.info('No channels configured, running wipe.')
    #         await asyncio.sleep(120)
    #         if not self.bot.dino_wipe_request.get(server_name):
    #             rcon_log.info('Wipe Delay requested')
    #             for i in range(10):
    #                 await asyncio.sleep(60)
    #                 await server_con.serverchat(f'The Wino Dino Wipe process will continue in {9 - i} '
    #                                             f'{"minute" if 9 - i == 1 else "minutes"}')
    #             await self.request_dinowipe(requester, server_name, server_con)
    #
    # @commands.command(name='dinowipe')
    # @commands.guild_only()
    # async def run_dino_wipe(self, ctx, *, server=None):
    #     """Runs DestroyWildDinos on the specified ARK server.
    #     If a server is not specified it will default to wiping the wild dinos on all servers in the guild\'s config.
    #     Will print out "Wild Dinos Wiped on <server name>" for each server when the command completes successfully."""
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         futures = []
    #         async with ctx.typing():
    #             if server is None:
    #                 rcon_connections: dict = await self.get_rcon_server_by_name(
    #                     guild_config=ctx.guild_config, name='*'
    #                 )
    #                 if rcon_connections:
    #                     for server_name, server_con in rcon_connections.items():
    #                         futures.append(self.start_dinowipe(ctx.channel, server_name, server_con))
    #                     self.bot.loop.create_task(asyncio.gather(*futures))
    #                 else:
    #                     await ctx.send('There are no available servers for this guild.')
    #             else:
    #                 server = server.replace('_', ' ').title()
    #                 server_con: arcon.ARKServer = await self.get_rcon_server_by_name(
    #                     guild_config=ctx.guild_config, name=server
    #                 )
    #                 if server_con:
    #                     # noinspection PyTypeChecker
    #                     await self.start_dinowipe(ctx.channel, server, server_con)
    #                 else:
    #                     await ctx.send(f'{server} is not currently in the configuration for this guild.')
    #     else:
    #         await ctx.send(f'You are not authorized to run this command.')
    #
    # @commands.command(name='run_command', aliases=['run'])
    # @commands.guild_only()
    # async def run_rcon_command(self, ctx, server=None, *, command=None):
    #     if await checks.is_rcon_admin(self.bot, ctx):
    #         if not server:
    #             await ctx.send('You must include a server when running this command.')
    #             return
    #         async with ctx.typing():
    #             server = server.replace('_', ' ').title()
    #             server_con: arcon.ARKServer = await self.get_rcon_server_by_name(
    #                 guild_config=ctx.guild_config, name=server
    #             )
    #             if server_con:
    #                 if not command:
    #                     await ctx.send('You must include a command to run on the server.')
    #                     return
    #
    #                 command = command.split(' ')
    #
    #                 if ctx.guild_config.get('allowed_rcon_commands'):
    #                     pass
    #
    #                 response = await server_con.run_command(command=' '.join(command), multi_packet=True)
    #                 if isinstance(response, str):
    #                     await ctx.send(response)
    #                 else:
    #                     body = response.body
    #                     pag = utils.Paginator(bot=self.bot)
    #                     pag.add(body)
    #                     book = utils.Book(pag, (None, ctx.channel, self.bot, ctx.message))
    #                     await book.create_book()
    #             else:
    #                 await ctx.send('That server was not found in the config for this guild.')


def setup(bot):
    bot.add_cog(Rcon(bot))
