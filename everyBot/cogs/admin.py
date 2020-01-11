import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

command_attrs = {
    'hidden': True
}

class Admin(commands.Cog, name='Admin Commands', command_attrs=command_attrs):
    def __init__(self, bot):
        self.bot = bot

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Admin(bot))