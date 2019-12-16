from discord.ext.commands.view import StringView


class MyStringView(StringView):
    def skip_string(self, string):
        strlen = len(string)
        if self.buffer[self.index:self.index + strlen].casefold() == string:
            self.previous = self.index
            self.index += strlen
            return True
        return False
