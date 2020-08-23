import discord
import asyncio
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import mongo

async def warn_member(member: discord.Member, reason: str, ctx) -> discord.Embed:
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

    # We need to check existing warnings
    try:
        response = await fetch_member_warnings(member.id, True)
    except Exception as e:
        await ctx.send(f"ERROR: { type(e).__name__ } - { e }")
    warnings = await response.to_list(length=None)

    # If member already has 3 warnings, 
    # temp mute them and set all warnings to inactive
    if len(warnings) >= 3:
        # Set all current warnings to be inactive
        for warning in warnings:
            warning.active = False
            await warning.commit() 
        # Mute member for 3 warnings
        await mute_member(member, ctx)

async def mute_member(member: discord.Member, ctx, time: int=300):
    role = discord.utils.get(ctx.guild.roles, name="muted")
    if not role:
        try:
            role = await ctx.guild.create_role(name="muted", reason="To use for muting")
            for channel in ctx.guild.channels: # removes permission to view and send in the channels 
                await channel.set_permissions(
                    role,
                    send_messages=False
                )
        except discord.Forbidden:
            return await ctx.send("No 'muted' role exists and I do not have the correct permissions to create a new one.")
    await member.add_roles(role)
    await asyncio.sleep(time)
    await member.remove_roles(role)

async def register_member(member: discord.Member) -> discord.Embed:
    embed=discord.Embed(
        title=f"Register User { member.display_name }",
    )
    # First we need to check if the member is already registered
    try:
        response = await get_member(member)
    except Exception as e:
        embed.colour = discord.Color.red()
        embed.description = f"**`ERROR:`** { type(e).__name__ } - { e }"
    # If member doesn't exist, register in db
    if response:
        embed.colour = discord.Color.red()
        embed.description = f"Member `{ member.display_name }` has already been registered."

    # Try to register member in db
    new_member = mongo.Member(id=member.id)
    try:
        await new_member.commit()
        embed.colour = discord.Color.green()
        embed.description = f"Member `{ member.display_name }` has successfully been registered."   
    except Exception as e:
        embed.colour = discord.Color.red()
        embed.description = f"**`ERROR:`** { type(e).__name__ } - { e }"

    return embed

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