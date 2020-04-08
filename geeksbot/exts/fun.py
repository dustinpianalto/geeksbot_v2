import discord
from discord.ext import commands
import asyncio


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='explode', aliases=['splode'])
    async def explode_user(self, ctx, member: discord.Member=None):
        """Trolls user by punching them to oblivion."""
        if member is None or member.id == 396588996706304010:
            member = ctx.author

        msg = await ctx.send(f'{member.mention}{"<:transparent:405943174809255956>"*20}{self.bot.unicode_emojis["left_fist"]}')
        for i in range(4):
            await asyncio.sleep(0.5)
            await msg.edit(content=f'{member.mention}{"<:transparent:405943174809255956>"*(20-(i*5))}{self.bot.unicode_emojis["left_fist"]}')
        await asyncio.sleep(0.1)
        await msg.edit(content=f'{self.bot.unicode_emojis["boom"]}')
        await asyncio.sleep(0.5)
        await msg.edit(content=f'{self.bot.unicode_emojis["boom"]} <---- {member.mention} that was you...')


def setup(bot):
    bot.add_cog(Fun(bot))
