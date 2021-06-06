# DiscordPingBot
Custom Pinging Bot made for Discord

Simply insert your bot's token, and your user id in the list of `userIDs` as an integer, and run the bot!

Any issues please post in Issues, thx.

Current functions:
### Emoji
Use any emoji the bot can see, just by typing the name of the emoji. Eg. `!!emoji smirk`. Note that this is not very helpful, but it is the backbone of automating emoji names in [`say`](#say) command. `!!emojiid` is for development purposes, you can use it to make the bot use a specific emoji.

### Daily
Has not been limited to be used once per day, but update will come soon:tm:. Will automatically ping a random user (not bot) in the server and remind them to revive a dead chat.

### Roll
A generic dice roller command. The number of sides on the die can be modified.

### Prefix
Reminds user that prefix is "!!". You can change it, but it is not recommended.

### Say
Make the bot say something. Must be a developer (their id is in userIDs). This has many hidden functions, for example you can make the bot say something in a completely different channel. Eg. `!!say #logs :customemoji: hi` in #general for example, would output `<emoji> hi` in the first #logs channel it can find, where emoji is the custom emoji. Locked for devs so it is not abused by too many members.

### Purge
A generic mass message deleting option. Defaults to 100 messages if you just use `!!purge`. Can have filters to delete from specific user, but would require a number (this will be changed in the future).

### Mute
A generic mute command. It will create a new muted role if there isn't one already with that name. Use this command again if you want to unmute someone.

### Quit
A generic shutdown command. It closes the bot without the developer having to close their python window.

### Pictures
There are 3 commands for dealing with pictures:

`!!pfp`, `!!modpfp`, and `!!modimg`. pfp is a generic grabbing pfp command, modpfp allows someone to apply an image kernel transformation to the picture. Currently, there are 4 supported kernels. [G]reyscale, [SU] Sharpen Unmask, [S]harpen, and "[E]dgify". [G], [SU], and [S] will all result in grayscale images, while [E] gives the illusion of a sharpened image, preserving the colour. modimg enables the user to apply any of the kernels to their own picture(s). The attached images must be in one message.

More features will be added in the future.
