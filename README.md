[![Red cogs](https://img.shields.io/badge/Red--DiscordBot-cogs-red.svg)](https://github.com/Cog-Creators/Red-DiscordBot/tree/V3/develop)
[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)

# DashCogs

Garbage I've made for Red (discord bot framework/API). https://github.com/Cog-Creators/Red-DiscordBot

# Installation

Add this repo using

`[p]repo add DashCogs https://github.com/DashGit/DashCogs`

>[p] is your prefix.

Then, install each cog individually with

`[p]cog install DashCogs <cog name>`

And load each cog with

`[p]load <cog name>`

## GImage

This cog allows you to search for either one or multiple images on [Google Images](https://images.google.com).

* `[p]img <search term>`: Download a single image. Only accepts one parameter, which is the image you would like to search for.
* `[p]mimg <search term> <amount>`: Download multiple images. Accepts two parameters - the search and the amount of images to get. Please note that large amounts may crash the bot. In addition, search terms with a space must be put in quotes.
* `[p]gimageset <setting>`: Manipulate various settings described below.
  * `[p]gimageset block`: Block a person from using GImage. If the person is already on the block list, they will be removed.
  * `[p]gimageset blocklist`: View the list of people blocked from using GImage.
