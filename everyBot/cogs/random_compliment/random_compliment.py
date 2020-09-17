import discord
from discord.ext import commands

import requests
import random

class RandomCompliment(commands.Cog, name="Random"):
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot != True and random.randint(0, 75) == 1:
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
    
