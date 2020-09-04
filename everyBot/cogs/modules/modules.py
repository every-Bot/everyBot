import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from pymongo.errors import ServerSelectionTimeoutError
from .. import database

class Modules(commands.Cog, name='Module'):
    def __init__(self, bot):
        self.bot = bot

    """ Add module to bot """
    @commands.command()
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def add_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.bot.base_cogs:
            await ctx.send(f'**`ERROR:`** This module cannot be modified')
            return

        try:
            # Attempt to add module to bot
            self.bot.load_extension(f'everyBot.cogs.{ cog }.{ cog }')
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was added')

    """ Remove module from bot """
    @commands.command()
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def remove_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.bot.base_cogs:
            await ctx.send(f'**`ERROR:`** This module cannot be modified')
            return

        try:
            # Attempt to remove module from bot
            self.bot.unload_extension(f'everyBot.cogs.{ cog }.{ cog }')
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was removed')

    """ Reload Module """
    @commands.command(aliases=['reload'])
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
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was reloaded')

    """ Disable Command """
    @commands.command(aliases=['remove_command'])
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

        embed = discord.Embed(
            title="Command disabled",
            colour=discord.Color.green(),
            description=f"Command '{ command }' successfully disabled"
        )
        return await ctx.send(embed=embed)

    """ Enable Command """
    @commands.command(aliases=['add_command'])
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

        embed = discord.Embed(
            title="Command disabled",
            colour=discord.Color.green(),
            description=f"Command '{ command }' successfully enabled"
        )
        return await ctx.send(embed=embed)   


    """ List Disabled Commands """
    @commands.command(
        name='disabled_commands',
        aliases=['disabled', 'list_disabled']
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

        commands = []
        for command in disabled_commands:
            commands.append(f"- { command }")

        commands_string = "\n" + "\n".join(commands)
        embed = discord.Embed(
            title=f"Disabled commands for { ctx.guild.name }",
            colour=discord.Color.blue(),
            description=f"{ commands_string }"
        )
        return await ctx.send(embed=embed)

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Modules(bot))
