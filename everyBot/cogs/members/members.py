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

class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """ Register new member into the database """
    @commands.command()
    @commands.guild_only()
    async def register(self, ctx):
        await database.register_member(ctx.author, ctx)

    """ Display profile """
    @commands.command()
    async def profile(self, ctx):
        member = await database.fetch_member(ctx.author)
        fetch_warnings = await database.fetch_member_warnings(ctx.author.id, True)
        warnings_list = await fetch_warnings.to_list(length=None)

        warnings = []
        for i, warning in enumerate(warnings_list):
            warnings.append(f"{ i+1 }: { warning.reason }")

        warnings_string = "\n" + "\n".join(warnings)
        print(warnings_string)

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

    @commands.command()
    @commands.guild_only()
    async def removeMember(self, ctx, member: discord.Member):
        await database.remove_member(member)
        # return await ctx.send(response)

    """ Check when the mentioned user joined the server """
    @commands.command()
    @commands.check(check_disabled)
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        await ctx.send(f'{ member.display_name } has joined on { member.joined_at }')

    """ Check top server role of the user """
    @commands.command(name='top_role', aliases=['toprole'])
    @commands.check(check_disabled)
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        
        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    """ Check all perms of mentioned user """
    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.check(check_disabled)
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        
        # Find user permissions
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # Format results into discord embed
        embed = discord.Embed(title='Permisisons for:', description=ctx.guild.name, color=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)

    """ Set A User's nickname """
    @commands.command(aliases=['nick'])
    @commands.check(check_disabled)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member=None, *nickname):
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
            await ctx.send(f'**`ERROR:`** { type(e).__name__ } - { e }')
        else:
            await ctx.send(f'**`SUCCESS: `** User { current_name }\'s nickname has been changed to { nickname }')

    """ Error Check """
    async def cog_command_error(self, ctx, error):
        # Handling any errors within commands
        await ctx.send(f'Error in { ctx.command.qualified_name }: { error }')

def setup(bot):
    bot.add_cog(Members(bot))