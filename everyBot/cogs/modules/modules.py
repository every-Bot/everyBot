import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio

from os import path
from os import scandir
import math

from pymongo.errors import ServerSelectionTimeoutError
from everyBot.cogs import database

class Modules(commands.Cog, name='modules'):
    def __init__(self, bot):
        self.bot = bot

    """ List all available modules """
    @commands.command(
        description="Lists all available modules"
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def list_modules(self, ctx):
        modules_per_page = 5
        modules = [f.name for f in scandir("everyBot/cogs") if f.is_dir() and f.name not in ["__pycache__", "help", "modules"]]
        page_amount = math.ceil(len(modules) / modules_per_page)
        pages = []

        # Creating the pages
        for x in range(page_amount):
            rows = 0
            page = discord.Embed(
                title=f"Modules page { x+1 }/{ page_amount }",
            )
            while rows < modules_per_page:
                try:
                    page.add_field(name=f"{ modules[0] }", value=f"{ modules[0] }", inline=False)
                except IndexError:
                    break
                del modules[0]
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

    """ Add module to bot """
    @commands.command(
        usage="[module]",
        description="Enable a module for your server"
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def install_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if not path.isdir(f"everyBot/cogs/{ cog }"):
            embed = discord.Embed(
                title="Module does not exist",
                colour=discord.Color.red(),
                description=f"The module you are trying to install, `{ cog }` does not exist."
            )
            return await ctx.send(embed=embed)
        if cog in self.bot.base_cogs:
            embed = discord.Embed(
                title="Error: Base modules cannot be modified",
                colour=discord.Color.red(),
                description=f"Module `{ cog }` cannot be modified as it is a base module"
            )
            return await ctx.send(embed=embed)

        try:
            # Attempt to add module to bot
            await database.install_module(ctx.guild.id, cog)
        except (database.ModuleAlreadyInstalled, ServerSelectionTimeoutError) as e:
            # Handle errors if any
            embed = discord.Embed(
                title=f"Error installing module: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        except AttributeError as e:
            embed = discord.Embed(
                title=f"Guild does not exist in db",
                colour=discord.Color.red(),
                description=f"Could not find properties for guild `{ ctx.guild.name }` in database"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="Module Installed",
            colour=discord.Color.green(),
            description=f"The module `{ cog }` was installed successfully"
        )
        return await ctx.send(embed=embed)

    """ Remove module from bot """
    @commands.command(
        usage="[module]",
        description="Disable a module for your server"
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def remove_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.bot.base_cogs:
            embed = discord.Embed(
                title="Error: Base modules cannot be modified",
                colour=discord.Color.red(),
                description=f"Module `{ cog }` cannot be modified as it is a base module"
            )
            return await ctx.send(embed=embed)

        try:
            # Attempt to add module to bot
            await database.remove_module(ctx.guild.id, cog)
        except (database.ModuleNotInstalled, ServerSelectionTimeoutError) as e:
            # Handle errors if any
            embed = discord.Embed(
                title=f"Error removing module: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        except AttributeError as e:
            embed = discord.Embed(
                title=f"Guild does not exist in db",
                colour=discord.Color.red(),
                description=f"Could not find properties for guild `{ ctx.guild.name }` in database"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="Module Removed",
            colour=discord.Color.green(),
            description=f"The module `{ cog }` was removed successfully"
        )
        return await ctx.send(embed=embed)

    """ List Installed Modules """
    @commands.command(
        description="List modules installed on your server"
    )
    @commands.guild_only()
    async def installed_modules(self, ctx):
        try:
            installed_modules = await database.fetch_guild_installed_modules(ctx.guild.id)
        except ServerSelectionTimeoutError as e:
            embed = discord.Embed(
                title=f"Error listing installed modules: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        except AttributeError as e:
            embed = discord.Embed(
                title=f"Guild does not exist in db",
                colour=discord.Color.red(),
                description=f"Could not find properties for guild `{ ctx.guild.name }` in database"
            )
            return await ctx.send(embed=embed)

        modules = []
        for module in installed_modules:
            modules.append(f"- { module }")

        modules_string = "\n" + "\n".join(modules)
        embed = discord.Embed(
            title=f"Installed modules for { ctx.guild.name }",
            description=f"{ modules_string }"
        )
        return await ctx.send(embed=embed)

    """ Reload Module """
    @commands.command(
        usage="[module]",
        description="Reload a module"
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def reload_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.bot.base_cogs:
            return await ctx.send(f'**`ERROR:`** This module cannot be modified')

        try:
            # Attempt to reload module
            self.bot.reload_extension(f'everyBot.cogs.{ cog }.{ cog }')
        except Exception as e:
            # Handle errors if any
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was reloaded')

    """ Disable Command """
    @commands.command(
        aliases=['remove_command'],
        usage="[command]",
        description="Disable a command for your server"
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def disable_command(self, ctx, *, command: str):
        bot_commands = [command.name for command in self.bot.commands]
        if command not in bot_commands:
            embed = discord.Embed(
                title="Error: Command does not exist",
                colour=discord.Color.red(),
                description=f"Command '{ command }' does not exist and therefore cannot be disabled."
            )
            return await ctx.send(embed=embed)

        try:
            await database.add_disabled_command(ctx.guild.id, command)
        except (database.CommandAlreadyDisabled, ServerSelectionTimeoutError) as e:
            embed = discord.Embed(
                title=f"Error disabling command: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        except AttributeError as e:
            embed = discord.Embed(
                title=f"Guild does not exist in db",
                colour=discord.Color.red(),
                description=f"Could not find properties for guild `{ ctx.guild.name }` in database"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="Command disabled",
            colour=discord.Color.green(),
            description=f"Command '{ command }' successfully disabled"
        )
        return await ctx.send(embed=embed)

    """ Enable Command """
    @commands.command(
        aliases=['add_command'],
        usage="[command]",
        description="Disable a command for your server"
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def enable_command(self, ctx, *, command: str):
        try:
            await database.remove_disabled_command(ctx.guild.id, command)
        except (database.CommandNotFound, ServerSelectionTimeoutError) as e:
            embed = discord.Embed(
                title=f"Error enabling command: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed) 
        except AttributeError as e:
            embed = discord.Embed(
                title=f"Guild does not exist in db",
                colour=discord.Color.red(),
                description=f"Could not find properties for guild `{ ctx.guild.name }` in database"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="Command disabled",
            colour=discord.Color.green(),
            description=f"Command '{ command }' successfully enabled"
        )
        return await ctx.send(embed=embed)   


    """ List Disabled Commands """
    @commands.command(
        name='disabled_commands',
        aliases=['disabled', 'list_disabled'],
        description="List all disabled commands for your server"
    )
    @commands.guild_only()
    async def list_disabled_commands(self, ctx):
        try:
            disabled_commands = await database.fetch_guild_disabled_commands(ctx.guild.id)
        except ServerSelectionTimeoutError as e:
            embed = discord.Embed(
                title=f"Error listing disabled commands: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        except AttributeError as e:
            embed = discord.Embed(
                title=f"Guild does not exist in db",
                colour=discord.Color.red(),
                description=f"Could not find properties for guild `{ ctx.guild.name }` in database"
            )
            return await ctx.send(embed=embed)

        commands = []
        for command in disabled_commands:
            commands.append(f"- { command }")

        commands_string = "\n" + "\n".join(commands)
        embed = discord.Embed(
            title=f"Disabled commands for { ctx.guild.name }",
            description=f"{ commands_string }"
        )
        return await ctx.send(embed=embed)

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Modules(bot))
