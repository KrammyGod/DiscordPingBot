import discord
from discord.ext import commands
from modules.settings import CONFIG

class CustomHelp(commands.HelpCommand):
    '''
    This class is a custom help command
    '''
    def __init__(self, **options):
        commands.HelpCommand.__init__(self, **options)
        self.paginator = commands.Paginator(prefix='', suffix='')
        self.indent = 4


    '''
    Command not found return
    '''
    def command_not_found(self, string):
        return f'No command called `{string}` found.'


    '''
    Subcommand not found return
    '''
    def subcommand_not_found(self, command, string=None):
        if string:
            return f'Command `{command.qualified_name}` has no subcommands.'
        else:
            return f'Command `{command.qualified_name}` has no subcommand named `{string}`.'


    '''
    Help page with no arguments
    '''
    async def send_bot_help(self, mapping):
        cogs = list(mapping.keys())
        cogs.remove(None)
        prefix = CONFIG.PREFIX
        for i in cogs:
            # Used for excluding empty cogs, like the "No Category"
            if mapping[i]:
                self.paginator.add_line(f'**__{i.qualified_name}:__**')
                self.paginator.add_line(f'**{i.description}**')
                for ii in mapping[i]:
                    self.paginator.add_line(f'> {prefix}{ii.name} - *{ii.short_doc}*')
                self.paginator.add_line('')
        await self.send_pages()


    '''
    Help command for a specific command.
    '''
    async def send_command_help(self, command):
        self.paginator.add_line(f'**__Command: {command.name}__**')
        self.paginator.add_line(command.help)
        await self.send_pages()


    '''
    Help command for a specific category.
    '''
    async def send_cog_help(self, cog):
        self.paginator.add_line(f'**__Category: {cog.qualified_name}__**')
        self.paginator.add_line(f'**{cog.description}**')
        prefix = CONFIG.PREFIX
        for i in cog.get_commands():
            self.paginator.add_line(f'> {prefix}{i.name} - *{i.short_doc}*')
        await self.send_pages()


    '''
    Paginator output.
    '''
    async def send_pages(self):
        ctx = self.context
        author = ctx.author
        dest = self.get_destination()
        prefix = CONFIG.PREFIX
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, colour=discord.Colour.from_rgb(173, 216, 230))
            name = f'{author.name}#{author.discriminator}'
            embed.set_author(name=name, icon_url=author.avatar_url)
            footer = f'Type {prefix}help command for more info on a command.'
            footer += f'\nType {prefix}help full category name for more info on a category.'
            embed.set_footer(text=footer)
            await dest.send(embed=embed)
