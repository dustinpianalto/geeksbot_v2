import os
import time
import json
from concurrent import futures
from multiprocessing import Pool
import logging

import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from geeksbot.imports.strings import MyStringView
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
        self.config_dir = 'geeksbot/config'
        self.config_file = 'bot_config.json'
        self.extension_dir = 'exts'
        self.cache = redis.Redis(host=os.environ['REDIS_HOST'], password=os.environ['REDIS_PASSWORD'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_DB'], charset="utf-8", decode_responses=True)
        self.settings_cache = redis.Redis(host=os.environ['REDIS_HOST'], password=os.environ['REDIS_PASSWORD'], port=os.environ['REDIS_PORT'], db=1, charset="utf-8", decode_responses=True)
        self.token = self.settings_cache.get('DISCORD_TOKEN')
        self.api_token = self.settings_cache.get('API_TOKEN')
        self.aio_session = aiohttp.ClientSession(loop=self.loop)
        self.auth_header = {'Authorization': f'Token {self.api_token}'}
        self.api_base = 'https://geeksbot.app/api'
        with open(f'{self.config_dir}/{self.config_file}') as f:
            self.bot_config = json.load(f)
        self.embed_color = discord.Colour.from_rgb(49, 107, 111)
        self.error_color = discord.Colour.from_rgb(142, 29, 31)
        self.tpe = futures.ThreadPoolExecutor(max_workers=20)
        self.process_pool = Pool(processes=4)
        self.geo_api = '2d4e419c2be04c8abe91cb5dd1548c72'
        self.git_url = 'https://github.com/dustinpianalto/geeksbot_v2'
        self.load_default_extensions()
        self.owner_id = 351794468870946827
        self.success_emoji = '\N{WHITE HEAVY CHECK MARK}'
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

    async def get_context(self, message, *, cls=Context):
        r"""|coro|

        Returns the invocation context from the message.

        This is a more low-level counter-part for :meth:`.process_commands`
        to allow users more fine grained control over the processing.

        The returned context is not guaranteed to be a valid invocation
        context, :attr:`.Context.valid` must be checked to make sure it is.
        If the context is not valid then it is not a valid candidate to be
        invoked under :meth:`~.Bot.invoke`.

        Parameters
        -----------
        message: :class:`discord.Message`
            The message to get the invocation context from.
        cls
            The factory class that will be used to create the context.
            By default, this is :class:`.Context`. Should a custom
            class be provided, it must be similar enough to :class:`.Context`\'s
            interface.

        Returns
        --------
        :class:`.Context`
            The invocation context. The type of this can change via the
            ``cls`` parameter.
        """

        view = MyStringView(message.content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)

        if self._skip_check(message.author.id, self.user.id):
            return ctx

        prefix = await self.get_prefix(message)
        invoked_prefix = prefix

        if isinstance(prefix, str):
            if not view.skip_string(prefix):
                return ctx
        else:
            try:
                # if the context class' __init__ consumes something from the view this
                # will be wrong.  That seems unreasonable though.
                if message.content.casefold().startswith(tuple(prefix)):
                    invoked_prefix = discord.utils.find(view.skip_string, prefix)
                else:
                    return ctx

            except TypeError:
                if not isinstance(prefix, list):
                    raise TypeError("get_prefix must return either a string or a list of string, "
                                    "not {}".format(prefix.__class__.__name__))

                # It's possible a bad command_prefix got us here.
                for value in prefix:
                    if not isinstance(value, str):
                        raise TypeError("Iterable command_prefix or list returned from get_prefix must "
                                        "contain only strings, not {}".format(value.__class__.__name__))

                # Getting here shouldn't happen
                raise

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        ctx.command = self.all_commands.get(invoker)
        return ctx

    async def close(self):
        await self.aio_session.close()
        await super().close()
        time.sleep(5)
        geeksbot_logger.info('Exiting...')
        # noinspection PyProtectedMember
        os._exit(1)
