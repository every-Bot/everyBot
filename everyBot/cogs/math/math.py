import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from pymongo.errors import ServerSelectionTimeoutError

from .. import database
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

class Math(commands.Cog, name='Math'):
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

    """ Add """
    @commands.command(aliases=['addition'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def add(self, ctx, *numbers):
        try:
            array = [float(i) for i in numbers]
            response = sum(array)

            title = numbers[0]
            for num in numbers[1:]:
                title = title + " + " + num
            title = title + " ="
        except (TypeError, ValueError) as e:
            embed = discord.Embed(
                title=f"{ type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title = f"{ title }",
            colour = discord.Color.green(),
            description=(f"""{ response }""")
        )

        return await ctx.send(embed=embed)
    
    """ Subtract """
    @commands.command(aliases=['minus'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def subtract(self, ctx, *numbers):
        try:
            array = [float(i) for i in numbers]
            response = array[0] - sum(array[1:])

            title = numbers[0]
            for num in numbers[1:]:
                title = title + " - " + num
            title = title + " ="
        except (TypeError, ValueError) as e:
            embed = discord.Embed(
                title=f"{ type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title = f"{ title }",
            colour = discord.Color.green(),
            description=(f"""{ response }""")
        )

        return await ctx.send(embed=embed)

    """ Multiply """
    @commands.command(aliases=['times'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def multiply(self, ctx, *numbers):
        try:
            array = [float(i) for i in numbers]
            result = 1
            for num in array:
                result = result * num

            title = numbers[0]
            for num in numbers[1:]:
                title = title + " x " + num
            title = title + " ="
        except (TypeError, ValueError) as e:
            embed = discord.Embed(
                title=f"{ type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title = f"{ title }",
            colour = discord.Color.green(),
            description=(f"""{ result }""")
        )

        return await ctx.send(embed=embed)

    """ Divide """
    @commands.command(aliases=['division'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def divide(self, ctx, *numbers):
        try:
            array = [float(i) for i in numbers]
            response = array[0]
            for num in array[1:]:
                response = response / num
            
            title = numbers[0]
            for num in numbers[1:]:
                title = title + " / " + num
            title = title + " ="
        except (TypeError, ValueError, ZeroDivisionError) as e:
            embed = discord.Embed(
                title=f"{ type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title = f"{ title }",
            colour = discord.Color.green(),
            description=(f"""{ response }""")
        )

        return await ctx.send(embed=embed)

    """ Calculate """
    @commands.command(aliases=['calc'])
    @commands.check(check_disabled)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def calculate(self, ctx, *, numbers):
        try:
            response = (eval(numbers))
        except (TypeError, ValueError, ZeroDivisionError, NameError) as e:
            embed = discord.Embed(
                title=f"{ type(e).__name__ }",
                colour=discord.Color.red(),
                description=f"{ e }"
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title = f"Calculate { numbers }",
            colour = discord.Color.green(),
            description=(f"""{ response }""")
        )

        return await ctx.send(embed=embed)

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        if 'The check functions for command' in str(error):
            return
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Math(bot))
