import discord
import random
from discord.ext import commands
from modules.converters import *
from modules.settings import CONFIG

# Function to check if the user is bot owner
def check_owner(ctx):
    '''
    This function checks if the user has the id of the bot owner.
    '''
    return ctx.author.id == CONFIG.ADMINS


class ModCommands(commands.Cog, name='Mod Commands'):
    '''
    This category contains all the commands for server moderators only.
    '''
    def __init__(self, bot, **options):
        super().__init__(**options)
        self.bot = bot


    # Mute command
    @commands.command(brief='Mute/Unmutes a member.')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user):
        '''
        Toggle's mute for a member.
        __**<<RESTRICTED FOR USERS WITH MANAGE ROLES PERMISSIONS ONLY>>**__

        Usage: !!mute [user]
        
        Eg. !!mute @Krammy

        NOTE: <user> must be initiated with @
        '''
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        await ctx.message.delete()

        if guild is None:
            await ctx.send('This is not a server.')
            return
        if user is None:
            ctx.send(f'Hm. {author.mention} you didn\'t enter any user. How am I supposed to mute someone?')
        else:
            user = convert_user(self.bot, user, guild)
            if user is None:
                await ctx.send(f'Hm. {author.mention} I cannot find the user specified. Please try again.')
                return

        # Find and create role if it doesn't exist already.
        role = discord.utils.get(guild.roles, name='Muted')
        if role is None:
            role = await guild.create_role(name='Muted', hoist=True)
            await ctx.send('There is no such Muted role. Creating new role...', delete_after=3.0)
            text_channels = guild.text_channels
            # Revoke send messages permission for all channels 
            for i in text_channels:
                await i.set_permissions(role, send_messages=False)
            # Push role to highest position possible
            pos = 0
            for i in guild.roles:
                # Finding own role name
                if i.name == self.bot.name:
                    break
                pos += 1
            await role.edit(position = pos)
    
        if not (role in user.roles):
            try:
                await user.add_roles(role)
                await ctx.send(f'{author.mention} I have muted {user.mention} successfully.', delete_after=3.0)
            except discord.errors.Forbidden:
                await ctx.send(f'{author.mention} I don\'t have permissions to mute them, please move my role above the "Muted" role.')
        else:
            await user.remove_roles(role)
            await ctx.send(f'{author.mention} I have unmuted {user.mention} successfully.', delete_after=3.0)


    # Random Ping
    @commands.command(brief='Random ping to revive ded chat. (Owner only)')
    @commands.check(commands.is_owner())
    async def revive(self, ctx):
        '''
        Pings a random member in the guild, can only be used by specific users.
        __**<<RESTRICTED ACCESS FOR OWNERS OF SERVER ONLY>>**__

        Usage: !!revive
        '''
        messages = []
        author = ctx.author
        userID = author.id
        guild = ctx.guild
        await ctx.message.delete()

        if guild is None:
            await ctx.send('This is not a server.')
            return

        members = list(guild.members)
        chosen = random.choice(members)
        while chosen.bot:
            chosen = random.choice(members)
        await ctx.send(f'{chosen.mention} you were selected to revive a dead chat!')


    # Making bot say message.
    @commands.command(brief='Make the bot say anything. (Owner only)')
    @commands.check(check_owner)
    async def say(self, ctx, *args):
        '''
        Says a line for you. First argument determines the channel to send to.
        The others tag the channel only if it exists in the guild.
        __**<<RESTRICTED ACCESS FOR ADMINS OF BOT ONLY>>**__

        Usage: !!say <channel> <emoji> <user> <message>

        Eg. !!say hi, !!say #general :crytilldie: @Krammy hi

        NOTES:
        - Channel must be initiated with #
        - Emoji must be surrounded with :
        - User must be initiated with @
        - Say cannot be empty
        '''
        author = ctx.author
        userID = author.id
        guild = ctx.guild
        message = ''
        await ctx.message.delete()
        
        if len(args) > 0:
            temp = args[0]
            if not temp.startswith('#'):
                temp = f'#{temp}'
            channel = convert_channel(self.bot, temp)
            # Found a corresponding channel
            if channel:
                guild = channel.guild
            # No channel is found
            else:
                emoji = convert_emoji(self.bot, args[0])
                user = convert_user(self.bot, args[0], guild)
                if emoji:
                    message += emoji + ' '
                elif user:
                    message += user.mention + ' '
                else:
                    message += args[0] + ' '
                channel = ctx.message.channel
            # Remove first element from arguments
            args = args[1:]
                
            # Do the same for all the other arguments
            for i in args:
                emoji = convert_emoji(self.bot, i)
                user = convert_user(self.bot, i, guild)
                tag_channel = convert_channel(self.bot, i)
                if emoji:
                    message += emoji + ' '
                elif user:
                    message += user.mention + ' '
                # Only add the tag channel if its in the same guild
                elif tag_channel and (guild == tag_channel.guild):
                    message += tag_channel.mention + ' '
                else:
                    message += i + ' '

            # Leftover special cases
            message = message.replace('@cherry', '<@306066993855987723>')
            message = message.replace('@charl', '<@382071744120225793>')
            message = message.replace('@mara', '<@282543246243266560>')
            message = message.replace('@miah', '<@303331822572666880>')
            message = message.replace('@nep', '<@163493698443804672>')
            message = message.replace('@julia', '<@163493698443804672>')
            message = message.replace('@duch', '<@216598875819999233>')
            message = message.replace('@cookie', '<@394597308702130178>')
            message = message.replace('@jipp', '<@456784879007563776>')
            message = message.replace('@jill', '<@456784879007563776>')
            await channel.send(message)
        else:
            await ctx.send('Hm. There is nothing to send.')


    # Purge command.
    @commands.command(brief="Clears Messages. Default is 100.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=None):
        '''
        Clears a specified number of messages (default is 100)
        __**<<RESTRICTED FOR USERS WITH MANAGE MESSAGE PERMISSIONS ONLY>>**__

        Usage: !!purge <amount> (from_user is optional, defaults to 100)

        Eg. !!purge, !!purge 10
        '''
        messages = []
        channel = ctx.channel
        author = ctx.author
        userID = author.id
        guild = ctx.guild
        await ctx.message.delete()
        
        if amount is None:
            amount = 100
        try:
            amount = int(amount)
        except ValueError:
            raise(commands.BadArgument)

        if not guild:
            await ctx.send('Not a discord server, cannot delete messages.')
            return

        if amount <= 0:
            raise(commands.BadArgument)

        deleted = await channel.purge(limit=amount)
        await ctx.send(f'{author.mention} deleted {len(deleted)} message(s).', delete_after=3.0)
