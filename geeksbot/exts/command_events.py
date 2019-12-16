import discord
from discord.ext import commands
from datetime import datetime
import logging
import traceback

from geeksbot.imports.utils import Paginator, Book


class CommandEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyMethodMayBeStatic
    async def on_command_error(self, ctx, error):
        pag = Paginator(ctx.bot, embed=True)
        pag.set_embed_meta(color=self.bot.error_color)
        pag.add(f'\uFFF6Command Error')
        pag.add(error)
        pag.add('\uFFF7\n\uFFF8')
        pag.add(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
        book = Book(pag, (None, ctx.channel, self.bot, ctx.message))
        await book.create_book()


def setup(bot):
    bot.add_cog(CommandEvents(bot))
