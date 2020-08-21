import discord

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import mongo

async def register_member(member: discord.Member) -> discord.Embed:
    # First we need to check if the member is already registered
    embed=discord.Embed(
            title=f"Register User { member.display_name }",
    )
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

async def get_member(member: discord.Member) -> mongo.Member:
    return await mongo.Member.find_one(
        { "_id": member.id }
    )

async def fetch_member_warnings(member_id: str) -> list:
    return mongo.MemberWarning.find(
        { 
            "member_id": member_id,
            "active": True
        }
    )

async def remove_member(member: discord.Member):
    mongo_member = await mongo.Member.find_one(
        { "_id": member.id }
    )
    await mongo_member.delete()