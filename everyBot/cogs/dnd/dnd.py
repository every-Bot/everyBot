import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from textwrap import dedent

import random

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

class DnD(commands.Cog, name='dnd'):
    def __init__(self, bot):
        self.bot = bot

    """ Rollto """
    @commands.command()
    @commands.check(check_disabled)
    async def rollto(self, ctx, *, text):
        embed = discord.Embed(
            title="Roll Results",
            colour=discord.Color.blue(),
            description=f"{ ctx.author.mention } rolled to { text } and got a { random.randint(0, 20) }!"
        )

        return await ctx.send(embed=embed)

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        embed = discord.Embed(
            title=f"Error in { ctx.command.qualified_name }",
            colour=discord.Color.red(),
            description=dedent(f"""
                { error }
                Use `{ self.bot.command_prefix }help { ctx.command.qualified_name }` for help with the command.
                """)
        )

        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DnD(bot))