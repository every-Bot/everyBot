import discord
from discord.ext import commands
from textwrap import dedent

import json
import requests

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

class Animals(commands.Cog, name='animals'):
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

    async def get_image(self, ctx, url, endpoint):
        try:
            # Get requested image
            res = requests.get(url)
            json_data = json.loads(res.text)
        except requests.exceptions.RequestException as e:
            raise e
            
        # Return data in json format
        return json_data


    """ Cats """
    @commands.command(aliases=['kitten', 'kitty'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, ctx):
        try:
            response = await self.get_image(ctx, 'https://api.alexflipnote.dev/cats', 'file')
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        
        return await ctx.send(response['file'])

    """ Sad Cat """
    @commands.command(aliases=['sadkitty'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def sadcat(self, ctx):
        try:
            response = await self.get_image(ctx, 'https://api.alexflipnote.dev/sadcat', 'file')
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        return await ctx.send(response['file'])

    """ Dogs """
    @commands.command(aliases=['doggo', 'puppy', 'pupper', 'woofer'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, ctx):
        try:
            response = await self.get_image(ctx, 'https://api.alexflipnote.dev/dogs', 'file')
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        return await ctx.send(response['file'])

    """ Birds """
    @commands.command(aliases=['birb', 'birdy'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def bird(self, ctx):
        try:
            response = await self.get_image(ctx, 'https://api.alexflipnote.dev/birb', 'file')
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        return await ctx.send(response['file'])

    """ Duck """
    @commands.command(aliases=['ducky', 'duckling'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        try:
            response = await self.get_image(ctx, 'https://random-d.uk/api/v1/random', 'url')
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        return await ctx.send(response['url'])

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        if 'The check functions for command' in str(error):
            return
        embed = discord.Embed(
            title=f"Error in { ctx.command.qualified_name }",
            colour=discord.Color.red(),
            description=dedent(f"""
                { error }
                Use `{ self.bot.command_prefix }help { ctx.command.qualified_name }` for help with the command.
                """)
        )

        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Animals(bot))
    