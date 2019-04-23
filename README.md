[![discord server](https://discordapp.com/api/guilds/569601555821756417/embed.png)](https://discord.gg/bYrGzyX)
[![red cogs](https://img.shields.io/badge/Red--DiscordBot-cogs-red.svg)](https://github.com/Cog-Creators/Red-DiscordBot/tree/V3/develop)
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

Search for either one or multiple images on [Google Images](https://images.google.com).

* `[p]img <search term>`: Download a single image. Only accepts one parameter, which is the image you would like to search for.
* `[p]mimg <search term> <amount>`: Download multiple images. Accepts two parameters - the search and the amount of images to get. Please note that large amounts may crash the bot. In addition, search terms with a space must be put in quotes.
* `[p]gimageset <setting>`: Manipulate various settings described below.
  * `[p]gimageset block <user> <list>`: Block or unblock a person from using GImage. If "list" is added after this command, it will print a list of all people currently blocked from using GImage.

## SelfMessage

Type messages using your bot's account. In order to send a message, PM the bot with what you would like to say. Make sure you've set the server and channel the bot should say the messages in first (using the commands listed below)!
**Note: Only the owner of the bot is allowed to do this. If you would like to allow someone else to access SelfMessage, add them with [p] toggleuser.**
* `[p]selfmessageset <setting>`: Manipulate various settings described below.
  * `[p]selfmessageset server <server>`: Sets the server the bot should look for channels in. The bot must be in the server specified.
  * `[p]selfmessageset channel <channel>`: Sets the channel the bot should send messages in. The channel must be one the bot can see.
  * `[p]selfmessageset enabled`: Toggles on and off whether the bot owner sending a PM to their bot will send a message.
  * `[p]selfmessageset user <user> <list>`: Toggles on and off whether someone can use the cog besides the bot owner. Add "list" to the end of this command to view all users allowed to use SelfMessage.

## Pokemon
  
Play a text-based game based around the Pokemon series. Set up a whitelisted channel or two for the bot to post pokemon in, and guess their names! This cog was inspired by Pokecord, the popular Discord bot. As such, the cog offers the ability to import all owned pokemon from Pokecord. The aim is to provide a more customizable experience than Pokecord on a per-server basis.

* `[p]pokemonimport`: Import all your pokemon from Pokecord. The command will walk you through the steps to do so. Please note that this can only be done once per person.
* `[p]pokemoninfo <id>`: Display all your pokemon that you have caught. It is also possible to view a detailed readout of each caught pokemon's statistics by adding their ID after this command.
* `[p]pokemonselect <id>`: Select a pokemon to recieve EXP. If no pokemon is selected, this defaults to the first pokemon caught.
* `[p]pokemonprint <search>`: Display a pokemon's base statistics. Can search by either name or ID.
* `[p]pokemonset <setting>`: Manipulate various settings described below.
  * `[p]pokmemonset debug`: Display values relevant for debugging.
  * `[p]pokmemonset listamt <amt>`: Change the amount of pokemon that will be displayed per page on `[p]pokemonlist`. Cannot be higher than 50.
  * `[p]pokmemonset randomlevels`: Toggle whether pokemon should spawn with a random level when caught. If off, all pokemon will be caught at level 1.
  * `[p]pokmemonset resetdata <type>`: Reset all data for either all guilds or all members in the server that the command is executed inside of. Only the bot owner can use this command.
  * `[p]pokmemonset spawntime`: Set the amount of time that it should take for a pokemon to spawn, in seconds. Cannot be less than or equal to 0. Can either be one value or two, if the bot should pick a random time between these two values for every pokemon spawned.
  * `[p]pokmemonset whitelist <list>`: Add the current channel to the whitelist, or list all currently whitelisted channels by adding "list" after this command.

## Coinflip

Flip coins with a fancy animation. Can either be one coin or multiple coins.

* `[p]coinflip <type>`: Flip either one coin or multiple coins at once.
