import asyncio
import logging

import discord
from discord.ext import commands
from geeksbot.imports.checks import is_me
from geeksbot.imports.utils import Book, Paginator, run_command

git_log = logging.getLogger("git")


class Git(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(case_insensitive=True, invoke_without_command=True)
    async def git(self, ctx):
        """Shows my Git link"""
        branch = (
            await asyncio.wait_for(
                self.bot.loop.create_task(
                    run_command(
                        "git rev-parse --symbolic-full-name " "--abbrev-ref HEAD"
                    )
                ),
                120,
            )
        ).split("\n")[0]
        url = f"{self.bot.git_url}/tree/{branch}"
        em = discord.Embed(
            title=f"Here is where you can find my code",
            url=url,
            color=self.bot.embed_color,
        )
        if branch == "master":
            em.description = (
                "I am Geeksbot. You can find my code here:\n" f"{self.bot.git_url}"
            )
        else:
            em.description = (
                f"I am the {branch} branch of Geeksbot. "
                f"You can find the master branch here:\n"
                f"{self.bot.git_url}/tree/master"
            )
        em.set_thumbnail(url=f"{ctx.guild.me.avatar_url}")
        await ctx.send(embed=em)

    @git.command()
    @is_me()
    async def pull(self, ctx):
        """Pulls updates from GitHub rebasing branch."""
        pag = Paginator(self.bot, max_line_length=100, embed=True)
        pag.set_embed_meta(
            title="Git Pull",
            color=self.bot.embed_color,
            thumbnail=f"{ctx.guild.me.avatar_url}",
        )
        pag.add(
            "\uFFF6"
            + await asyncio.wait_for(
                self.bot.loop.create_task(run_command("git fetch --all")), 120
            )
        )
        pag.add("\uFFF7\n\uFFF8")
        pag.add(
            await asyncio.wait_for(
                self.bot.loop.create_task(
                    run_command(
                        "git reset --hard "
                        "origin/$(git "
                        "rev-parse --symbolic-full-name"
                        " --abbrev-ref HEAD)"
                    )
                ),
                120,
            )
        )
        pag.add("\uFFF7\n\uFFF8")
        pag.add(
            await asyncio.wait_for(
                self.bot.loop.create_task(
                    run_command("git show --stat | " 'sed "s/.*@.*[.].*/ /g"')
                ),
                10,
            )
        )
        book = Book(pag, (None, ctx.channel, self.bot, ctx.message))
        await book.create_book()

    @git.command()
    @is_me()
    async def status(self, ctx):
        """Gets status of current branch."""
        pag = Paginator(self.bot, max_line_length=44, max_lines=30, embed=True)
        pag.set_embed_meta(
            title="Git Status",
            color=self.bot.embed_color,
            thumbnail=f"{ctx.guild.me.avatar_url}",
        )
        result = await asyncio.wait_for(
            self.bot.loop.create_task(run_command("git status")), 120
        )
        pag.add(result)
        book = Book(pag, (None, ctx.channel, self.bot, ctx.message))
        await book.create_book()

    @git.command()
    @is_me()
    async def checkout(self, ctx, branch: str = "master"):
        """Checks out the requested branch.
        If no branch name is provided will checkout the master branch"""
        pag = Paginator(self.bot, max_line_length=44, max_lines=30, embed=True)
        branches_str = await asyncio.wait_for(
            self.bot.loop.create_task(run_command(f"git branch -a")), 120
        )
        existing_branches = [
            b.strip().split("/")[-1]
            for b in branches_str.replace("*", "").split("\n")[:-1]
        ]
        if branch not in existing_branches:
            pag.add(f"There is no existing branch named {branch}.")
            pag.set_embed_meta(
                title="Git Checkout",
                color=self.bot.error_color,
                thumbnail=f"{ctx.guild.me.avatar_url}",
            )
        else:
            pag.set_embed_meta(
                title="Git Checkout",
                color=self.bot.embed_color,
                thumbnail=f"{ctx.guild.me.avatar_url}",
            )
            result = await asyncio.wait_for(
                self.bot.loop.create_task(run_command(f"git checkout -f {branch}")), 120
            )
            pag.add(result)
        book = Book(pag, (None, ctx.channel, self.bot, ctx.message))
        await book.create_book()


def setup(bot):
    bot.add_cog(Git(bot))
