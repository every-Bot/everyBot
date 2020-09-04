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

class Mod(commands.Cog, name="moderator"):
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

    """ Warn member """
    @commands.command()
    @commands.check(check_disabled)
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        await database.warn_member(member, reason, ctx)

    """ Check member warnings """
    @commands.command(aliases=['warnings'])
    @commands.check(check_disabled)
    @commands.guild_only()
    async def check_warnings(self, ctx, member: discord.Member=None):
        if not member:
            member = ctx.author

        fetch_warnings = await database.fetch_member_warnings(member.id, True)
        warnings_list = await fetch_warnings.to_list(length=None)
        embed = discord.Embed(
            title=f"Warnings for { member.display_name }",
            colour=discord.Color.green()
        )

        if not warnings_list:
            embed.description="Member does not have any active warnings."
        else:
            warnings = []
            for i, warning in enumerate(warnings_list):
                warnings.append(f"{ i+1 }: { warning.reason }")
            embed.description="\n".join(warnings)

        return await ctx.send(embed=embed)


    """ Kick Member """
    @commands.command()
    @commands.check(check_disabled)
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member=None, *reason):
        if reason:
            reason = ' '.join(reason)
        else:
            reason = None

        # Kick member
        try:
            await member.kick(reason=reason)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS`** User { member.display_name } has been kicked')

    """ Ban Member """
    @commands.command()
    @commands.check(check_disabled)
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member=None, *reason):
        if reason:
            reason = ' '.join(reason)
        else:
            reason = None

        # Ban member
        try:
            await member.ban(reason=reason)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** User { member.display_name } has been banned')

    """ Unban Member """
    @commands.command()
    @commands.check(check_disabled)
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: int=None, *reason):
        if reason:
            reason = ' '.join(reason)
        else:
            reason = None
        user = await self.bot.fetch_user(member)

        # Unban Member
        try:
            await ctx.guild.unban(user=user, reason=reason)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS: `** User { user.display_name } has been unbanned')
        
    """ Add Role """
    @commands.command(aliases=['setrole', 'ar', 'sr'])
    @commands.check(check_disabled)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def addrole(self, ctx, member: discord.Member=None, *role):
        role = discord.utils.get(ctx.guild.roles, name=' '.join(role))
        
        # Add role to member
        try:
            await member.add_roles(role)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** role { role.name } added to { member.display_name }')

    """ Remove Role """
    @commands.command(aliases=['rmrole', 'rr'])
    @commands.check(check_disabled)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def removerole(self, ctx, member: discord.Member=None, *role):
        role = discord.utils.get(ctx.guild.roles, name=' '.join(role))

        # Remove role from member
        try:
            await member.remove_roles(role)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS:`** role { role.name } removed from { member.display_name }')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Mod(bot))