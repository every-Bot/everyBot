import discord
import sys
import os
import traceback
import json

from discord.ext import commands

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from everyBot.cogs import database

# modules
modules = [
    'everyBot.cogs.help',
    'everyBot.cogs.text.text',
    'everyBot.cogs.members.members',
    'everyBot.cogs.modules.modules',
    'everyBot.cogs.owner.owner',
    'everyBot.cogs.moderation.moderation',
    'everyBot.cogs.fun.fun',
    'everyBot.cogs.animals.animals',
    'everyBot.cogs.random_compliment.random_compliment',
    'everyBot.cogs.dnd.dnd',
    'everyBot.cogs.math.math'
    ]

bot = commands.Bot(
    command_prefix=os.getenv("PREFIX"),
    owner_id=os.getenv("OWNER_ID"),
    case_insensitive=True,
    help_command=None
)
bot.disabled_commands = []
bot.base_cogs = ['modules', 'owner']

if __name__ == '__main__':
    for module in modules:
        try:
            bot.load_extension(module)
        except Exception as e:
            print(f'Failed to load module {module}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')

@bot.event
async def on_guild_join(guild):
    await database.add_guild(guild)

bot.run(os.getenv("TOKEN"), bot=True, reconnect=True)