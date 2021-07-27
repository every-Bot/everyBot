import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from textwrap import dedent

import typing
import re
import time

from pymongo.errors import ServerSelectionTimeoutError
from everyBot.cogs import database

from d20 import parse, roll, RollSyntaxError

def die(arg):
    return parse(arg, allow_comments=True)

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

    async def cog_check(self, ctx):
        try:
            installed_modules = await database.fetch_guild_installed_modules(ctx.guild.id)
        except (ServerSelectionTimeoutError, AttributeError) as e:
            embed = discord.Embed(
                title="Failed checking module",
                colour=discord.Color.red(),
                description=f"Could not check if module is installed: { e }"
            )
            return await ctx.send(embed=embed)

        return ctx.command.cog_name.lower() in installed_modules

    """ Roll """
    @commands.command(
        usage="[dice]",
        description="Roll a specified dice (eg. 2d6) followed by an optional action"
    )
    @commands.check(check_disabled)
    async def roll(self, ctx, dice: typing.Optional[die] = "1d20", *, action: str = None):
        try:
            result = roll(dice, allow_comments=True)
        except RollSyntaxError: # Theoretically this shouldn't be possible, but just in case.
            return await ctx.message.reply(f"Invalid dice format: { dice }")

        embed = discord.Embed(
            title=f"{ ctx.author.display_name } Rolled ({ dice })",
            colour=discord.Color.blue(),
            description=f"{ result }"
        )
        if action:
            embed.description = f"{ embed.description } to { action }"

        return await ctx.send(embed=embed)

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        if 'The check functions for command' in str(error):
            return
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
