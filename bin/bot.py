import discord
import sys
import os
import traceback
import json
import asyncio
from pymongo.errors import ServerSelectionTimeoutError
import logging

from discord.ext import commands

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(filename=os.getenv("LOG_FILE"), level=logging.INFO, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

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

async def determine_prefix(bot, message):
    guild = message.guild
    if not guild:
        return os.getenv("PREFIX")
    
    try:
        db_guild = await database.fetch_guild(guild.id)
    except (ServerSelectionTimeoutError, AttributeError) as e:
        return os.getenv("PREFIX")

    return db_guild.prefix

bot = commands.Bot(
    command_prefix=determine_prefix,
    owner_id=int(os.getenv("OWNER_ID")),
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
    for guild in bot.guilds:
        try:
            db_guild = await database.fetch_guild(guild.id)
        except (ServerSelectionTimeoutError, AttributeError) as e:
            return
        if not db_guild:
            await database.add_guild(guild)
    print("\n\nAll guilds added to db")
    print(f'Logged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')

@bot.event
async def on_guild_join(guild):
    await database.add_guild(guild)

@bot.before_invoke
async def command_logger(ctx):
  server = ctx.guild.name
  logging.info(str(server) + ":" + str(ctx.author) + " ran the command "+ bot.command_prefix + str(ctx.command))


bot.run(os.getenv("TOKEN"), bot=True, reconnect=True)