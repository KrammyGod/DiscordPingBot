# -*- coding: utf-8 -*-
from discord.ext import commands, tasks
from discord.abc import Messageable
import discord
import random
import asyncio
from datetime import datetime
import sys
import traceback
# Custom image_utils file
from image_utils import *

# Global variables and setting up bot.
PREFIX = ["!!"]
# Set token here
TOKEN = ''
_intents = discord.Intents(messages=True, guilds=True)
_intents.members = True
_temp_member = 1
# Set help category
_HELP = commands.DefaultHelpCommand(no_category='Available Commands', commands_heading='')
client = commands.Bot(command_prefix=PREFIX, intents=_intents, help_command=_HELP)
COMMAND_LIST = ["help", "emoji", "daily", "roll", "prefix", "say", 
                "purge", "mute", "quit", "emojiid", "pfp",
                "modpfp", "modimg"]
# List of user ids that are developers of this bot
# List of int types
_ADMINS = []
# ID of #log channel
LOG_ID = 0


def _is_user(message):
    '''
    This function will check if the message author is the user indicated.
    '''
    global _temp_member
    if _temp_member == None:
        return True
    return message.author == _temp_member


# Function that returns id with given name
def _find_emoji(emoji_name):
    # Deny any emoji that is not surrounded by colons
    if not (emoji_name.startswith(':') and emoji_name.endswith(':')):
        return None
        
    emoji_name = emoji_name.replace(':', '')
    for emoji in client.emojis:
        if emoji_name.lower() == emoji.name.lower():
            ID = str(emoji.id)
            name = emoji.name
            if emoji.animated:
                return f'<a:{name}:{ID}>'
            else:
                return f'<:{name}:{ID}>'
    return None


# Function that can find user given name OR id
def _find_user(text, guild):
    # Deny any user without @ before it
    if not ('@' in text):
        return None
    
    text = text.replace('<', '')
    text = text.replace('@', '')
    text = text.replace('!', '')
    text = text.replace('>', '')
    # For getting with id
    try:
        text = int(text)
        text = guild.get_member(text) if guild else client.get_user(text)
        return text
    except ValueError:
        pass
    
    # For getting with name
    if guild:
        text = discord.utils.find(lambda m : ((text.lower() in m.display_name.lower()) or
                                              (text.lower() in m.name.lower())), guild.members)
    else:
        text = discord.utils.find(lambda m : (text.lower() in m.name.lower()), client.get_all_members())
    return text


# Function that can find channel given name OR id
def _find_channel(text):
    # Deny any channel without # in it
    if not ('#' in text):
        return None
    
    text = text.replace('<', '')
    text = text.replace('#', '')
    text = text.replace('!', '')
    text = text.replace('>', '')
    # Find channel with id
    try:
        text = client.get_channel(int(text))
        return text
    except ValueError:
        pass
    
    # Find channel with name
    text = discord.utils.get(client.get_all_channels(), name=text)
    return text


def _modify_img(org_img, width, height, m):
    # Convert to grayscale
    g_img = grayscale(org_img)

    # If the modification was wrong character
    e = False
    # Sharpen (Unmask)
    if m.upper().startswith('SU'):
        kernel = [[-1/256,-4/256,-6/256,-4/256,-1/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                  [-6/256,-24/256,476/256,-24/256,-6/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                  [-1/256,-4/256,-6/256,-4/256,-1/256]]
        g_img = modify(g_img, width, height, kernel)
    # Sharpen
    elif m.upper().startswith('S'):
        kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        g_img = modify(g_img, width, height, kernel)
    # Edgify alternative 1
    elif m.upper().startswith('E2'):
        kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        g_img = modify_colour(g_img, org_img, width, height, kernel)
    # Edgify default
    elif m.upper().startswith('E'):
        kernel = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
        g_img = modify_colour(g_img, org_img, width, height, kernel)
    # Cursed
    elif m.upper().startswith('C'):
        kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        g_img = modify(g_img, width, height, kernel)
    else:
        e = True

    return g_img, e


@client.command(brief='Mute/Unmutes a member.')
async def mute(ctx, user):
    '''
    Toggle's mute for a member.

    Usage: !!mute [user]
    
    Eg. !!mute @Krammy

    NOTE: <user> must be initiated with @
    '''
    channel = ctx.message.channel
    author = ctx.message.author
    guild = ctx.message.guild
    if guild is None:
        await ctx.send('This is not a server.')
        return
    if user is None:
        ctx.send(f'Hm. {author.mention} you didn\'t enter any user. How am I supposed to mute someone?')
    else:
        user = _find_user(user, ctx.message.guild)
        if user is None:
            await ctx.send(f'Hm. {author.mention} I cannot find the user specified. Please try again.')
            return
            
    # Only administrator can mute others
    if channel.permissions_for(author).administrator:
        # Find and create role if it doesn't exist already.
        role = discord.utils.get(guild.roles, name='Muted')
        if role is None:
            role = await guild.create_role(name='Muted', hoist=True)
            await channel.send('There is no such Muted role. Creating new role...', delete_after=3.0)
            text_channels = guild.text_channels
            # Revoke send messages permission for all channels 
            for i in text_channels:
                await i.set_permissions(role, send_messages=False)
            # Push role to highest position possible
            pos = 0
            for i in guild.roles:
                if i.name == "Useful Bot Pings":
                    break
                pos += 1
            await role.edit(position = pos)

        if not (role in user.roles):
            await user.add_roles(role)
            await channel.send(f'{author.mention} I have muted {user.mention} successfully.', delete_after=3.0)
        else:
            await user.remove_roles(role)
            await channel.send(f'{author.mention} I have unmuted {user.mention} successfully.', delete_after=3.0)
    else:
        await channel.send(f'Hm. {author.mention} you do not have permissions to do that.')


# Works for any emoji the bot can see
@client.command(brief="Use bot to display emoji.")
async def emoji(ctx, emoji_text, number=1):
    '''
    Makes the bot display an emoji for you. Enter the name of emoji only.

    Usage: !!emoji [emoji_name] <number> (number is optional and defaults to 1)
    
    Eg. !!emoji crytilldie, !!emoji wesmart 5
    '''
    author = ctx.message.author
    # Pad with colons to check emoji
    if not emoji_text.startswith(':'):
        emoji_text = ':' + emoji_text
    if not emoji_text.endswith(':'):
        emoji_text = emoji_text + ':'
        
    emoji = _find_emoji(emoji_text)
    if number < 1 or number > 10:
        await ctx.send(f'Hm. {author.mention} Please enter a valid integer. (No overflows)') 
    elif emoji:
        emoji *= number
        await ctx.send(emoji)
    else:
        await ctx.send(f'Hm. {author.mention} I couldn\'t find `{emoji_text}`.')


# Emoji ID for any emoji
@client.command(brief="Get the ID and name of any emoji.")
async def emojiid(ctx, emoji_text):
    '''
    Returns emoji ID and name of any emoji.

    Usage: !!emojiid [emoji_name]

    Eg. !!emojiid wesmart
    '''
    author = ctx.message.author
    # Pad with colons to check emoji
    if not emoji_text.startswith(':'):
        emoji_text = ':' + emoji_text
    if not emoji_text.endswith(':'):
        emoji_text = emoji_text + ':'
    
    emoji = _find_emoji(emoji_text)
    if emoji:
        emoji = emoji.replace('<', '')
        emoji = emoji.replace('>', '')
        emoji = emoji.split(':')
        await ctx.send(f'Emoji name: {emoji[-2]}, Emoji ID: {emoji[-1]}')
    else:
        await ctx.send(f'{author.mention} I couldn\'t find `{emoji_text}`.')
    

# Roll any sided dice command.
@client.command(brief="Roll a die.")
async def roll(ctx, number=6):
    '''
    Randomly rolls a die from 1 to <number>.

    Usage: !!roll <number> (number is optional and defaults to 6)

    Eg. !!roll, !!roll 10
    '''
    author = ctx.message.author
    dice = str(random.randint(1, number))
    await ctx.send(f'{author.mention}, you rolled a {dice}.')


# Check prefix of bot.
@client.command(brief='Find prefix of bot.')
async def prefix(ctx):
    '''
    Shows the current prefix of the bot.

    Usage: !!prefix
    '''
    author = ctx.message.author
    await ctx.send(f'{author.mention}, the prefix is !!')


# Random Ping
@client.command(brief='Random ping to revive ded chat.')
async def daily(ctx):
    '''
    Pings a random member in the guild, can only be used by specific users.
    <<RESTRICTED ACCESS FOR ADMINS OF BOT ONLY>>

    Usage: !!daily
    '''
    messages = []
    author = ctx.message.author
    userID = author.id
    guild = ctx.message.guild
    if guild is None:
        await ctx.send('This is not a server.')
        return
    # Only devs can use command
    if int(userID) in _ADMINS:
        members = list(guild.members)
        chosen = random.choice(members)
        while chosen.bot:
            chosen = random.choice(members)
        chosen = chosen.mention
        await ctx.send(f'{chosen} you were selected to revive a dead chat!')
    else:
        await ctx.send(f"{author.mention} you cannot use this command.\nOnly developers of the bot can use it.")
        

# Give someone's pfp
@client.command(brief='Get a user\'s pfp.')
async def pfp(ctx, user=None):
    '''
    Get the image of a user's pfp.

    Usage: !!pfp <user> (user is optional and defaults to yourself)

    Eg. !!pfp, !!pfp @Krammy

    NOTE: <user> must be initiated with @
    '''
    if user is None:
        user = ctx.message.author
    else:
        user = _find_user(user, ctx.message.guild)
        if user is None:
            await ctx.send('Hm. I cannot find the user specified. Please try again.')
            return

    pfp = user.avatar_url_as(static_format='png')
    pfp_name = 'pfp.' + str(pfp).split('?')[0].split('.')[-1]
    await pfp.save(pfp_name)
    
    await ctx.send(f'{user.display_name}\'s profile picture:', file=discord.File(pfp_name))


# Modify someone's pfp
@client.command(brief='Modify the image of someone\'s pfp.')
async def modpfp(ctx, *args):
    '''
    [G]rayscale, [S]harpen, [SU]Sharpen (Unmask), "[E]dgify", or "[C]ursify" someone's pfp to ruin their day. Leave empty for self grayscale.
    Protip: [E]dgify retains colour and sharpens edges. If [E] gives bad result, try [E2].

    Usage: !!modpfp <user> <modification> (user and modification are optional and defaults to self grayscale)

    Eg. !!modpfp, !!modpfp E, !!modpfp @Krammy E

    NOTES: Order of <user> and <modification> do NOT matter. <user> must be initiated with @
    '''
    if args:
        if '@' in args[0]:
            user = args[0]
            modification = args[1] if len(args) > 1 else None
        else:
            modification = args[0]
            user = args[1] if len(args) > 1 else None
    else:
        modification = None
        user = None

    if modification is None:
        await ctx.send('You did not input any modification. Defaulting to [G]rayscale...', delete_after=3.0)
        modification = 'G'
        
    if user is None:
        user = ctx.message.author
    else:
        user = _find_user(user, ctx.message.guild)
        if user is None:
            await ctx.send('Hm. I cannot find the user specified. Please try again.')
            return
    
    await ctx.send('Retrieving photo and editing...', delete_after=3.0)
    # Force png of pfp
    pfp = user.avatar_url_as(format='png', static_format='png')
    pfp_name = 'pfp.png'
    await pfp.save(pfp_name)
    img, width, height = convert_pixels(pfp_name)

    img, e = _modify_img(img, width, height, modification)
    
    if e:
        await ctx.send('Hm. That was a bad modification letter. Defaulting to [G]rayscale...', delete_after=3.0)

    save_image(img, width, height, filename=pfp_name)
    await asyncio.sleep(3)

    await ctx.send(f'Here is a modified verison of {user.display_name}\'s profile picture:', file=discord.File(pfp_name))


# Modify any image(s)
@client.command(brief='Modify any image.')
async def modimg(ctx, modification=None):
    '''
    [G]rayscale, [S]harpen, [SU]Sharpen (Unmask), "[E]dgify", or "[C]ursify" any image. Leave empty for self grayscale.
    Protip: [E]dgify retains colour and sharpens edges. If [E] gives bad result, try [E2].

    Usage: !!modimg <modification> (modification is optional and defaults to grayscale)

    Eg. !!modimg, !!modimg E
    '''
    imgs = ctx.message.attachments
    if not imgs:
        await ctx.send('I don\'t see any images, please use command again and attach some images.')
        return

    if modification is None:
        await ctx.send('You did not input any modification. Defaulting to [G]rayscale...', delete_after=3.0)
        modification = 'G'

    await ctx.send('Received image(s)! Modifying now (please be patient)...', delete_after=3.0)
    images = []
    too_large = False
    for img in imgs:
        await img.save(img.filename)
        new_img, width, height = convert_pixels(img.filename)
        # If image too large, do not modify it
        if new_img is None:
            too_large = True
            continue
        
        # Apply modifications
        new_img, e = _modify_img(new_img, width, height, modification)
        save_image(new_img, width, height, filename=img.filename)
        # Add to files to send
        images.append(discord.File(img.filename))
    if e:
        await ctx.send('Hm. That was a bad modification letter. Defaulting to [G]rayscale...', delete_after=3.0)
    if too_large:
        await ctx.send('Some or all of the image(s) is/are too large. They have not been modified.')
    await asyncio.sleep(3)
    if images:
        await ctx.send('Here is/are the modified image(s):', files=images)


# Making bot say message.
@client.command(brief='Don\'t bother, you can\'t use it.')
async def say(ctx, *args):
    '''
    Says a line for you. But you can't use it ;) First argument determines the channel to send to.
    The others tag the channel only if it exists in the guild.
    <<RESTRICTED ACCESS FOR ADMINS OF BOT ONLY>>

    Usage: !!say <channel> <emoji> <user> <message>

    Eg. !!say hi, !!say #general :crytilldie: @Krammy hi

    NOTES:
    - Channel must be initiated with #
    - Emoji must be surrounded with :
    - User must be initiated with @
    - Say cannot be empty
    '''
    author = ctx.message.author
    userID = author.id
    message = ''
    # Only devs can use this command
    if int(userID) in _ADMINS:
        if len(args) > 0:
            channel = _find_channel(args[0])
            guild = ctx.message.guild
            # Found a corresponding channel
            if channel:
                guild = channel.guild
            # No channel is found
            else:
                emoji = _find_emoji(args[0])
                user = _find_user(args[0], guild)
                if emoji:
                    message += emoji + ' '
                elif user:
                    message += user.mention + ' '
                else:
                    message += args[0] + ' '
                channel = ctx.message.channel
            # Remove first element from arguments
            args = args[1:] if len(args) > 1 else []
                
            # Do the same for all the other arguments
            for i in args:
                emoji = _find_emoji(i)
                user = _find_user(i, guild)
                tag_channel = _find_channel(i)
                if emoji:
                    message += emoji + ' '
                elif user:
                    message += user.mention + ' '
                # Only add the tag channel if its in the same guild
                elif tag_channel and (guild == tag_channel.guild):
                    message += tag_channel.mention + ' '
                else:
                    message += i + ' '
            await channel.send(message)
        else:
            await ctx.send('Hm. There is nothing to send.')
    else:
        channel = ctx.message.channel
        await channel.send(f"Sorry {author.mention}, you can\'t use that.")


# Purge command.
@client.command(brief="Clears Messages. Default is 100 (Admin Only)")
async def purge(ctx, amount=100, condition=None):
    '''
    Clears a specified number of messages (default is 100)
    <<RESTRICTED FOR USERS WITH MANAGE MESSAGE PERMISSIONS ONLY>>

    Usage: !!purge <amount> <from_user> (amount and from_user is optional, defaults to 100 and no user)

    Eg. !!purge, !!purge 10 @Krammy

    NOTES: <from_user> must be a valid user name
    '''
    global _temp_member
    channel = ctx.message.channel
    messages = []
    author = ctx.message.author
    userID = author.id
    guild = ctx.message.guild
    _temp_member = None
    if guild:
        _temp_member = discord.utils.get(guild.members, name=condition)
    else:
        await ctx.send('Not a discord server, cannot delete messages.')

    if int(userID) in _ADMINS or channel.permissions_for(ctx.message.author).manage_messages:
        if amount <= 0:
            await ctx.send(f"Hm. {author.mention} please enter an integer larger than 0.")
        else:
            await asyncio.sleep(1.0)
            deleted = await channel.purge(limit=amount, check=_is_user)
            await ctx.send(f'{author.mention} deleted {len(deleted)} message(s).', delete_after=3.0)
            _temp_member = 1
    else:
        await ctx.send(f'Hm. {author.mention}, you do not have permission to use this command.\nYou need the `manage messages` permission.')


# Quitting Bot
@client.command(brief='You can\'t use this.')
async def quit(ctx):
    '''
    Only the god can end the bot.
    <<RESTRICTED ACCESS FOR ADMINS OF BOT ONLY>>

    Usage: !!quit
    '''
    messages = []
    author = ctx.message.author
    userID = author.id
    # Makes sure only devs can use this command.
    if int(userID) in _ADMINS:
        await ctx.send(f"Roger that, {author.mention}!", delete_after=3.0)
        # Destroy task before shutting down
        _auto_collect.stop()
        # Mark bot as offline before disconnecting
        await client.change_presence(status=discord.Status.offline)
        # Stop "Event loop is closed" runtime error
        await asyncio.sleep(1)
        await client.close()
    else:
        await ctx.send(f'{author.mention}, you do not have permission to use this command.\nOnly developers may close the bot.', delete_after=5.0)


@client.event
async def on_message(message):
    a_command = False
    # Make sure bot isn't counting own messages
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX[0] + 'modpfp') or message.content.startswith(PREFIX[0] + 'pfp') or \
       message.content.startswith(PREFIX[0] + 'modimg') or message.content.startswith(PREFIX[0] + 'emojiid'):
        await client.process_commands(message)
        return
    # Making sure bot doesn't delete any messages except commands.
    if any((message.content.startswith(PREFIX[0] + i) or \
            message.content.startswith(PREFIX[1] + i) or \
            message.content.startswith(PREFIX[2] + i)) for i in COMMAND_LIST):
        await message.delete(delay=0.5)
        await client.process_commands(message)
        return
            
    #Custom bot replies.
    


@client.event
async def on_message_delete(message):
    if not message.author.bot:
        if not message.content.startswith(PREFIX[0]) and \
           not message.content.startswith(PREFIX[1]) and \
           not message.content.startswith(PREFIX[2]):
            sent_message = str(message.clean_content).replace('`', '')
            # Logs channel
            channel = client.get_channel(LOG_ID)
            if message.content == '':
                sent_message = message.content

            print(message.author, "deleted a message in #", \
                  message.channel, "in", message.guild, "on", \
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ",")
            print(sent_message)

            sent_message = '```'+sent_message+'```' if sent_message else sent_message
            await channel.send(f'{message.author} deleted a message in #{message.channel} in {message.guild}:\n{sent_message}')
            if message.attachments:
                files = []
                for attachment in message.attachments:
                    await attachment.save(attachment.filename, use_cached=True)
                    files.append(discord.File(attachment.filename))
                if files:
                    await channel.send(files=files)
                else:
                    await channel.send('Uncached File')
            await channel.send('---------------------------------')


# Errors
@client.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
          
    error = getattr(error, 'original', error)
    
    if isinstance(error, commands.BadArgument):
        member = ctx.message.author
        await ctx.send(f'Hm. Seems like !!{str(ctx.command)} has a wrong argument, please check the required arguments and try again.')
        return
      
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Hm. Seems like !!{str(ctx.command)} is missing a parameter. Try !!help {str(ctx.command)} and try again!.')
        return
    
    # All other Errors not returned come here... And we can just print the default TraceBack.
    print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# Shows that bot is ready for use.
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


loop = asyncio.get_event_loop()
try:
    # Start the bot
    loop.run_until_complete(client.start(TOKEN))
except:
    # Mark bot as offline before disconnecting
    loop.run_until_complete(client.change_presence(status=discord.Status.offline))
    loop.run_until_complete(client.close())
    # Stop "Event loop is closed" runtime error
    loop.run_until_complete(asyncio.sleep(1))
finally:
    loop.close()
