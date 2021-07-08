import discord
from discord.ext import commands
from modules.image_utils import *
from modules.converters import *

class ImageCommands(commands.Cog, name='Image Commands'):
    '''
    This category is for commands that deal with image modification.
    '''
    def __init__(self, bot, **options):
        super().__init__(**options)
        self.bot = bot


    ################################ HELPER FUNCTIONS #####################################
    # Function that modifies image given
    def modify_img(self, org_img, width, height, m):
        '''
        This method modifies an image with given modification, m.

        :param: org_img <- pixels form rgb/grayscale converted from image_utils
        :param: width   <- width of org_img
        :param: height  <- height of org_img
        :param: m       <- Modification letter (SU, S, E2, E, C)

        :return: tuple(modified image, error) <- error will be True if modification letter was faulty
        '''
        # Convert to grayscale
        g_img = grayscale(org_img)

        # Sharpen (Unmask)
        if m.upper().startswith('SU'):
            kernel = [[-1/256,-4/256,-6/256,-4/256,-1/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                      [-6/256,-24/256,476/256,-24/256,-6/256],[-4/256,-16/256,-24/256,-16/256,-4/256],
                      [-1/256,-4/256,-6/256,-4/256,-1/256]]
            g_img = modify(g_img, width, height, kernel)
            e = 'SU'
        # Sharpen
        elif m.upper().startswith('S'):
            kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
            g_img = modify(g_img, width, height, kernel)
            e = 'S'
        # Edgify alternative 1
        elif m.upper().startswith('E2'):
            kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
            g_img = modify_colour(g_img, org_img, width, height, kernel)
            e = 'E2'
        # Edgify default
        elif m.upper().startswith('E'):
            kernel = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
            g_img = modify_colour(g_img, org_img, width, height, kernel)
            e = 'E'
        # Cursed
        elif m.upper().startswith('C'):
            kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
            g_img = modify(g_img, width, height, kernel)
            e = 'C'
        else:
            e = 'G' if m.upper().startswith('G') else None

        return g_img, e


    # Helper to save the profile picture
    async def save_pfp(self, ctx, user):
        '''
        This function saves a profile picture in either png or gif.
        '''
        pfp = user.avatar_url_as(static_format='png')
        # Get suffix if gif pfp
        suffix = str(pfp).split('?')[0].split('.')[-1]
        pfp_name = f'pfp.{suffix}'
        await pfp.save(f'files/{pfp_name}')
        return pfp_name
    ############################### END HELPER FUNCTIONS #####################################


    # Give someone's pfp
    @commands.command(brief='Get a user\'s pfp.')
    async def pfp(self, ctx, user=None):
        '''
        Get the image of a user's profile picture.

        Usage: !!pfp <user> (user is optional and defaults to yourself)

        Eg. !!pfp, !!pfp @Krammy

        NOTE: <user> must be initiated with @
        '''
        author = ctx.author

        if user is None:
            user = author
        else:
            user = convert_user(self.bot, user, ctx.guild)

        # Save profile picture
        pfp_name = await self.save_pfp(ctx, user)
        # Create new embed object
        embed = discord.Embed(title=f'{user.name}#{user.discriminator}\'s profile picture:')
        embed.set_author(name=f'{author.name}#{author.discriminator}', icon_url=author.avatar_url)
        embed.set_image(url=f'attachment://{pfp_name}')
        await ctx.send(file=discord.File(f'files/{pfp_name}'), embed=embed)


    # Modify someone's pfp
    @commands.command(brief='Modify someone\'s pfp.')
    async def modpfp(self, ctx, *args):
        '''
        [G]rayscale, [S]harpen, [SU]Sharpen (Unmask), "[E]dgify", or "[C]ursify"
        someone's profile picture to ruin their day. Leave empty for self grayscale.
        Protip: [E]dgify retains colour and sharpens edges. If [E] gives bad result, try [E2].

        Usage: !!modpfp <user> <modification> (user and modification are optional 
        and defaults to self grayscale)

        Eg. !!modpfp, !!modpfp E, !!modpfp @Krammy E

        NOTES: Order of <user> and <modification> do NOT matter. <user> must be initiated with @
        '''
        author = ctx.author

        if len(args) > 2:
            raise(commands.TooManyArguments)

        if args:
            if '@' in args[0]:
                user = args[0]
                modification = args[1] if len(args) > 1 else 'G'
            else:
                modification = args[0]
                user = args[1] if len(args) > 1 else None
        else:
            modification = 'G'
            user = None

        if user is None:
            user = author
        else:
            user = convert_user(self.bot, user, ctx.guild)
        
        msg = await ctx.send('Retrieving photo and editing...')
        # Force png of pfp
        pfp = user.avatar_url_as(format='png', static_format='png')
        pfp_name = 'pfp.png'
        pfp_path = f'files/{pfp_name}'
        await pfp.save(pfp_path)
        img, width, height = convert_pixels(pfp_path)

        img, e = self.modify_img(img, width, height, modification)
        
        if e is None:
            await ctx.send('Hm. That was a bad modification letter. Defaulting to [G]rayscale...', delete_after=2.0)
            e = 'G'

        save_image(img, width, height, filename=pfp_path)

        embed = discord.Embed(title=f'Here is a modified verison of\n*{user.name}#{user.discriminator}\'s* profile picture:', description=f'__Modification type:__ **{e}**')
        embed.set_author(name=f'{author.name}#{author.discriminator}', icon_url=author.avatar_url)
        embed.set_image(url=f'attachment://{pfp_name}')
        await msg.delete()
        await ctx.send(file=discord.File(pfp_path), embed=embed)


    # Modify any image(s)
    @commands.command(brief='Modify any image(s).')
    async def modimg(self, ctx, modification=None):
        '''
        [G]rayscale, [S]harpen, [SU]Sharpen (Unmask), "[E]dgify", or "[C]ursify"
        any image. Leave empty for self grayscale.
        Protip: [E]dgify retains colour and sharpens edges. If [E] gives bad result, try [E2].

        Usage: !!modimg <modification> (modification is optional and defaults to grayscale)

        Eg. !!modimg, !!modimg E
        '''
        imgs = ctx.message.attachments
        author = ctx.author

        if not imgs:
            await ctx.send('I don\'t see any images, please use command again and attach some images.')
            return

        if modification is None:
            modification = 'G'

        msg = await ctx.send('Received image(s)! Modifying now (please be patient)...')
        images = []
        img_names = []
        too_large = False
        e = None
        for img in imgs:
            img_name = img.filename
            img_path = f'files/{img_name}'
            await img.save(img_path)
            new_img, width, height = convert_pixels(img_path)
            # If image too large, do not modify it
            if new_img is None:
                too_large = True
                continue
            
            # Apply modifications
            new_img, e = self.modify_img(new_img, width, height, modification)
            save_image(new_img, width, height, filename=img_path)
            # Add to files to send
            images.append(discord.File(img_path))
            img_names.append(img_name)
        
        # Send modified images
        await msg.delete()
        if images:
            # Only include modification letter if there were images successfully saved
            if e is None:
                await ctx.send('Hm. That was a bad modification letter. Defaulting to [G]rayscale...', delete_after=3.0)
                e = 'G'
            
            embed = discord.Embed(title='Here is/are your modified image(s):', description=f'__Modification type:__ **{e}**')
            embed.set_author(name=f'{author.name}#{author.discriminator}', icon_url=author.avatar_url)
            name = img_names.pop(0)
            d_file = images.pop(0)
            embed.set_image(url=f'attachment://{name}')
            await ctx.send(file=d_file, embed=embed)

            embed.description = 'Cont.'
            for i in images:
                name = img_names.pop(0)
                images.remove(i)
                embed.set_image(url=f'attachment://{name}')
                await ctx.send(file=i, embed=embed)

        if too_large:
            await ctx.send('Note: Some or all of the image(s) is/are too large. They have not been modified.')
