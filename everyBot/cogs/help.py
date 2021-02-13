import discord
from discord.ext import commands
from pymongo.errors import ServerSelectionTimeoutError
import math
import asyncio

from everyBot.cogs import database

class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, module=None):
        try:
            installed_modules = await database.fetch_guild_installed_modules(ctx.guild.id)
            disabled_commands = await database.fetch_guild_disabled_commands(ctx.guild.id)
        except ServerSelectionTimeoutError as e:
            embed = discord.Embed(
                title=f"Error listing installed modules: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        modules = sorted(installed_modules + self.bot.base_cogs)

        if module == None:
            embed = discord.Embed(
                title=f"{ ctx.me.display_name } Modules",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=ctx.me.avatar_url)
            for bot_module in modules:
                cog = self.bot.get_cog(bot_module)
                if cog is not None:
                    if not cog.__cog_settings__ or not cog.__cog_settings__['hidden']:
                        embed.add_field(name=bot_module, value=f"`{ ctx.prefix }help { bot_module }`", inline=False)
                
            return await ctx.send(embed=embed)

        ## If user specified a module
        if module not in modules:
            embed = discord.Embed(
                title=f"No module { module }",
                colour=discord.Colour.red(),
                description=f"The module `{ module }` does not exist or is not installed.\nSee `$list_modules` for a list of installable modules"
            )
            embed.set_thumbnail(url=ctx.me.avatar_url)

            return await ctx.send(embed=embed)

        commands_per_page = 5
        cog = self.bot.get_cog(module)
        commands = cog.get_commands()
        active_commands = [com for com in commands if com.name not in disabled_commands]
        page_amount = math.ceil(len(commands) / commands_per_page)
        pages = []

        for x in range(page_amount):
            rows = 0
            page = discord.Embed(
                title=f"{ cog.qualified_name.capitalize() } Module ({ x + 1 }/{ page_amount })",
            )
            page.set_thumbnail(url=ctx.me.avatar_url)

            # Creating pages
            while rows < commands_per_page and len(active_commands) >= 1:
                field_prefix = ""
                if rows > 0:
                    field_prefix = "\u200b\n"
                try:
                    if active_commands[0].usage:
                        page.add_field(name=f"{ field_prefix }`{ ctx.prefix }{ active_commands[0].name } { active_commands[0].usage }`", value=active_commands[0].description, inline=False)
                    else:
                        page.add_field(name=f"{ field_prefix }`{ ctx.prefix }{ active_commands[0].name }`", value=active_commands[0].description, inline=False)
                except IndexError:
                    break
                active_commands.pop(0)
                rows += 1
            pages.append(page)

        message = await ctx.send(embed=pages[0])

        # Adding reactions to the message
        await message.add_reaction(emoji='\u23ee')
        await message.add_reaction(emoji='\u25c0')
        await message.add_reaction(emoji='\u25b6')
        await message.add_reaction(emoji='\u23ed')

        def check(reaction, member):
            return reaction.message.id == message.id and member == ctx.author

        # Adding controls for user to change pages
        page = 0
        while True:
            try:
                reaction, member = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

                if reaction.emoji == '\u23ee':
                    page = 0
                if reaction.emoji == '\u25c0' and page > 0:
                    page -= 1
                if reaction.emoji == '\u25b6' and page < page_amount-1:
                    page += 1
                if reaction.emoji == '\u23ed':
                    page = len(pages) - 1

                await message.remove_reaction(reaction.emoji, member)
                await message.edit(embed=pages[page])
            except asyncio.TimeoutError:
                pass


def setup(bot):
    bot.add_cog(Help(bot))
