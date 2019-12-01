import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Patron:
    def __init__(self, *, discord_name: str=None, steam_id: int=None, patreon_tier: str=None, patron_of: str=None,
                 discord_discrim: int=None, discord_id: int=None, patreon_name: str=None, steam_name: str=None):
        self.discord_name = discord_name
        self.discord_discrim = discord_discrim
        self.steam_id = steam_id
        self.discord_id = discord_id
        self.patreon_tier = patreon_tier
        self.patron_of = patron_of
        self.patreon_name = patreon_name
        self.steam_name = steam_name

    @classmethod
    async def from_id(cls, bot, steam_id: int, *, discord_id: int=None):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(bot.google_secret, scope)

        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(bot.bot_secrets['sheet'])
        ws = sh.worksheet('Current Whitelist')
        try:
            cell = ws.find(f'{steam_id}')
        except gspread.CellNotFound:
            return -1
        else:
            steam_name = None
            if discord_id:
                user_ref = bot.fs_db.document(f'users/{discord_id}')
                user_info = (await bot.loop.run_in_executor(bot.tpe, user_ref.get)).to_dict()
                if user_info:
                    steam_name = user_info.get('steam_name')
            row = ws.row_values(cell.row)
            return cls(patreon_name=row[1],
                       discord_name=row[2],
                       steam_id=row[5],
                       patreon_tier=row[4].split(' (')[1].strip(')') if len(row[4].split(' (')) > 1 else row[4],
                       patron_of=row[3].split(' (')[0],
                       discord_id=discord_id,
                       steam_name=steam_name)

    @classmethod
    async def from_name(cls, bot, discord_name: discord.Member, *, discord_id: int=None):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(bot.google_secret, scope)

        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(bot.bot_secrets['sheet'])
        ws = sh.worksheet('Current Whitelist')
        try:
            cell = ws.find(f'{discord_name.name if isinstance(discord_name, discord.Member) else discord_name}')
        except gspread.CellNotFound:
            try:
                cell = ws.find(f'{discord_name.nick if isinstance(discord_name, discord.Member) else discord_name}')
            except gspread.CellNotFound:
                return -1
        steam_name = None
        discord_id = discord_name.id if isinstance(discord_name, discord.Member) else discord_id
        if discord_id:
            user_ref = bot.fs_db.document(f'users/{discord_id}')
            user_info = (await bot.loop.run_in_executor(bot.tpe, user_ref.get)).to_dict()
            if user_info:
                steam_name = user_info.get('steam_name')
        row = ws.row_values(cell.row)
        return cls(patreon_name=row[1],
                   discord_name=row[2],
                   discord_id=discord_id,
                   steam_id=row[5],
                   patreon_tier=row[4].split(' (')[1].strip(')') if len(row[4].split(' (')) > 1 else row[4],
                   patron_of=row[3].split(' (')[0],
                   steam_name=steam_name)
