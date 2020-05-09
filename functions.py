from ftplib import FTP
import http.client
import json
import logging
import math
import os
import pprint
import random
import sys

import discord
import dotenv
import praw
import requests

dotenv.load_dotenv()
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
pp = pprint.PrettyPrinter(indent=4)

is_db_remote = False
remote_ftp_host = os.getenv('remote_db_ftp_host')
remote_ftp_user = os.getenv('remote_db_ftp_user')
remote_ftp_pw = os.getenv('remote_db_ftp_pw')
remote_ftp_path = os.getenv('remote_db_ftp_path')

def get_env_from_args():
	hostDict = {
		"local":"local machine",
		"aws":"AWS",
		"pi":"Raspberry Pi",
		"heroku":"Heroku"
	}
	for arg in sys.argv:
		if arg in hostDict:
			logging.info(f"Running on {hostDict[arg]}")
			return arg
	raise SystemExit("Unknown host, please specify it as an argument. Available hosts: local, aws, pi, heroku")

host = get_env_from_args()

if host == "local":
	is_db_remote = True
	db_filename = os.getenv('local_db_filename')
	chromedriver_path = os.getenv('local_chromedriver_path')
elif host == "aws":
	is_db_remote = True
	db_filename = os.getenv('aws_db_filename')
	chromedriver_path = os.getenv('aws_chromedriver_path')
elif host == "pi":
	db_filename = os.getenv('pi_db_filename')
	chromedriver_path = os.getenv('pi_chromedriver_path')
elif host == "heroku":
	is_db_remote = True
	db_filename = os.getenv('heroku_db_filename')
	chromedriver_path = os.getenv('CHROMEDRIVER_PATH')

def get_prefix(bot, message):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r') as json_file:
			data = json.load(json_file)
		#logging.DEBUG(f"prefix should be: {data['servers'][str(message.guild.id)]['prefix']}")
		return data["servers"][str(message.guild.id)]['prefix']

class CustomCtx:
  def __init__(self, guild, user):
  	self.guild = guild
  	self.author = user

def ftp_get(filename, host, path, user, pw):
	if is_db_remote:
		logging.debug(f"grabDB({filename})")
		logging.debug(f"ftp_get args: filename: {filename}, host: {host}, path: {path}, user: {user}, pw: {pw}")
		try:
			ftp = FTP(host)
			ftp.login(user = user, passwd = pw)
			ftp.cwd(path)
			localfile = open(filename, 'wb')
			ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
			ftp.quit()
			localfile.close()
			return True
		except Exception as e:
			logging.error(f"Error connecting to ftp: {pp.pformat(e)}")
	else:
		return True

#Function that sends the bot configuration JSON file to a remote FTP location
def ftp_put(filename, host, path, user, pw):
	if is_db_remote:
		logging.debug(f"placeDB({filename})")
		logging.debug(f"ftp_put args: filename: {filename}, host: {host}, path: {path}, user: {user}, pw: {pw}")
		try:
			ftp = FTP(host)
			ftp.login(user = user, passwd = pw)
			ftp.cwd(path)
			ftp.storbinary('STOR '+filename, open(filename, 'rb'))
			ftp.quit()
			return True
		except:
			logging.error("Error connecting to ftp")

def write_JSON(data, json_file):
	logging.debug(f"writingJSON({pp.pformat(data)}, {pp.pformat(json_file)})")
	json_file.seek(0)
	json.dump(data, json_file, indent=4)
	json_file.truncate()

def has_perms(ctx):
	if ctx.author == ctx.guild.owner or ctx.author.id == 435446721485733908:
		return True
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename) as json_file:
			data = json.load(json_file)
			for member in ctx.guild.members:
				for role in member.roles:
					if role.id in data["servers"][str(ctx.guild.id)]["privileged_roles"] and member.id == ctx.author.id:
						return True
		return False

#Function that checks if the message was sent as direct message to the bot
def ctx_is_dm(ctx):
	if ctx.guild is None:
		return True
	return False

#Function that pseudo-casts a string to boolean
def to_bool(val):
	if str(val) == "True":
		return True
	return False

def usable_mention(mention):
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


#works but things align too much to the left
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

def gen_espace():
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
		if eligibleChars:
			randInt = math.trunc(random.random()*len(eligibleChars))
			resList.append(eligibleChars[randInt-1])
		else:
			resList.append(random.choice(["	", "　"]))
	for i in [100, 200, 300]:
		resList.insert(i, '\n​' + u'\u200B' + "  ")
	return ''.join(resList)

def fetch_corona_info(elementDict, elementType, countryName, embed):
	for k in elementDict:
		elementDict[k] = elementType.find_element_by_xpath(elementDict[k]).text
		if len(elementDict[k]) == 0:
			elementDict[k] = "No info"
	embed.set_author(name = "Statistiques sur le Coronavirus en " + countryName + ", selon worldometers.info:")
	embed.description = "‣ Nombre de cas en cours: **"+elementDict["active_cases"]+"**\n‣ Nombre de cas critiques: **"+elementDict["critical_cases"]+"**\n‣ Nombre de cas total: **"+elementDict["total_cases"]+"**\n‣ Nombre de nouveaux cas aujourd'hui: **"+elementDict["new_cases"]+"**\n‣ Nombre de guéris: **"+elementDict["total_recovered"]+"**\n‣ Nombre total de morts: **"+elementDict["total_deaths"]+"**\n‣ Nombre de nouvelles morts aujourd'hui: **"+elementDict["new_deaths"]+"**"
	return embed

def random_meme(reddit):
	embed = discord.Embed(colour = discord.Color.blue())
	embed.set_author(name = "Dankmeme de hot")
	subreddit = reddit.subreddit("dankmemes")
	hot = subreddit.hot(limit=100)
	randInt = math.trunc(random.random()*99)
	target_post = None
	i = 0
	for post in hot:
		if i == randInt:
			target_post = post
		i += 1
	if random.random()*100 > 98:
		url = "https://www.youtube.com/watch?v=ub82Xb1C8os"
	else:
		url = f"https://www.reddit.com{target_post.permalink}"
	embed.description = f"[**{target_post.title}**]({url})	:arrow_up: {parse_reddit_post_score(target_post.score)}"
	if target_post.link_flair_text:
		embed.description += "\n_" + target_post.link_flair_text + "_"
	embed.description += "\nu/" + target_post.author.name
	embed.set_footer(text="From reddit.com/r/dankmemes")
	embed.set_image(url=target_post.url)
	return embed

def parse_reddit_post_score(score):
	if score < 1000:
		return str(score)
	elif score < 999999:
		return str("{:.2f}".format(score/1000))+"k"
	else:
		return str("{:.2f}".format(score/1000000))+"mio"

def parse_covid_num(num):
	if num == 'None':
		return '-'
	return num