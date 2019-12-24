import discord
from discord.ext import commands
import logging
import inspect
import sys
import psutil
import math
from geeksbot.imports import utils

admin_logger = logging.getLogger('admin')


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reboot(self, ctx):
        await ctx.send('Geeksbot is restarting.')
        with open(f'{self.bot.config_dir}/restart', 'w') as f:
            f.write(f'1\n{ctx.channel.id}')
        admin_logger.info("Rebooting")
        await self.bot.close()

    # TODO Fix view_code
    @commands.command(hidden=True)
    @commands.is_owner()
    async def view_code(self, ctx, code_name):
        pag = utils.Paginator(self.bot, prefix='```py', suffix='```')
        pag.add(inspect.getsource(self.bot.all_commands[code_name].callback))
        book = utils.Book(pag, (None, ctx.channel, ctx.bot, ctx.message))
        await book.create_book()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sysinfo(self, ctx):
        """Gets system status for my server."""
        await ctx.send(f'```ml\n'
                       f'CPU Percentages: {psutil.cpu_percent(percpu=True)}\n'
                       f'Memory Usage: {psutil.virtual_memory().percent}%\n'
                       f'Disc Usage: {psutil.disk_usage("/").percent}%\n'
                       f'```')

    @commands.command(aliases=['oauth', 'link'])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def invite(self, ctx, guy: discord.User = None):
        """Shows you the bot's invite link.
           If you pass in an ID of another bot, it gives you the invite link to that bot.
        """
        guy = guy or self.bot.user
        url = discord.utils.oauth_url(guy.id)
        await ctx.send(f'**<{url}>**')

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def ping(self, ctx):
        """Check the Bot\'s connection to Discord"""
        em = discord.Embed(style='rich',
                           title=f'Pong 🏓',
                           color=discord.Colour.green()
                           )
        msg = await ctx.send(embed=em)
        time1 = ctx.message.created_at
        time = (msg.created_at - time1).total_seconds() * 1000
        em.description = f'Response Time: **{math.ceil(time)}ms**\n' \
                         f'Discord Latency: **{math.ceil(self.bot.latency*1000)}ms**'
        await msg.edit(embed=em)


def setup(bot):
    bot.add_cog(Admin(bot))
