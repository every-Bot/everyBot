import discord
from discord.ext import commands
from pymongo.errors import ServerSelectionTimeoutError

from everyBot.cogs import database

import requests
import random

class RandomCompliment(commands.Cog, name="Random"):
    def __init__(self, bot):
        self.bot = bot

    async def _check_active(self, guild_id):
        try:
            guild_installed_modules = await database.fetch_guild_installed_modules(guild_id)
        except Exception:
            # No output is needed, just do not send compliment
            return False
        
        if "random_compliment" in guild_installed_modules:
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot != True and random.randint(0, 100) == 1:
            if not await self._check_active(message.guild.id):
                return
            # Getting compliment from api
            response = requests.get('https://complimentr.com/api')
            # Formatting response
            compliment = response.json()['compliment']
            return await message.channel.send(f'{ message.author.display_name }, { compliment }')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(RandomCompliment(bot))
