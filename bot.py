# -*- coding: utf-8 -*-
import os
import discord
import asyncio
import sys
import traceback
from discord.ext import commands

################ CUSTOM PACKAGES #################
from modules.converters import *
from modules.settings import CONFIG
# Command cogs
from cogs.help_command import CustomHelp
from cogs.mod_commands import ModCommands
from cogs.image_commands import ImageCommands
from cogs.misc_commands import MiscCommands
############# END CUSTOM PACKAGES #################

# Global variables and setting up bot.
HELP = CustomHelp()
LOGS_CHANNEL = CONFIG.LOGS_CHANNEL
bot = commands.Bot(command_prefix=CONFIG.PREFIX, intents=CONFIG.INTENTS, help_command=HELP, owner_ids=set(CONFIG.ADMINS))

# Add command cogs
modCog = ModCommands(bot)
imageCog = ImageCommands(bot)
miscCog = MiscCommands(bot)
bot.add_cog(modCog)
bot.add_cog(imageCog)
bot.add_cog(miscCog)


# Replies to users
@bot.listen('on_message')
async def reply(message):
    '''
    This method replies to user's pings to the bot.

    :param: message (the Message object)
    '''
    author = message.author
    channel = message.channel
    msg = message.content
    mentions = message.mentions
    userID = author.id
    # Make sure bot isn't counting own messages
    if author == bot.user:
        return

    #Custom bot replies. These are just some defaults, you can freely customize.
    if 'welcome' in msg.lower() and bot.user in mentions:
        await channel.send(f"Thank you, {author.mention}!")
    elif bot.user in mentions
        await channel.send(f'{author.mention} I agree!')


# Replacing emojis.
@bot.listen('on_message')
async def replace_emoji(message):
    '''
    This method replaces any emojis that user cannot use and impersonates them, outputting the emoji.

    :param: message (the Message object)
    '''
    channel = message.channel
    author = message.author

    msg_list = message.content.split(' ')
    impersonate = False
    msg = ''
    for i in msg_list:
        emoji = convert_emoji(bot, i)
        if emoji is None:
            msg += f'{i} '
        else:
            msg += f'{emoji} '
            impersonate = True

    if impersonate:
        await message.delete()
        wb = await channel.create_webhook(name=author.display_name)
        msg = msg.strip()
        await wb.send(msg, username=author.display_name, avatar_url=author.avatar_url)
        await wb.delete()


# Saving deleted messages
@bot.event
async def on_raw_message_delete(message):
    '''
    This listener will save deleted messages and images, cache them, and output them to logs channel.
    '''
    message = message.cached_message
    if message is None:
        return

    author = message.author
    channel = message.channel
    guild = message.guild

    if not author.bot:
        # Do not count bot commands.
        prefixes = await bot.get_prefix(message)
        if not message.content.startswith(tuple(prefixes)):
            sent_message = str(message.clean_content)
            # Logs channel
            log_channel = bot.get_channel(LOGS_CHANNEL)

            print(author, "deleted a message in #", \
                  channel, "in", guild, "on", \
                  datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S') + " UTC,")
            print(sent_message)

            # Embed setup
            _name = f'{author.name}#{author.discriminator}'
            title = f'A message by {_name} was deleted!'
            embed = discord.Embed(title=title)
            embed.set_author(name=f'Deleted by {_name}', icon_url=author.avatar_url)
            field_name = f'In #{message.channel} of *{message.guild}*:'
            # Cannot send empty message
            sent_message = sent_message if sent_message else '*Empty Message*'
            embed.add_field(name=field_name, value=sent_message, inline=False)

            # Save attachments
            attachments = message.attachments
            num_attach = len(attachments)
            for i in range(num_attach):
                # Save image with custom name
                suffix = attachments[i].filename.split('.')[-1]
                filename = f'image{i}.{suffix}'
                await attachments[i].save(f'files/{filename}', use_cached=True)
                # For embeds after the first embed
                if i > 0:
                    embed.set_field_at(0, name=field_name, value='Cont.')

                # Attach file and send embed
                embed.set_image(url=f'attachment://{filename}')
                await log_channel.send(file=discord.File(f'files/{filename}'), embed=embed)

            # No attachments
            if not attachments:
                await log_channel.send(embed=embed)
                

# Errors
@bot.event
async def on_command_error(ctx, error):
    '''
    This method will handle all the command errors

    :param: ctx (Context object containing information)
    :param: error (Exception object containing error information)
    '''
    author = ctx.author

    if hasattr(ctx.command, 'on_error'):
        return
          
    error = getattr(error, 'original', error)
    
    # Bad data type passed in error
    if isinstance(error, commands.BadArgument):
        await ctx.send(f'Hm. Seems like `!!{str(ctx.command)}` has a wrong argument. Try `!!help {str(ctx.command)}` and try again!')
        return
    
    # Missing parameter error
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Hm. Seems like `!!{str(ctx.command)}` is missing a parameter. Try `!!help {str(ctx.command)}` and try again!')
        return

    # Bot missing permissions error
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f'Hm. I am missing permissions to do that action, please check permissions required using `!!help invite`!')
        return

    # Too many arguments given error
    if isinstance(error, commands.TooManyArguments):
        await ctx.send(f'Too many arguments in `!!{str(ctx.command)}`. Try `!!help {str(ctx.command)}` and try again!')
        return
    
    # No permissions for author invoking command
    if isinstance(error, commands.CheckFailure):
        try:
            perms = error.missing_perms[0]
        except AttributeError:
            perms = 'owner'
        await ctx.send(f'{author.mention} you do not have permissions to use `{ctx.command}`. Required permission: {perms}.')
        return

    # Member not found error
    if isinstance(error, AttributeError):
        await ctx.send('I couldn\'t find that user. Please check your spelling and try again.')
        return

    # Ignore command not found
    if isinstance(error, commands.errors.CommandNotFound):
        return
    
    # All other Errors not returned come here... And we can just print the default TraceBack.
    print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# Shows that bot is ready for use.
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# Control own event loop
loop = asyncio.get_event_loop()
try:
    # Start the bot
    loop.run_until_complete(bot.start(CONFIG.TOKEN))
except:
    # Mark bot as offline before disconnecting
    loop.run_until_complete(bot.change_presence(status=discord.Status.offline))
    loop.run_until_complete(bot.close())
    # Stop "Event loop is closed" runtime error
    loop.run_until_complete(asyncio.sleep(0.1))
finally:
    loop.close()
