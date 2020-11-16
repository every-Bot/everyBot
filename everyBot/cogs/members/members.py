import discord
from discord.ext import commands

from pymongo.errors import ServerSelectionTimeoutError
from .. import database

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

class Members(commands.Cog, name="members"):
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

    """ Register new member into the database """
    @commands.command(
        description="Register yourself in the bot"
    )
    @commands.guild_only()
    async def register(self, ctx):
        await database.register_member(ctx.author, ctx)

    """ Display profile """
    @commands.command(
        description="Display your bot profile"
    )
    async def profile(self, ctx):
        member = await database.fetch_member(ctx.author)
        fetch_warnings = await database.fetch_member_warnings(ctx.author.id, True)
        warnings_list = await fetch_warnings.to_list(length=None)

        warnings = []
        for i, warning in enumerate(warnings_list):
            warnings.append(f"{ i+1 }: { warning.reason }")

        warnings_string = "\n" + "\n".join(warnings)

        embed = discord.Embed()

        if not member:
            embed.title = "Failed"
            embed.colour = discord.Color.red()
            embed.description = f"Could not fetch profie. You may not be registered."
        else:
            embed.title = f"Profile for { ctx.author.display_name }"
            embed.colour = discord.Color.green()
            embed.description = f"""
                **Name:** { ctx.author.name }#{ ctx.author.discriminator }
                **Coins:** { member.coins }
                **Warnings:** { warnings_string }
            """
            embed.set_thumbnail(url=ctx.author.avatar_url)
        
        return await ctx.send(embed=embed)

    """ Check when the mentioned user joined the server """
    @commands.command(
        usage="(optional member)",
        description="Check when a member joined the server"
    )
    @commands.check(check_disabled)
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        return await ctx.send(f'{ member.display_name } has joined on { member.joined_at }')

    """ Check top server role of the user """
    @commands.command(
        aliases=['tr'],
        usage="(optional member)",
        description="Check top role of a member"
    )
    @commands.check(check_disabled)
    @commands.guild_only()
    async def toprole(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        
        return await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    """ Check all perms of mentioned user """
    @commands.command( 
        aliases=['perms_for', 'perms'],
        usage="(optional member)",
        description="Check all permissions of a member"
    )
    @commands.check(check_disabled)
    @commands.guild_only()
    async def permissions(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        
        # Find user permissions
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # Format results into discord embed
        embed = discord.Embed(title='Permisisons for:', description=ctx.guild.name, color=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        embed.add_field(name='\uFEFF', value=perms)

        return await ctx.send(content=None, embed=embed)

    """ Set A User's nickname """
    @commands.command(
        aliases=['nick'],
        usage="[nickname] (optional member)",
        description="Set a members nickname"
    )
    @commands.check(check_disabled)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, *nickname, member: discord.Member=None,):
        # Checking user permissions
        if member != ctx.author and member.top_role >= ctx.author.top_role:
            return await ctx.send(f'**`ERROR:`** You do not have high enough permissions to change { member.display_name }\'s role.')

        nickname = ' '.join(nickname)
        current_name = member.display_name

        # Change user's nickname
        try:
            # Attempt to set member's nickname
            await member.edit(nick=nickname)
        except Exception as e:
            # Handle errors if any
            return await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            return await ctx.send(f'**`SUCCESS: `** User { current_name }\'s nickname has been changed to { nickname }')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        return await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Members(bot))