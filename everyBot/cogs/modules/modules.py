import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

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
        if command in bot_commands:
            self.bot.disabled_commands.append(command)
            await ctx.send(f'**`SUCCESS:`** Command `{ command }` was disabled')
        else:
            await ctx.send(f'**`ERROR:`** Command `{ command }` not found')

    """ Enable Command """
    @commands.command(aliases=['add_command'])
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def enable_command(self, ctx, *, command: str):
        try:
            self.bot.disabled_commands.remove(command)
        except ValueError:
            return await ctx.send(f'**`ERROR:`** `{ command }` is either not a command or is not currently disabled')
        except Exception as e:
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ command }` command was enabled')

    """ List Disabled Commands """
    @commands.command(
        name='disabled_commands',
        aliases=['disabled', 'list_disabled']
    )
    @commands.guild_only()
    async def list_disabled_commands(self, ctx):
        if not self.bot.disabled_commands:
            return await ctx.send("There are no disabled commands.")
        return await ctx.send(f"The disabled commands are: { (', ').join(self.bot.disabled_commands) }")

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Modules(bot))
