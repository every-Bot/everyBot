import discord
import sys
import os
import traceback
import json

from discord.ext import commands

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_prefix(bot, message):
    prefixes = get_secret("prefixes")

    if not message.guild:
        return '?'

    return commands.when_mentioned_or(*prefixes)(bot, message)

def get_secret(secret):
    try:
        with open(".secrets.json") as file:
            data = json.load(file)
            return data[secret]
    except FileNotFoundError:
        sys.exit("Error: Please ensure there is a .secrets.json file in everyBot's root directory")

# modules
modules = [
    'everyBot.cogs.help.help',
    'everyBot.cogs.text.text',
    'everyBot.cogs.members.members',
    'everyBot.cogs.modules.modules',
    'everyBot.cogs.owner.owner',
    'everyBot.cogs.mod.mod',
    'everyBot.cogs.module_bot.module_bot',
    'everyBot.cogs.fun.fun',
    'everyBot.cogs.animals.animals',
    'everyBot.cogs.random_compliment.random_compliment',
    'everyBot.cogs.dnd.dnd'
    ]

bot = commands.Bot(
    command_prefix=get_prefix,
    owner_id=get_secret("ownerId"),
    case_insensitive=True
)
bot.disabled_commands = []
bot.base_cogs = ['modules', 'owner', 'module_bot']

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


bot.run(get_secret("token"), bot=True, reconnect=True)