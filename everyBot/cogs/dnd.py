import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from . import modules

import random

""" Disabled Check """
async def check_disabled(ctx):
    return ctx.command.name not in modules.disabled_commands

class DnD(commands.Cog, name='DnD'):
    def __init__(self, bot):
        self.bot = bot

    """ Rollto """
    @commands.command()
    @commands.check(check_disabled)
    async def rollto(self, ctx, *, text):
        return await ctx.send(f"{ ctx.author.mention } rolled to { text } and got a { random.randint(0, 20) }!")

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        if 'The check functions for command' in str(error):
            return
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(DnD(bot))