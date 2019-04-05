[![Red cogs](https://img.shields.io/badge/Red--DiscordBot-cogs-red.svg)](https://github.com/Cog-Creators/Red-DiscordBot/tree/V3/develop)
[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)

# DashCogs

Garbage I've made for Red (discord bot framework/API). https://github.com/Cog-Creators/Red-DiscordBot

# Installation

Add this repo using

`[p]repo add DashCogs https://github.com/DashGit/DashCogs`

Then, install each cog individually with

`[p]cog install DashCogs <cog name>`

And load each cog with

`[p]load <cog name>`

## GImage

This cog allows you to search for either one or multiple images on [Google Images](https://images.google.com).

* `[p]img <search term>`: Download a single image. Only accepts one parameter, which is the image you would like to search for.
* `[p]mimg <search term> <amount>`: Download multiple images. Accepts two parameters - the search and the amount of images to get. Please note that large amounts may crash the bot. In addition, search terms with a space must be put in quotes.
* `[p]gimageset <setting>`: Manipulate various settings described below.
  * `[p]gimageset block <user>`: Block a person from using GImage. If the person is already on the block list, they will be removed.
  * `[p]gimageset blocklist`: View the list of people blocked from using GImage.
## SelfMessage

This cog allows you to type messages using your bot's account. In order to send a message, PM the bot with what you would like to say. Make sure you've set the server and channel the bot should say the messages in first (using the commands listed below)!
**Note: Only the owner of the bot is allowed to do this. If you would like to allow someone else to access SelfMessage, add them with [p] toggleuser.**
* `[p]selfmessageset <setting>`: Manipulate various settings described below.
  * `[p]selfmessageset server <server>`: Sets the server the bot should look for channels in. The bot must be in the server specified.
  * `[p]selfmessageset channel <channel>`: Sets the channel the bot should send messages in. The channel must be one the bot can see.
  * `[p]selfmessageset enabled`: Toggles on and off whether the bot owner sending a PM to their bot will send a message.
  * `[p]selfmessageset toggleuser <user>`: Toggles on and off whether someone can use the cog besides the bot owner.
