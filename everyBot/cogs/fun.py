import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from . import modules

import random
import urllib.parse
import json
import requests

""" Disabled Check """
async def check_disabled(ctx):
    return ctx.command.name not in modules.disabled_commands

class Fun(commands.Cog, name='Fun Commands'):
    def __init__(self, bot):
        self.bot = bot

    """ Eight Ball """
    @commands.command(aliases=['eight', '8ball'])
    @commands.check(check_disabled)
    async def eightball(self, ctx, *, question: commands.clean_content):
        # Define all 8ball responses
        responses = [
            'Yes', 'No', 'Take a wild guess...', 'Very doubtful',
            'Sure', 'Without a doubt', 'Most likely', 'Might be possible',
            'You\'ll be the judge', 'no... (╯°□°）╯︵ ┻━┻', 'no... baka',
            'senpai, pls no ;-;'
        ]
        # Choose random reply
        response = random.choice(responses)
        await ctx.send(f':8ball:: "{ question }" { response }')

    """ FML """
    @commands.command()
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def fml(self, ctx):
        # Getting 'fml' from api
        response = requests.get('https://api.alexflipnote.dev/fml')
        # Formatting 'fml'
        json_data = json.loads(response.text)
        await ctx.send(json_data['text'])

    """ Dad Joke """
    @commands.command(aliases=['dad', 'dad-joke'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def dadjoke(self, ctx):
        # Getting dad joke from api
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        await ctx.send(response.json()['joke'])

    """ Compliment User """
    @commands.command()
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def compliment(self, ctx, member: discord.Member):
        # Getting compliment from api
        response = requests.get('https://complimentr.com/api')
        # Formatting response
        compliment = response.json()['compliment']
        await ctx.send(f'{ member.display_name }, { compliment }')

    """ Insult User """
    @commands.command()
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def insult(self, ctx, member: discord.Member):
        # Getting insult from api
        response = requests.get('https://insult.mattbas.org/api/insult')
        await ctx.send(f'{ member.display_name }, { response.text }')

    """ Achievement Get """
    @commands.command(aliases=['achievement-get', 'achievementget'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def achievement(self, ctx, *, text):
        text = urllib.parse.quote(text)
        await ctx.send(f'https://api.alexflipnote.dev/achievement?text={ text }')

    """ Truth Scroll """
    @commands.command(aliases=['truthscroll', 'truth-scroll'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def scroll(self, ctx, *, text):
        text = urllib.parse.quote(text)
        await ctx.send(f'https://api.alexflipnote.dev/scroll?text={ text }') 

    """ Supreme """
    @commands.command()
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def supreme(self, ctx, *, text):
        text = urllib.parse.quote(text)
        await ctx.send(f'https://api.alexflipnote.dev/supreme?text={ text }')

    """ Facts """
    @commands.command()
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def facts(self, ctx, *, text):
        text = urllib.parse.quote(text)
        await ctx.send(f'https://api.alexflipnote.dev/facts?text={ text }')
        
    """ Trump Quote """
    @commands.command()
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def trump(self, ctx):
        response = requests.get('https://api.tronalddump.io/random/quote')
        json_data = response.json()['value']
        quote = f'"{ json_data }" - Donald Trump'
        await ctx.send(quote)

    """ Roulette """
    @commands.command()
    @commands.check(check_disabled)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=1800, type=commands.BucketType.user)
    async def roulette(self, ctx):
        responses = [
            ':gun:', ':safety_vest:', ':safety_vest:',
            ':safety_vest:', ':safety_vest:', ':safety_vest:'
        ]
        response = random.choice(responses)
        if response == ':gun:':
            try:
                await ctx.author.kick(reason='roulette')
            except Exception as e:
                # Handle errors if any
                await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
            else:
                await ctx.send(f'{ response }! { ctx.author.display_name } got unlucky')
        else:
            await ctx.send(f'{ response }! { ctx.author.display_name } was safe.. this time')

    """ Mock """
    @commands.command()
    @commands.check(check_disabled)
    async def mock(self, ctx, *, text):
        new_text = list(text)
        for i, char in enumerate(new_text):
            if i % 2 == 0:
                new_text[i] = char.capitalize()
        
        await ctx.send("".join(new_text))


    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        if 'The check functions for command' in str(error):
            return
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Fun(bot))
