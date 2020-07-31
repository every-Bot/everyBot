import discord
from discord.ext import commands

from . import modules

""" Disabled Check """
async def check_disabled(ctx):
    return ctx.command.name not in modules.disabled_commands

class General(commands.Cog, name="General Commands"):
    def __init__(self, bot):
        self.bot = bot

    """ Say """
    @commands.command()
    @commands.check(check_disabled)
    async def say(self, ctx, * text):
        await ctx.message.delete()
        return await ctx.send(" ".join(text))

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(General(bot))