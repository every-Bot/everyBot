import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

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

class ModuleBot(commands.Cog, name="Bot"):
    def __init__(self, bot):
        self.bot = bot

    """ Change Bot Nickname """
    @commands.command(aliases=['nickname_bot', 'nb'])
    @commands.check(check_disabled)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nick_bot(self, ctx, *name):
        nickname = ' '.join(name)

        # Change bot's nickname
        try:
            await ctx.me.edit(nick=nickname)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS`** Bot nickname has been changed to { nickname }')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(ModuleBot(bot))