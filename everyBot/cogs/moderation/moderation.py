import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from pymongo.errors import ServerSelectionTimeoutError
from everyBot.cogs import database

import psutil
import asyncio
import time

async def mute_member(ctx, member: discord.Member, reason: str, time: int):
    # Try to get muted role from guild
    role = discord.utils.get(ctx.guild.roles, name="muted")

    # If the role doesn't exist, we need to create it
    if not role:
        # Try to create muted role
        try:
            role = await ctx.guild.create_role(name="muted", reason="To use for muting bad members")
            # Remove perms for role to chat in any channel
            for channel in ctx.guild.channels: 
                await channel.set_permissions(
                    role,
                    send_messages=False
                )
        # If the bot can't create the new role
        except discord.Forbidden as e:
            raise e
    
    # Add muted role to the member, wait the specified amount of time,
    # then unmute member by removing the role.
    try:   
        await member.add_roles(role)
        embed = discord.Embed(
            title=f"{ member.display_name } has been muted",
            colour=discord.Color.green(),
            description=f"**Time:** { time } minutes\n**Reason:** { reason }"
        )
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)
        await asyncio.sleep(time*60)
        await member.remove_roles(role)
    except discord.Forbidden as e:
        raise e

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

class Mod(commands.Cog, name="moderation"):
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
    @commands.command(
        usage="[member] (optional reason)",
        description="Warns a member"
    )
    @commands.check(check_disabled)
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="None"):
        # response = await database.warn_member(ctx.guild.id, member.id, reason)
        response = await database.warn_member(ctx, member, reason)
        return await ctx.send(embed=response)

    """ Clear member warnings"""
    @commands.command(
        usage="[member]",
        description="Clears a member's warnings"
    )
    @commands.check(check_disabled)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def clear_warnings(self, ctx, member: discord.Member):
        fetch_warnings = await database.fetch_member_warnings(ctx.guild.id, member.id, True)
        warnings = await fetch_warnings.to_list(length=None)

        if not warnings:
            embed = discord.Embed(
                title=f"No warnings for { member.display_name }",
                colour=discord.Color.red(),
                description=f"{ member.display_name } has no warnings, therefore their warnings cannot be cleared."
            )
            embed.set_thumbnail(url=member.avatar_url)
            return await ctx.send(embed=embed)
        for warning in warnings:
            warning.active = False
            await warning.commit()
        
        embed = discord.Embed(
            title=f"{ member.display_name }'s warnings have been cleared",
            colour=discord.Color.green(),
            description=f"All active warnings for { member.display_name } have been cleared.\n\n{ member.mention }, try not to give the mods a reason to give you more ;)"
        )
        embed.set_thumbnail(url=member.avatar_url)
        return await ctx.send(embed=embed)

    """ Check member warnings """
    @commands.command(
        usage="(optional member)",
        description="Check warnings of a member"
    )
    @commands.check(check_disabled)
    @commands.guild_only()
    async def warnings(self, ctx, member: discord.Member=None):
        if not member:
            member = ctx.author

        fetch_warnings = await database.fetch_member_warnings(ctx.guild.id, member.id, True)
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
        embed.set_thumbnail(url=member.avatar_url)
        return await ctx.send(embed=embed)

    """ Mute Member """
    @commands.command(
        usage="[member] (optional reason) (optional time)",
        description="Mutes a member"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, reason: str="None", time: int=5):
        try:
            await mute_member(ctx, member, reason, time)
        except discord.Forbidden as e:
            embed = discord.Embed(
                title=f"Failed muting { member.display_name }",
                colour=discord.Color.red(),
                description=f"{ ctx.author.display_name }, you do not have the correct permissions to mute { member.display_name }"
            )
            return await ctx.send(embed=embed)

    """ Unmute Member """
    @commands.command(
        usage="[member]",
        description="Unmutes a member before time is up"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member):
        # Try to get muted role from guild
        role = discord.utils.get(ctx.guild.roles, name="muted")

        # If the role doesn't exist, we need to create it
        if not role:
            # Try to create muted role
            try:
                role = await ctx.guild.create_role(name="muted", reason="To use for muting bad members")
                # Remove perms for role to chat in any channel
                for channel in ctx.guild.channels: 
                    await channel.set_permissions(
                        role,
                        send_messages=False
                    )
            # If the bot can't create the new role
            except discord.Forbidden as e:
                embed = discord.Embed(
                    title=f"Failed unmuting { member.display_name }",
                    colour=discord.Color.red(),
                    description=f"{ ctx.author.display_name }, you do not have the correct permissions to unmute { member.display_name }"
                )
                return await ctx.send(embed=embed)

        if role not in member.roles:
            embed = discord.Embed(
                title="Error unmuting member",
                colour=discord.Color.red(),
                description=f"{ member.display_name } is not currently muted."
            )
            embed.set_thumbnail(url=member.avatar_url)
            return await ctx.send(embed=embed)

        await member.remove_roles(role)
        embed = discord.Embed(
            title="Member has been unmuted",
            colour=discord.Color.green(),
            description=f"{ member.display_name } has been successfully unmuted."
        )
        embed.set_thumbnail(url=member.avatar_url)
        return await ctx.send(embed=embed)


    """ Kick Member """
    @commands.command(
        usage="[member] (optional reason)",
        description="Kicks a member"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *reason):
        if reason:
            reason = ' '.join(reason)
        else:
            reason = None

        # Kick member
        try:
            await member.kick(reason=reason)
        except Exception as e:
            # Handle errors if any
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS`** User { member.display_name } has been kicked')

    """ Ban Member """
    @commands.command(
        usage="[member] (optional reason)",
        description="Bans a member"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *reason):
        if reason:
            reason = ' '.join(reason)
        else:
            reason = None

        # Ban member
        try:
            await member.ban(reason=reason)
        except Exception as e:
            # Handle errors if any
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS:`** User { member.display_name } has been banned')

    """ Unban Member """
    @commands.command(
        usage="[member_id] (optional reason)",
        description="Unbans a member"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: int, *reason):
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
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS: `** User { user.display_name } has been unbanned')
        
    """ Add Role """
    @commands.command(
        aliases=['setrole'],
        usage="(optional member) [role]",
        description="Adds role to member"
    )
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
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS:`** role { role.name } added to { member.display_name }')

    """ Remove Role """
    @commands.command(
        aliases=['rmrole'],
        usage="(optional member) [role]",
        description="Removes role to member"
    )
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
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS:`** role { role.name } removed from { member.display_name }')

    """ System Status """
    @commands.command(
        aliases=['system','host'],
        description="Checks status of bot server host"
    )
    @commands.check(check_disabled)
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def systemstatus(self, ctx):
        info={}
        info['ram']=psutil.virtual_memory().percent
        info['cpu']=psutil.cpu_percent()
        info['uptime']=time.time() - psutil.boot_time()

        embed=discord.Embed(
            title = "System Status", 
            description = "Bot Host System Status", 
            color = discord.Color.green()
        )
        if ((info['ram'] > 90) or (info['cpu'] > 90)):
            embed.color =  discord.Color.red()
        elif ((info['ram'] > 75) or (info['cpu'] > 75)):
            embed.color =  discord.Color.orange()

        embed.add_field(name="Uptime", value=str(round(info['uptime']/60/60,2))+" Hours", inline=True)
        embed.add_field(name="Memory", value=str(info['ram'])+"%", inline=True)
        embed.add_field(name="CPU", value=str(info['cpu'])+"%", inline=True)
        

        return await ctx.send(embed=embed)

    """ Set Server Prefix """
    @commands.command()
    @commands.check(check_disabled)
    @commands.guild_only()
    async def set_prefix(self, ctx, *, prefix):
        try:
            guild = await database.fetch_guild(ctx.guild.id)
        except (ServerSelectionTimeoutError, AttributeError) as e:
            embed = discord.Embed(
                title="Error setting prefix",
                colour=discord.Color.red(),
                description=f"Could not set server prefix: { e }"
            )
            return await ctx.send(embed=embed)
        guild.prefix = prefix
        await guild.commit()

        embed = discord.Embed(
            title="Prefix set",
            colour=discord.Color.green(),
            description=f"Server prefix now set to `{ prefix }`"
        )
        return await ctx.send(embed=embed)

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within command
        embed = discord.Embed(
            title=f"Error in { ctx.command.qualified_name }",
            colour=discord.Color.red(),
            description=f"{ error }"
        )
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Mod(bot))
