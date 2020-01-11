import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

command_attrs = {
    'hidden': True
}

class Modules(commands.Cog, name='Module Commands', command_attrs=command_attrs):
    def __init__(self, bot):
        self.bot = bot

        self.base_cogs = ['modules', 'owner', 'module_bot']

    """ Add module to bot """
    @commands.command(aliases=['add', 'load'], hidden=True)
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def add_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.base_cogs:
            await ctx.send(f'**`ERROR:`** This module cannot be modified')
            return

        try:
            # Attempt to add module to bot
            self.bot.load_extension(f'everyBot.cogs.{ cog }')
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was added')

    """ Remove module from bot """
    @commands.command(aliases=['remove', 'unload'], hidden=True)
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def remove_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.base_cogs:
            await ctx.send(f'**`ERROR:`** This module cannot be modified')
            return

        try:
            # Attempt to remove module from bot
            self.bot.unload_extension(f'everyBot.cogs.{ cog }')
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was removed')

    """ Reload Module """
    @commands.command(
        name='reload_module',
        aliases=['reload'],
        hidden=True
    )
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def reload_module(self, ctx, *, cog: str):
        # Checking if user is trying to modify a base module
        if cog in self.base_cogs:
            return await ctx.send(f'**`ERROR:`** This module cannot be modified')

        try:
            # Attempt to reload module
            self.bot.reload_extension(f'everyBot.cogs.{ cog }')
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** The `{ cog }` module was reloaded')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Modules(bot))
