import discord
from discord.ext import commands

class HelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f"{ self.clean_prefix }{ command.qualified_name } { command.signature }"

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot):
    bot.add_cog(Help(bot))
