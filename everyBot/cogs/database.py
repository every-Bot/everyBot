import discord
import asyncio
from datetime import datetime
from pymongo.errors import ServerSelectionTimeoutError

from everyBot.cogs.moderation import moderation
from everyBot.database import mongo

import sys
import os

class CommandAlreadyDisabled(Exception):
    def __init__(self, command_name):
        self.message = f"Command `{ command_name }` is already disabled"
        super().__init__(self.message)

class CommandNotFound(Exception):
    def __init__(self, command_name):
        self.message = f"Command `{ command_name }` is not in the list of disabled commands"
        super().__init__(self.message)

class ModuleAlreadyInstalled(Exception):
    def __init__(self, module_name):
        self.message = f"The module `{ module_name }` has already been installed on this server"
        super().__init__(self.message)
    
class ModuleNotInstalled(Exception):
    def __init__(self, module_name):
        self.message = f"The module `{ module_name }` is not in the list of installed modules"
        super().__init__(self.message)  

async def warn_member(ctx, member, reason):
    guild_id = ctx.guild.id
    member_id = member.id
    """Warn a member

    This function will create a warning for a given member and if the member
    has accumulated 3 warnings, it will call for them to be muted temporarily

    Args:
        ctx: Discord context object
        member: The discord member to be warned
        reason: The reason for the member's warn

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        discord.Forbidden: Bot does not have correct permissions for action
    """
    # Create new warning for member
    new_warning = mongo.MemberWarning(
        member_id=member_id,
        guild_id=guild_id,
        reason=reason,
        active=True,
        date_issued=datetime.now()
    )
    await new_warning.commit()

    # We need to check existing warnings to see if the member has ammassed 
    # over 3, if they have, we need to mute them.
    try:
        response = await fetch_member_warnings(guild_id, member_id, True)
    except (ServerSelectionTimeoutError) as e:
        raise e
    
    # Get the warnings in a list
    warnings = await response.to_list(length=None)

    # If member has 3 warnings, 
    # temp mute them and set all warnings to inactive
    if len(warnings) >= 3:
        # Set all current warnings to be inactive
        for warning in warnings:
            warning.active = False
            await warning.commit() 
        # Mute member for 3 warnings
        try:
            await moderation.mute_member(ctx, member, 5, "Warned too many times")
        except (ServerSelectionTimeoutError, discord.Forbidden, AttributeError) as e:
            raise e
    
    embed = discord.Embed(
        title=f"{ member.display_name } has been warned",
        colour=discord.Color.green(),
        description=f"**Reason:** { reason }"
    )
    embed.set_thumbnail(url=member.avatar_url)
    return embed

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
        embed.set_thumbnail(url=member.avatar_url)
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
    embed.set_thumbnail(url=member.avatar_url)
    return await ctx.send(embed=embed)

async def fetch_member(member: discord.Member) -> mongo.Member:
    """Fetch member from database

    This function will search the database for a member with a given member id
    and return the first one it finds.

    Args:
        member: discord Member object

    Returns:
        Mongodb member object
    """
    return await mongo.Member.find_one(
        { "_id": member.id }
    )

async def fetch_member_warnings(guild_id: int, member_id: int, active: bool=None) -> list:
    """Fetch list of member warnings

    This function will find and return a list of warnings for a given member
    from the database

    Args:
        member_id
        active: find active or all warnings

    Returns:
        list of mongo warnings
    """
    if active == None:
        return mongo.MemberWarning.find(
            {
                "member_id": member_id,
                "guild_id": guild_id
            }
        )

    return mongo.MemberWarning.find(
        { 
            "member_id": member_id,
            "guild_id": guild_id,
            "active": active
        }
    )

async def remove_member(member: discord.Member):
    """Remove member from database

    This funciton will remove a given member from the database

    Args:
        member: discord member object
    """
    mongo_member = await mongo.Member.find_one(
        { "_id": member.id }
    )
    await mongo_member.delete()

async def fetch_guild(guild_id: str):
    """Fetch guild from db

    This function will search for and return a guild by
    a given guild id from the database

    Args:
        guild_id: the id of the guild to find

    Raises:
        ServerSelectionTimroutError: Cannot connect to database
    
    Returns:
        Mongo guild object
    """
    try:
        return await mongo.Guild.find_one(
            { "guild_id": guild_id }
        )
    except ServerSelectionTimeoutError as e:
        raise e

async def add_guild(guild):
    """Add guild to db

    This function will add a given guild to the database

    Args:
        guild: discord guild object
    """
    new_guild = mongo.Guild(
        guild_id = guild.id,
        prefix = os.getenv("PREFIX")
    )

    await new_guild.commit()

async def fetch_guild_installed_modules(guild_id):
    """Fetch installed modules

    This funciton will fetch all 'installed' modules for a given guild
    and return a list containing the names of the installed modules

    Args:
        guild_id: guild id to find installed modules of

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        AttributeError: Guild does not exist

    Returns:
        List of strings
    """
    try:
        guild = await fetch_guild(guild_id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        raise e

    return guild.installed_modules.dump()

async def fetch_guild_disabled_commands(guild_id):
    """Fetch disabled commands

    This function will fetch all disabled commands for a given guild
    and return a list containing the names of the commands

    Args:
        guild_id: guild id to find disabled commands of

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        AttributeError: Guild does not exist
    
    Returs:
        List of strings
    """
    try:
        guild = await fetch_guild(guild_id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        raise e

    return guild.disabled_commands.dump()

async def install_module(guild_id, module_name):
    """Install module to guild

    This function will insert a module into a given guild's list
    of installed modules

    Args:
        guild_id: guild id to install module to
        module_name: name of module to be installed

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        AttributeError: Guild does not exist
        ModuleAlreadyInstalled: Module is already installed for guild
    """
    # Get guild instance from db
    try:
        guild = await fetch_guild(guild_id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        raise e 

    # First we need to check if module is already installed
    if module_name in guild.installed_modules.dump():
        raise ModuleAlreadyInstalled(module_name)

    # Install module
    guild.installed_modules.append(module_name)
    await guild.commit()

async def remove_module(guild_id, module_name):
    """Uninstall module for guild

    This function will attempt to uninstall a given module for a 
    given guild

    Args:
        guild_id: guild id to remove module from
        module_name: name of module to be removed

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        AttributeError: Guild does not exist
        ModuleNotInstalled: The given module is not installed
    """
    # Get guild instance from db
    try:
        guild = await fetch_guild(guild_id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        raise e 

    # First we need to check if command is in disabled commands
    if module_name not in guild.installed_modules.dump():
        raise ModuleNotInstalled(module_name)

    guild.installed_modules.remove(module_name)
    await guild.commit()

async def add_disabled_command(guild_id, command_name):
    """Disable command for server

    This function will attempt to disable a given command for 
    a given guild

    Args:
        guild_id: guild id to disable command for
        command_name: command to be disabled

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        AttributeError: Guild does not exist
        CommandAlreadyDisabled: Command is already disabled
    """
    # Get guild instance from db
    try:
        guild = await fetch_guild(guild_id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        raise e 

    # First we need to check if the command has already been disabled
    if command_name in guild.disabled_commands.dump():
        raise CommandAlreadyDisabled(command_name)

    # Add command to list
    guild.disabled_commands.append(command_name)
    await guild.commit()

async def remove_disabled_command(guild_id, command_name):
    """Re-enable command

    This function will attempt to re-enable a given command for
    a given guild

    Args:
        guild_id: guild id to enable command for
        command_name: command to be enabled

    Raises:
        ServerSelectionTimeoutError: Cannot connect to database
        AttributeError: Guild does not exist
        CommandNotFound: Given command has not been disabled for guild
    """
    # Get guild instance from db
    try:
        guild = await fetch_guild(guild_id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        raise e 

    # First we need to check if command is in disabled commands
    if command_name not in guild.disabled_commands.dump():
        raise CommandNotFound(command_name)

    guild.disabled_commands.remove(command_name)
    await guild.commit()
