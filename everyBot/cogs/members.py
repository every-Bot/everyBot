import discord
from discord.ext import commands

class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """ Check when the mentioned user joined the server """
    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        await ctx.send(f'{ member.display_name } has joined on { member.joined_at }')

    """ Check top server role of the user """
    @commands.command(name='top_role', aliases=['toprole'])
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member=None):
        # If no member is mentioned, assume author
        if member is None:
            member = ctx.author
        
        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    """ Check all perms of mentioned user """
    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
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