import asyncio
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

lang_path = ''

if host == 'local':
	is_db_remote = True
	db_filename = os.getenv('local_db_filename')
	chromedriver_path = os.getenv('local_chromedriver_path')
elif host == 'aws':
	is_db_remote = False
	db_filename = os.getenv('aws_db_filename')
	chromedriver_path = os.getenv('aws_chromedriver_path')
	lang_path = os.getenv('aws_lang_path')
elif host == 'pi':
	db_filename = os.getenv('pi_db_filename')
	chromedriver_path = os.getenv('pi_chromedriver_path')
elif host == 'heroku':
	is_db_remote = True
	db_filename = os.getenv('heroku_db_filename')
	chromedriver_path = os.getenv('CHROMEDRIVER_PATH')

async def testfunc(ctx):
	await ctx.channel.send("testttt")

def get_prefix(bot, message):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r') as json_file:
			data = json.load(json_file)
		#logging.DEBUG(f"prefix should be: {data['servers'][str(message.guild.id)]['prefix']}")
		if not ctx_is_dm(message):
			return data["servers"][str(message.guild.id)]['prefix']
		else:
			return '!'
	else:
		return '!'

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
		#print("db not remote, returning true")
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
					if role.id in data['servers'][str(ctx.guild.id)]['privileged_roles'] and member.id == ctx.author.id:
						return True
		return False

def can_ex_cmd(ctx):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename) as json_file:
			data = json.load(json_file)
			if data['servers'][str(ctx.guild.id)]['commands'][ctx.command.name]['privileged'] == 'false' or has_perms(ctx):
				if data['servers'][str(ctx.guild.id)]['commands'][ctx.command.name]['enabled'] == 'true':
					return True
				else:
					return False
			else:
				return False
	return False

def is_owner(ctx):
	if ctx.author.id == 435446721485733908:
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

def parse_u_pdp_url(url):
	if url.find("?width=") > 0:
		return url[:url.find("?width=")]
	else:
		return url

def random_meme(ctx, user_agent, client_id, client_secret, link=None):
	embed = discord.Embed(colour = discord.Color.blue())
	post = None
	if not link:
		r = requests.get('https://www.reddit.com/r/dankmemes/.json?limit=100', headers={"User-agent":user_agent, "client_id":client_id,"client_secret":client_secret})
		res = r.json()
		randInt = math.trunc(random.random()*99)
		i = 0
		for element in res['data']['children']:
			if i == randInt:
				post = element
			i += 1
	else:
		r = requests.get(f'{link}.json', headers={"User-agent":user_agent, "client_id":client_id,"client_secret":client_secret})
		res = r.json()
		post = res[0]['data']['children'][0]
	if random.random()*100 > 98:
		url = "https://www.youtube.com/watch?v=ub82Xb1C8os"
	else:
		url = f"https://www.reddit.com{post['data']['permalink']}"
		#print(url)
	r = requests.get(f"https://www.reddit.com/u/{post['data']['author']}/about.json", headers={"User-agent"	:user_agent, "client_id":client_id,"client_secret":client_secret})
	res_pdp = r.json()
	embed.set_author(name = f"u/{post['data']['author']}", icon_url=parse_u_pdp_url(res_pdp['data']['icon_img']))
	if link:
		embed.description = f"{localize(ctx, 'meme_issued_by', vars={'issuer':ctx.author.mention})}\n[**{post['data']['title']}**]({url})\n{parse_reddit_post_score(post['data']['ups'])} <:updoot:709528623958327317>" #<:updoot:709528623958327317>
	else:
		embed.description = f"[**{post['data']['title']}**]({url})\n{parse_reddit_post_score(post['data']['ups'])} <:updoot:709528623958327317>"
	if post['data']['link_flair_text']:
		embed.description += f"\n_{translate_emoji(post['data']['link_flair_text'])}_"
	embed.set_footer(text=f"{localize(ctx, 'number_of_awards')} {post['data']['total_awards_received']}, {localize(ctx, 'upvote_ratio')} {post['data']['upvote_ratio']}")
	embed.set_image(url=post['data']['url'])
	r = requests.get(f'https://www.reddit.com/r/dankmemes/about.json', headers={"User-agent":user_agent, "client_id":client_id,"client_secret":client_secret})
	res_sub_icon = r.json()
	embed.set_thumbnail(url=res_sub_icon['data']['icon_img'])
	print(parse_u_pdp_url(res_pdp['data']['icon_img']))
	return embed

def parse_reddit_post_score(score):
	if score < 1000:
		return str(score)
	elif score < 999999:
		return str("{:.2f}".format(score/1000))+"k"
	else:
		return str("{:.2f}".format(score/1000000))+"mio"

def parse_covid_num(num):
	if not num:
		return '-'
	return num

#vars = {'var1':'jour', 'var2':'bon'}
#'string_to_translate':['{var2}', '{var1}', " Jean, ca va?"]
#	=> "bonjour Jean, ca va?"
def localize(ctx, string, vars = None, random = False):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		modifier = None
		with open(db_filename, 'r') as json_file:
			data = json.load(json_file)
			lang = data['servers'][str(ctx.guild.id)]['lang']
			if data['servers'][str(ctx.guild.id)]['lang_modifier'] != 'none':
				modifier = data['servers'][str(ctx.guild.id)]['lang_modifier']
		with open(f'{lang_path}{lang}.lang', 'r') as json_file:
			lang_json = json.load(json_file)
		if string == 'country_name':
			if not modifier:
				return lang_json['countries'][vars['country']]['name']
			elif modifier == 'uwu':
				return lang_json['countries'][vars['country']]['name'].replace('r', 'w').replace('R', 'W')
		elif string == 'country_declined':
			print("vars: "+pp.pformat(vars))
			if lang_json['countries'][vars['country']]['declined'] == '-':
				print("declined is2: "+lang_json['countries'][vars['country']]['declined'])
				if not modifier:
					return lang_json['countries'][vars['country']]['name']
				elif modifier == 'uwu':
					return lang_json['countries'][vars['country']]['name'].replace('r', 'w').replace('R', 'W')
			else:
				if not modifier:
					return lang_json['countries'][vars['country']]['declined']
				elif modifier == 'uwu':
					return lang_json['countries'][vars['country']]['declined'].replace('r', 'w').replace('R', 'W')
		elif string == 'country_prefix':
			#print("pre is: " +lang_json['countries'][vars['country']]['pre'])
			if not modifier:
				return lang_json['countries'][vars['country']]['pre']
			elif modifier == 'uwu':
				return lang_json['countries'][vars['country']]['pre'].replace('r', 'w').replace('R', 'W')
		elif string == 'month_name':
			if not modifier:
				return lang_json['months'][vars['month']]
			elif modifier == 'uwu':
				return lang_json['months'][vars['month']].replace('r', 'w').replace('R', 'W')
		elif vars:
			#print("vars: "+pp.pformat(vars))
			res = []
			for element in lang_json[string]:
				if element[0] == '{':
					res.append(vars[element[1:len(element)-1]])
				else:
					res.append(element)
			if not modifier:
				return ''.join(str(elem) for elem in res)
			elif modifier == 'uwu':
				return ''.join(str(elem) for elem in res).replace('r', 'w').replace('R', 'W')
		else:
			if random:
				if not modifier:
					return random.choice(lang_json[string])
				elif modifier == 'uwu':
					return random.choice(lang_json[string]).replace('r', 'w').replace('R', 'W')
			else:
				if not modifier:
					return lang_json[string]
				elif modifier == 'uwu':
					return lang_json[string].replace('r', 'w').replace('R', 'W')

def get_locale(ctx):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r') as json_file:
			data = json.load(json_file)
			return data['servers'][str(ctx.guild.id)]['lang']

def get_modifier(ctx):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r') as json_file:
			data = json.load(json_file)
			return data['servers'][str(ctx.guild.id)]['lang_modifier']

def apply_lang_modifier(ctx, message):
	modifier = get_modifier(ctx)
	if modifier == 'uwu':
		return message.replace('r', 'w').replace('R', 'W')
	else:
		return message

#for testing purposes only. Can only be executed by the owner of the bot.
def crash(ctx):
	if is_owner(ctx):
	    try:
	        crash(ctx)
	    except:
	        crash(ctx)

def translate_emoji(string): #TODO
	for i in range(len(string)):
		if string[i] == ':' and string[i+1:].find(':') != -1:
			with open(f'{lang_path}emojis.lang', 'r') as json_file:
				emoji_json = json.load(json_file)
				print(f"looking for emoji {string[i+1:string.find(':')]}")
				for key in emoji_json:
					if key == string[i+1:string.find(':')]:
						print("found emoji")
						break
	return string

#.cmd -privileged true
def set_privilege(ctx):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r+') as json_file:
			data = json.load(json_file)
			res_bool = ctx.message.content[14 + len(ctx.command.name):]
			if res_bool == 'true':
				data['servers'][str(ctx.guild.id)]['commands'][ctx.command.name]['privileged'] = 'true'
				return True
			elif res_bool == 'false':
				data['servers'][str(ctx.guild.id)]['commands'][ctx.command.name]['privileged'] = 'false'
				return False
			else:
				return 'error'
			write_JSON(data, json_file)
		ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)

def enable_cmd(ctx):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r+') as json_file:
			data = json.load(json_file)
			data['servers'][str(ctx.guild.id)]['commands'][ctx.command.name]['enabled'] = 'true'
			write_JSON(data, json_file)
		ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)

def disable_cmd(ctx):
	if ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r+') as json_file:
			data = json.load(json_file)
			data['servers'][str(ctx.guild.id)]['commands'][ctx.command.name]['enabled'] = 'false'
			write_JSON(data, json_file)
		ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)

async def shared_cmd_actions(ctx):
	msg = ctx.message.content[len(ctx.command.name)+2:]
	print("msg: "+msg)
	if msg.startswith('-privileged') and has_perms(ctx):
		print("issued -privileged")
		if set_privilege(ctx) == 'error':
			await ctx.channel.send(localize(ctx, 'command_privileged_syntax'))
		elif set_privilege(ctx) == False:
			await ctx.channel.send(localize(ctx, 'command_privileged_off', vars = {'name':ctx.command.name}))
		else:
			await ctx.channel.send(localize(ctx, 'command_privileged_on', vars = {'name':ctx.command.name}))
	elif msg.startswith('-enable') and has_perms(ctx):
		enable_cmd(ctx)
		await ctx.channel.send(localize(ctx, 'command_enabled', vars = {'name':ctx.command.name}))
	elif msg.startswith('-disable') and has_perms(ctx):
		disable_cmd(ctx)
		await ctx.channel.send(localize(ctx, 'command_disabled', vars = {'name':ctx.command.name}))

def has_args(ctx):
	for arg in ['-help', '-privileged', '-enable', '-disable']:
		if ctx.message.content[len(ctx.command.name)+2:].startswith(arg):
			return True
	return False