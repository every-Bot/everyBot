import discord
import asyncio
from datetime import datetime
from pymongo.errors import ServerSelectionTimeoutError

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import mongo

class CommandAlreadyDisabled(Exception):
    def __init__(self, command_name):
        self.message = f"Command `{ command_name }` is already disabled"
        super().__init__(self.message)

class CommandNotFound(Exception):
    def __init__(self, command_name):
        self.message = f"Command `{ command_name }` is is not in the list of disabled commands"
        super().__init__(self.message)

async def warn_member(member: discord.Member, reason: str, ctx):
    """Warn a member

    This function will create a warning for a given member and if the member
    has accumulated 3 warnings, it will call for them to be muted temporarily.

    Args:
        member: The discord member to be warned
        reason: The reason for the member's warn
        ctx: Discord context object 

    """
    # Create new warning for member
    new_warning = mongo.MemberWarning(
        member_id=member.id,
        reason=reason,
        active=True,
        date_issued=datetime.now()
    )
    await new_warning.commit()

    # Alert discord that member has been warned
    embed = discord.Embed(
        title=f"Warn Member { member.display_name }",
        description=f"Member { member.mention } has been warned for '{ reason }'",
    )
    embed.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=embed)

    # We need to check existing warnings to see if the member has ammassed 
    # over 3, if they have, we need to mute them.
    try:
        response = await fetch_member_warnings(member.id, True)
    except Exception as e:
        await ctx.send(f"ERROR: { type(e).__name__ } - { e }")
    
    # Get the warnings in a list
    warnings = await response.to_list(length=None)

    # If member has 3 warnings, 
    # temp mute them and set all warnings to inactive
    print(warnings)
    if len(warnings) >= 3:
        # Set all current warnings to be inactive
        for warning in warnings:
            warning.active = False
            await warning.commit() 
        # Mute member for 3 warnings
        await mute_member(member, ctx)

async def mute_member(member: discord.Member, ctx, time: int=300):
    """ Mute a discord member

    This function will temporarily give the member the 'muted' role to mute them
    server wide. If the role doesn't exist, the function will create it.

    Args:
        member: Discord member to mute
        ctx: Discord contect object
        time: Optional, the time for which the member will be muted.
    """

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
        except discord.Forbidden:
            embed = discord.Embed(
                title="Role creation failed",
                colour=discord.Color.red(),
                description="No 'muted' role exists and I do not have the correct permissions to create a new one."
            )
            return await ctx.send(embed=embed)
    
    # Add muted role to the member, wait the specified amount of time,
    # then unmute member by removing the role.
    await member.add_roles(role)
    await asyncio.sleep(time)
    await member.remove_roles(role)

async def register_member(member: discord.Member, ctx):
    """ Register member to the database

    This function will register the discord member that runs the command into
    the database for minigames etc.

    Args:
        member: Discord member to be registered
        ctx: Discord context object
    """

    embed=discord.Embed(
        title=f"Register User { member.display_name }",
    )
    # First we need to check if the member is already registered
    try:
        response = await fetch_member(member)
    except Exception as e:
        # Output any errors in fetching from db to discord
        embed = discord.Embed(
            title=f"Error registering member { discord.display_name }",
            colour=discord.Colour.red(),
            description=f"Error: { type(e).__name__ } - { e }"
        )
        return await ctx.send(embed=embed)

    # If member doesn't exist, register in db
    if response:
        embed = discord.Embed(
            title="Member already Exists",
            colour=discord.Color.blue(),
            description=f"Member { member.mention } already exists.\nUse `$profile` to check your profile."
        )
        return await ctx.send(embed=embed)

    # Create new member object
    new_member = mongo.Member(id=member.id)
    try:
        # Try to register member in db
        await new_member.commit()
    except Exception as e:
        # Output any errors in registering member to discord
        embed = discord.Embed(
            title=f"Error registering member { member.display_name }",
            colour=discord.Color.red(),
            description=f"Error: { type(e).__name__ } - { e }"
        )
        return await ctx.send(embed=embed)

    # If member was successfully registered, alert the discord server.
    embed = discord.Embed(
        title=f"Successfully registered member { member.display_name }",
        colour=discord.Color.green(),
        description=f"{ member.display_name } has been registered.\nUse `$profile` to see your new profile."
    )
    return await ctx.send(embed=embed)

async def fetch_member(member: discord.Member) -> mongo.Member:
    return await mongo.Member.find_one(
        { "_id": member.id }
    )

async def fetch_member_warnings(member_id: str, active: bool=None) -> list:
    if active == None:
        return mongo.MemberWarning.find(
            {
                "member_id": member_id
            }
        )

    return mongo.MemberWarning.find(
        { 
            "member_id": member_id,
            "active": active
        }
    )

async def remove_member(member: discord.Member):
    mongo_member = await mongo.Member.find_one(
        { "_id": member.id }
    )
    await mongo_member.delete()

async def fetch_guild(guild_id: str):
    try:
        return await mongo.Guild.find_one(
            { "guild_id": guild_id }
        )
    except ServerSelectionTimeoutError as e:
        raise e

async def add_guild(guild):
    new_guild = mongo.Guild(
        guild_id = guild.id
    )

    await new_guild.commit()

async def fetch_guild_disabled_commands(guild_id):
    try:
        guild = await fetch_guild(guild_id)
    except ServerSelectionTimeoutError as e:
        raise e

    return guild.disabled_commands.dump()

async def add_disabled_command(guild_id, command_name):
    # Get guild instance from db
    try:
        guild = await fetch_guild(guild_id)
    except ServerSelectionTimeoutError as e:
        raise e 

    # First we need to check if the command has already been disabled
    if command_name in guild.disabled_commands.dump():
        raise CommandAlreadyDisabled(command_name)

    # Add command to list
    guild.disabled_commands.append(command_name)
    await guild.commit()

async def remove_disabled_command(guild_id, command_name):
    # Get guild instance from db
    try:
        guild = await fetch_guild(guild_id)
    except ServerSelectionTimeoutError as e:
        raise e 

    # First we need to check if command is in disabled commands
    if command_name not in guild.disabled_commands.dump():
        raise CommandNotFound(command_name)

    guild.disabled_commands.remove(command_name)
    await guild.commit()
