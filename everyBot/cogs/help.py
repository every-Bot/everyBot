import discord
from discord.ext import commands
from pymongo.errors import ServerSelectionTimeoutError

from everyBot.cogs import database

class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, module=None):
        try:
            installed_modules = await database.fetch_guild_installed_modules(ctx.guild.id)
            modules = installed_modules + self.bot.base_cogs
            modules = sorted(modules)
        except ServerSelectionTimeoutError as e:
            embed = discord.Embed(
                title=f"Error listing installed modules: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        if module == None:
            embed = discord.Embed(
                title=f"{ ctx.me.display_name } Modules",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=ctx.me.avatar_url)
            for module in modules:
                cog = self.bot.get_cog(module)
                if cog is not None:
                    if not cog.__cog_settings__ or not cog.__cog_settings__['hidden']:
                        embed.add_field(name=module, value=f"`{ ctx.prefix }help { module }`", inline=False)
                
            return await ctx.send(embed=embed)

        if module not in modules:
            embed = discord.Embed(
                title=f"No module { module }",
                colour=discord.Colour.red(),
                description=f"The module `{ module }` does not exist or is not installed.\nSee `$list_modules` for a list of installable modules"
            )
            embed.set_thumbnail(url=ctx.me.avatar_url)
            return await ctx.send(embed=embed)

        disabled_commands = await database.fetch_guild_disabled_commands(ctx.guild.id)
        cog = self.bot.get_cog(module)
        commands = cog.get_commands()

        embed = discord.Embed(
            title=f"{ cog.qualified_name.capitalize() } Module",
            colour=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.me.avatar_url)
        for command in commands:
            if command.name in disabled_commands:
                continue
            if command.usage:
                embed.add_field(name=f"`{ ctx.prefix }{ command.name } { command.usage }`", value=command.description, inline=False)
            else:
                embed.add_field(name=f"`{ ctx.prefix }{ command.name }`", value=command.description, inline=False)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
