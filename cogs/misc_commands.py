import discord
from discord.ext import commands
from modules.converters import *
from modules.settings import CONFIG

class MiscCommands(commands.Cog, name='Misc Commands'):
    '''
    This category contains all the commands for fun, or are informational.
    '''
    def __init__(self, bot, **options):
        super().__init__(**options)
        self.bot = bot


    # Emoji command to show any emoji the bot can see
    @commands.command(brief="Use bot to display emoji.")
    async def emoji(self, ctx, emoji_text, number=None):
        '''
        Makes the bot display an emoji for you. Enter the name of emoji only.

        Usage: !!emoji [emoji_name] <number> (number is optional and defaults to 1)
        
        Eg. !!emoji crytilldie, !!emoji wesmart 5
        '''
        await ctx.message.delete()

        if number is None:
            number = 1
        try:
            number = int(number)
        except ValueError:
            raise(commands.BadArgument)

        author = ctx.author
        # Pad with colons to check emoji
        if not (emoji_text.startswith(':') and emoji_text.endswith(':')):
            emoji_text = ':' + emoji_text + ':'
            
        # Get emoji
        emoji = convert_emoji(self.bot, emoji_text)
        if number < 1 or number > 10:
            await ctx.send(f'Hm. {author.mention} Please enter a valid integer. (No overflows)') 
        elif emoji:
            emoji *= number
            # Webhook to send emojis impersonating user
            wb = await ctx.channel.create_webhook(name=author.display_name)
            await ctx.message.delete()
            await wb.send(emoji, username=author.display_name, avatar_url=author.avatar_url)
            await wb.delete()
        else:
            await ctx.send(f'Hm. {author.mention} I couldn\'t find `{emoji_text}`.')


    # Emoji ID for any emoji
    @commands.command(brief="Get the ID and name of any emoji.")
    async def emojiid(self, ctx, emoji_text):
        '''
        Returns emoji ID and name of any emoji.

        Usage: !!emojiid [emoji_name]

        Eg. !!emojiid wesmart
        '''
        author = ctx.author
        # Pad with colons to check emoji
        if not (emoji_text.startswith(':') and emoji_text.endswith(':')):
            emoji_text = ':' + emoji_text + ':'
        
        emoji = convert_emoji(self.bot, emoji_text)
        if emoji:
            await ctx.send(f'Emoji name: {emoji.name}, Emoji ID: {emoji.id}')
        else:
            await ctx.send(f'{author.mention} I couldn\'t find `{emoji_text}`.')


    # Check prefix of bot.
    @commands.command(brief='Current prefix of bot.')
    async def prefix(self, ctx):
        '''
        Shows the current prefix of the bot.

        Usage: !!prefix
        '''
        prefix = CONFIG.PREFIX
        await ctx.send(f'{ctx.author.mention}, the prefix is {prefix}')


    # Invite link. Please read this carefully.
    @commands.command(brief='Show invite link for bot.')
    async def invite(self, ctx):
        '''
        Get the invite link for the bot. Permissions required:
        - **View Audit Log** *(Logging purposes)*
        - **Manage Roles** *(Mute command)*
        - **Manage Channels** *(Mute command)*
        - **Manage webhooks** *(emoji replacements)*
        - **View Channels** *(for any command)*
        - **Send Messages** *(for any command)*
        - **Manage Messages** *(purge command and other commands)*
        - **Embed Links** *(many commands, including help)*
        - **Attach files** *(image commands)*
        - **Read Message History** *(purge commands)*
        - **Use External Emojis** *(reply to users)*

        Usage: !!invite
        '''
        author = ctx.author
        
        url = CONFIG.INVITE_URL
        inv = f'{author.mention} here is the invite link:\n{url}'
        inv += '\n\nPlease do not forget to use `!!help invite` to verify permissions required!'
        await ctx.send(inv)