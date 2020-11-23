import discord
from discord.ext import commands

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

class Text(commands.Cog, name="Text"):
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

    """ Say """
    @commands.command(
        usage="[text]",
        description="The bot said it, not me"
    )
    @commands.check(check_disabled)
    async def say(self, ctx, *text):
        await ctx.message.delete()
        return await ctx.send(" ".join(text))

    """ Mock """
    @commands.command(
        usage="[text]",
        description="MoCk SoMeThInG SoMe MoWoN SaId"
    )
    @commands.check(check_disabled)
    async def mock(self, ctx, *, text):
        mock_text = list(text)
        for i, char in enumerate(text):
            if i % 2 == 0:
                mock_text[i] = char.capitalize()
        
        return await ctx.send(f"{ ''.join(mock_text) }")

    """ Clap """
    @commands.command(
        usage="[text]",
        description="Say :clap: something :clap: powerfully :clap:"
    )
    @commands.check(check_disabled)
    async def clap(self, ctx, *text):
        return await ctx.send(f"{ ' :clap: '.join(text) } :clap:")

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Text(bot))