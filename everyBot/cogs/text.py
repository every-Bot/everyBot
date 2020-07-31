import discord
from discord.ext import commands

from . import modules

""" Disabled Check """
async def check_disabled(ctx):
    return ctx.command.name not in modules.disabled_commands

class Text(commands.Cog, name="Text Commands"):
    def __init__(self, bot):
        self.bot = bot

    """ Say """
    @commands.command()
    @commands.check(check_disabled)
    async def say(self, ctx, *text):
        await ctx.message.delete()
        return await ctx.send(" ".join(text))

    """ Mock """
    @commands.command()
    @commands.check(check_disabled)
    async def mock(self, ctx, *, text):
        await ctx.message.delete()
        mock_text = list(text)
        for i, char in enumerate(text):
            if i % 2 == 0:
                mock_text[i] = char.capitalize()
        
        return await ctx.send(f"{ ctx.author.display_name }: **{ ''.join(mock_text) }**")

    """ Clap """
    @commands.command()
    @commands.check(check_disabled)
    async def clap(self, ctx, *text):
        await ctx.message.delete()
        return await ctx.send(f"{ ctx.author.display_name }: **{ ' :clap: '.join(text) }**")

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Text(bot))