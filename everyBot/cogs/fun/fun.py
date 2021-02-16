import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from pymongo.errors import ServerSelectionTimeoutError

from everyBot.cogs import database

import random
import urllib.parse
import json
import requests

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

class Fun(commands.Cog, name='fun'):
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

    """ Eight Ball """
    @commands.command(
        aliases=['eight', '8ball'],
        usage="[question]",
        description="Test your fate with the eight ball"
    )
    @commands.check(check_disabled)
    async def eightball(self, ctx, *, question: commands.clean_content):
        # Define all 8ball responses and pick random choice
        response = random.choice([
            'Yes', 'No', 'Take a wild guess...', 'Very doubtful',
            'Sure', 'Without a doubt', 'Most likely', 'Might be possible',
            'You\'ll be the judge', 'no... (╯°□°）╯︵ ┻━┻', 'no... baka',
            'senpai, pls no ;-;'
        ])      
        
        embed = discord.Embed(
            title = f"eightball '{ question }'",
            colour = discord.Color.green(),
            description=(f"""{ response }""")
        )

        return await ctx.send(embed=embed)

    """ Dad Joke """
    @commands.command(
        aliases=['dad', 'dad-joke'],
        description="Clearly the best type of joke"
    )
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def dadjoke(self, ctx):
        # Getting dad joke from api
        headers = {
            'Accept': 'application/json'
        }
        try:
            response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title = f"Dad Joke",
            colour = discord.Color.green(),
            description=(f"""{ response.json()['joke'] }""")
        )
        return await ctx.send(embed=embed)

    """ Compliment User """
    @commands.command(
        usage="[member]",
        description="Compliment your favourite discord user"
    )
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def compliment(self, ctx, member: discord.Member):
        try:
            # Get compliment from api and format response
            compliment = (requests.get('https://complimentr.com/api')).json()['compliment']
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title = f"Compliment",
            colour = discord.Color.green(),
            description=(f'{ member.display_name }, { compliment }')
        )
        return await ctx.send(embed=embed)

    """ Insult User """
    @commands.command(
        usage="[member]",
        description="Roast an unsuspecting user"
    )
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def insult(self, ctx, member: discord.Member):
        # Getting insult from api
        try:
            response = requests.get('https://insult.mattbas.org/api/insult')
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title = f"Insult User",
            colour = discord.Color.green(),
            description=(f'{ member.display_name }, { response.text }')
        )
        return await ctx.send(embed=embed)

    """ Trump Quote """
    @commands.command(
        description="Random quote from everyone's favourite president"
    )
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def trump(self, ctx):
        try:
            response = (requests.get('https://api.tronalddump.io/random/quote')).json()['value']
            quote = f'"{ response }" - Donald Trump'
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title=f"Request Error: { type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title = f"Trump Quote",
            colour = discord.Color.green(),
            description=(quote)
        )
        return await ctx.send(embed=embed)

    """ Roulette """
    @commands.command(
        description="Test your luck"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(rate=1, per=1800, type=commands.BucketType.user)
    async def roulette(self, ctx):
        response = random.choice([':gun:', ':safety_vest:', ':safety_vest:',':safety_vest:', ':safety_vest:', ':safety_vest:'])

        if response == ':gun:':
            try:
                await ctx.author.kick(reason='roulette')
                embed = discord.Embed(
                    title = f"Roulette",
                    colour = discord.Color.green(),
                    description=(f'{ response }! { ctx.author.display_name } got unlucky')
                )
                return await ctx.send(embed=embed)
            except requests.exceptions.RequestException as e:
                embed = discord.Embed(
                    title=f"Request Error: { type(e).__name__ }",
                    colour=discord.Color.red(),
                    description=f"{ e }"
                )
                return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title = f"Roulette",
            colour = discord.Color.green(),
            description=(f'{ response }! { ctx.author.display_name } was safe.. this time')
        )
        return await ctx.send(embed=embed)

    """ Urban Dictionary """
    @commands.command(
        usage="[text]",
        description="Search anything in urban dictionary"
    )
    @commands.check(check_disabled)
    async def urban(self, ctx, *text):
        # Getting definition from api
        text = urllib.parse.quote(" ".join(text))
        response = requests.get(f'http://api.urbandictionary.com/v0/define?term={ text }')

        # Check if there is a definition for the given text
        if not response.json()['list']:
            error=discord.Embed(
                title=f"No definition found",
                color=discord.Color.red(),
                description=f"Sorry, We could not find a definition for '{ text }' "
            )
            return await ctx.send(embed=error)

        # Construct embed for valid request, the example and rating vars are 
        # for whitespaces on multiline strings.
        example=f"**Example:**\n{ response.json()['list'][0]['example'] }"
        rating=f":thumbsup: { response.json()['list'][0]['thumbs_up'] } :thumbsdown: { response.json()['list'][0]['thumbs_down'] }"
        embed=discord.Embed(
            title=f"Definition of { response.json()['list'][0]['word'] }",
            color=discord.Color.green(),
            url=response.json()['list'][0]['permalink'],
            description=f"{ response.json()['list'][0]['definition'] }\n\n{ example }\n\n{ rating }"
        )
        embed.set_thumbnail(url="https://i.imgur.com/RoKVYoy.jpeg")
        embed.set_author(name=f"Definition by: { response.json()['list'][0]['author'] } ")

        return await ctx.send(embed=embed)

    """ Weather """
    @commands.command(
        usage="[location]",
        description="Check the current weather"   
    )
    @commands.check(check_disabled)
    async def weather(self, ctx, *location):
        try:
            location = ' '.join(location)
            chars = set("{}[]<>?_@#\$&")
            if any((c in chars) for c in location):
                embed = discord.Embed(
                    title=f"Error: Prohibited character(s) in string.",
                    colour=discord.Color.red(),
                    description=f"Request contains prohibited characters. Remove non-alphabetical characters and try again."
                )
                return await ctx.send(embed=embed)

            loc = (location.replace(" ", "+")).replace(",", "+")
            response = requests.get('http://wttr.in/'+loc+'?format=%c+%C+%t+%w').text

        except Exception as e:
            embed = discord.Embed(
                title=f"{ type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title = f"{ location.capitalize() }",
            colour = discord.Color.green(),
            description=(f"{ response }")
        )
        return await ctx.send(embed=embed)


    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        if 'The check functions for command' in str(error):
            return
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Fun(bot))
