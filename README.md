# Points_Cruncher_V2
Updated Version of the Points Cruncher


Points Cruncher is a Discord Bot that uses python and the discord.py library

This bot is used for points management in a tournament-style point betting system for head-to-head games.

Players can invoke multiple commands in the discord message chats to enter info and call commands.
This includes entering in as a player, betting points, using powerups, and checking their current status (powerups, points, how much points is bet, etc).

Alot of the nitty gritty of the commands can be found commented in the code.

Player objects carry majority of the player-related data including:
name, points, powerups (what they are and how many left), status (says if certain powerups are used or not, or if there are any left), 
spectatorsChoice (the team the non-currently playing player chose to bet on ), bet (poitns bet), and channel (player's privated channel name).

A lot of debugging still needs to be done (including reset commands).
