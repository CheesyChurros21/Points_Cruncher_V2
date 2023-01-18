import discord

from discord.ext import commands, tasks

import asyncio

from Helper_Functions import *

from Player import *


#PLAYER RELATED LISTS

playerDicto = {} #NOTE: keys are discord userID, values are the player objects
                       #player object consists of name, points, powerups, status, spectatorsChoice, bet, channel


#IN-GAME PLAYER RELATED LIST

currentlyPlaying = [] #the indexes are specific for each team of players (aka index 0 for both lists are reserved for player 1) 

playerHolder = [] #just a list that holds which players are playing, order doesnt matter


#POINTS RELATED LISTS

totalBets = [] #sum of the bets for each playing team, indexing scheme is based on the team creation order (team 1 uses index 0, etc)
                #NOTE may not be needed


#POWERUPS

settings = [1, 2, 3] #used to turn the lists below on or off (each index represents the toggle for the following powerups from top to bottom)
                     #each index is a unique number for the "gimmick" function to determine if the powerup is turned on or not
                     #the "toggle" command will replace the values with 0 if associated powerup is turned off

blockTarget = {} #the dictionary that carries whos blocked by who

switchList = [] #switches 2 players and their bets (not gonna lie, this one sucks, needs to be improved)


#STORE LISTS

storeList = ["Block", "Shield"] #holds possible powerups that can be bought for points

storeCheck = [[], []] #holds the current rounds top 2 in sublist 1, and bottom 2 in sublist 2 (used for store tax or discount)


#OTHER LISTS

#NOTE: variables in the void are whack with bots, the rounds list just increments the number in index 0 by 1 to increase round number, 

rounds = [0, 0] #NOTE: index 0 is for current round, index 1 is for total number of rounds (set before starting)


#STATUS LIST


status = ["Type *help", "Eating Good", "Crunching Points", "Nyaeh"]
 

#BOT PREFIX (TOO LOAD THE BOT)

bot = commands.Bot(command_prefix = "*", help_command=None) #turns off default help list (its trash)


#ANYBODY CAN USE COMMANDS

@bot.command()
async def hi(a): #hi
    await a.send("Greetings from Sunny Milk!!!")

@bot.command()
async def enter(a, name=None): #adds players to the game
    if name is None: #for whitespace
        await a.send("Forgot to put your name you silly goose")
        return

    if name in namesList(playerDicto.values()): #duplicate name in playerDicto namesList function
        await a.send("Name taken you goofball")
        return
    
    if a.author.id in playerDicto.keys():
        await a.send("Already Joined, Stop Spamming")
        return

    powerups = {}
    status = {}

    for i in storeList:
        powerups[i] = 1
        status[i] = "AVAILABLE"

    playerDicto[a.author.id] = Player(str(name), 0, powerups, status, 0, 0, bot.get_channel(a.channel.id))

    await a.send("Welcome to the Fairy Crew " + name + "!!!") 


@bot.command()
async def leave(a): #if the player doesnt like their name they entered or if they put the enter command in the wrong channel and got the wrong channel id in their player object
    if a.author.id in playerDicto.keys():
        playerDicto.pop(a.author.id)
        await a.send("Left the Fairy Crew")

    else:
        await a.send("You haven't even joined you Goof")


@bot.command()
async def info(a):

    stringo = ""

    for userID, player in playerDicto.items():

        stringo = stringo + "index: " + str(list(playerDicto).index(userID)) + "    id: " + str(userID) + "    name: " + str(player.getName()) + "    points: " + str(player.getPoints()) + "    powerups: " + str(player.getPowerups()) + "    powerups status: " + str(player.getStatus()) + "    chosen player/team: " + str(player.getSpectatorsChoice()) + "    channel ID: " + str(player.getChannel()) + "\n\n"

    await a.send(stringo)


@bot.command(aliases=["round"])
async def roundNumber(a): #round check
    await a.send("Round " + str(rounds[0]))


@bot.command()
async def current(a): #shows whos currently playing
    if len(currentlyPlaying) == 0: #check if "playing" command was successfully used to set playing players
        await a.send("Teams aren't set yet")
        return

    else:
        teamNumber = 1 #for printing team number
        for i in currentlyPlaying: #makes a readable string for each sublist using .join()
            await a.send("Team " + str(teamNumber) + ":   " + ", ".join(i))

            teamNumber = teamNumber + 1


@bot.command()
async def balance(a, userID = None): #gives user their total points amounts and how much is waiting in bet limbo
#NOTE the balance shows the bet points deducted already, ex - my total points was 20 and i bet 5, "balance" command shows 15 for balance and 5 in pending bet
    if (userID == None): #default the argument to NONE, (this is whenever a player asks for their balance cause they obviously dont know channel IDs)
        await a.send("Your balance is: " + str(playerDicto[a.author.id].getPoints()) + " points    Pending Bet: " + str(playerDicto[a.author.id].getBet()) + " points")

    else: #used in the winner command and sends the balance to each channelID from the userID key
        await playerDicto[userID].getChannel().send("End of Round " + str(rounds[0]) + "\nYour balance is: " + str(playerDicto[userID].getPoints()) + " points    Pending Bet: " + str(playerDicto[userID].getBet()) + " points")


@bot.command()
async def block(a, player):
    if len(currentlyPlaying) == 0:
        await a.send("Playing players have not been decided yet, please wait till after they are chosen")
        return

    if playerDicto[a.author.id].getStatus().get("Block") == "ACTIVATED": #checks if block command called already in current round
            await a.send("Already Activated Block")
    elif playerDicto[a.author.id].getPowerups().get("Block") == 0: #checks if no more block powerup left
        await a.send("All Blocks Gone, No More Blocking")

    else: #player has block amount > 0
        if str(player) not in namesList(playerDicto.values()): #if typed name is typoed and not an actual player
                await a.send("Player " + str(player) + " does not exist")
                return
                
        elif str(player) in playerHolder: #if typed name is a player that is playing
            await a.send("Can't block a currently playing player")
            return

        else:
            playerDicto[a.author.id].updateStatus("Block", "ACTIVATED") #successful called command with valid player and has powerups to use
            playerDicto[a.author.id].updatePowerups("Block", -1)
            blockTarget[a.author.id] = nameToID(player, playerDicto)

            #await printLog(a, str(playerList[z]  + " blocked " + player)) # add to log
            await a.send("You have blocked " + str(player))

               
@bot.command()
async def shield(a):
    if playerDicto[a.author.id].getStatus().get("Shield") == "ACTIVATED": #checks if shield command called already in current round
            await a.send("Already Activated Shield")

    elif playerDicto[a.author.id].getPowerups().get("Shield") == 0: #checks if no more shield powerup left
        await a.send("All Blocks Gone, No More Shielding")

    else: #player has shield amount > 0 (aka can use it)
        playerDicto[a.author.id].updateStatus("Shield", "ACTIVATED")
        playerDicto[a.author.id].updatePowerups("Shield", -1)

        #await printLog(a, str(playerList[z] + " shielded this round"))
        await a.send("I have now made you invisible, no one can attack you")


@bot.command()
async def bet(a, points): #2 step command, first part requires points needed to be bet
    await current(a) #brings out teamlist so you dont have to check again (also so you dont break bot by putting command during the input section)

    await a.send("Choose a Team")

    valid = 0 #for players entering bad info, continues to ask

    choice = 0 #the team the user is betting on

    while valid != 1:

        reply = await bot.wait_for('message', check=None) #checks the users next message

        if (reply.content == "kill"): #stops command if you need to
            await a.send("Command Killed")
            return

        if ((reply.content)[-1]).isnumeric() and 0 < int((reply.content)[-1]) <= len(currentlyPlaying): #checks the last charcater (should be a number)
            choice = int((reply.content)[-1]) #NOTE: #covers only single digit amount of teams aka 9 at most, change to cover whatever amount of team later
            valid = 1 #exits loop

        else:
            await a.send("Messed up team input, try again")

    #starts point adding/subtracting process

    playerDicto[a.author.id].updatePoints(-int(points)) #removes bet amount from total points from player object slot

    playerDicto[a.author.id].updateBet(int(points)) #put bet into player object bet slot

    totalBets[choice-1] = totalBets[choice-1] + int(points) #adds the points to the existing bank total (indexed by team number-1)

    playerDicto[a.author.id].updateSpectatorsChoice(choice) #updates the player choice slot from 0 (which is no team, reserved for playing players) to whatever team they chose

    #FOR LATER maybe add the player names in the team bet statement below

    #await printLog(a, str(playerList[z] + " bets " + str(points) + " on Team " + str(choice))) # add to log
    await a.send("You bet " + str(points) + " points on Team " + str(choice))
    await balance(a, None)  



#ADMIN ONLY COMMANDS


#@commands.has_role("Admin")
@bot.command()
async def setRounds(a, totalRounds):
    rounds[1] = int(totalRounds)
    await a.send("Set total rounds to " + str(rounds[1]))


#@commands.has_role("Admin")
@bot.command(aliases=["start"])
async def startGame(a): #starts game, updates round number (via appending to round list) and adds needed empty values for betting related lists

    #if await adminCheck(a) == False:
        #return

    rounds[0] = rounds[0] + 1

    if rounds[1] == 0:
        rounds[1] = 10
        await a.send("Forgot to set total rounds, so defaulting to 10 rounds")

        '''
        reply = await bot.wait_for('message', check=None) #checks the users next message

        if (reply.content == "kill"): #stops command if you need to
            await a.send("Command Killed")
            return

        if (reply.content).isnumeric() == False: #if size sent is nonnumber
            await a.send("Typo, try again (give number as number, not word)")

        else:
            await setRounds(a, int(reply.content)) #valid response given
        '''

    if (rounds[0] == rounds[1] // 2):
        await a.send("It's half-time! So everyone plays!")

    if (rounds[0] == rounds[1]):
        await a.send("Final round! Admins assign teams accordingly!")

   
    if (rounds[0] == rounds[1] // 2):
        await a.send("It's half-time! So everyone plays!")

    if (rounds[0] == rounds[1]):
        await a.send("Final round! Admins assign teams accordingly!")

    for i in range(0, len(playerDicto)): #makes these lists usable (they are cleared empty each round start)
        totalBets.append(0)

    if rounds[0] >= 3: #store discounts or taxes should apply after atleast some gameplay

        first = max([i.getPoints() for i in playerDicto.values()]) #current highest amount of points
        last = min([i.getPoints() for i in playerDicto.values()]) #current lowest amount of points

        second = 0 #current second highest amount of points (placeholder for logic checks)
        secondLast = 0 #current second lowest amount of points (placeholder for logic checks)

        if len(sorted(set([i.getPoints() for i in playerDicto.values()]))) == 1: #if miraculously, first and last tie, meaning everyone has the same points
            first = None
            last = None   
            second = None #essentially disables them from store price changes
            secondLast = None

        elif len(sorted(set([i.getPoints() for i in playerDicto.values()]))) <= 3: #if somehow theres only 2 or 3 unique points, aka second and second last share values with something
            second = None #essentially disables them from store price changes
            secondLast = None 
        
        else: #when each of the 4 spots are unique
            second = sorted(set([i.getPoints() for i in playerDicto.values()]))[-2] #current second highest amount of points
            secondLast = sorted(set([i.getPoints() for i in playerDicto.values()]))[1] #current second lowest amount of points

        for userID, player in playerDicto.items():
            if (player.getPoints() == first) or (player.getPoints() == second):
                storeCheck[0].append(userID)

            elif (player.getPoints() == last) or (player.getPoints() == secondLast):
                storeCheck[1].append(userID)
        
    await a.send("Great Fairy Wars Round " + str(rounds[0]) + " Begins!!!")


#@commands.has_role("Admin")
@bot.command(aliases = ["nextRound"])
async def newRound(a): #used to clear round specific lists + player object slots (essentially the points related lists and who is playing list)

    #if await adminCheck(a) == False:
        #return

    totalBets.clear() 

    currentlyPlaying.clear()

    await startGame(a) #reuses startGame command to refill the lists


#@commands.has_role("Admin")
@bot.command(aliases = ["teamSize", "teamSizes"])
async def playing(a, amount = None): #3 step command
    """
    if await adminCheck(a) == False:
        return
    """
    size = 0 #team size
    
    if rounds[0] == rounds[1] // 2: # half-time check, free-for-all match, doesn't care if any amount is entered
        amount = len(playerDicto)
        for i in playerDicto.values(): # adds each player into a team, then adds to player list
            team = []
            team.append(i.getName())
            currentlyPlaying.append(team)
        await a.send("Half-time modifier: All players added")
        return

    sizeCheck = primeNumber(int(amount))

    if sizeCheck == False: #if team sizes can vary (aka more than solos is valid split)

        await a.send("Size of Teams?") #includes single player teams

        while size < 1: #team sizes (obviously gotta be more than 0 players a team)

            reply = await bot.wait_for('message', check=None) #checks the users next message

            if (reply.content == "kill"): #stops command if you need to
                await a.send("Command Killed")
                return

            if (reply.content).isnumeric() == False: #if size sent is nonnumber
                await a.send("Typo, try again")

            else:
                if int(amount) % int(reply.content) != 0: #uneven team check, e.g cant have trios, but only 5 people are playing
                    await a.send("Team size and amount of players are not evenly distributed")

                elif int(amount) / int(reply.content) == 1: #say team size is 4, but theres only 4 playing, theres no players left for the opposing team
                    await a.send("all players on one team, lower team size")

                else:
                    size = int(reply.content) #valid size given

    else: #only solos is valid team size split
        size = 1

    teamNum = 1 #teamnumber, also used for looping condition

    repeatCheck = [] #players who are added to a team is put here, debug to avoid duplicate names

    while teamNum < (int(amount)/size)+1:

        await a.send("Team " + str(teamNum) + " Players?")

        reply = await bot.wait_for('message', check=None) #checks the users next message

        players = "" #string to manipulate the sent message (reply)

        if (reply.content == "kill"): #stops command if you need to
            await a.send("Command Killed")
            currentlyPlaying.clear() #because currently playing could be filled somewhat by this point, needa clear it to avoid errors
            return

        if "," in reply.content: #sent team message should be separated by a "," or ", " (a,b or a, b)
            players = (reply.content).replace(", ", ",") #remove the whitespace after comma if present, does nothing for just ","

        elif size == 1: #single player teams dont need any "," of ", " cause they single
            players = reply.content

        else:
            await a.send("Typo, makes sure players are separated by a ','") #bad input, reminds user to put commas

        playerHolder = players.split(",") #splits the "," and puts each player in the playerHolder list for checks

        team = [] #creates team sublist to add to currentlyPlaying list

        for i in playerHolder:
            if i not in namesList(playerDicto.values()): #if typed name is typoed and not an actual player
                await a.send("Player " + str(i) + " does not exist")
                break #return to asking the team players again, does not increment the loop condition (teamNum) 
                #NOTE CHECK LATER - not sure if repeating the same typo name breaks something

            if len(team) < int(size): #checks for team to be fully filled
                team.append(i)
                repeatCheck.append(i) #adds player for a repeat check (can only be a valid name by this point)

                if len(repeatCheck) != len(set(repeatCheck)): #set removes non unique elements (for repeated players)
                                                              #if not same size, gotta ask the team members again
                    
                    repeat = repeatCheck.pop() #returns last element aka repeat player
                    
                    if len(repeatCheck) % 2 == 1: #essentially for if the first player inputted for the bogus team is valid
                        repeatCheck = repeatCheck[:-1] #gotta remove that guy as well just in case for the user team imput redo 

                    await a.send("repeat player inputted - " + str(repeat)) #put out repeated player
                    break #NOTE MAYBE UPDATE probs wanna send out both players at once if they both invalid (shows first one only)

            if len(team) == int(size): #if team has enough players

                currentlyPlaying.append(team) #add to curently playing

                stringo = "Team " + str(teamNum) + ": "

                for i in team:

                    if stringo == ("Team " + str(teamNum) + ": "):

                        stringo = stringo + i

                    else:
                        stringo = stringo + ", " + i
                    
                #await printLog(a, str(stringo))
                
                team = [] #resets team holding list

                teamNum = teamNum + 1 #next team, closer to fulfilling loop requirement

    await current(a) #prints out all the teams and their members so people know whos on what


#@commands.has_role("Admin")
@bot.command()
async def winner(a, *team): #says whos on winning team (i dont think ties are going to happen, props tiebreak thing of somesort if it does, so no code needed)

    #if await adminCheck(a) == False:
        #return

    win = int("".join(team)[-1]) #removes whitespace and gets team number #NOTE CHANGE LATER aka [-1] for single digit teams only to something for multi digit

    await blocker(a, blockTarget, playerDicto) #calls block powerup (specifically before underdog to not cause extra points returned)

    underdogBoost(totalBets) #call underdogboost to see if player is eligible for point boost

    for i in currentlyPlaying[win-1]: #goes to the winning team index and loops through the players in the sublist

        playerDicto[nameToID(i, playerDicto)].updatePoints(totalBets[win-1]) #grabs the playing players id and awards points #NOTE this is kinda slow, improve in future

    for userID, player in playerDicto.items():

        if playerDicto[userID].getStatus().get("Block") == "ACTIVATED": #checks if block was used
            if playerDicto[userID].getPowerups().get("Block") == 0:
                playerDicto[userID].updateStatus("Block", "EMPTY")
            else:
                playerDicto[userID].updateStatus("Block", "AVAILABLE")


        if playerDicto[userID].getStatus().get("Shield") == "ACTIVATED": #checks if shield was used
            if playerDicto[userID].getPowerups().get("Shield") == 0:
                playerDicto[userID].updateStatus("Shield", "EMPTY")
            else:
                playerDicto[userID].updateStatus("Shield", "AVAILABLE")

        if player.getSpectatorsChoice() == win: #checks if the team number stored is the winning one
            playerDicto[userID].updatePoints(playerDicto[userID].getBet() * 3) #awards points (gets what they originally betted back + double of that)


    await a.send("Points Crunched")

    for i in playerDicto.keys(): #grabs userID
        playerDicto[i].updateBet(-playerDicto[i].getBet())
        await balance(a, i) #using the userID key, sends the balance to their respective channels from the player object

    await forceNextRound(a) #calls "forceNextRound" command to clear round specific lists, the command also calls the "startGame" command when its done


#@commands.has_role("Admin")
@bot.command(aliases=["placings"])
async def standings(a): #NOTE FIX LATER - does not take into account ties, so no combined placements
                        #NOTE this is for points as soon as the round started, so loss points from bet and shop dont count
    #if await adminCheck(a) == False:
        #return

    if len(playerDicto) == 0:#if no players are entered
        await a.send("Create Players First")
        return

    standingDicto = dict(sorted(playerDicto.items(), key=lambda item: item[1], reverse=True))

    rank = 1

    placings = ""

    for i in standingDicto:
        placings = placings + "\nRank " + str(rank) + ": " + i + "    Points: " + str(standingDicto[i])
        rank = rank + 1

    await a.send(placings)


@bot.command(aliases=["injectPoints"])
async def addPoints(a, amount, player):

    userID = nameToID(player, playerDicto)

    if userID != False:
        playerDicto[userID].updatePoints(amount)
        await a.send("Injected Player " + str(player) + " with " + str(amount) + " Points")

    else:
        await a.send("Player does not exist")


@bot.command(aliases=["injectPlayers"])
async def addPlayers(a, amount):

    if float(amount).is_integer() == False:
        await a.send("Not Number")
        return

    powerups = {}
    status = {}

    for i in storeList:
        powerups[i] = 1
        status[i] = "AVAILABLE"

    for i in range(len(playerDicto) + 1, len(playerDicto) + int(amount) + 1):
        playerDicto[str("Test-ID-" + str(i))] = Player(str("Test-Player-" + str(i)), 0, powerups, status, 0, 0, discord.utils.get(a.guild.channels, name="player-" + str(i)))

    await info(a)

#RESET RELATED COMMANDS #NOTE can probs write a function in the object itself that resets everthing


#@commands.has_role("Admin")
@bot.command()
async def reset(a): #resets everything absolutely

    #if await adminCheck(a) == False:
        #return

    playerDicto.clear()

    playerHolder.clear()

    totalBets.clear() 

    rounds = [0, 0]

    currentlyPlaying.clear()

    blockTarget.clear()

    storeCheck.clear()

    await a.send("Everything Reset")


@bot.command()
async def softReset(a): #reset eveything except players entered, goes back to round 1

    #if await adminCheck(a) == False:
        #return

    for i in playerDicto.values():
        i.updatePoints(-i.getPoints() + 10)
        i.updateBet(-i.getBet())
        i.updateSpectatorsChoice(0)

        for item in storeList:
            i.updatePowerups(item, -i.getPowerups(item) + 1)
            i.updateStatus(item, "AVAILABLE")


    totalBets.clear() 

    currentlyPlaying.clear()

    rounds.clear()

    blockTarget.clear()

    storeCheck.clear()

    await startGame(a) #calls "startGame" command to fill in whatevers needed again


@bot.command(aliases = ["roundRestart"])
async def restartRound(a): #reset current round specific things only, used to remove incorrect, but valid info that was inputted

    #if await adminCheck(a) == False:
        #return

    for i in playerDicto.values():
        i.updatePoints(i.getBets())
        i.updateBets(-i.getBets())
        i.updateSpectatorsChoice(0)

        for item in storeList:
            if i.getStatus().get(item) == "ACTIVATED":
                i.updateStatus(item, "AVAILABLE")
                i.updatePowerups(item, 1)

    totalBets.clear() 

    currentlyPlaying.clear()

    #NOTE this wont work for the store, need a workaround

    if rounds[0] > 0:
        rounds[0] = rounds[0] - 1 #sets round back 1 because startGame" command adds 1 round

    await startGame(a) #calls "startGame" command to fill in whatevers needed again


@bot.command(aliases=["next"])
async def forceNextRound(a): #skips round and clears round specific info (probs only used alone when restarting something cause of a catastrophic mistake)

    #if await adminCheck(a) == False:
        #return

    totalBets.clear() 

    currentlyPlaying.clear()

    blockTarget.clear()

    storeCheck[0].clear()
    storeCheck[1].clear()

    await startGame(a) #calls "startGame" command to fill in whatevers needed again


#POWERUP COMMANDS


#@commands.has_role("Admin")
@bot.command(aliases=["gimmickStatus", "gimmick", "powerup"])
async def playerItemStatus(a, powerup):

    if (str(powerup).lower().capitalize()) in storeList:

        #itemCheck = eval("i.get" + str(powerup).lower().capitalize() + "()") #NOTE may be needed in future, maybe not

        await a.send(str(powerup).capitalize() + " Status")

        totalStatus = ""

        for i in playerDicto.values():

            status = i.getName() + ": "

            if i.getPowerups().get(str(powerup)) > 0 and i.getStatus().get(str(powerup)) == "AVAILABLE":
                status = status + "Not used this round   Total Remaining: " + str(i.getPowerups().get(str(powerup))) #player has some left, did not use yet this round

            elif i.getStatus().get(str(powerup)) == "ACTIVATED":
                status = status + "Currently activated   Total Remaining: " + str(i.getPowerups().get(str(powerup))) #player used it this round, shows whats left

            else:
                status = status + "empty" #no more to use

            totalStatus = totalStatus + "\n" + status

        await a.send(totalStatus)

    else:
        await a.send("Invalid Powerup")


@bot.command(aliases=["shop"])
async def store(a):
    await a.send("Welcome to the Kirisame Magic Shop!!!")

    priceList = [6, 8] #temporary

    if a.author.id in storeCheck[0]:
        await a.send("Interesting, your doing pretty good at the moment compared to the other fairies, Congratulations!!! Just to let you know, there is a slight service tax, but your a successful fairy, so I'm sure you can afford this.")

    elif a.author.id in storeCheck[1]:
        await a.send("Aw man, you ain't doing too hot right now. I feel kinda bad, so I'll give you a discount.")


    await a.send("Here's this rounds deals:")


    selection = ""

    for i in storeList:
        if (a.author.id in storeCheck[0]) and (rounds[0] >= 3):
            selection = selection + "\n" + i + ": " + str(round(priceList[storeList.index(i)] * 1.5)) 

        elif (a.author.id in storeCheck[1]) and (rounds[0] >= 3):
            selection = selection + "\n" + i + ": " + str(priceList[storeList.index(i)] // 2)

        else:
            selection = selection + "\n" + i + ": " + str(priceList[storeList.index(i)])

        
    await a.send(selection + "\nCancel")

    valid = 0 #for players entering bad info, continues to ask

    while valid != 1:

        reply = await bot.wait_for('message', check=None) #checks the users next message

        if (str(reply.content).lower() == "cancel"): #stops command if you need to
            await a.send("Come Back Next Time!!! (and don't window shop, jerk)")
            return

        elif str(reply.content).lower().capitalize() not in storeList: #user message is not valid item
            await a.send("I don't carry that item. Check your choice again")

        else:
            item = str(reply.content).lower().capitalize()
       
            if (a.author.id in storeCheck[0]):
                    playerDicto[a.author.id].updatePoints(-round(priceList[storeList.index(item)] * 1.5))

            elif (a.author.id in storeCheck[1]):
                    playerDicto[a.author.id].updatePoints(-priceList[storeList.index(item)] // 2)

            else:
                playerDicto[a.author.id].updatePoints(-priceList[storeList.index(item)])

            playerDicto[a.author.id].updatePowerups(item, 1)

            if playerDicto[a.author.id].getStatus().get(item) == "EMPTY":
                playerDicto[a.author.id].updateStatus(item, "AVAILABLE")

            valid = 1

    await balance(a, None)
    await a.send("Thank you for your purchase!!! Come Back Next Time!!!")


#TASKS LOOP (SIMILAR TO BOT EVENTS)

@tasks.loop(seconds=5)
async def change_status():
    for i in status:
        await bot.change_presence(activity=discord.Game(i))
        await asyncio.sleep(5)

        
#BOT EVENTS (READYING + RUNNING AND ERROR HANDLING)


@bot.event
async def on_ready(): #prints in terminal bot is ready to be used
    change_status.start()
    print("Sunny Milk is now preparing, please wait warmly")

'''
@bot.event
async def on_command_error(a, error): #for general bad inputs not already locally handled, causes entire command to be killed
    if isinstance(error, commands.CommandNotFound): #non-existant command called
        await a.send('Command does not exist, try the "help" command or check your spelling')

    elif isinstance(error, commands.MissingRequiredArgument): #when a command needs multiple inputs, but less than required is put (deprecated cause multi step commands)
        await a.send("You forgot something when putting the info after the command, check your inputs again")

    elif isinstance(error, commands.CommandInvokeError): #when input is not valid
        await a.send("You messed up something when putting the info after the command, probably a typo or you put too many inputs")

    elif isinstance(error, commands.MissingPermissions): #NOTE dont know how to make this one work, adminCheck command is a workaround for this
        await a.send("Only the head fairy can run these commands")
'''
bot.run("redacted bot token") #runs bot (inside is the bot token, which is not shown for privacy reasons)
