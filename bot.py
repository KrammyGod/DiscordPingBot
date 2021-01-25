# -*- coding: utf-8 -*-
# Work with Python 3.6
from discord.ext import commands
from discord.abc import Messageable
import discord
import random
import asyncio
from datetime import datetime
from PIL import Image
import sys
import traceback
import requests

# Global variables and setting up bot.
PREFIX = ["!!", "<@498219323337474049> ", "<@!498219323337474049> "]
TOKEN = 'omitted'
intents = discord.Intents(messages=True, guilds=True)
intents.members = True
userID = "0"
member_check = 1
client = commands.Bot(command_prefix=PREFIX, intents=intents)
command_list = ["help", "emoji", "daily", "roll", "prefix", 
                "say", "purge", "mute", "quit", "emojiid"]
userIDs = ['omitted']

#Function that returns id with given name
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
    member = member.replace('<@!', '')
    member = member.replace('>', '')
    member = int(member)
    member = guild.get_member(member)
    role = discord.utils.get(guild.roles, name='Muted')
    if role is None:
        role = await guild.create_role(name='Muted', hoist=True)
        await channel.send('There is no such Muted role. Creating new role...', delete_after=3.0)
        await guild.edit_role_positions({role: 22})
    if channel.permissions_for(author).administrator:
        if member.guild_permissions.text():
            await member.add_roles(role)
            await channel.send(f'<@{userID}> I have muted <@{member.id}> successfully.', delete_after=3.0)
        else:
            await member.remove_roles(role)
            await channel.send(f'<@{userID}> I have unmuted <@{member.id}> successfully.', delete_after=3.0)
    else:
        await channel.send(f'<@{userID}> Error, you do not have permissions to do that.', delete_after=3.0)

# Works for any emoji now
@client.command(description='Makes the bot display an emoji for you. Enter the name of emoji only.',
                brief="Use bot to display emoji.")
async def emoji(ctx, emoji_text, number=1):
    emoji = emojiID(emoji_text)
    if number < 1 or number > 10:
        await ctx.send(f'<@{userID}> Please enter a valid integer. (No overflows)', delete_after=3.0) 
        return
    if emoji:
        emoji*=number
        await ctx.send(emoji)
        return
    await ctx.send(f'<@{userID}> I couldn\'t find `{emoji_text}`.', delete_after=3.0)

# Emoji ID for any emoji
@client.command(description="Returns emoji ID and name of any emoji.",
                brief="Get the ID and name of any emoji.")
async def emojiid(ctx, emoji_text:emojiID):
    if emoji_text:
        emoji_text = emoji_text.replace('<', '')
        emoji_text = emoji_text.replace('>', '')
        emoji_text = emoji_text.split(':')
        await ctx.send(f'Emoji name: {emoji_text[len(emoji_text)-2]}, Emoji ID: {emoji_text[len(emoji_text)-1]}')
    else:
        await ctx.send(f'<@{userID}> I couldn\'t find `{emoji_text}`.', delete_after=3.0)
    
# Roll any sided dice command.
@client.command(description="Randomly gives you a positive integer from 1 to whatever you want.",
                brief="Test your RNG luck. It takes one parameter.")
async def roll(ctx, number=6):
    dice = str(random.randint(1, number))
    await ctx.send(f'<@{userID}>, you rolled a ' + dice)

# Check prefix of bot.
@client.command(description="Shows the current prefix of the bot.",
                brief='Find prefix of bot.')
async def prefix(ctx):
    await ctx.send(f'<@{userID}>, the prefix is !!')
        
# Making bot say message. continue later....
@client.command(description='Says a line for you. But you can\'t use it ;)',
                brief='Don\'t bother, you can\'t use it.')
async def say(ctx, channel, *args):
    global userIDs
    message = ''
    if '#' in channel:
        channel = channel.replace('<#', '')
        channel = channel.replace('>', '')
        channel = client.get_channel(channel)
        await ctx.send(channel)
    if int(userID) in userIDs:
        channel = str(channel)
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
        await Messageable.send(channel, message)
    else:
        channel = ctx.message.channel
        await channel.send(f"Sorry <@{userID}>, you can\'t use that right now. :(", delete_after=3.0)

def is_user(message):
    '''
    This function will check if the message author is the user indicated.
    '''
    global member_check
    if member_check == None:
        return True
    return message.author == member_check


# Purge command.
@client.command(description="Clears a specified number of messages (default is 100)",
                brief="Clears Messages. Default is 100 (Admin Only)")
async def purge(ctx, amount=100, condition=None):
    channel = ctx.message.channel
    messages = []
    global member_check
    member_check = discord.utils.get(ctx.message.guild.members, name=condition)
    if channel.permissions_for(ctx.message.author).manage_messages:
        if amount <= 0:
            await channel.send(f"Error. <@{userID}>. Please enter an integer larger than 0.", delete_after=3.0)
        else:
            await asyncio.sleep(1.0)
            deleted = await channel.purge(limit=amount, check=is_user)
            await channel.send(f'<@{userID}> deleted {len(deleted)} message(s).', delete_after=3.0)
    else:
        await channel.send(f'<@{userID}>, you do not have permission to use this command.\nYou need the manage messages permission.', delete_after=3.0)


@client.command(description="Only the god can end the bot.",
                brief='You can\'t use this.')
async def quit(ctx):
    messages = []
    # Makes sure only owner can use this command.
    if int(userID) == omitted:
        await ctx.send("Okay <@omitted>, I'm restarting!", delete_after=3.0)
        await client.logout()
    else:
        await ctx.send(f'<@{userID}>, you do not have permission to use this command.\nOnly person who can use it: omitted', delete_after=3.0)

# Fixing this later, very inefficient.
@client.event
async def on_message(message):
    global userID
    a_command = False
    # Make sure bot isn't counting own messages
    if not message.author == client.user:
        # Very inefficient. Making sure bot doesn't delete any messages except commands.
        for i in command_list:
            command1 = PREFIX[0] + i
            command2 = PREFIX[1] + i
            command3 = PREFIX[2] + i
            if (message.content.startswith(command1)) or \
                (message.content.startswith(command2)) or \
                (message.content.startswith(command3)):
                a_command = True
                break
                
    if a_command:
        # userID helps mention the person who typed command.
        userID = str(message.author.id)
        await message.delete(delay=0.5)
        await client.process_commands(message)
        return
            
    #Custom bot replies.
    # Welcoming bot
    if 'welcome' in message.content.lower() and client.user in message.mentions:
        if int(message.author.id) == omitted:
            await Messageable.send(message.channel, "Hi there <@omitted>!!! <a:yayyyyy:528042979563274240>")
        else:
            await Messageable.send(message.channel, f"Thank you, <@{message.author.id}>! <a:wow:530244108736790528>")
    # For chatting with bot
    elif client.user in message.mentions and not message.author == client.user:
        if int(message.author.id) == omitted:
            await Messageable.send(message.channel, '<@omitted> <a:yayyyyy:528042979563274240>')
            return
        await Messageable.send(message.channel, f'<@{message.author.id}> I\'m sorry, who\'re you? <:christ:531286899881672704>')
    # Revenge ping
    if 'omitted' in message.content and not message.author == client.user:
        if int(message.author.id) in userIDs:
            await Messageable.send(message.channel, f'Placeholder')
        else:
            await Messageable.send(message.channel, f'Wat u want <@{message.author.id}>? <:christ:531286899881672704>')
    # Use emoji when owner says woaw
    if message.author.id == omitted:
        if message.content.lower() == "woaw":
            message_send = emojiID("pikasparkle")
            message_send *= 5
            await Messageable.send(message.channel, message_send)

@client.event
async def on_message_delete(message):
    if not message.author.bot:
        # Record deleted messages
        if not message.content.startswith(PREFIX[0]) and \
            not message.content.startswith(PREFIX[1]) and \
            not message.content.startswith(PREFIX[2]):
            sent_message = str(message.clean_content).replace('`', '')
            channel = client.get_channel(omitted)
            if message.content == '':
                sent_message = message.content
            print(message.author, "deleted a message in #", \
                  message.channel, "in", message.guild, "on", \
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ",")
            print(sent_message)
            sent_message = '```'+sent_message+'```' if sent_message
            await Messageable.send(channel, f'{message.author} deleted a message in #{message.channel} in {message.guild}:\n{sent_message}')
            # If message contains a picture, save it and send it
            if message.attachments:
                files = []
                for attachment in message.attachments:
                    await attachment.save(attachment.filename, use_cached=True)
                    files.append(discord.File(attachment.filename))
                if len(files) == 1:
                    await Messageable.send(channel, file=files[0])
                elif len(files) > 1:
                    await Messageable.send(channel, files=files)
                else:
                    await Messageable.send(channel, 'Uncached File')
            await Messageable.send(channel, '---------------------------------')

# Errors
@client.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
          
    error = getattr(error, 'original', error)
    
    if isinstance(error, commands.BadArgument):
        await Messageable.send(ctx.message.channel, 'Error in command !!'+str(ctx.command)+', <@'+userID+'> please check the required arguments and try again.', delete_after=3.0)
        return
      
    if isinstance(error, commands.MissingRequiredArgument):
        await Messageable.send(ctx.message.channel, 'Hm. Seems like !!'+str(ctx.command)+' is missing a parameter. Try !!help '+str(ctx.command)+' and try again!.', delete_after=3.0)
        return
    
    # All other Errors not returned come here... And we can just print the default TraceBack.
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# Shows that bot is ready for use.
@client.event
async def on_ready():
    _activity = discord.Activity(name="activity",
                              url="url",
                              type=discord.ActivityType.streaming, 
                              start=datetime.today())
    await client.change_presence(activity=_activity, status=discord.Status.dnd)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    servers = client.guilds
    for i in servers:
        print(i.name)
client.run(TOKEN)
