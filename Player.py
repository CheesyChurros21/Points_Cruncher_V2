class Player:
    def __init__(self, name, points, powerups, status, spectatorsChoice, bet, channel): #multiple useful player-related information that is accessed as a dictionary value from the userID key
        #self.userID = userID
        self.name = name 
        self.points = points 
        self.powerups = powerups
        self.status = status
        self.spectatorsChoice = spectatorsChoice
        self.bet = bet
        self.channel = channel

    #def getUserID(self):
        #return self.userID

    def getName(self):
        return self.name

    def getPoints(self):
        return self.points

    def getPowerups(self):
        return self.powerups

    def getStatus(self):
        return self.status

    def getSpectatorsChoice(self):
        return self.spectatorsChoice

    def getBet(self):
        return self.bet

    def getChannel(self): #the players own private channel, for channel specific message sending
        return self.channel

    #def updateName(self, name):
        #self.name = name

    def updatePoints(self, points):
        self.points = self.points + points
    
    def updatePowerups(self, powerup, increment): #when powerups are used, keeps track of how many of each powerup the player has
        self.powerups[powerup] = self.powerups[powerup] + increment

    def updateStatus(self, powerup, status): #when powerups are used, keeps track of if a player used something or is empty on powerups
        self.status[powerup] = status 

    def updateSpectatorsChoice(self, teamChoice): #when players bet and choose a team
        self.spectatorsChoice = teamChoice

    def updateBet(self, bets):
        self.bet = self.bet + bets
