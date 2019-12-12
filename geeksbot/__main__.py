import logging
import time
from datetime import datetime
import os

log_format = '{asctime}.{msecs:03.0f}|{levelname:<8}|{name}::{message}'
date_format = '%Y.%m.%d %H.%M.%S'

log_dir = '/tmp/logs/geeksbot'

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = '{0}/geeksbot_{1}.log'.format(log_dir, datetime.now().strftime('%Y%m%d_%H%M%S%f'))

ch = logging.StreamHandler()
fh = logging.FileHandler(log_file)
ch.setLevel(logging.INFO)
fh.setLevel(logging.INFO)
formatter = logging.Formatter(log_format, datefmt=date_format, style='{')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[ch, fh])
logger = logging.getLogger()
logger.info('Logging Setup Complete')

time.sleep(1)

logger.info('Starting Imports')

start = datetime.utcnow()
# noinspection PyPackageRequirements
import discord  # noqa: E402
logger.info('Discord.py Imported')
# noinspection PyPackageRequirements
from discord.ext import commands  # noqa: E402
logger.info('commands Imported')
# noinspection PyPackageRequirements
from discord.ext.commands.view import StringView  # noqa: E402
logger.info('StringView Imported')
# noinspection PyPackageRequirements
from discord.ext.commands.context import Context  # noqa: E402
logger.info('Context Imported')
logger.info(f'Discord.py Import Complete - Took {(datetime.utcnow() - start).total_seconds()} seconds')
# noinspection PyRedeclaration
start = datetime.utcnow()
from concurrent import futures  # noqa: E402
logger.info('Concurrent futures Imported')
from multiprocessing import Pool  # noqa: E402
logger.info('Multiprocesing Pool Imported')
logger.info(f'Process Libs Import Complete - Took {(datetime.utcnow() - start).total_seconds()} seconds')
# noinspection PyRedeclaration
start = datetime.utcnow()
import re  # noqa: E402
logger.info('re Imported')
import json  # noqa: E402
logger.info('JSON Imported')
import aiohttp  # noqa: E402
logger.info('aiohttp Imported')
import redis # noqa: E402
logger.info('redis Imported')
logger.info(f'Misc Libs Import Complete - Took {(datetime.utcnow() - start).total_seconds()} seconds')
# noinspection PyRedeclaration
# start = datetime.utcnow()
# from geeksbot.imports.rcon_lib import arcon
# from geeksbot.imports import message_logging
# logger.info(f'Geeksbot Libs Import Complete - Took {(datetime.utcnow() - start).total_seconds()} seconds')


logger.info('Imports Complete')


class Geeksbot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.default_prefix = os.environ('DISCORD_DEFAULT_PREFIX') or 'g$'
        kwargs['command_prefix'] = self.default_prefix
        self.description = "Geeksbot v2"
        kwargs['description'] = self.description
        super().__init__(*args, **kwargs)
        self.config_dir = 'geeksbot/config/'
        self.config_file = 'bot_config.json'
        self.extension_dir = 'exts'
        self.cache = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=1, charset="utf-8", decode_responses=True)
        self.api_token = os.environ['API_TOKEN']
        self.aio_session = aiohttp.ClientSession(loop=self.loop)
        self.auth_header = {'Authorization': f'Token {self.api_token}'}
        self.api_base = 'https://geeksbot.app/api'
        with open(f'{self.config_dir}{self.config_file}') as f:
            self.bot_config = json.load(f)
        self.embed_color = discord.Colour.from_rgb(49, 107, 111)
        self.error_color = discord.Colour.from_rgb(142, 29, 31)
        self.owner_id = 351794468870946827
        self.tpe = futures.ThreadPoolExecutor(max_workers=20)
        self.process_pool = Pool(processes=4)
        self.geo_api = '2d4e419c2be04c8abe91cb5dd1548c72'
        self.git_url = 'https://github.com/dustinpianalto/geeksbot_v2'
        self.load_default_extensions()

        self.book_emojis = {
                            'unlock': '🔓',
                            'start': '⏮',
                            'back': '◀',
                            'hash': '#\N{COMBINING ENCLOSING KEYCAP}',
                            'forward': '▶',
                            'end': '⏭',
                            'close': '🇽',
                            }

    async def load_ext(self, mod):
        self.load_extension(f'geeksbot.{self.extension_dir}.{mod}')
        logger.info(f'Extension Loaded: {mod}')

    async def unload_ext(self, mod):
        self.unload_extension(f'geeksbot.{self.extension_dir}.{mod}')
        logger.info(f'Extension Unloaded: {mod}')

    def load_default_extensions(self):
        for load_item in self.bot_config['load_list']:
            self.loop.create_task(self.load_ext(load_item))

    async def close(self):
        await super().close()
        await self.aio_session.close()


bot = Geeksbot(case_insensitive=True)


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, mod=None):
    """Allows the owner to load extensions dynamically"""
    await bot.load_ext(mod)
    await ctx.send(f'{mod} loaded')


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, mod=None):
    """Allows the owner to reload extensions dynamically"""
    if mod == 'all':
        load_list = bot.bot_config['load_list']
        for load_item in load_list:
            await bot.unload_ext(f'{load_item}')
            await bot.load_ext(f'{load_item}')
            await ctx.send(f'{load_item} reloaded')
    else:
        await bot.unload_ext(mod)
        await bot.load_ext(mod)
        await ctx.send(f'{mod} reloaded')


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, mod):
    """Allows the owner to unload extensions dynamically"""
    await bot.unload_ext(mod)
    await ctx.send(f'{mod} unloaded')


@bot.event
async def on_message(message):
    if message.guild:
        message.content = message.content.replace('@everyone', '@\uFFF0everyone').replace('@here', '@\uFFF0here')
        await bot.process_commands(message)


@bot.event
async def on_ready():
    logger.info('Logged in as {0.name}|{0.id}'.format(bot.user))
    guild = bot.get_guild(396156980974059531)
    channel = guild.get_channel(404569276012560386)
    await channel.send('Geeksbot v2 Running')
    logger.info('Done loading, Geeksbot is active.')
    with open(f'{bot.config_dir}restart') as f:
        reboot = f.readlines()
    if int(reboot[0]) == 1:
        await bot.get_channel(int(reboot[1])).send('Restart Finished.')
    with open(f'{bot.config_dir}restart', 'w') as f:
        f.write('0')

bot.run(os.environ['TOKEN'])
