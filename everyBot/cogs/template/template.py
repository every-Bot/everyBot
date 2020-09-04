import discord
from discord.ext import commands

"""
This template cog is for reference purposes only.
It serves no function other then to be used as a reference point for creating over cogs.
"""

from pymongo.errors import ServerSelectionTimeoutError
from .. import database

""" Disabled Check """
async def check_disabled(ctx):
    try:
        disabled_commands = await database.fetch_guild_disabled_commands(ctx.guild.id)
    except ServerSelectionTimeoutError as e:
        embed = discord.Embed(
            title="Failed checking command",
            colour=discord.Color.red(),
            description=f"Could not check if command is disabled: { e }"
        )
        return await ctx.send(embed=embed)

    return ctx.command.name not in disabled_commands

class Template(commands.Cog, name="Template"):
    def __init__(self, bot):
        self.bot = bot

    """ Example Command """
    @commands.command(aliases=['ex', 'eg'])
    @commands.check(check_disabled)
    async def example(self, ctx, *, text):
        return await ctx.send(f"These aren't the droids you're looking for. You said { text }.")

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Template(bot))
