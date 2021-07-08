import discord

'''
This file contains converters that are necessary to grab discord objects.
'''

def convert_emoji(bot, emoji_name):
    # Deny any emoji that is not surrounded by colons
    if not (emoji_name.startswith(':') and emoji_name.endswith(':')):
        return None
        
    emoji_name = emoji_name.replace(':', '')
    for emoji in bot.emojis:
        if emoji_name.lower() == emoji.name.lower():
            ID = str(emoji.id)
            name = emoji.name
            if emoji.animated:
                return f'<a:{name}:{ID}>'
            else:
                return f'<:{name}:{ID}>'
    return None


def convert_user(bot, user, guild=None):
    # Deny any user without @ before it
    if not ('@' in user):
        return None
    
    user = user.replace('<', '')
    user = user.replace('@', '')
    user = user.replace('!', '')
    user = user.replace('>', '')
    # For getting with id
    try:
        user = int(user)
        user = guild.get_member(user) if guild else bot.get_user(user)
        return user
    except ValueError:
        pass
    
    # For getting with name
    members = guild.members if guild else bot.get_all_members()
    return discord.utils.find(lambda m : ((user.lower() in m.display_name.lower()) or
                                         (user.lower() in m.name.lower())), members)


def convert_channel(bot, text):
    # Deny any channel without # in it
    if not ('#' in text):
        return None
    
    text = text.replace('<', '')
    text = text.replace('#', '')
    text = text.replace('!', '')
    text = text.replace('>', '')
    # Find channel with id
    try:
        text = bot.get_channel(int(text))
        return text
    except ValueError:
        pass
    
    # Find channel with name
    text = discord.utils.get(bot.get_all_channels(), name=text)
    return text
