# -*- coding: utf-8 -*-
# Work with Python 3.6
from discord.ext import commands
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
TOKEN = ''
intents = discord.Intents(messages=True, guilds=True)
intents.members = True
member_check = 1
client = commands.Bot(command_prefix=PREFIX, intents=intents)
command_list = ["help", "emoji", "daily", "roll", "prefix", "say", "purge", "mute", 
                "quit", "emojiid", "pfp", "modpfp", "modimg"]
# List of user ids that are developers of this bot
# List of int types
userIDs = []

# Function that returns id with given name
def emojiID(emoji_name):
    for emoji in client.emojis:
        if emoji_name.lower() == emoji.name.lower():
            ID = str(emoji.id)
            name = emoji.name
            if emoji.animated:
                return f'<a:{name}:{ID}>'
            else:
                return f'<:{name}:{ID}>'
    return None


@client.command(description="Toggle's mute for a member.",
                brief='Mute/Unmutes a member.')
async def mute(ctx, member):
    channel = ctx.message.channel
    author = ctx.message.author
    guild = ctx.message.guild
    member = member.replace('<@', '')
    member = member.replace('!', '')
    member = member.replace('>', '')
    try:
        member = int(member)
    except ValueError:
        await ctx.send('Error, I cannot find the user specificed. Please try again.', delete_after=3.0)
        return
    member = guild.get_member(member)
    if member is None:
        await ctx.send('Error, I cannot find the user specificed. Please try again.', delete_after=3.0)
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
      
        if not (role in member.roles):
            await member.add_roles(role)
            await channel.send(f'{author.mention} I have muted {member.mention} successfully.', delete_after=3.0)
        else:
            await member.remove_roles(role)
            await channel.send(f'{author.mention} I have unmuted {member.mention} successfully.', delete_after=3.0)
    else:
        await channel.send(f'{author.mention} Error, you do not have permissions to do that.', delete_after=3.0)


# Works for any emoji the bot can see
@client.command(description='Makes the bot display an emoji for you. Enter the name of emoji only.',
                brief="Use bot to display emoji.")
async def emoji(ctx, emoji_text, number=1):
    author = ctx.message.author
    emoji = emojiID(emoji_text)
    if number < 1 or number > 10:
        await ctx.send(f'{author.mention} Please enter a valid integer. (No overflows)', delete_after=3.0) 
    elif emoji:
        emoji *= number
        await ctx.send(emoji)
    else:
        await ctx.send(f'{author.mention} I couldn\'t find `{emoji_text}`.', delete_after=3.0)


# Emoji ID for any emoji
@client.command(description="Returns emoji ID and name of any emoji.",
                brief="Get the ID and name of any emoji.")
async def emojiid(ctx, emoji_text):
    author = ctx.message.author
    emoji = emojiID(emoji_text)
    if emoji:
        emoji = emoji.replace('<', '')
        emoji = emoji.replace('>', '')
        emoji = emoji.split(':')
        await ctx.send(f'Emoji name: {emoji[-2]}, Emoji ID: {emoji[-1]}')
    else:
        await ctx.send(f'{author.mention} I couldn\'t find `{emoji_text}`.', delete_after=3.0)
    

# Roll any sided dice command.
@client.command(description="Randomly gives you a positive integer from 1 to whatever you want.",
                brief="Test your RNG luck. It takes one parameter.")
async def roll(ctx, number=6):
    author = ctx.message.author
    dice = str(random.randint(1, number))
    await ctx.send(f'{author.mention}, you rolled a {dice}.')


# Check prefix of bot.
@client.command(description="Shows the current prefix of the bot.",
                brief='Find prefix of bot.')
async def prefix(ctx):
    author = ctx.message.author
    await ctx.send(f'{author.mention}, the prefix is !!')


# Random Ping
@client.command(description="Pings a random member in the guild, can only be used by specific users.",
                brief='Random ping to revive ded chat.')
async def daily(ctx):
    messages = []
    author = ctx.message.author
    userID = author.id
    # Only devs can use command
    if int(userID) in userIDs:
        members = list(ctx.message.guild.members)
        chosen = random.choice(members)
        while chosen.bot:
            chosen = random.choice(members)
        chosen = chosen.mention
        await ctx.send(f'{chosen} you were selected to revive a dead chat!')
    else:
        await ctx.send(f"{author.mention} you cannot use this command. Only developers of the bot can use it.", delete_after=3.0)
        

# Give someone's pfp
@client.command(description='Get the image of a user\'s pfp.',
                brief='Get a user\'s pfp.')
async def pfp(ctx, member=None):
    guild = ctx.message.guild
    if member is None:
        member = ctx.message.author.mention
    member = member.replace('<@', '')
    member = member.replace('!', '')
    member = member.replace('>', '')
    try:
        member = int(member)
    except ValueError:
        await ctx.send('Error, I cannot find the user specified. Please try again.', delete_after=3.0)
        return
    member = guild.get_member(member)
    if member is None:
        await ctx.send('Error, I cannot find the user specified. Please try again.', delete_after=3.0)
        return

    pfp = member.avatar_url_as(static_format='png')
    pfp_name = 'pfp.' + str(pfp).split('?')[0].split('.')[-1]
    await pfp.save(pfp_name)
    name = member.nick
    if name is None:
        name = member.name
    await ctx.send(f'{name}\'s profile picture:', file=discord.File(pfp_name))


# Modify someone's pfp
@client.command(description='[G]rayscale, [S]harpen, [SU]Sharpen (Unmask), or "[E]dgify" someone\'s pfp to ruin their day. Leave empty for self grayscale. \
                             Eg. !!modpfp @KrammyGod S\nProtip: [E]dgify retains colour and sharpens edges.',
                brief='Modify the image of someone\'s pfp.')
async def modpfp(ctx, *args):
    guild = ctx.message.guild
    # Allow modification/ping in any order
    if args:
        if '@' in args[0]:
            member = args[0]
            modification = args[1] if len(args) > 1 else None
        else:
            modification = args[0]
            member = args[1] if len(args) > 1 else None
    else:
        modification = None
        member = None

    if modification is None:
        modification = 'G'
    if member is None:
        member = ctx.message.author.mention
    member = member.replace('<@', '')
    member = member.replace('!', '')
    member = member.replace('>', '')
    try:
        member = int(member)
    except ValueError:
        await ctx.send('Error, I cannot find the user specified. Please try again.', delete_after=3.0)
        return

    member = guild.get_member(member)
    if member is None:
        await ctx.send('Error, I cannot find the user specified. Please try again.', delete_after=3.0)
        return
    
    await ctx.send('Retrieving photo and editing...', delete_after=3.0)
    # Force png of pfp
    pfp = member.avatar_url_as(format='png', static_format='png')
    pfp_name = 'pfp.png'
    await pfp.save(pfp_name)
    img, width, height = convert_pixels(pfp_name)
    g_img = grayscale(img)
    
    # Sharpen (Unmask)
    if modification.upper().startswith('SU'):
        kernel = [[-1/256,-4/256,-6/256,-4/256,-1/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                  [-6/256,-24/256,476/256,-24/256,-6/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                  [-1/256,-4/256,-6/256,-4/256,-1/256]]
        g_img = modify(g_img, width, height, kernel)
    # Sharpen
    elif modification.upper().startswith('S'):
        kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        g_img = modify(g_img, width, height, kernel)
    # Edgify
    elif modification.upper().startswith('E'):
        # Also a nice kernel, but second one is better
        # kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        kernel = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
        g_img = modify_colour(g_img, img, width, height, kernel)
    # Not grayscale
    elif not (modification.upper().startswith('G')):
        await ctx.send('Error, bad modification value, defaulting to [G]rayscale...', delete_after=3.0)

    img = g_img
    save_image(img, width, height, filename=pfp_name)
    await asyncio.sleep(3)

    name = member.nick
    if name is None:
        name = member.name
    await ctx.send(f'Here is a modified verison of {name}\'s profile picture:', file=discord.File(pfp_name))


# Modify any image(s)
@client.command(description='[G]rayscale, [S]harpen, [SU]Sharpen (Unmask), or "[E]dgify" a picture to ruin someone\'s day. Leave [modification] empty for grayscale.\
                             \nProtip: [E]dgify retains colour and sharpens edges.',
                brief='Modify any image.')
async def modimg(ctx, modification=None):
    if modification is None:
        modification = 'G'
    imgs = ctx.message.attachments
    if not imgs:
        await ctx.send('I don\'t see any images, please use command again and attach some images.')
        return
    if (not (modification.upper().startswith('G')) and (not (modification.upper().startswith('S')) and (not (modification.upper().startswith('E'))))):
        await ctx.send('Bad modification letter. Please use command again.')
        return

    await ctx.send('Received image(s)! Modifying now...', delete_after=3.0)
    images = []
    for img in imgs:
        await img.save(img.filename)
        new_img, width, height = convert_pixels(img.filename)
        g_img = grayscale(new_img)

        # Sharpen (Unmask)
        if modification.upper().startswith('SU'):
            kernel = [[-1/256,-4/256,-6/256,-4/256,-1/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                      [-6/256,-24/256,476/256,-24/256,-6/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                      [-1/256,-4/256,-6/256,-4/256,-1/256]]
            g_img = modify(g_img, width, height, kernel)
        # Sharpen
        elif modification.upper().startswith('S'):
            kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
            g_img = modify(g_img, width, height, kernel)
        # Edgify
        elif modification.upper().startswith('E'):
            # Also a nice kernel, but second one is better
            # kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
            kernel = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
            g_img = modify_colour(g_img, new_img, width, height, kernel)
        
        # Apply modifications
        new_img = g_img
        save_image(new_img, width, height, filename=img.filename)
        # Add to files to send
        images.append(discord.File(img.filename))

    await asyncio.sleep(3)
    await ctx.send('Here is/are the modified image(s):', files=images)


# Making bot say message.
@client.command(description='Says a line for you. But you can\'t use it ;)',
                brief='Don\'t bother, you can\'t use it.')
async def say(ctx, channel, *args):
    author = ctx.message.author
    userID = author.id
    message = ''
    # Tag a channel
    if '#' in channel:
        channel = channel.replace('<#', '')
        channel = channel.replace('>', '')
        try:
            channel = client.get_channel(int(channel))
        except ValueError:
            pass
    # Only devs can use this command
    if int(userID) in userIDs:
        channel = str(channel)
        # Edge case where they attempt to tag a channel but tagging failed
        channel = channel.replace('#', '')
        channel_temp = discord.utils.get(client.get_all_channels(), name=channel)
        if channel_temp == None:
            emoji = emojiID(channel)
            if emoji:
                channel = emoji

            if '@' in channel:
                channel = channel.replace('@', '')
                member_temp = discord.utils.find(lambda m : ((channel.lower() in m.name.lower()) or 
                                            (channel.lower() in m.display_name.lower())), 
                                            client.get_all_members())
                if member_temp:
                    channel = member_temp.mention

            message += channel+' '
            channel = ctx.message.channel
        else:
            channel = channel_temp
        for arg in args:
            emoji = emojiID(arg)
            if emoji:
                arg = emoji
            if '@' in arg:
                arg = arg.replace('@', '')
                member_temp = discord.utils.find(lambda m : ((arg.lower() in m.name.lower()) or 
                                            (arg.lower() in m.display_name.lower())), 
                                            client.get_all_members())
                if member_temp:
                    arg = member_temp.mention
                    
            message += arg+' '
            
        await channel.send(message)
    else:
        channel = ctx.message.channel
        await channel.send(f"Sorry {author.mention}, you can\'t use that right now. Only developers can use this command.", delete_after=3.0)


def is_user(message):
    '''
    This function will check if the message author is the user indicated.
    '''
    global member_check
    if member_check == None:
        return True
    return message.author == member_check


# Purge command. channel.send isn't working rn for some reason.
@client.command(description="Clears a specified number of messages (default is 100)",
                brief="Clears Messages. Default is 100 (Admin Only)")
async def purge(ctx, amount=100, user=None):
    global member_check
    channel = ctx.message.channel
    messages = []
    author = ctx.message.author
    userID = author.id
    member_check = discord.utils.get(ctx.message.guild.members, name=user)
    # Only developers and manage message permissions can use this command
    if int(userID) in userIDs or channel.permissions_for(ctx.message.author).manage_messages:
        if amount <= 0:
            await ctx.send(f"Error. {author.mention}. Please enter an integer larger than 0.", delete_after=3.0)
        else:
            await asyncio.sleep(1.0)
            deleted = await channel.purge(limit=amount, check=is_user)
            await ctx.send(f'{author.mention} deleted {len(deleted)} message(s).', delete_after=3.0)
            member_check = 1
    else:
        await ctx.send(f'{author.mention}, you do not have permission to use this command.\nYou need the manage messages permission.', delete_after=3.0)


# Quitting Bot
@client.command(description="Only the god can end the bot.",
                brief='You can\'t use this.')
async def quit(ctx):
    messages = []
    author = ctx.message.author
    userID = author.id
    # Makes sure only developers can use this command
    if int(userID) in userIDs:
        await ctx.send(f"Okay {author.mention}, I'm quitting!", delete_after=3.0)
        await client.logout()
    else:
        await ctx.send(f'{author.mention}, you do not have permission to use this command. Only developers may close the bot.', delete_after=3.0)


@client.event
async def on_message(message):
    a_command = False
    # Make sure bot isn't counting own messages
    if message.author == client.user:
        return
  
    # Don't delete commands for modifying or grabbing images
    if message.content.startswith(PREFIX[0] + 'modpfp') or message.content.startswith(PREFIX[0] + 'pfp') or \
       message.content.startswith(PREFIX[0] + 'modimg'):
        await client.process_commands(message)
        return
    # Making sure bot doesn't delete any messages except commands.
    if any((message.content.startswith(PREFIX[0] + i) or \
            message.content.startswith(PREFIX[1] + i) or \
            message.content.startswith(PREFIX[2] + i)) for i in command_list):
        await message.delete(delay=0.5)
        await client.process_commands(message)
        return
            
    #Custom bot replies. Add your own here!


@client.event
async def on_message_delete(message):
    # Track and output deleted messages and images.
    if not message.author.bot:
        if not message.content.startswith(PREFIX[0]) and \
            not message.content.startswith(PREFIX[1]) and \
            not message.content.startswith(PREFIX[2]):
            sent_message = str(message.clean_content).replace('`', '')
            # Enter id (int) of logs channel in <id>
            #channel = client.get_channel(<id>)
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
        await ctx.message.channel.send(f'Error in command !!{str(ctx.command)}, {member.mention} please check the required arguments and try again.', delete_after=3.0)
        return
      
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.channel.send(f'Hm. Seems like !!{str(ctx.command)} is missing a parameter. Try !!help {str(ctx.command)} and try again!.', delete_after=3.0)
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
    
client.run(TOKEN)
