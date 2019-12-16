import os
import json
from concurrent import futures
from multiprocessing import Pool
import logging

import discord
from discord.ext import commands
import redis
import aiohttp

geeksbot_logger = logging.getLogger('Geeksbot')


class Geeksbot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.default_prefix = os.environ.get('DISCORD_DEFAULT_PREFIX', 'g$')
        kwargs['command_prefix'] = self.get_prefixes
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
        self.tpe = futures.ThreadPoolExecutor(max_workers=20)
        self.process_pool = Pool(processes=4)
        self.geo_api = '2d4e419c2be04c8abe91cb5dd1548c72'
        self.git_url = 'https://github.com/dustinpianalto/geeksbot_v2'
        self.load_default_extensions()
        self.owner_id = 351794468870946827

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
        try:
            self.load_extension(f'geeksbot.{self.extension_dir}.{mod}')
            geeksbot_logger.info(f'Extension Loaded: {mod}')
        except Exception:
            geeksbot_logger.exception(f"Error loading {mod}")

    async def unload_ext(self, mod):
        try:
            self.unload_extension(f'geeksbot.{self.extension_dir}.{mod}')
            geeksbot_logger.info(f'Extension Unloaded: {mod}')
        except Exception:
            geeksbot_logger.exception(f"Error loading {mod}")

    def load_default_extensions(self):
        for load_item in self.bot_config['load_list']:
            self.loop.create_task(self.load_ext(load_item))

    async def get_prefixes(self, bot, message):
        return self.default_prefix.casefold()

    async def close(self):
        try:
            await super().close()
            await self.aio_session.close()
        except Exception:
            geeksbot_logger.exception(f"Error Closing Connections.")
        geeksbot_logger.info('Exiting...')

