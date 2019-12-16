import logging
import time
from datetime import datetime
import os

from geeksbot.imports.geeksbot import Geeksbot
from geeksbot.imports.checks import is_me

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

bot = Geeksbot(case_insensitive=True)


@is_me()
@bot.command(hidden=True)
async def load(ctx, mod=None):
    """Allows the owner to load extensions dynamically"""
    await bot.load_ext(mod)
    await ctx.send(f'{mod} loaded')


@is_me()
@bot.command(hidden=True)
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


@is_me()
@bot.command(hidden=True)
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
