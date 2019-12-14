import discord


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == ctx.bot.owner_id
    return discord.ext.commands.check(predicate)
