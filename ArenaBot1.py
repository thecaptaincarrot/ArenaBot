import random
import asyncio
import aiohttp
import json
import csv
import math
from discord import Game
from discord.ext import commands
from discord.utils import get
import discord

import fnmatch

global YellowRostercsv
global BlueRostercsv 

global BlueTeamID
global YellowTeamID
global BlueInArenaID
global YellowInArenaID

global DungeonMasterID



#What this bot should do
#1. Be able to roll dice for two players at once
#2. Figure out what users are in the arena
#3. Figure out who the DM is
#4. Keep track of the arena roster
#5. Print the Arena roster
#6. Add a player to the roster via discord

#Character Sheet Goals
#1. Update names and nicknames every time a user related function is called
#2. Implement wild card searches for users
#3. Create better character sheet format
#4. Truncate Roster

BOT_PREFIX = ("A!","a!")

TOKEN = 'NjAzNzIwMjg1OTg3OTMwMTM2.XTs9Lw.OYCgaTqypqflYPTJRdpyUmwC6qQ'

bot = commands.Bot(command_prefix=BOT_PREFIX)

BlueRostercsv = "C:\\Users\\trevo\\Dropbox\\ArenaBot\\BlueRoster.csv"
YellowRostercsv = "C:\\Users\\trevo\\Dropbox\\ArenaBot\\YellowRoster.csv"

###################################################################################################
#class definitions
###################################################################################################
class Combatant:
	def __init__(self, ID="0", User="", Avatar="", Name="", Rank= "Pit Dog", Race="", Class="", Weapon="", Wins = 0, Losses = 0, Ties = 0,UserNick="", WinLoss = 1):
		
		self.ID = ID
		self.User = User
		self.Avatar = Avatar
		self.Name = Name
		self.Rank = Rank
		self.Race = Race
		self.Class = Class
		self.Weapon = Weapon
		self.Wins = int(Wins)
		self.Losses = int(Losses)
		self.Ties = int(Ties)
		self.WinLoss = float(WinLoss)
		self.UserNick = UserNick
	def CalculateWinLoss(self):
		if(int(self.Losses) != 0):
			self.WinLoss = round(float(self.Wins)/(float(self.Losses)+float(self.Wins)+float(self.Ties)),3)
			print("???" + str(self.WinLoss))
			return self.WinLoss
		else:
			print("???" + str(self.WinLoss))
			self.WinLoss = 1
			return self.WinLoss
	def PrintCombatant(self):
		print(self.ID + ", " + self.User + ", " + self.Avatar + ", " + self.Name + ", " + self.Rank + ", " + self.Race + ", " + self.Class)
	def tolist(self):
		combatantlist = [self.ID, self.User, self.Avatar, self.Name, self.Rank, self.Race, self.Class, self.Weapon, self.Wins, self.Losses, self.Ties, self.UserNick] #do not return winloss
		return combatantlist

#Read the .csv file specified for definitions manually entered
#As of right now, it's looking for Code,Name,Type,Description


###################################################################################################
##################################	Function	###################################################
###################################################################################################

def ReadBlueCSV():
	#Encodes the blue team's csv to the dictionary that is the combat roster. A tuple is returned first with the dict of the combatants followed by an ordered list of the combatants.
	print("reading blue")
	ReturnDict = {}
	ReturnList = []
	with open('BlueRoster.csv', 'rt', encoding='utf-8') as BlueRead: #BlueWrite bcomes the open file
		readCSVfile = csv.reader(BlueRead, delimiter = ",", quotechar='|')
		print("read file")
		for row in readCSVfile:
			if len(row) == 12:
				if row[0] == "UserID": #we are at the first line. just ignore it and move on.
					Startup = True 
				else:
					ReadingCombatant = Combatant(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])
					ReadingCombatant.CalculateWinLoss() #need to calculate after reading in
					ReadingCombatant.PrintCombatant()
					ReturnDict[row[0]] = ReadingCombatant #row[0] is the user ID, 
					ReturnList.append(ReadingCombatant) #ordered list starting from the top for rankings
		BlueRead.close
		return ReturnDict, ReturnList

def WriteBlueCSV(ctx,BlueList):
	#Decodes the blue roster list back into a csv readable format
	with open(BlueRostercsv, 'wt',newline='', encoding='utf-8') as BlueWrite: #BueWrite bcomes the open file
		csvwriter = csv.writer(BlueWrite, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		csvwriter.writerow(['UserID','Discord Username','Avatar','Name','Rank','Race','Class','Weapon','Wins','Losses','Ties','Nickname'])
		#we should organize the list here as we write it back in. 
		BlueList = organize(BlueList)
		for combatant in BlueList:
			combatant.PrintCombatant()
			#Update Names right now
			NewName,NewNick = GetNamesFromID(ctx,combatant.ID)
			if NewName is not None:
				combatant.User = NewName
				combatant.UserNick = NewNick
				print("Updated name to: " + combatant.User)
			else:
				print("No name for " + str(combatant.ID))
			#combatant = CheckRankUp(ctx,combatant)
			csvwriter.writerow(combatant.tolist())
		print("I'm writing the blue CSV")
	BlueWrite.close

def ReadYellowCSV():
	#Encodes the Yellow team's csv to the dictionary that is the combat roster. A tuple is returned first with the dict of the combatants followed by an ordered list of the combatants.
	print("reading Yellow")
	ReturnDict = {}
	ReturnList = []
	with open('YellowRoster.csv', 'rt', encoding='utf-8') as YellowRead: #YellowRead bcomes the open file
		readCSVfile = csv.reader(YellowRead, delimiter = ",", quotechar='|')
		print("read file")
		for row in readCSVfile:
			if len(row) == 12:
				if row[0] == "UserID": #we are at the first line. just ignore it and move on.
					Startup = True 
				else:
					ReadingCombatant = Combatant(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])
					ReadingCombatant.CalculateWinLoss() #need to calculate after reading in
					ReadingCombatant.PrintCombatant()
					ReturnDict[row[0]] = ReadingCombatant #row[0] is the user ID, 
					ReturnList.append(ReadingCombatant) #ordered list starting from the top for rankings
		YellowRead.close
		return ReturnDict, ReturnList

def WriteYellowCSV(ctx,YellowList):
	#Decodes the yellow roster list back into a csv readable format
	with open('YellowRoster.csv', 'wt',newline='', encoding='utf-8') as YellowWrite: #Yellowwrite bcomes the open file
		csvwriter = csv.writer(YellowWrite, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		csvwriter.writerow(['UserID','Discord Username','Avatar','Name','Rank','Race','Class','Weapon','Wins','Losses','Ties','Nickname'])
		YellowList = organize(YellowList)
		for combatant in YellowList:
			combatant.PrintCombatant()
			#Update Names right now
			NewName,NewNick = GetNamesFromID(ctx,combatant.ID) #Nicknames are not used right now
			if NewName is not None:
				combatant.User = NewName
				combatant.UserNick = NewNick
				print("Updated name to: " + combatant.User)
			else:
				print("No name for " + str(combatant.ID))
			#combatant = CheckRankUp(ctx,combatant)
			csvwriter.writerow(combatant.tolist())
		print("I'm writing the Yellow CSV")
	YellowWrite.close

def organize(list):
	#organize the list by the number of wins, then the win/loss ratio.
	#list is organized by moving higher winner up. first check if one higher has higher wins. if yes, move up and reset i. if no, check if the wins is the same but the win/loss ratio is higher. if yes, move up and reset i.
	#return organized list
	length = len(list)
	i = 1 #need an iterative variable. starting at 1 because we only ever move the list element up
	print("length: "+str(length))
	while i < length:
		print("i: "+str(i))
		if int(list[i].Wins) > int(list[i-1].Wins):
			temp = list[i-1] #this will move down
			list [i-1] = list [i] #copy the ith value to the previous value in the list
			list[i] =  temp #add the stored value back in.
			print("moved up the value in "+str(i)+"due to Wins")
			i = 1 #back to the top and try again
		elif float(list[i].WinLoss) > float(list[i-1].WinLoss) and int(list[i].Wins) == int(list[i-1].Wins):
			temp = list[i-1] #this will move down
			list [i-1] = list [i] #copy the ith value to the previous value in the list
			list[i] =  temp #add the stored value back in.
			print("moved up the value in "+str(i)+"due to W/L")
			i = 1 #back to the top and try again
		else:
			i = i + 1 #iterate
	return list
	
def GetFighter(UserID):
	ID = str(UserID)
	bluedict , bluelist = ReadBlueCSV()
	yellowdict, yellowlist = ReadYellowCSV()
	
	if ID in bluedict:
		return bluedict.get(ID)
	elif ID in yellowdict:
		return yellowdict.get(ID)
	else:
		print("Tried to find a combatant with ID " + ID+ " but it failed")
		return None

def CheckDM(context):
	guild = context.message.guild
	DMrole = [discord.utils.get(guild.roles, name = "Space Master"),discord.utils.get(guild.roles, name = "Amaranth"),discord.utils.get(guild.roles, name = "Loredinator"),discord.utils.get(guild.roles, name = "Dungeon Master"),discord.utils.get(guild.roles, name = "Dungeon Master (admin)")]
	for role in DMrole:
		if role in context.author.roles:
			return True
	return False

def GetNamesFromID(context,ID):
	#Goal: from the guild, search for the particular ID specified. this will be looped in regular use.
	#When the user is found from the ID, return a tuple that contains both the User Name and the Nick Name for the user.
	#This wll probably be called as part of a larger Update function that will be called each time.
	#If the player is not in the guild, returh "NULL". UPDATE FUNCTION SHOULD UNDERSTAND WHAT THIS MEANS AND NOT UPDATE ANYTHING
	guild = context.message.guild
	integer_ID = int(ID)
	Player = guild.get_member(int(ID))
	if Player is None:
		return None, None
	else:
		if Player.nick is None:
			Player.nick = Player.name
		return Player.name, Player.nick
	
def UpdateRosters(context):
	
	bluedict , bluelist = ReadBlueCSV()
	yellowdict, yellowlist = ReadYellowCSV()
	
	for Entry in bluedict:
		print("aaa")
	
	return None
	
#def CheckRankUp(ctx,Fighter):
#	#for the given fighter, check if they have a rank up
#	#A rank is increased every 3 wins. 
#	#Rank order from highest to lowest:
#	#Champion
#	#Hero
#	#Gladiator
#	#Warrior
#	#Myrmidon
#	#Bloodletter
#	#Brawler
#	#Pit Dog
#	
#	#Check if the fighter has a rank up. from fighter.wins % 3, compared against a dictionary of the ranks.
#	#Change the fighter's rank in the class to the given
#	#take the user's ID and rank them up.
#	#Return the fighter, changed or not.
#	
#	RanksDict = {7 : "Champion",6 : "Hero",15 : "Gladiator",4 : "Warrior",3 : "Myrmidon",2 : "Bloodletter",1 : "Brawler",0 : "Pit Dog"}
#	Rankwins = math.floor(fighter.Wins/3)
#	print(Rankwins)
#	rank = fighter.Rank
#	truerank = RanksDict.get(Rankwins)
#	
#	print(rank)
#	print(truerank)
#	
#	guild = ctx.message.guild
#	print(fighter.ID)
#	user = guild.get_member(int(fighter.ID))
#	
#	print(user)
#	print(guild)
#	
#	oldrole = discord.utils.get(guild.roles, name = rank)
#	newrole = discord.utils.get(guild.roles, name = truerank)
#	
#	print(oldrole)
#	print(newrole)
#	if rank != truerank and truerank is not None:
#		fighter.Rank = truerank
#		await user.remove_roles(oldrole)
#		await user.add_roles(newrole)
#		await ctx.send("Congratulations " + str(fighter.User) + " on ranking up to " + str(truerank) + "!")
#		print("I tried my best")
#	return fighter
	
#Commands
#1. Be able to roll dice for two players at once
#2. Figure out what users are in the arena
#3. Figure out who the DM is
#4. Keep track of the arena roster
#4.5 declare results
#5. Print the Arena roster
#6. Add a player to the roster via discord

#the roster from each team is read in every time a command is given. Nothing should be saved in local memory.

#A!Roll - Rolls dice for the two combatants
#A!Combatant Yellow @xxx adds the player xxx to the yellow team, replacing any current user
#A!Combatant Blue @xxx add the player xx to the blue team, replacing any current user
#A!Close empties both players from the teams
#A!DM @xxx Player xxx is added as a DM. only DM's can use certain commands? Possibly should be set to a role rather than a user.
#A!roster reads and prints the current roster for both teams. this also gives the numbers of wins and losses for each player, and for the team as a whole. Roster is organized with the
#A!fighter @xxx, displays the @'d player's character sheet. if no one is @'d just gives the caller's character sheet or none.
#A!score - gives the wins and losses for blue and yellow team. also displays the #1 player from both.
#A!ping - lets you know if the bot is working or not.

#For now, assume the csv already exists. one csv per team. 

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	

@bot.command(name='purge',
				description = 'Removes a fighter from the roster. Be aware that this will reset the wins and losses of the purged fighter.',
				brief= 'DM Only: Fighter Removal',
				aliases = ['p','Purge','P','Remove','remove','delete','Delete','del','Del'])
async def _purge(ctx, User=None):
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
		
	if User is None:
		await ctx.send("Your forgot to mention anyone")
		return
	Player = ctx.message.mentions[0]
	ToPurge = str(Player.id)
	print("I got the following user ID:" + str(ToPurge))
	bluedict , bluelist = ReadBlueCSV()
	yellowdict, yellowlist = ReadYellowCSV()
	if ToPurge in bluedict:
		print("found it in blue")
		PurgedCombatant = bluedict.get(ToPurge)
		bluedict.pop(ToPurge)
		bluelist.remove(PurgedCombatant)
		role = discord.utils.get(Player.guild.roles, name="Blue Team")
		await Player.remove_roles(role)
		WriteBlueCSV(ctx,bluelist)
		Team = "Blue"
	elif ToPurge in yellowdict:
		print("found it in yellow")
		PurgedCombatant = yellowdict.get(ToPurge)
		yellowdict.pop(ToPurge)
		yellowlist.remove(PurgedCombatant)
		role = discord.utils.get(Player.guild.roles, name="Yellow Team")
		await Player.remove_roles(role)
		WriteYellowCSV(ctx,yellowlist)
		Team = "Yellow"
	else:
		await ctx.send("I could not find that user. perhaps they aren't registered?")
		return
	await ctx.send("I have removed " + ctx.message.mentions[0].name + " from the " + Team + " team.")

@bot.command(description = 'Adds a fighter to the combat roster. A little finnicky so please double check your work. Order of information is Team, @ player, Avatar, Name, Race, Class, Weapon. If any of these information pieces contain more than one word, enclode with ""',
				brief= 'DM only: Fighter Adding',
				aliases = ["Register","reg","Reg"])
async def register(ctx, Team = None, User=None, Avatar=None, Name=None, Race=None, Class=None, Weapon=None):
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
	
	if Weapon is None:
		await ctx.send("You didn't add enough arguments. Remember that it goes Team, '@'d player', Avatar, Name, Race, Class, Weapon,")
		return
	Player = ctx.message.mentions[0]
	guild = ctx.message.guild
	AvatarName = Avatar
	CreatedCombatant = Combatant(str(Player.id), Player.name, AvatarName, Name, "Pit Dog", Race, Class, Weapon)
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()
	if str(Player.id) in bluedict :
		await ctx.send("Player already registered to the blue team.")
		return
	if str(Player.id) in yellowdict:
		await ctx.send("Player already registered to the yellow team.")
		return
	if Team == "Blue" or Team == "blue":
		bluedict , bluelist = ReadBlueCSV()
		bluedict[str(Player.id)]=CreatedCombatant
		bluelist.append(CreatedCombatant)
		role = discord.utils.get(guild.roles, name = "Blue Team")
		await Player.add_roles(role)
		print("I tried")
		WriteBlueCSV(ctx,bluelist)
		await ctx.send("Succesfully registered " + Player.name + " to the Blue team! 💙")
	elif Team == "Yellow" or Team == "yellow":
		yellowdict , yellowlist = ReadYellowCSV()
		yellowdict[str(Player.id)]=CreatedCombatant
		yellowlist.append(CreatedCombatant)
		role = discord.utils.get(guild.roles, name = "Yellow Team")
		await Player.add_roles(role)
		WriteYellowCSV(ctx,yellowlist)
		await ctx.send("Succesfully registered " + Player.name + " to the Yellow team! 💛")
	else:
		await ctx.send("You typed in a bad team name so I couldn't put them on a team. Try again.")

@bot.command(description = 'Gives the combat roster of the specified team and page. If no valid team is recognized, will show the top from each team. Roster is organized by # of wins followed by win/loss ratio.',
				brief= 'Shows the Combat Roster',
				aliases = ["Roster","Ros","ros"])
async def roster(ctx, team = None, page = 1):
	#Read the csv file for the chosen team
	#Parse the team into a number of 10-player pages
	#Display the chosen team page. if the page team exceeds the number of pages, display the last page
	Message = "" #Append to this variable and print it all at the end.
	try:
		page = int(team)
	except:
		pass
	if team == "Blue" or team == "blue":
		bluedict , bluelist = ReadBlueCSV()
		length = len(bluelist)
		maximumpage = math.ceil(length/5)
		if page > maximumpage:
			page = maximumpage
		#the starting value is 10*pagenumber-1 to page + 8
		start = 5 * (page - 1)
		end = 5 * (page - 1) + 5
		i = 0
		print ("length: " + str(length))
		Message = Message + "__***Roster for the Blue Team***__ 💙\n"
		for i in range(start,end):
			print(i)
			if i > length-1:
				break
			print(i)
			combatant = bluelist[i]
			winloss = combatant.CalculateWinLoss()
			#first line is the character
			Message = Message + str(i+1) + ". **" + combatant.User + "** " + combatant.Avatar + ", Name: **"+combatant.Name+"**, Rank: **"+combatant.Rank+"**, Wins: **"+str(combatant.Wins)+"**, Losses: **"+ str(combatant.Losses)+"**, Ties: **"+str(combatant.Ties)+"**\n\n"
		Message = Message + "**Page** " + str(page) + " of " + str(maximumpage) + "..."
	elif team == "Yellow" or team == "yellow":
		yellowdict , yellowlist = ReadYellowCSV()
		length = len(yellowlist)
		maximumpage = math.ceil(length/5)
		if page > maximumpage:
			page = maximumpage
		#the starting value is 10*pagenumber-1 to page + 8
		start = 5 * (page - 1)
		end = 5 * (page - 1) + 5
		i = 0
		Message = Message + "__***Roster for the Yellow Team***__ 💛\n"
		for i in range(start,end):
			if i > length-1:
				break
			combatant = yellowlist[i]
			winloss = combatant.CalculateWinLoss()
			#first line is the character
			Message = Message + str(i+1) + ". **" + combatant.User + "** " + combatant.Avatar + ", Name: **"+combatant.Name+"**, Rank: **"+combatant.Rank+"**, Wins: **"+str(combatant.Wins)+"**, Losses: **"+ str(combatant.Losses)+"**, Ties: **"+str(combatant.Ties)+"**\n\n"
		Message = Message + "**Page** " + str(page) + " of " + str(maximumpage) + "..."
	else: #Print the top 5 of both teams
		bluedict , bluelist = ReadBlueCSV()
		yellowdict , yellowlist = ReadYellowCSV()
		print(str(len(bluelist)))
		maximumbluepage = math.ceil(len(bluelist)/3)
		if page > maximumbluepage:
			bluepage = maximumbluepage
		else:
			bluepage = page
		maximumyellowpage = math.ceil(len(yellowlist)/3)
		if page > maximumyellowpage:
			yellowpage = maximumyellowpage
		else:
			yellowpage = page
		#build blue part first
		start = 3 * (bluepage - 1)
		end = 3 * (bluepage - 1) + 3
		i = 0
		Message = Message + "__***Roster for the Blue Team***__ 💙\n"
		print("start: "+str(start))
		print("end: "+str(end))
		for i in range(start,end):
			print(i)
			if i > len(bluelist)-1:
				break
			print(i)
			combatant = bluelist[i]
			winloss = combatant.CalculateWinLoss()
			#first line is the character
			Message = Message + str(i+1) + ". **" + combatant.User + "** " + combatant.Avatar + ", Name: **"+combatant.Name+"**, Rank: **"+combatant.Rank+"**, Wins: **"+str(combatant.Wins)+"**, Losses: **"+ str(combatant.Losses)+"**, Ties: **"+str(combatant.Ties)+"**\n\n"
		Message = Message + "**Page** " + str(bluepage) + " of " + str(maximumbluepage) + "...\n\n"
		#build yellow roster
		Message = Message + "__***Roster for the Yellow Team***__ 💛\n"
		start = 3 * (yellowpage - 1)
		end = 3 * (yellowpage - 1) + 3
		i = 0
		for i in range(start,end):
			if i > len(yellowlist)-1:
				break
			combatant = yellowlist[i]
			winloss = combatant.CalculateWinLoss()
			#first line is the character
			Message = Message + str(i+1) + ". **" + combatant.User + "** " + combatant.Avatar + ", Name: **"+combatant.Name+"**, Rank: **"+combatant.Rank+"**, Wins: **"+str(combatant.Wins)+"**, Losses: **"+ str(combatant.Losses)+"**, Ties: **"+str(combatant.Ties)+"**\n\n"
		Message = Message + "**Page** " + str(yellowpage) + " of " + str(maximumyellowpage) + "..."
	Message = '>>> '+Message
	await ctx.send(Message)

@bot.command(description = "Finds and displays the character sheet of a player",
				brief = "Shows Character Sheet",
				aliases = ["CharacterSheet","Charactersheet","Character","character","char","Char","CS","cs","Cs","cS"])
async def charactersheet(ctx,username = None):
	guild = ctx.message.guild
	if username == None:
		await ctx.send("Did you forget to mention a user?")
		return
	if len(ctx.message.mentions) >= 1:
		mentioneduser = ctx.message.mentions[0]
		username = mentioneduser.name
	#Read the two rosters
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()

	#use FNmatch to search both rosters.
	#Both must be searched as there is no other way
	#search both nicknames and usernames, prioritize usernames first out of necessity
	found = False
	embedcolor = 0xffffff
	for fighter in bluelist:
		if found is False:
			if fnmatch.fnmatch(fighter.User,'*'+username+'*'):
				character = fighter
				embedcolor = 0x0080ff
				found = True
	for fighter in yellowlist:
		if found is False:
			if fnmatch.fnmatch(fighter.User,'*'+username+'*'):
				character = fighter
				embedcolor = 0xffff00
				found = True
				
	for fighter in bluelist:
		if found is False:
			if fnmatch.fnmatch(fighter.UserNick,'*'+username+'*'):
				character = fighter
				embedcolor = 0x0080ff
				found = True
	for fighter in yellowlist:
		if found is False:
			if fnmatch.fnmatch(fighter.UserNick,'*'+username+'*'):
				character = fighter
				embedcolor = 0xffff00
				found = True
	#Break if not found
	if found is False:
		await ctx.send("I was unable to find anyone on the roster with that name.")
		return
	
	#create embed from character
	#long Term, figure out how to display the emoji avatar
	embed = discord.Embed(title = "Character Sheet for "+character.User,color = embedcolor)
	embed.add_field(name="Character Name:", value = character.Name, inline = True)
	embed.add_field(name="Race:", value = character.Race, inline = True)
	embed.add_field(name="Class:", value = character.Class, inline = False)
	embed.add_field(name="Weapon:", value = character.Weapon, inline = True)
	embed.add_field(name="Rank:", value = character.Rank, inline = True)
	embed.add_field(name="Wins: " + str(character.Wins) + "\nLosses: " + str(character.Losses) + "\nTies: "+str(character.Ties),value = "Win Ratio: "+str(character.WinLoss), inline = False)
	#Thumbnail should be a link to the emoji image of discord.
	#emoji URLs are in the format of https://cdn.discordapp.com/emojis/<ID>.png (or svg for actual emojis)
	emojistring = character.Avatar
	if len(emojistring) > 5: #i.e. it's not just one emoji. larger than needed for failsafe!?
		emojiID = int(emojistring[len(emojistring)-19:len(emojistring)-1]) # ID is 18 characters long, ignoring the last bracket
		emoji = discord.utils.get(guild.emojis, id=emojiID)
		if emoji:
			embed.set_thumbnail(url=emoji.url)
	
	
	
	await ctx.send(embed=embed)

#@bot.command(description = "ignore me")
#async def test(ctx):
#	guild = ctx.message.guild
#	if CheckDM(ctx) is False:
#		await ctx.send("insufficient permissions to use this command")
#		return
#	emoji = discord.utils.get(guild.emojis, id=128512)
#	await ctx.send(emoji.url)
	
	

@bot.command(description = "Mentioned user's score in the combat registry is ",
				brief= 'DM only: Edits score',
				aliases = ["Edit","e","E"])
async def edit(ctx,user, wins=0, losses=0, ties=0):
	#change the wins and losses of the chosen dude, then just write back both lists into the csv.
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
		
	Player = ctx.message.mentions[0]
	ID = str(Player.id)
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()
	if ID not in bluedict and ID not in yellowdict:
		await ctx.send("I couldn't find "+Player.name+" on the roster. Are you sure they're registered?")
		return
	else:
		for fighter in bluelist:
			if fighter.ID == ID:
				fighter.Wins = wins
				fighter.Losses = losses
				fighter.Ties = ties
				await ctx.send("I found " + Player.name + " on the blue team.")
		for fighter in yellowlist:
			if fighter.ID == ID:
				fighter.Wins = wins
				fighter.Losses = losses
				fighter.Ties = ties
				await ctx.send("I found " + Player.name + " on the yellow team.")
		WriteYellowCSV(ctx,yellowlist)
		WriteBlueCSV(ctx,bluelist)
		
@bot.command(description = "Mentioned User is given a Win result which is logged in the combat registry file",
				brief= 'DM only: Gives win',
				aliases = ["Win","win","w","W","Winner"])
async def winner(ctx,user=None):
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
	Player = ctx.message.mentions[0]
	guild = ctx.message.guild
	ID = str(Player.id)
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()
	
	
	#We gotta do the ranking up now
	RanksDict = {7 : "Champion",6 : "Hero",15 : "Gladiator",4 : "Warrior",3 : "Myrmidon",2 : "Bloodletter",1 : "Brawler",0 : "Pit Dog"}
	
	if ID not in bluedict and ID not in yellowdict:
		await ctx.send("I couldn't find "+Player.name+" on the roster. Are you sure they're registered?")
		return
	else:
		for fighter in bluelist:
			if fighter.ID == ID:
				fighter.Wins = fighter.Wins + 1
				await ctx.send(Player.name +" on the blue team has been given a Win!")
				
				Rankwins = math.floor(fighter.Wins/2)
				print(Rankwins)
				
				rank = fighter.Rank
				truerank = RanksDict.get(Rankwins)
				
				oldrole = discord.utils.get(guild.roles, name = rank)
				newrole = discord.utils.get(guild.roles, name = truerank)
				
				if rank != truerank and truerank is not None:
					fighter.Rank = truerank
					try:
						await Player.remove_roles(oldrole)
					except:
						pass
					await Player.add_roles(newrole)
					await ctx.send("Congratulations " + str(fighter.User) + " on ranking up to " + str(truerank) + "!")
					print("I tried my best")
					
		for fighter in yellowlist:
			if fighter.ID == ID:
				fighter.Wins = fighter.Wins + 1
				await ctx.send(Player.name + " on the Yellow team has been given a Win!")
				
				Rankwins = math.floor(fighter.Wins/2)
				print(Rankwins)
				
				rank = fighter.Rank
				truerank = RanksDict.get(Rankwins)
				
				oldrole = discord.utils.get(guild.roles, name = rank)
				newrole = discord.utils.get(guild.roles, name = truerank)
				
				if rank != truerank and truerank is not None:
					fighter.Rank = truerank
					try:
						await Player.remove_roles(oldrole)
					except:
						pass
					await Player.add_roles(newrole)
					await ctx.send("Congratulations " + str(fighter.User) + " on ranking up to " + str(truerank) + "!")
					print("I tried my best")
					
		WriteYellowCSV(ctx,yellowlist)
		WriteBlueCSV(ctx,bluelist)
	
@bot.command(description = "Mentioned User is given a Loss result which is logged in the combat registry file.",
				brief= 'DM only: gives lose',
				aliases = ["Loser","lose","Lose","l","L"])
async def loser(ctx,user=None):
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
	Player = ctx.message.mentions[0]
	ID = str(Player.id)
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()
	if ID not in bluedict and ID not in yellowdict:
		await ctx.send("I couldn't find "+Player.name+" on the roster. Are you sure they're registered?")
		return
	else:
		for fighter in bluelist:
			if fighter.ID == ID:
				fighter.Losses = fighter.Losses + 1
				await ctx.send(Player.name +" on the Blue team has been given a Loss.")
		for fighter in yellowlist:
			if fighter.ID == ID:
				fighter.Losses = fighter.Losses + 1
				await ctx.send(Player.name +" on the Yellow team has been given a Loss.")
		WriteYellowCSV(ctx,yellowlist)
		WriteBlueCSV(ctx,bluelist)

@bot.command(description = "Mentioned User is given a Tie result which is logged in the file.",
				brief= "DM only: Gives tie",
				aliases = ["Tie","t","T"])
async def tie(ctx,user=None):
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
	Player = ctx.message.mentions[0]
	ID = str(Player.id)
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()
	if ID not in bluedict and ID not in yellowdict:
		await ctx.send("I couldn't find "+Player.name+" on the roster. Are you sure they're registered?")
		return
	else:
		for fighter in bluelist:
			if fighter.ID == ID:
				fighter.Ties = fighter.Ties + 1
				await ctx.send(Player.name +" on the Blue team has been given a Tie.")
		for fighter in yellowlist:
			if fighter.ID == ID:
				fighter.Ties = fighter.Ties + 1
				await ctx.send(Player.name +" on the Yellow team has been given a Tie.")
		WriteYellowCSV(ctx,yellowlist)
		WriteBlueCSV(ctx,bluelist)

@bot.command(aliases = ["Roll"],
				brief = "DM only: Rolls dice for the Arena",
				description = "Rolls one dice for both the Blue team and the Yellow team with a single roll.")
async def roll(ctx):
	if CheckDM(ctx) is False:
		await ctx.send("insufficient permissions to use this command")
		return
	YellowRoll = random.randint(1,10)
	BlueRoll = random.randint(1,10)

	if BlueRoll > YellowRoll:
		embedcolor = 0x0080ff
		Result = "💙Blue Wins!💙"
	elif YellowRoll > BlueRoll:
		embedcolor = 0xffff00
		Result = "💛Yellow Wins!💛"
	else:
		embedcolor = 0x00ff00
		Result = "💙It's a Draw!💛"
	
	BlueMessage = "rolled "+str(BlueRoll)+" on a d10"
	YellowMessage = "rolled "+str(YellowRoll)+" on a d10"
	
	if YellowRoll == 10:
		YellowMessage = YellowMessage + "\n		 Critical Hit!"
	elif YellowRoll == 1:
		YellowMessage = YellowMessage + "\n		 Critical Miss!"
	if BlueRoll == 10:
		BlueMessage = BlueMessage + "\n		 Critical Hit!"
	elif BlueRoll == 1:
		BlueMessage = BlueMessage + "\n		 Critical Miss!"
	
	print (str(BlueRoll) + str(YellowRoll))
	print(Result)
	print(embedcolor)
	embed=discord.Embed(title="The Fight is Begun 🎲", color=embedcolor)
	embed.add_field(name="Rolling for Yellow Team...", value=YellowMessage, inline=False)
	#if YellowRoll == 10:
	#	embed.add_field(name= ".", value="Critcal Hit!", inline=False)
	#elif YellowRoll == 1:
	#	embed.add_field(name= ".", value="Critcal Miss!", inline=False)
	embed.add_field(name="Rolling for Blue Team...", value=BlueMessage, inline=False)
	#if BlueRoll == 10:
	#	embed.add_field(name= ".", value="Critcal Hit!", inline=False)
	#elif BlueRoll == 1:
	#		embed.add_field(name= ".", value="Critcal Miss!", inline=False)
	embed.add_field(name="Result:", value= Result, inline=True)
	await ctx.send(embed=embed)
	

@bot.command(description = "Flips a coin to see which team has initiative",
				brief = "Flips a Coin",
				aliases = ["Flip", "flip", "F", "f"])
async def _Flip(ctx):
	#roll a random number between zero and 100
	#add 1
	#take mod 2
	#if 0, blue team has initiative, if 1, yellow team has initiative
	diceroll = random.randint(0,100)
	cointoss = diceroll % 2
	
	if cointoss == 1:
		embedcolor = 0x0080ff
		result = "The Coin Landed on Heads"
		result1 = "💙Blue Team has Initiative💙"
	else:
		embedcolor = 0xffff00
		result = "The Coin Landed on Tails"
		result1 = "💛Yellow Team has Initiative💛"
	embed=discord.Embed(title="Flipping a Coin to See Who Goes First <:septim:587292039905935511>", color=embedcolor)
	embed.add_field(name = result, value = result1, inline = False)
	await ctx.send(embed = embed)

@bot.command(description = "DM Only: Updates Roster",
				aliases = ["update","U","u"])
async def Update(ctx):
	bluedict , bluelist = ReadBlueCSV()
	yellowdict , yellowlist = ReadYellowCSV()
	WriteYellowCSV(ctx,yellowlist)
	WriteBlueCSV(ctx,bluelist)
	
	
@bot.command(description = "Tells the crab to fuck off")
async def crab(ctx):
	await ctx.send("Crab-bot sucks. Arenabot reigns supreme!")

#@bot.command(description = "Puts two mentioned users in the arena. Uses one player's team to determine which team to put them on. If both players are on the same team, will randomly assign teams.",
#				brief= "adds players to arena",
#				aliases = ["arena","a","A"])
##async def Arena(ctx,*user=None):
#	####We're going to do this later ###
#	#Checks the team of fighter one. Assigns both teams according to that, if fighter1 has no team, check if fighter 2 does. if neither do, return and tell the DM to figure it out himself.
#	#Add the in arena role accordingly
#	#change nickname to fit naming convetions. truncate if necessary.
#	if len(ctx.message.mentions) != 2
#		await ctx.send("You specified a number of combatants other than two. Functionality only works with 2 mentions.")
#		return
#	Fighter1 = ctx.message.mentions[0]#Most everything is done off of fighter1's situation. This is not perfect, but it should work *well enough*
#	Fighter2 = ctx.message.mentions[1] 
#	guild = ctx.message.guild
#	
#	Fighter1ID = Fighter1.id
#	Fighter2ID = Fighter2.id
#	
#	Fighter1Character = GetFighter(Fighter1ID)
#	Fighter2Character = GetFighter(Fighter2ID)
#	
#	
#	bluerole = discord.utils.get(guild.roles, name = "Blue Team")
#	blueinarenarole = discord.utils.get(guild.roles, name = "in arena (Blue Team)")
#	yellowrole = discord.utils.get(guild.roles, name = "Yellow Team")
#	yellowinarenarole =d iscord.utils.get(guild.roles, name = "in arena (Yellow Team)")
#	
#	#check team of fighter 1 now.
	
	

YellowRoster = {}
BlueRoster = {}

print("I should be online by now.")
print(len("😀"))
bot.run(TOKEN)