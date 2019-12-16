import discord
import asyncio
import typing
from datetime import datetime


async def get_guild_config(bot, guild_id):
    guild_config = bot.cache.get()


def create_date_string(time, time_now):
    diff = (time_now - time)
    date_str = time.strftime('%Y-%m-%d %H:%M:%S')
    return f"{diff.days} {'day' if diff.days == 1 else 'days'} " \
           f"{diff.seconds // 3600} {'hour' if diff.seconds // 3600 == 1 else 'hours'} " \
           f"{diff.seconds % 3600 // 60} {'minute' if diff.seconds % 3600 // 60 == 1 else 'minutes'} " \
           f"{diff.seconds % 3600 % 60} {'second' if diff.seconds % 3600 % 60 == 1 else 'seconds'} ago.\n{date_str}"


def process_snowflake(snowflake: int) -> typing.Tuple[datetime, int, int, int]:
    DISCORD_EPOCH = 1420070400000
    TIME_BITS_LOC = 22
    WORKER_ID_LOC = 17
    WORKER_ID_MASK = 0x3E0000
    PROCESS_ID_LOC = 12
    PROCESS_ID_MASK = 0x1F000
    INCREMENT_MASK = 0xFFF
    creation_time = datetime.fromtimestamp(((snowflake >> TIME_BITS_LOC) + DISCORD_EPOCH) / 1000.0)
    worker_id = (snowflake & WORKER_ID_MASK) >> WORKER_ID_LOC
    process_id = (snowflake & PROCESS_ID_MASK) >> PROCESS_ID_LOC
    counter = snowflake & INCREMENT_MASK
    return creation_time, worker_id, process_id, counter


# noinspection PyDefaultArgument
def to_list_of_str(items, out: list = list(), level=1, recurse=0):
    # noinspection PyShadowingNames
    def rec_loop(item, key, out, level):
        quote = '"'
        if type(item) == list:
            out.append(f'{"    "*level}{quote+key+quote+": " if key else ""}[')
            new_level = level + 1
            out = to_list_of_str(item, out, new_level, 1)
            out.append(f'{"    "*level}]')
        elif type(item) == dict:
            out.append(f'{"    "*level}{quote+key+quote+": " if key else ""}{{')
            new_level = level + 1
            out = to_list_of_str(item, out, new_level, 1)
            out.append(f'{"    "*level}}}')
        else:
            out.append(f'{"    "*level}{quote+key+quote+": " if key else ""}{repr(item)},')

    if type(items) == list:
        if not recurse:
            out = list()
            out.append('[')
        for item in items:
            rec_loop(item, None, out, level)
        if not recurse:
            out.append(']')
    elif type(items) == dict:
        if not recurse:
            out = list()
            out.append('{')
        for key in items:
            rec_loop(items[key], key, out, level)
        if not recurse:
            out.append('}')

    return out


def format_output(text):
    if type(text) == list:
        text = to_list_of_str(text)
    elif type(text) == dict:
        text = to_list_of_str(text)
    return text


async def run_command(args):
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        f'time -f "Process took %e seconds (%U user | %S system) and used %P of the CPU" {args}',
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout
    if stderr and stderr.strip() != '':
        output = f'{stdout.decode().strip()}\n{stderr.decode().strip()}'
    else:
        output = stdout.decode().strip()
    return output


# noinspection PyShadowingNames
class Paginator:
    def __init__(self,
                 bot: discord.ext.commands.Bot,
                 *,
                 max_chars: int = 1970,
                 max_lines: int = 20,
                 prefix: str = '```md',
                 suffix: str = '```',
                 page_break: str = '\uFFF8',
                 field_break: str = '\uFFF7',
                 field_name_char: str = '\uFFF6',
                 inline_char: str = '\uFFF5',
                 max_line_length: int = 100,
                 embed=False,
                 header: str = ''):
        _max_len = 6000 if embed else 1980
        assert 0 < max_lines <= max_chars

        self._parts = list()
        self._prefix = prefix
        self._suffix = suffix
        self._max_chars = max_chars if max_chars + len(prefix) + len(suffix) + 2 <= _max_len \
            else _max_len - len(prefix) - len(suffix) - 2
        self._max_lines = max_lines - (prefix + suffix).count('\n') + 1
        self._page_break = page_break
        self._max_line_length = max_line_length
        self._pages = list()
        self._max_field_chars = 1014
        self._max_field_name = 256
        self._max_description = 2048
        self._embed = embed
        self._field_break = field_break
        self._field_name_char = field_name_char
        self._inline_char = inline_char
        self._embed_title = ''
        self._embed_description = ''
        self._embed_color = None
        self._embed_thumbnail = None
        self._embed_url = None
        self._bot = bot
        self._header = header

    def set_embed_meta(self, title: str = None,
                       description: str = None,
                       color: discord.Colour = None,
                       thumbnail: str = None,
                       footer: str = '',
                       url: str = None):
        if title and len(title) > self._max_field_name:
            raise RuntimeError('Provided Title is too long')
        else:
            self._embed_title = title
        if description and len(description) > self._max_description:
            raise RuntimeError('Provided Description is too long')
        else:
            self._embed_description = description
        self._embed_color = color
        self._embed_thumbnail = thumbnail
        self._embed_url = url

    def pages(self, page_headers: bool = True) -> typing.List[str]:
        _pages = list()
        _fields = list()
        _page = ''
        _lines = 0
        _field_name = ''
        _field_value = ''
        _inline = False

        def open_page(initial: bool = False):
            nonlocal _page, _lines, _fields
            if not self._embed:
                if initial and not page_headers:
                    _page = self._header
                elif page_headers:
                    _page = self._header
                else:
                    _page = ''
                _page += self._prefix
                _lines = 0
            else:
                _fields = list()

        def close_page():
            nonlocal _page, _lines, _fields
            if not self._embed:
                _page += self._suffix
                _pages.append(_page)
            else:
                if _fields:
                    _pages.append(_fields)
            open_page()

        open_page(initial=True)

        if not self._embed:
            for part in [str(p) for p in self._parts]:
                if part.startswith(self._page_break):
                    close_page()

                new_chars = len(_page) + len(part)

                if new_chars > self._max_chars:
                    close_page()
                elif (_lines + (part.count('\n') + 1 or 1)) > self._max_lines:
                    close_page()

                _lines += (part.count('\n') + 1 or 1)
                _page += '\n' + part
        else:
            def open_field(name: str):
                nonlocal _field_value, _field_name
                _field_name = name
                _field_value = self._prefix

            def close_field(next_name: str = None):
                nonlocal _field_name, _field_value, _fields
                _field_value += self._suffix
                if _field_value != self._prefix + self._suffix:
                    _fields.append({'name': _field_name, 'value': _field_value, 'inline': _inline})
                if next_name:
                    open_field(next_name)

            open_field('\uFFF0')

            for part in [str(p) for p in self._parts]:
                if part.strip().startswith(self._page_break):
                    close_page()
                elif part == self._field_break:
                    if len(_fields) + 1 < 25:
                        close_field(next_name='\uFFF0')
                    else:
                        close_field()
                        close_page()
                    continue

                if part.startswith(self._field_name_char):
                    part = part.replace(self._field_name_char, '')
                    if part.startswith(self._inline_char):
                        _inline = True
                        part = part.replace(self._inline_char, '')
                    else:
                        _inline = False
                    if _field_value and _field_value != self._prefix:
                        close_field(part)
                    else:
                        _field_name = part
                    continue

                _field_value += '\n' + part

            close_field()

        close_page()
        self._pages = _pages
        return _pages

    # noinspection PyUnresolvedReferences
    def process_pages(self) -> typing.List[str]:
        _pages = self._pages or self.pages()
        _len_pages = len(_pages)
        _len_page_str = len(f'{_len_pages}/{_len_pages}')
        if not self._embed:
            for i, page in enumerate(_pages):
                if len(page) + _len_page_str <= 2000:
                    _pages[i] = f'{i + 1}/{_len_pages}\n{page}'
        else:
            for i, page in enumerate(_pages):
                em = discord.Embed(title=self._embed_title,
                                   description=self._embed_description,
                                   color=self._bot.embed_color,
                                   )
                if self._embed_thumbnail:
                    em.set_thumbnail(url=self._embed_thumbnail)
                if self._embed_url:
                    em.url = self._embed_url
                if self._embed_color:
                    em.color = self._embed_color
                em.set_footer(text=f'{i + 1}/{_len_pages}')
                for field in page:
                    em.add_field(name=field['name'], value=field['value'], inline=field['inline'])
                _pages[i] = em
        return _pages

    def __len__(self):
        return sum(len(p) for p in self._parts)

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self.__class__ == other.__class__ and self._parts == other._parts

    def set_header(self, header: str = ''):
        self._header = header

    def add_page_break(self, *, to_beginning: bool = False) -> None:
        self.add(self._page_break, to_beginning=to_beginning)

    def add(self, item: typing.Any, *, to_beginning: bool = False, keep_intact: bool = False, truncate=False) -> None:
        item = str(item)
        i = 0
        if not keep_intact and not item == self._page_break:
            item_parts = item.strip('\n').split('\n')
            for part in item_parts:
                if len(part) > self._max_line_length:
                    if not truncate:
                        length = 0
                        out_str = ''

                        def close_line(line):
                            nonlocal i, out_str, length
                            self._parts.insert(i, out_str) if to_beginning else self._parts.append(out_str)
                            i += 1
                            out_str = line + ' '
                            length = len(out_str)

                        bits = part.split(' ')
                        for bit in bits:
                            next_len = length + len(bit) + 1
                            if next_len <= self._max_line_length:
                                out_str += bit + ' '
                                length = next_len
                            elif len(bit) > self._max_line_length:
                                if out_str:
                                    close_line(line='')
                                for out_str in [bit[i:i + self._max_line_length]
                                                for i in range(0, len(bit), self._max_line_length)]:
                                    close_line('')
                            else:
                                close_line(bit)
                        close_line('')
                    else:
                        line = f'{part:.{self._max_line_length-3}}...'
                        self._parts.insert(i, line) if to_beginning else self._parts.append(line)
                else:
                    self._parts.insert(i, part) if to_beginning else self._parts.append(part)
                    i += 1
        elif keep_intact and not item == self._page_break:
            if len(item) >= self._max_chars or item.count('\n') > self._max_lines:
                raise RuntimeError('{item} is too long to keep on a single page and is marked to keep intact.')
            if to_beginning:
                self._parts.insert(0, item)
            else:
                self._parts.append(item)
        else:
            if to_beginning:
                self._parts.insert(0, item)
            else:
                self._parts.append(item)


class Book:
    def __init__(self, pag: Paginator, ctx: typing.Tuple[typing.Optional[discord.Message],
                                                         discord.TextChannel,
                                                         discord.ext.commands.Bot,
                                                         discord.Message]) -> None:
        self._pages = pag.process_pages()
        self._len_pages = len(self._pages)
        self._current_page = 0
        self._message, self._channel, self._bot, self._calling_message = ctx
        self._locked = True
        if pag == Paginator(self._bot):
            raise RuntimeError('Cannot create a book out of an empty Paginator.')

    def advance_page(self) -> None:
        self._current_page += 1
        if self._current_page >= self._len_pages:
            self._current_page = 0

    def reverse_page(self) -> None:
        self._current_page += -1
        if self._current_page < 0:
            self._current_page = self._len_pages - 1

    async def display_page(self) -> None:
        if isinstance(self._pages[self._current_page], discord.Embed):
            if self._message:
                await self._message.edit(content=None, embed=self._pages[self._current_page])
            else:
                self._message = await self._channel.send(embed=self._pages[self._current_page])
        else:
            if self._message:
                await self._message.edit(content=self._pages[self._current_page], embed=None)
            else:
                self._message = await self._channel.send(self._pages[self._current_page])

    async def create_book(self) -> None:
        # noinspection PyUnresolvedReferences
        async def reaction_checker():
            # noinspection PyShadowingNames
            def check(reaction, user):
                if self._locked:
                    return str(reaction.emoji) in self._bot.book_emojis.values() \
                           and user == self._calling_message.author \
                           and reaction.message.id == self._message.id
                else:
                    return str(reaction.emoji) in self._bot.book_emojis.values() \
                           and reaction.message.id == self._message.id

            await self.display_page()

            if len(self._pages) > 1:
                for emoji in self._bot.book_emojis.values():
                    try:
                        await self._message.add_reaction(emoji)
                    except (discord.Forbidden, KeyError):
                        pass
            else:
                try:
                    await self._message.add_reaction(self._bot.book_emojis['unlock'])
                    await self._message.add_reaction(self._bot.book_emojis['close'])
                except (discord.Forbidden, KeyError):
                    pass

            while True:
                try:
                    reaction, user = await self._bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    try:
                        await self._message.clear_reactions()
                    except (discord.Forbidden, discord.NotFound):
                        pass
                    raise asyncio.CancelledError
                else:
                    await self._message.remove_reaction(reaction, user)
                    if str(reaction.emoji) == self._bot.book_emojis['close']:
                        await self._calling_message.delete()
                        await self._message.delete()
                        raise asyncio.CancelledError
                    elif str(reaction.emoji) == self._bot.book_emojis['forward']:
                        self.advance_page()
                    elif str(reaction.emoji) == self._bot.book_emojis['back']:
                        self.reverse_page()
                    elif str(reaction.emoji) == self._bot.book_emojis['end']:
                        self._current_page = self._len_pages - 1
                    elif str(reaction.emoji) == self._bot.book_emojis['start']:
                        self._current_page = 0
                    elif str(reaction.emoji) == self._bot.book_emojis['hash']:
                        m = await self._channel.send(f'Please enter a number in range 1 to {self._len_pages}')

                        def num_check(message):
                            if self._locked:
                                return message.content.isdigit() \
                                        and 0 < int(message.content) <= self._len_pages \
                                        and message.author == self._calling_message.author
                            else:
                                return message.content.isdigit() \
                                       and 0 < int(message.content) <= self._len_pages

                        try:
                            msg = await self._bot.wait_for('message', timeout=30, check=num_check)
                        except asyncio.TimeoutError:
                            await m.edit(content='Message Timed out.')
                        else:
                            self._current_page = int(msg.content) - 1
                            try:
                                await m.delete()
                                await msg.delete()
                            except (discord.Forbidden, discord.NotFound):
                                pass
                    elif str(reaction.emoji) == self._bot.book_emojis['unlock']:
                        self._locked = False
                        await self._message.remove_reaction(reaction, self._channel.guild.me)
                        continue
                    await self.display_page()

        self._bot.loop.create_task(reaction_checker())
