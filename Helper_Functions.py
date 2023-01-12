import discord

from discord.ext import commands

from Player import *

#HELPER FUNCTIONS (NOT COMMANDS)
def primeNumber(number): #breath of life check for "playing" command, no point of asking team size if prime number, defaults solos
    for i in range(2, number):
        if number%i == 0:
            return False
    return True


def namesList(playerDictoValues):
    return([i.getName() for i in playerDictoValues])


def nameToID(name, playerDicto): #FIX THIS, userID is int and cant be accessed
    for userID, player in playerDicto.items():
        if name == player.getName():
            return userID
    return False


def underdogBoost(totalBets): #used in "winner" command, gives more points depending on bet circumstances
    pressure = max(totalBets) #NOTE: the +1 for each boost is for when everyone bets low enough where the floor division gives 0 for each boost (atleast they get something)

    for i in range (0, len(totalBets)): #NOTE prob breaks, either do all at end, or one at a time

        if totalBets[i] == 0: #if no one bets on you, you get big boost
            totalBets[i] = 1 + pressure // 3 #just in case the int division gives 0, atleast you get 1 point

        elif totalBets[i] <= pressure / 2: #if you have some bets, but is half or less the highest bet, you get medium boost
            totalBets[i] = totalBets[i] + 1 + pressure // 4 #just in case the int division gives 0, atleast you get 1 point


async def blocker(a, blockTarget, playerDicto):
    for blockUser, blockVictim in blockTarget.items(): #keys are the player who activated the block, values are the block victims
        if playerDicto[blockVictim].getStatus().get("Shield") == "ACTIVATED": #checks if target has shield activated
            await playerDicto[blockVictim].getChannel().send("Successfully Shielded Against Player: " + playerDicto[blockUser].getName()) #tells block victim their shield worked and who tried to block them
            await playerDicto[blockUser].getChannel().send("Got Shielded, Block Wasted") #tells block user that the block got shielded
            #await a.send("shielded") #NOTE probs wanna send to specific channels to tell them their block was wasted
            pass

        else: #no shield activated
            playerDicto[blockVictim].updatePoints(playerDicto[blockVictim].getBet()) #returns the betted points back to held points
            playerDicto[blockVictim].updateBet(-playerDicto[blockVictim].getBet()) #the math turns bet to 0 (bet - bet = 0)


#DEPRECATED/OUTDATED COMMANDS

'''
async def getPlayerIndex(a, playerList): #only for user specific command requests ex: user 1 wants to know his stuff
    for i in playerList:
        if i.getUserID() == a.author.id:
            return (playerList.index(i))
'''

'''
async def getChannel(a, playerDicto, channelList):
    for i in range(1, len(playerDicto)+1): #amount fo channels for amount of players
        channel = discord.utils.get(a.guild.channels, name="player-" + str(i)) #gets channel
        channelList.append(channel)
    #logsChannel.append(discord.utils.get(a.guild.channels, name="history"))

'''

"""
async def adminCheck(a): #for specific commands, checks if user who requested command is admin
    role = discord.utils.get(a.guild.roles, name="Admin") 
    if role in a.author.roles: #checks discord role (like custom role name, not actual administrator power)
        return True
    else:
        await a.send("Only the head fairy can run these commands") #stops the command if player isnt Admin role
        return False


async def printLog(self, history):
    await logsChannel[0].send(str(history))

"""

'''
async def blocker(a, blockTarget, playerDicto):
    for i in blockTarget.values(): #keys are the player who activated the block, values are the block victims
        if playerDicto[i].getStatus().get("Shield") == "ACTIVATED": #checks if target has shield activated
            await a.send("shielded") #NOTE probs wanna send to specific channels to tell them their block was wasted
            pass

        else: #no shield activated
            playerDicto[i].updatePoints(playerDicto[i].getBet()) #returns the betted points back to held points
            playerDicto[i].updateBet(-playerDicto[i].getBet()) #the math turns bet to 0 (bet - bet = 0)

'''
#if shieldList[playerList.index(str(player))] == 1:
        #return
    
