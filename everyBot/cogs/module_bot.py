import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class ModuleBot(commands.Cog, name="Bot Commands"):
    def __init__(self, bot):
        self.bot = bot

    """ Change Bot Nickname """
    @commands.command(aliases=['nickname_bot', 'nb'])
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