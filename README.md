# This repository will soon be archived. A link to a public repo will be provided for the updated bot written in JS/TS.

# DiscordPingBot
Custom Pinging Bot made for Discord

## Setup
The setup is very simple, but it can be customized which is for advanced users only. The basic setup is to set the correct environment variables as shown below:

First grab the files by forking/cloning, or downloading the zip. Then, navigate to the directly in your command line, and install requirements by running `python -m pip install -r requirements.txt`. If python is undefined, you must add python to PATH (plenty of resources online). Then we need to setup the environment variables.

On windows: Go to search -> type `environment` and click "Edit the system environment variables". In the pop-up, click "Environment Variables...". 
In user variables, create new environment variables according to this list:

**OS_TOKEN** with value containing the token of your discord bot.

**OS_ADMIN** with an integer containing your full user ID. **DO NOT ADD ANYTHING ELSE OR THE BOT MAY FAIL**

**OS_INVITE** with value containing the invite link for your bot. To get the invite link, go to your bot in developer portal, click OAuth2, select bot, and copy your client ID. Then, replace CLIENTID with the value you copied it in the link below:

`https://discord.com/api/oauth2/authorize?client_id=CLIENTID&permissions=805683344&scope=bot` 

The full list of permissions and commands that require the permissions are contained in cogs/misc_commands.py (the docstring under "async def invite").

**OS_LOGS** with an integer containing the logs channel you wish to output to. This will not work if the integer is wrong, or it is not an integer. It will not affect how the bot runs.

Any issues please post in Issues, thx.

You can also join my support server @ https://discord.gg/BKAWvgVZtN. There, I have a fully functioning bot running with slightly more commands than this bot has. (omitted for privacy purposes)

## Trial Bot
Alternatively, you can try the bot with similar features to this one by inviting my public bot using https://discord.com/api/oauth2/authorize?client_id=498219323337474049&permissions=805694672&scope=bot. This bot is always undergoing improvements, and any big changes being made to that one will be eventually updated here.

Current functions:

## Cog: Image Commands
A cog made for image modifications.

### Pictures
There are 3 commands for dealing with pictures:

`!!pfp`, `!!modpfp`, and `!!modimg`. pfp is a generic grabbing pfp command, modpfp allows someone to apply an image kernel transformation to the picture. Currently, there are 4 supported kernels. [G]reyscale, [SU] Sharpen Unmask, [S]harpen, and "[E]dgify". [G], [SU], and [S] will all result in grayscale images, while [E] gives the illusion of a sharpened image, preserving the colour. modimg enables the user to apply any of the kernels to their own picture(s). The attached images must be in one message.

## Cog: Mod Commands
A cog made for commands for restricted users only.

### Mute
A generic mute command. It will create a new muted role if there isn't one already with that name. Use this command again if you want to unmute someone. User must have "manage roles" permission.

### Revive
A command that randomly pings a user in the guild. Only one person can do this (user id is in CONFIG.ADMINS).

### Say
Make the bot say something. Must be a developer (their id is in ADMINS). This has many hidden functions, for example you can make the bot say something in a completely different channel. Eg. `!!say #logs :customemoji: hi` in #general for example, would output `<emoji> hi` in the first #logs channel it can find, where emoji is the custom emoji. Locked for devs so it is not abused by too many members (user id is in CONFIG.ADMINS).

### Purge
A generic mass message deleting option. Defaults to 100 messages if you just use `!!purge`. User must have manage messages permission.

## Cog: Misc Commands
A cog made for commands for fun/informational.

### Emoji
Use any emoji the bot can see, just by typing the name of the emoji. Eg. `!!emoji smirk`. Note that this will "impersonate" as the user. `!!emojiid` is for development purposes, you can use it to make the bot use a specific emoji.

### Prefix
Reminds user that prefix is "!!". You can change it in settings.py, but it is not recommended.

### Invite
Gets the invite link to the bot. This must be initialized (see [setup](#setup)).

## Logging
This bot will log all deleted messages it can see, into logs channel (must be setup, see [setup](#setup)). This includes deleted images/files.

## Custom Replies
There are currently two custom replies, one where a user pings the bot and enters welcome, the bot will respond with "Thank you". If a user simply pings the bot, it will reply with "I agree!".

More features will be added in the future.
