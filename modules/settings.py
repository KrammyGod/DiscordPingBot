# settings
import os
import discord

__all__ = ['CONFIG']


class _Config:
    # Bot settings
    PREFIX = "!!"
    TOKEN = os.environ['OS_TOKEN']
    INTENTS = discord.Intents(messages=True, guilds=True)
    INTENTS.members = True
    INTENTS.reactions = True
    ADMINS = int(os.environ['OS_ADMIN'])
    INVITE_URL = os.environ['OS_INVITE']
    LOGS_CHANNEL = os.environ['OS_LOGS']

CONFIG = _Config()
