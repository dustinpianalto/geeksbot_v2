import discord


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == ctx.bot.owner_id
    return discord.ext.commands.check(predicate)


def is_moderator():
    async def predicate(ctx):
        resp = await ctx.bot.aio_session.get(f'{ctx.bot.api_base}/guilds/{ctx.guild.id}/roles/moderator/',
                                             headers=ctx.bot.auth_header)
        if resp.status == 200:
            mod_roles = await resp.json()
            for role in mod_roles:
                if discord.utils.get(ctx.author.roles, id=role["id"]):
                    return True
        return False
    return discord.ext.commands.check(predicate)


def is_admin():
    async def predicate(ctx):
        resp = await ctx.bot.aio_session.get(f'{ctx.bot.api_base}/guilds/{ctx.guild.id}/roles/admin/',
                                             headers=ctx.bot.auth_header)
        if resp.status == 200:
            admin_roles = await resp.json()
            for role in admin_roles:
                if discord.utils.get(ctx.author.roles, id=role["id"]):
                    return True
        return False
    return discord.ext.commands.check(predicate)
