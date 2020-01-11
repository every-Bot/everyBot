import discord
from discord.ext import commands

import requests
import random

class RandomCompliment(commands.Cog, name="Random compliment"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot != True and random.randint(0, 75) == 1:
            # Getting compliment from api
            response = requests.get('https://complimentr.com/api')
            # Formatting response
            compliment = response.json()['compliment']
            await message.channel.send(f'{ message.author.display_name }, { compliment }')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(RandomCompliment(bot))