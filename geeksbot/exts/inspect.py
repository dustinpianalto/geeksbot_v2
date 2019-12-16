import discord
from discord.ext import commands
from datetime import datetime, timedelta
from geeksbot.imports.utils import process_snowflake


class Inspect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['u'])
    async def user(self, ctx, member: discord.Member):
        em = discord.Embed(style='rich',
                           title=f'{member.name}#{member.discriminator} ({member.display_name})',
                           description=f'({member.id})',
                           color=self.bot.embed_color)
        em.set_thumbnail(url=f'{member.avatar_url}')
        em.add_field(name=f'Highest Role:',
                     value=f'{member.top_role.mention}',
                     inline=True)
        em.add_field(name=f'Bot:',
                     value=f'{member.bot}',
                     inline=True)
        em.add_field(name=f'Joined Guild:',
                     value=f'{self.create_date_string(member.joined_at, ctx.message.created_at)}',
                     inline=False)
        em.add_field(name=f'Joined Discord:',
                     value=f'{self.create_date_string(member.created_at, ctx.message.created_at)}',
                     inline=False)
        em.add_field(name=f'Current Status:',
                     value=f'{member.status}',
                     inline=True)
        em.add_field(name=f"Currently{' ' + member.activity.type.name.title() if member.activity else ''}:",
                     value=f"{member.activity.name if member.activity else 'Not doing anything important.'}",
                     inline=True)
        count = 0
        async for message in ctx.channel.history(after=(ctx.message.created_at - timedelta(hours=1))):
            if message.author == member:
                count += 1
        em.add_field(name=f'Activity:',
                     value=f'{member.display_name} has sent {count} '
                           f'{"message" if count == 1 else "messages"} in the last hour to this channel.',
                     inline=False)
        await ctx.send(embed=em)

    @commands.command(aliases=['s'])
    async def snowflake(self, ctx, snowflake: int):
        try:
            snowflake = int(snowflake)
        except ValueError:
            await ctx.send('That is not a valid snowflake')
        if len(bin(snowflake))-2 < 63 or len(bin(snowflake))-2 > 64:
            await ctx.send('That is not a valid snowflake')
        creation_time, worker, process, counter = process_snowflake(snowflake)
        em = discord.Embed(title=str(snowflake),
                           description=f'Created At: {creation_time.strftime("%c")}\n'
                                       f'Worker: {worker}\n'
                                       f'Process: {process}\n'
                                       f'Increment Counter: {counter}',
                           color=self.bot.embed_color)
        await ctx.send(em)


def setup(bot):
    bot.add_cog(Inspect(bot))
