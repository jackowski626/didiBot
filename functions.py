from variables import *
from secret import *
import ftplib
from ftplib import FTP
import json
import pprint
import copy
import os
import http.client
import random
import logging
import math
from functions import REMOTEFTPDB
from types import MethodType

class CustomCtx:
  def __init__(self, guild, user):
  	self.guild = guild
  	self.author = user

def grabDB(name):
	if REMOTEFTPDB:
		if DEBUG: print("grabDB("+name+")")
		try:
			ftp = FTP('ftpupload.net')
		except:
			print("error connecting to ftp")
			return False
		ftp.login(user = DB_USER, passwd = DB_PW)
		ftp.cwd('/htdocs/didiBot')
		filename = name
		localfile = open(filename, 'wb')
		ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
		ftp.quit()
		localfile.close()
		return True

#Function that sends the bot configuration JSON file to a remote FTP location
def placeDB(name):
	if REMOTEFTPDB:
		if DEBUG: print("placeDB("+name+")")
		try:
			ftp = FTP('ftpupload.net')
		except:
			print("error connecting to ftp")
			return False
		ftp.login(user = DB_USER, passwd = DB_PW)
		ftp.cwd('/htdocs/didiBot')
		filename = name
		ftp.storbinary('STOR '+filename, open(filename, 'rb'))
		ftp.quit()
		return True

def ftpGrab(name):
	if DEBUG: print("ftpGrab("+name+")")
	ftp = FTP('ftpupload.net')
	ftp.login(user = DB_USER, passwd = DB_PW)
	ftp.cwd('/htdocs/didiBot')
	filename = name
	localfile = open(filename, 'wb')
	ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
	ftp.quit()
	localfile.close()
def ftpPlace(name):
	if DEBUG: print("placeDB("+name+")")
	ftp = FTP('ftpupload.net')
	ftp.login(user = DB_USER, passwd = DB_PW)
	ftp.cwd('/htdocs/didiBot')
	filename = name
	ftp.storbinary('STOR '+filename, open(filename, 'rb'))
	ftp.quit()
def writeJSON(data, json_file):
	if DEBUG: print("writingJSON("+pp.pformat(data)+", "+pp.pformat(json_file)+")")
	json_file.seek(0)
	json.dump(data, json_file, indent=4)
	json_file.truncate()

def hasPerms(ctx):
	if ctx.author == ctx.guild.owner or ctx.author.id == 435446721485733908:
		return True
	grabDB(DB_FILENAME)
	with open(DB_FILENAME) as json_file:
		data = json.load(json_file)
		for member in ctx.guild.members:
			for role in member.roles:
				if role.id in data["servers"][str(ctx.guild.id)]["privileged_roles"] and member.id == ctx.author.id:
					return True
	return False

#Function that checks if the message was sent as direct message to the bot
def isMessageFromDM(ctx):
	if ctx.guild is None:
		return True
	return False

#Function that pseudo-casts a string to boolean
def toBool(val):
	if str(val) == "True":
		return True
	return False

#Functions that checks if the prefix which a command has been issued with is the prefix in a given guild
def guildHasThisPrefix(guild_id, prefix):
	guild_id = str(guild_id)
	grabDB(DB_FILENAME)
	with open(DB_FILENAME) as json_file:
		data = json.load(json_file)
		if prefix == data["servers"][guild_id]["prefix"]:
			return True
	return False

#WIP #Function that checks if the user does not have a pending response to the bot (for example issued the host command but didn't respond to the bot)
waitingResponsesDict = {"usersWaitingForNicknameConfirmation":"nom d'utilisateur Minecraft", "usersWaitingForFtpModeConfirmation":"mode ftp ou sftp","usersWaitingForFtpHostConfirmation":"hôte FTP","usersWaitingForFtpUserConfirmation":"nom d'utilisateur FTP","usersWaitingForFtpPasswordConfirmation":"mot de passe FTP","usersWaitingForFtpPathConfirmation":"chemin d'accès au fichier whitelist.json"}
def hasPendingResponses(user_id, bot):
	grabDB(DB_FILENAME)
	with open(DB_FILENAME) as json_file:
		data = json.load(json_file)
		for server in data["servers"]:
			for key in waitingResponsesDict:
				if key == "usersWaitingForNicknameConfirmation" and user_id in data["servers"][server]["hasRespondedWithValidUname"]:
					return False
				if user_id in data["servers"][server][key]:
					print("the user has pending stuff",waitingResponsesDict[key], bot.get_guild(int(server)).name)
					return (waitingResponsesDict[key], bot.get_guild(int(server)).name)
	return False

def stringBeginsWith(haystack, needle):
	for i in range(len(needle) - 1):
		if haystack[i] != needle[i]:
			return False
	return True

def usableMention(mention):
	res = ""
	for i in range(len(mention)):
		if mention[i] != "!":
			res += mention[i]
	return res

def strip(string, char=" "):
	res = ""
	for i in range(len(string)):
		if string[i] != char:
			res += string[i]
	return res

#31 lignes de 74 chars. 2294 chars

"""
def genEspace():
	resList = []
	chars = ["✦", "　", ".", "˚", ",", ":earth_africa:", ":earth_americas:", ":earth_asia:", ":sunny:", ":comet:", ":full_moon:", ":waning_gibbous_moon:", ":first_quarter_moon:", ":last_quarter_moon:", ":waning_crescent_moon:", ":waxing_crescent_moon:", ":crescent_moon:", ":new_moon:", ":ringed_planet:"]
	myweights = [200, 10000, 700, 500, 400, 6, 6, 6, 6, 6, 3, 3, 3, 3, 3, 3, 3, 3, 5]
	for i in range(350):
		resList.append(random.choices(chars, weights=myweights, k=1)[0])
	for i in [100, 200, 300]:
		resList.insert(i, '\n​n' + u'\u200B' + "  ")
	return ''.join(resList)
"""

def genEspace():
	resList = []
	chars = {
		"✦":70,
		"　":900,
		".":200,
		"˚":70,
		",":100,
		":earth_africa:":5,
		":earth_americas:":5,
		":earth_asia:":5,
		":sunny:":5,
		":comet:":5,
		":full_moon:":3,
		":waning_gibbous_moon:":3,
		":first_quarter_moon:":3,
		":last_quarter_moon:":3,
		":waning_crescent_moon:":3,
		":waxing_crescent_moon:":3,
		":crescent_moon:":3,
		":new_moon:":3,
		":ringed_planet:":4
	}
	for i in range(300):
		randInt = math.trunc(random.random()*1000)
		eligibleChars = []
		for char in chars:
			if chars[char] >= randInt:
				eligibleChars.append(char)
		if len(eligibleChars) > 0:
			randInt = math.trunc(random.random()*len(eligibleChars))
			print("len(eligibleChars: "+str(len(eligibleChars)))
			print("randInt: "+str(randInt))
			resList.append(eligibleChars[randInt-1])
		else:
			resList.append(random.choice(["	", "　"]))
	for i in [100, 200, 300]:
		resList.insert(i, '\n​' + u'\u200B' + "  ")
	return ''.join(resList)

def fetchCoronaInfo(elementDict, elementType, countryName, embed):
	for k in elementDict:
		elementDict[k] = elementType.find_element_by_xpath(elementDict[k]).text
		if len(elementDict[k]) == 0:
			elementDict[k] = "No info"
	embed.set_author(name = "Statistiques sur le Coronavirus en " + countryName + ", selon worldometers.info:")
	embed.description = "‣ Nombre de cas en cours: **"+elementDict["active_cases"]+"**\n‣ Nombre de cas critiques: **"+elementDict["critical_cases"]+"**\n‣ Nombre de cas total: **"+elementDict["total_cases"]+"**\n‣ Nombre de nouveaux cas aujourd'hui: **"+elementDict["new_cases"]+"**\n‣ Nombre de guéris: **"+elementDict["total_recovered"]+"**\n‣ Nombre total de morts: **"+elementDict["total_deaths"]+"**\n‣ Nombre de nouvelles morts aujourd'hui: **"+elementDict["new_deaths"]+"**"
	return embed