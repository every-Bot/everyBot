import discord
import sys
import os
import traceback

from discord.ext import commands

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_prefix(bot, message):
    prefixes = ['$', 'e!']

    if not message.guild:
        return '?'

    return commands.when_mentioned_or(*prefixes)(bot, message)

# modules
modules = [
    'everyBot.cogs.members',
    'everyBot.cogs.modules',
    'everyBot.cogs.owner',
    'everyBot.cogs.admin',
    'everyBot.cogs.mod',
    'everyBot.cogs.module_bot',
    'everyBot.cogs.fun',
    'everyBot.cogs.animals',
    'everyBot.cogs.random_compliment',
    'everyBot.cogs.dnd'
]

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True
)

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


bot.run(token, bot=True, reconnect=True)