from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import textwrap
import time
import os
from datetime import datetime
from contextlib import redirect_stdout
import io
from geeksbot.imports.utils import run_command, format_output, Paginator, Book
import logging

repl_log = logging.getLogger('repl')


class Exec(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:(- 1)])
        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(e):
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    @commands.command(hidden=True, name='exec')
    async def _eval(self, ctx, *, body: str):
        if ctx.author.id != self.bot.owner_id:
            return
        pag = Paginator(self.bot)
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'server': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }
        env.update(globals())
        body = self.cleanup_code(body)
        stdout = io.StringIO()
        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')
        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))
        func = env['func']
        # noinspection PyBroadException
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            pag.add(stdout.getvalue())
            pag.add(traceback.format_exc())
            for page in pag.pages():
                await ctx.send(page)
        else:
            value = stdout.getvalue()
            # noinspection PyBroadException
            try:
                await ctx.message.add_reaction('✅')
            except Exception:
                pass
            value = format_output(value)
            pag.add(value)
            pag.add(f'\nReturned: {ret}')
            self._last_result = ret
            for page in pag.pages():
                await ctx.send(page)

    @commands.command(hidden=True)
    async def repl(self, ctx):
        if ctx.author.id != self.bot.owner_id:
            return
        msg = ctx.message
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': msg,
            'server': msg.guild,
            'channel': msg.channel,
            'author': msg.author,
            '_': None,
        }
        if msg.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return
        self.sessions.add(msg.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')
        while True:
            response = await self.bot.wait_for('message', check=(lambda m: m.content.startswith('`')))
            if response.author.id == self.bot.owner_id:
                cleaned = self.cleanup_code(response.content)
                if cleaned in ('quit', 'exit', 'exit()'):
                    await response.channel.send('Exiting.')
                    self.sessions.remove(msg.channel.id)
                    return
                executor = exec
                if cleaned.count('\n') == 0:
                    try:
                        code = compile(cleaned, '<repl session>', 'eval')
                    except SyntaxError:
                        pass
                    else:
                        executor = eval
                if executor is exec:
                    try:
                        code = compile(cleaned, '<repl session>', 'exec')
                    except SyntaxError as e:
                        await response.channel.send(self.get_syntax_error(e))
                        continue
                variables['message'] = response
                fmt = None
                stdout = io.StringIO()
                # noinspection PyBroadException
                try:
                    with redirect_stdout(stdout):
                        result = executor(code, variables)
                        if inspect.isawaitable(result):
                            result = await result
                except Exception:
                    value = stdout.getvalue()
                    fmt = '{}{}'.format(value, traceback.format_exc())
                else:
                    value = stdout.getvalue()
                    if result is not None:
                        fmt = '{}{}'.format(value, result)
                        variables['_'] = result
                    elif value:
                        fmt = '{}'.format(value)
                try:
                    if fmt is not None:
                        pag = Paginator(self.bot)
                        pag.add(fmt)
                        for page in pag.pages():
                            await response.channel.send(page)
                            await ctx.send(response.channel)
                except discord.Forbidden:
                    pass
                except discord.HTTPException as e:
                    await msg.channel.send('Unexpected error: `{}`'.format(e))

    @commands.command(hidden=True)
    async def os(self, ctx, *, body: str):
        if ctx.author.id != self.bot.owner_id:
            return
        try:
            body = self.cleanup_code(body)
            pag = Paginator(self.bot)
            pag.add(await asyncio.wait_for(self.bot.loop.create_task(run_command(body)), 120))
            for page in pag.pages():
                await ctx.send(page)
            await ctx.message.add_reaction('✅')
        except asyncio.TimeoutError:
            await ctx.send(f"Command did not complete in the time allowed.")
            await ctx.message.add_reaction('❌')

    @commands.command(name='haskell', aliases=['hs'])
    async def haskell_compiler(self, ctx, *, body: str = None):
        if ctx.author.id != self.bot.owner_id:
            return

        if body is None:
            await ctx.send('Nothing to do.')
            return

        async with ctx.typing():
            msg = await ctx.send('Warming up GHC... Please wait.')
            try:
                body = self.cleanup_code(body)
                file_name = f'haskell_{datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")}'
                with open(f'{file_name}.hs', 'w') as f:
                    f.write(body)
                pag = Paginator(self.bot)
                compile_start = time.time()
                pag.add(await asyncio.wait_for(
                    self.bot.loop.create_task(run_command(f'ghc -o {file_name} {file_name}.hs')), timeout=60))
                compile_end = time.time()
                compile_real = compile_end - compile_start
                book = Book(pag, (msg, ctx.channel, ctx.bot, ctx.message))
                await book.create_book()
                pag = Paginator(self.bot)
                if file_name in os.listdir():
                    run_start = time.time()
                    pag.add(await asyncio.wait_for(self.bot.loop.create_task(run_command(f'./{file_name}')),
                                                   timeout=600))
                    run_end = time.time()
                    run_real = run_end - run_start
                    total_real = run_real + compile_real
                    pag.add(f'\n\nCompile took {compile_real:.2f} seconds')
                    pag.add(f'Total Time {total_real:.2f} seconds')
                    book = Book(pag, (None, ctx.channel, ctx.bot, ctx.message))
                    await msg.delete()
                    await book.create_book()
                os.remove(file_name)
                os.remove(f'{file_name}.hs')
                os.remove(f'{file_name}.o')
                os.remove(f'{file_name}.hi')
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send(f"Command did not complete in the time allowed.")
                await ctx.message.add_reaction('❌')
            except FileNotFoundError as e:
                repl_log.warning(e)


def setup(bot):
    bot.add_cog(Exec(bot))
