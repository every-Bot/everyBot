import discord
from discord.ext import commands

"""
This template cog is for reference purposes only.
It serves no function other then to be used as a reference point for creating over cogs.
"""

""" Disabled Check """
async def check_disabled(ctx):
    return ctx.command.name not in ctx.bot.disabled_commands

class Template(commands.Cog, name="Template"):
    def __init__(self, bot):
        self.bot = bot

    """ Example Command """
    @commands.command(aliases=['example', 'ex', 'eg'])
    @commands.command()
    @commands.check(check_disabled)
    async def example(self, ctx, *, text):
        formatted_text = " ".join(text)
        return await ctx.send(f"These aren't the droids you're looking for. You said { formatted_text }.")

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Template(bot))