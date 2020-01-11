import discord
from discord.ext import commands

import json
import requests

class Animals(commands.Cog, name='Cute Animals'):
    def __init__(self, bot):
        self.bot = bot

    async def get_image(self, ctx, url, endpoint):
        try:
            # Get requested image
            res = requests.get(url)
            json_data = json.loads(res.text)
        except Exception as e:
            # Handle errors if any
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            # Return data in json format
            return json_data


    """ Cats """
    @commands.command(aliases=['kitten', 'kitty'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, ctx):
        response = await self.get_image(ctx, 'https://api.alexflipnote.dev/cats', 'file')
        await ctx.send(response['file'])

    """ Sad Cat """
    @commands.command(aliases=['sadkitty'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def sadcat(self, ctx):
        response = await self.get_image(ctx, 'https://api.alexflipnote.dev/sadcat', 'file')
        await ctx.send(response['file'])

    """ Dogs """
    @commands.command(aliases=['doggo', 'puppy', 'pupper', 'woofer'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, ctx):
        response = await self.get_image(ctx, 'https://api.alexflipnote.dev/dogs', 'file')
        await ctx.send(response['file'])

    """ Birds """
    @commands.command(aliases=['birb', 'birdy'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def bird(self, ctx):
        response = await self.get_image(ctx, 'https://api.alexflipnote.dev/birb', 'file')
        await ctx.send(response['file'])

    """ Duck """
    @commands.command(aliases=['ducky', 'duckling'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        response = await self.get_image(ctx, 'https://random-d.uk/api/v1/random', 'url')
        await ctx.send(response['url'])

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Animals(bot))
    