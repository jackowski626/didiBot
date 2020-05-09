#invite: https://discordapp.com/api/oauth2/authorize?client_id=659120033519108115&permissions=2147482867&scope=bot
import copy
import datetime
import http.client
import json
import logging
import os
import pprint
import random
import sys

from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import dotenv
from fuzzywuzzy import fuzz
import praw
import requests
#import selenium
#from selenium import webdriver

import functions as fn


dotenv.load_dotenv()
#logging.basicConfig(filename='./bot_log.log',format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


"""log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s", 
                          datefmt="%Y-%m-%d - %H:%M:%S")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
fh = logging.FileHandler("mylog.log", "w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(ch)
log.addHandler(fh)"""


##Variables

#Selenium options
#options = selenium.webdriver.chrome.options.Options()
#options.add_argument('--headless')
#options.add_argument('--no-sandbox')

logging.debug(f"client agent: {os.getenv('reddit_user_agent')}")

#Misc
pp = pprint.PrettyPrinter(indent=4)
reddit = praw.Reddit(client_id=os.getenv('reddit_client_id'),client_secret=os.getenv('reddit_client_secret'), user_agent=os.getenv('reddit_user_agent'))
#reddit = praw.Reddit(client_id='reddit_client_id',client_secret='reddit_client_secret', user_agent='reddit_user_agent')
is_db_remote = False
remote_ftp_host = os.getenv('remote_db_ftp_host')
remote_ftp_user = os.getenv('remote_db_ftp_user')
remote_ftp_pw = os.getenv('remote_db_ftp_pw')
remote_ftp_path = os.getenv('remote_db_ftp_path')

#Host dependent vars
host = fn.get_env_from_args()
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

#For random bot messages
random_greet = ["bonsoeir", "bonsoir, ici c'est le COFOP", "yo mec", "bonjour", "bsoir, tu me dois une girafe"]
random_goodbye = ["Arrivederci", "Goodnight girl, I'll see you tomorrow", "last seen online: 6 years ago", "stop! you can't ju"]
error_messages = ["Je pense que mon foie a lâché cette fois", "Ambulance! vite!", "Aidez-moi! je ne sens plus ma byte"]

#Custom relay
author_id = 435446721485733908
default_channel_id = 445985682410831882
bar_id = 445983404832587805

#Rapid API
rapid_api_key = os.getenv('rapid_api_key')

#Other
country_dict = {'usa':'USA','america':'USA','amerique':'USA','china':'China','germany':'Germany','france':'France','switzerland':'Switzerland','suisse':'Switzerland','netherlands':'Netherlands','belgium':'Belgium','canada':'Canada','norway':'Norway','sweden':'Sweden','brazil':'Brazil','malaysia':'Malaysia','ireland':'Ireland','luxembourg':'Luxembourg','japan':'Japan','pakistan':'Pakistan','south africa':'South Africa','saudi arabia':'Saudi Arabia','finland':'Finland','greece':'Greece','india':'India','singapore':'Singapore','panama':'Panama','argentina':'Argentina','mexico':'Mexico','peru':'Peru','qatar':'Qatar','hong kong':'Hong Kong','colombia':'Colombia','iraq':'Iraq','lebanon':'Lebanon','lithuania':'Lithuania','uae':'UAE','hungary':'Hungary','latvia':'Latvia','andorra':'Andorra','uruguay':'Uruguay','costa rica':'Costa Rica','ukraine':'Ukraine','san marino':'San Marino','jordan':'Jordan','albania':'Albania','azerbaijan':'Azerbaijan','cyprus':'Cyprus','faeroe islands':'Faeroe Islands','kazakhstan':'Kazakhstan','oman':'Oman','brunei':'Brunei','sri lanka':'Sri Lanka','ivory coast':'Ivory Coast','mauritius':'Mauritius','palestine':'Palestine','uzbekistan':'Uzbekistan','georgia':'Georgia','channel islands':'Channel Islands','guadeloupe':'Guadeloupe','trinidad and tobago':'Trinidad and Tobago','bolivia':'Bolivia','liechtenstein':'Liechtenstein','paraguay':'Paraguay','mayotte':'Mayotte','bangladesh':'Bangladesh','macao':'Macao','french polynesia':'French Polynesia','polynesie francaise':'French Polynesia','aruba':'Aruba','jamaica':'Jamaica','togo':'Togo','madagascar':'Madagascar','uganda':'Uganda','bermuda':'Bermuda','maldives':'Maldives','tanzania':'Tanzania','equatorial guinea':'Equatorial Guinea','mali':'Mali','saint martin':'Saint Martin','greenland':'Greenland','eswatini':'Eswatini','guinea':'Guinea','namibia':'Namibia','curaçao':'Curaçao','antigua and barbuda':'Antigua and Barbuda','mozambique':'Mozambique','benin':'Benin','laos':'Laos','guyana':'Guyana','fiji':'Fiji','myanmar':'Myanmar','syria':'Syria','angola':'Angola','vatican city':'Vatican City','sudan':'Sudan','car':'CAR','liberia':'Liberia','saint lucia':'Saint Lucia','somalia':'Somalia','anguilla':'Anguilla','british virgin islands':'British Virgin Islands','saint kitts and nevis':'Saint Kitts and Nevis','libya':'Libya','st. vincent grenadines':'St. Vincent Grenadines','italy':'Italy','spain':'Spain','iran':'Iran','uk':'UK','united kingdom':'UK','s. korea':'S. Korea','south corea':'S. Korea','austria':'Austria','turkey':'Turkey','portugal':'Portugal','australia':'Australia','israel':'Israel','czechia':'Czechia','denmark':'Denmark','chile':'Chile','ecuador':'Ecuador','poland':'Poland','romania':'Romania','thailand':'Thailand','indonesia':'Indonesia','russia':'Russia','iceland':'Iceland','philippines':'Philippines','diamond princess':'Diamond Princess','slovenia':'Slovenia','croatia':'Croatia','dominican republic':'Dominican Republic','estonia':'Estonia','serbia':'Serbia','egypt':'Egypt','bahrain':'Bahrain','algeria':'Algeria','new zealand':'New Zealand','morocco':'Morocco','armenia':'Armenia','bulgaria':'Bulgaria','slovakia':'Slovakia','taiwan':'Taiwan','bosnia and herzegovina':'Bosnia and Herzegovina','tunisia':'Tunisia','kuwait':'Kuwait','north macedonia':'North Macedonia','moldova':'Moldova','burkina faso':'Burkina Faso','vietnam':'Vietnam','réunion':'Réunion','malta':'Malta','ghana':'Ghana','senegal':'Senegal','venezuela':'Venezuela','cambodia':'Cambodia','afghanistan':'Afghanistan','belarus':'Belarus','cameroon':'Cameroon','martinique':'Martinique','cuba':'Cuba','montenegro':'Montenegro','honduras':'Honduras','nigeria':'Nigeria','kyrgyzstan':'Kyrgyzstan','gibraltar':'Gibraltar','drc':'DRC','rwanda':'Rwanda','monaco':'Monaco','kenya':'Kenya','isle of man':'Isle of Man','french guiana':'French Guiana','guatemala':'Guatemala','barbados':'Barbados','zambia':'Zambia','ethiopia':'Ethiopia','new caledonia':'New Caledonia','el salvador':'El Salvador','djibouti':'Djibouti','dominica':'Dominica','mongolia':'Mongolia','niger':'Niger','bahamas':'Bahamas','cayman islands':'Cayman Islands','haiti':'Haiti','suriname':'Suriname','gabon':'Gabon','grenada':'Grenada','seychelles':'Seychelles','eritrea':'Eritrea','cabo verde':'Cabo Verde','zimbabwe':'Zimbabwe','montserrat':'Montserrat','st. barth':'St. Barth','nepal':'Nepal','congo':'Congo','gambia':'Gambia','bhutan':'Bhutan','chad':'Chad','mauritania':'Mauritania','sint maarten':'Sint Maarten','nicaragua':'Nicaragua','belize':'Belize','guinea-bissau':'Guinea-Bissau','turks and caicos':'Turks and Caicos','papua new guinea':'Papua New Guinea','timor-leste':'Timor-Leste'}
date_dict = {'01':'janvier','02':'février','03':'mars','04':'avril','05':'mai','06':'juin','07':'juillet','08':'août','09':'septembre','10':'octobre','11':'novembre','12':'decembre'}
world_list = ['global','world','monde','warudo','zawarudo','za warudo']

bot = commands.Bot(command_prefix = fn.get_prefix)
bot.remove_command("help")

#Some bot vars
default_prefix = "!"
bot.executing_repetitive_task = False
bot.cancelled_command = False

#driver = selenium.webdriver.Chrome(chromedriver_path, options = options)

#logging.debug(f"driver: {pp.pformat(driver)}")


########---------
#EVENTS
########---------

@bot.event
async def on_ready():
	logging.warning(f'{bot.user} shall serve his master!')

@bot.event
async def on_guild_join(guild):
	if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r+') as json_file:
			data = json.load(json_file)
			#Add a new server entry to the json
			data["servers"][str(guild.id)] = {"server_id":guild.id,"prefix":default_prefix,"privileged_roles":[],"statusMessagesReservedToPrivileged":"False","greetedUsers": [],"notDisturbUsers": [],"goodbyedUsers": [],"lastUsedEspace": {}}
			#Send message which pings a role with admin privileges and says that the bot should be configured
			validRole = None
			for role in guild.roles:
				if role.permissions.administrator:
					data["servers"][str(guild.id)]["privileged_roles"].append(role.id)
					validRole = role
					break
			for channel in guild.text_channels:
				if channel.permissions_for(guild.me).send_messages:
					if validRole:
						await channel.send(guild.owner.mention+" "+role.mention+" Bonjour, je viens d'arriver sur le serveur. Je suis un bot de Jacques et je n'ai pas de but précis, proposez lui des idées de commandes.")
					else:
						await channel.send(guild.owner.mention+" Bonjour, je viens d'arriver sur le serveur. Je suis un bot de Jacques et je n'ai pas de but précis, proposez lui des idées de commandes.")
					break
			fn.write_JSON(data, json_file)
	else:
		logging.error("Could not connect to DB")
	fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)

@bot.event
async def on_guild_remove(guild):
	if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
		with open(db_filename, 'r+') as json_file:
			data = json.load(json_file)
			del data["servers"][str(guild.id)]
			fn.write_JSON(data, json_file)
		fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)

@bot.event
async def on_message(message):
	#print("message.guild.id: "+str(message.guild.id))
	#print("message.author.id: "+str(message.author.id))
	##print("message.content: "+message.content)
	#print("bot.user.mention: "+bot.user.mention)
	if message.author == bot.user:
		return
	#changer de prefixe avec le ping
	##print("usableMention: "+usableMention(bot.user.mention))
	if len(fn.usable_mention(message.content)) == len(bot.user.mention) and fn.usable_mention(message.content).startswith(bot.user.mention):
		print("bot has been pinged")
		prefix = "[Error while fetching prefix]" + random.choice(error_messages)
		if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
			with open(db_filename) as json_file:
				data = json.load(json_file)
				prefix = data["servers"][str(message.guild.id)]["prefix"]
			await message.channel.send("Mon préfixe est:\n> " + prefix)
		else:
			await message.channel.send("[FTP error] " + random.choice(error_messages))
	elif fn.usable_mention(message.content).startswith(bot.user.mention):
		pingMessage = message.content[len(bot.user.mention)+1:len(message.content)]
		pingMessageNoSpaces = fn.strip(pingMessage)
		if pingMessageNoSpaces.startswith("prefix"):
			newPrefix = pingMessageNoSpaces[6:len(pingMessageNoSpaces)]
			if len(newPrefix) > 0 and not fn.ctx_is_dm(message) and fn.has_perms(message):
				async with message.channel.typing():
					if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
						with open(db_filename, 'r+') as json_file:
							data = json.load(json_file)
							data["servers"][str(message.guild.id)]["prefix"] = newPrefix
							fn.write_JSON(data, json_file)
						fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
						bot.command_prefix.append(newPrefix)
						logging.debug("bot prefixes: " + pp.pformat(bot.command_prefix))
						await message.channel.send("Le préfixe a été changé en " + newPrefix)
					else:
						await message.channel.send("[FTP error] " + random.choice(error_messages))
					
	#reagir aux msg de arlind
	if message.author.id == 309052661569814528 and message.guild.id == 445983404832587805:
		await message.add_reaction("<:bescherelle:694172190282874961>")
	#reagir aux msg de jacques
	#if message.author.id == 435446721485733908 and message.guild.id == 445983404832587805:
	#	await message.add_reaction("<:bescherelle:694172190282874961>")
	if message.content.lower().startswith('salut'):
		#channel = client.get_channel(-)
		await message.channel.send(random.choice(random_greet))
	if message.content.lower().startswith('je suis'):
		#channel = client.get_channel(-)
		await message.channel.send(f"Salut {message.content[8:]}, je suis papa")
	if message.content.lower().startswith("i'm"):
		#channel = client.get_channel(-)
		await message.channel.send(f"Hello {message.content[4:]}, I'm dad")
	if message.content.lower() == "nice":
		#await message.channel.send("nice")
		if random.randint(0,20)<20:
			#updoot
			await message.add_reaction("⬆️")
		else:
			#downdoot
			await message.add_reaction("⬇")
	if message.author.id == author_id and fn.ctx_is_dm(message) and stringBeginsWith(message.content, "relay"):
		await bot.get_channel(default_channel_id).send(message.content[5:len(message.content)])
	await bot.process_commands(message)
	#technologie mee6 word filter pass
	if message.author.id == author_id and message.channel.guild.id == bar_id and "mec" in message.content.lower():
		await message.channel.send(f"[{message.author.display_name}]: \n> {message.content}\n_MecPass™_")
	if fuzz.ratio(message.content.lower(), 'rape me') > 80:
		await message.channel.send("tg")

##@bot.event
##async def on_member_update(before, after):
	#'activities','activity','add_roles','avatar','avatar_url','avatar_url_as','ban','block','bot','color','colour','create_dm','created_at','default_avatar','default_avatar_url','desktop_status','discriminator','display_name','dm_channel','edit','fetch_message','guild','guild_permissions','history','id','is_avatar_animated','is_blocked','is_friend','is_on_mobile','joined_at','kick','mention','mentioned_in','mobile_status','move_to','mutual_friends','name','nick','permissions_in','pins','premium_since','profile','relationship','remove_friend','remove_roles','roles','send','send_friend_request','status','system','top_role','trigger_typing','typing','unban','unblock','voice','web_status'
	##print("--------")
	#print(pp.pformat(dir(after)))
	##print(pp.pformat(after._user.display_name))
	##print(pp.pformat(after.status))
	#if after.:
		#pass

########---------
#COMMANDS
########---------

@bot.command(pass_context=True)
async def help(ctx):
	embed = discord.Embed(colour = discord.Color.blue())
	embed.set_author(name = "Help")
	embed.add_field(name="add_privileged", value="Donne aux rôles mentionnés les permissions pour les fonctions avancées du bot", inline=False)
	embed.add_field(name="remove_privileged", value="Enlève aux rôles mentionnés les permissions pour les fonctions avancées du bot", inline=False)
	embed.add_field(name="complimente", value="Affirme qui est le patron", inline=False)
	embed.add_field(name="corona", value="Affiche les statistiques sur le coronavirus en Suisse. Si invoqué avec un nom de pays en anglais, les statistiques seront pour ce pays. Exemples d'utilisation:\n_.corona_\n_.corona italy_\nCette commande est aussi disponible sous les alias suivants: coronal, plague", inline=False)
	embed.add_field(name="motd", value="Invoqué sans arguments, affiche le message du jour. Si invoqué avec un message, ce message sera mis comme nouveau message du jour.\nExemple d'utilisation:\n_.motd il fait beau aujourd'hui_", inline=False)
	embed.add_field(name="prefix", value="Si invoqué sans arguments, affiche le préfixe du bot. Si invoqué avec un préfixe, met le préfixe à jour.\nExemple d'utilisation:\n_.prefix !_\nNote: si le préfixe est le même pour un autre bot et cette commande change le préfixe pour les deux, vous pouvez mentionner le bot comme ceci pour changer son préfixe:\n_@Didier prefix !_\nSimplement mentionner le bot affiche son préfixe actuel", inline=False)
	embed.add_field(name="say", value="Fait répéter le bot ce qui suit la commande", inline=False)
	embed.add_field(name="repeat", value="Fait répéter le bot ce qui suit la commande plusieurs fois\nExemple d'utilisation:\n_.repeat tg 420_", inline=False)
	embed.add_field(name="espace", value="Remplit le chat d'étoiles ✦\nCette commande peut aussi être répétée comme ceci:\n_.espace 69_", inline=False)
	embed.add_field(name="urban", value="Cherche le mot donné dans Urban Dictionnary\nExemple d'utilisation:\n_.urban hanus_", inline=False)
	embed.add_field(name="dankmeme", value="Affiche un meme aléatoire parmi les 100 memes les plus hot de r/dankmemes", inline=False)
	embed.add_field(name="cancel", value="Permet d'annuler la commande _.repeat_ ou _.espace_", inline=False)
	await ctx.author.send(embed=embed)

@bot.command()
async def say(ctx, *, arg):
	if fn.has_perms(ctx):
		await ctx.send(arg)

@bot.command()
async def motd(ctx, *, motd=None):
	if motd:
		motd = motd.replace("'", "\\'").replace('"', '\\"')
		if fn.ftp_get("motd.json", remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
			with open("motd.json", 'r+') as json_file:
				motd_data = json.load(json_file)
				motd_data["motd"] = motd
				fn.write_JSON(motd_data, json_file)
			fn.ftp_put("motd.json", remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
			await ctx.send("Le message du jour a été mis à jour: http://jacques.ml/didiBot/motd.php")
		else:
			await ctx.send(f"Erreur FTP {random.choice(error_messages)}")
	else:
		if fn.ftp_get("motd.json", remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
			with open("motd.json") as json_file:
				motd_data = json.load(json_file)
				motd = motd_data["motd"]
				await ctx.channel.send(f"Le message du jour est: {motd}")
		else:
			await ctx.send(f"Erreur FTP {random.choice(error_messages)}")

@bot.command()
async def complimente(ctx):
	await ctx.send("Cédric, t'es beau")

@bot.command(pass_context=True)
async def add_privileged(ctx, *, message):
	if fn.has_perms(ctx):
		print("issued add_privileged")
		if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
			with open(db_filename, 'r+') as json_file:
				data = json.load(json_file)
				logging.debug(f"message {message}")
				addedRoles = []
				#print(role.mention)
				for role in ctx.guild.roles:
					if role.mention in message and role.id not in data["servers"][str(ctx.guild.id)]["privileged_roles"]:
						data["servers"][str(ctx.guild.id)]["privileged_roles"].append(role.id)
						addedRoles.append(role.name)
					elif role.mention in message and role.id in data["servers"][str(ctx.guild.id)]["privileged_roles"]:
						await ctx.channel.send(f"Le rôle {role.name} est déjà privilégié")
				fn.write_JSON(data, json_file)
			fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
			if len(addedRoles) > 0:
				if len(addedRoles) == 1:
					await ctx.channel.send(f"Le rôle **{addedRoles[0]}** a été ajouté à la liste des rôles avec accès privilégié au bot")
				else:
					await ctx.channel.send(f"Les rôles **{'**, **'.join(addedRoles)}** ont été ajoutés à la liste des rôles avec accès privilégié au bot")
	else:
		await message.channel.send(f"Erreur FTP {random.choice(error_messages)}")
@add_privileged.error
async def info_error(ctx, error):
	if isinstance(error, commands.errors.MissingRequiredArgument):
		await ctx.channel.send("Veuillez mentionner au moins un rôle")

#Command used to remove roles from the privileged_roles list
@bot.command(pass_context=True)
async def remove_privileged(ctx, *, message):
	print("called remove_privileged")
	if fn.has_perms(ctx):
		if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
			with open(db_filename, 'r+') as json_file:
				data = json.load(json_file)
				removedRoles = []
				for role in ctx.guild.roles:
					#print(f"message: {message.content}, mention: {role.mention}, role id: {role.id}, privileges_roles: {data['servers'][str(ctx.guild.id)]['privileged_roles']}")
					if role.mention in message and role.id in data["servers"][str(ctx.guild.id)]["privileged_roles"]:
						data["servers"][str(ctx.guild.id)]["privileged_roles"].remove(role.id)
						removedRoles.append(role.name)
				if len(removedRoles) > 0:
					if len(removedRoles) == 1:
						await ctx.channel.send(f"Le rôle **{removedRoles[0]}** a été supprimé de la liste des rôles avec accès privilégié au bot")
					else:
						await ctx.channel.send(f"Les rôles **{'**, **'.join(removedRoles)}** ont été supprimés de la liste des rôles avec accès privilégié au bot")
					fn.write_JSON(data, json_file)
				else:
					await ctx.chnnel.send("Aucun rôle n'était dans la liste")
			fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
			if len(removedRoles) < message.mentions:
				notRemoved = []
				for role in message.mentions:
					notRemoved.append(role.name)
				if len(notRemoved) == 1:
					await ctx.channel.send(f"Le rôle {notRemoved[0]} n'a pas été supprimé de la liste de rôles avec accès privilégié au bot")
				else:
					await ctx.channel.send(f"Les rôles {', '.join(notRemoved)} n'ont pas été supprimés de la liste de rôles avec accès privilégié au bot")
		else:
			await ctx.channel.send(f"Erreur FTP {random.choice(error_messages)}")
@remove_privileged.error
async def info_error(ctx, error):
	if isinstance(error, commands.errors.MissingRequiredArgument):
		await ctx.channel.send("Veuillez mentionner au moins un rôle")

@bot.command(pass_context=True)
async def set_prefix(ctx, message):
	if fn.has_perms(ctx):
		if not " " in message:
			bot.command_prefix.remove(ctx.prefix)
			bot.command_prefix.append(message)
			logging.debug(f"bot prefixes: {pp.pformat(bot.command_prefix)}")
			if fn.ftp_get(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw):
				with open(db_filename, 'r+') as json_file:
					data = json.load(json_file)
					data["servers"][str(ctx.guild.id)]["prefix"] = message
					fn.write_JSON(data, json_file)
				fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
				await ctx.channel.send(f"Le préfixe a été changé en {message}")
			else:
				await ctx.channel.send(f"Erreur FTP {random.choice(error_messages)}")
		else:
			await ctx.channel.send("Le nouveau préfixe ne doit pas comporter d'espaces")
	else:
		await ctx.channel.send("Vous n'avez pas les permissions nécessaires pour exécuter cette commande")
@set_prefix.error
async def info_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		logging.error("Bad argument(s) for prefix command")

@bot.command(pass_context=True, aliases=['coronal', 'plague'])
async def corona(ctx, *, country=None):
	#countries = ['China','Italy','USA','Spain','Germany','Iran','France','Switzerland','S. Korea','UK','Netherlands','Austria','Belgium','Norway','Canada','Portugal','Sweden','Australia','Brazil','Malaysia','Denmark','Ireland','Poland','Greece','Indonesia','Philippines','Hong Kong','Iraq','Algeria','China','Italy','USA','Spain','Germany','Iran','France','S. Korea','Switzerland','UK','Netherlands','Austria','Belgium','Norway','Canada','Portugal','Sweden','Brazil','Australia','Malaysia','Denmark','Ireland','Poland','Greece','Indonesia','Philippines','Hong Kong','Iraq','Algeria']
	#country_dict = {'china':'china','italy':'italy','usa':'us','spain':'spain','germany':'germany','iran':'iran','france':'france','switzerland':'switzerland','s. korea':'south-korea','uk':'uk','netherlands':'netherlands','austria':'austria','belgium':'belgium','norway':'norway','canada':'canada','portugal':'portugal','sweden':'sweden','australia':'brazil','brazil':'australia','malaysia':'malaysia','denmark':'denmark','ireland':'ireland','poland':'poland','greece':'greece','indonesia':'indonesia','philippines':'philippines','hong kong':'china-hong-kong-sar','iraq':'iraq','algeria':'algeria','china':'china','italy':'italy','usa':'us','spain':'spain','germany':'germany','iran':'iran','france':'france','s. korea':'south-korea','switzerland':'switzerland','uk':'uk','netherlands':'netherlands','austria':'austria','belgium':'belgium','norway':'norway','canada':'canada','portugal':'portugal','sweden':'sweden','brazil':'brazil','australia':'australia','malaysia':'malaysia','denmark':'denmark','ireland':'ireland','poland':'poland','greece':'greece','indonesia':'indonesia','philippines':'philippines','hong kong':'china-hong-kong-sar','iraq':'iraq','algeria':'algeria','america':'us','united kingdom':'uk', 'amerique':'us'}
	embed = discord.Embed(colour = discord.Color.blue())
	embed.set_thumbnail(url='https://github.com/jackowski626/didiBot/blob/master/images/corona.png?raw=true')
	
	#logging.debug(f"r: {r}")
	if country:
		if country.lower() not in world_list:
			url = 'https://covid-193.p.rapidapi.com/statistics'
			headers = {'x-rapidapi-host': 'covid-193.p.rapidapi.com','x-rapidapi-key': rapid_api_key}
			res = requests.request("GET", url, headers=headers).json()['response']
			#print(res)
			selectedCountry = None
			for element in res:
				if not selectedCountry:
					selectedCountry = element
				elif fuzz.ratio(country.lower(), element['country'].lower()) > fuzz.ratio(country.lower(), selectedCountry['country'].lower()): 	 	 	
					selectedCountry = element
			embed.description = f"**Statistiques sur le Coronavirus en {selectedCountry['country']}**			\n\n‣ Nouveaux cas confirmés: **{parse_covid_num(selectedCountry['cases']['new'])}**\n‣ Cas actifs: **{parse_covid_num(selectedCountry['cases']['active'])}**\n‣ Cas critiques: **{parse_covid_num(selectedCountry['cases']['critical'])}**\n‣ Total de cas confirmés: **{parse_covid_num(selectedCountry['cases']['total'])}**\n‣ Nouvelles morts: **{parse_covid_num(selectedCountry['deaths']['new'])}**\n‣ Total de morts: **{parse_covid_num(selectedCountry['deaths']['total'])}**\n‣ Nombre de cas guéris: **{parse_covid_num(selectedCountry['cases']['recovered'])}**\n‣ Total de tests effectués: **{parse_covid_num(selectedCountry['tests']['total'])}**"
		elif country.lower() in world_list:
			res = requests.get('https://api.covid19api.com/summary').json()
			selectedCountry = {'Country': '[the world](https://www.youtube.com/watch?v=7ePWNmLP0Z0)','NewConfirmed': res['Global']['NewConfirmed'],'TotalConfirmed': res['Global']['TotalConfirmed'],'NewDeaths': res['Global']['NewDeaths'],'TotalDeaths': res['Global']['TotalDeaths'],'NewRecovered': res['Global']['NewRecovered'],'TotalRecovered': res['Global']['TotalRecovered'],'Date': '-'}
			embed.description = f"**Statistiques sur le Coronavirus dans le [monde](https://www.youtube.com/watch?v=7ePWNmLP0Z0)**			\n\n‣ Nombre de cas confirmés total: **{selectedCountry['TotalConfirmed']}**\n‣ Nombre de morts total: **{selectedCountry['TotalDeaths']}**\n‣ Nombre de guérisons total: **{selectedCountry['TotalRecovered']}**"
	else:
		url = 'https://covid-193.p.rapidapi.com/statistics'
		headers = {'x-rapidapi-host': 'covid-193.p.rapidapi.com','x-rapidapi-key': rapid_api_key}
		res = requests.request("GET", url, headers=headers, params= {"country":"Switzerland"}).json()['response'][0]
		embed.description = f"**Statistiques sur le Coronavirus en Suisse**			\n\n‣ Nouveaux cas confirmés: **{res['cases']['new']}**\n‣ Cas actifs: **{res['cases']['active']}**\n‣ Cas critiques: **{res['cases']['critical']}**\n‣ Total de cas confirmés: **{res['cases']['total']}**\n‣ Nouvelles morts: **{res['deaths']['new']}**\n‣ Total de morts: **{res['deaths']['total']}**\n‣ Nombre de cas guéris: **{res['cases']['recovered']}**\n‣ Total de tests effectués: **{res['tests']['total']}**"

	#else:
	#	await ctx.channel.send(f"Erreur, réponse vide. {random.choice(error_messages)}")
	#embed.description = f"**Statistiques sur le Coronavirus en {selectedCountry['Country']}			**\n\n‣ Nombre de nouveaux cas confirmés: **{selectedCountry['NewConfirmed']}**\n‣ Nombre de cas confirmés total: **{selectedCountry['TotalConfirmed']}**\n‣ Nombre de nouvelles morts: **{selectedCountry['NewDeaths']}**\n‣ Nombre de morts total: **{selectedCountry['TotalDeaths']}**\n‣ Nombre de nouvelles guérisons: **{selectedCountry['NewRecovered']}**\n‣ Nombre de guérisons total: **{selectedCountry['TotalRecovered']}**"
	#embed.set_footer(text=f"Date des résultats: {selectedCountry['Date'][0:10]}")
	await ctx.channel.send(embed=embed)
#shuts the bot down
@bot.command(pass_context=True)
async def s(ctx):
    if ctx.author.id == author_id:
        await ctx.channel.send(random.choice(random_goodbye))
        await bot.logout()
    elif ctx.author.id != author_id:
    	await ctx.channel.send("T'as cru t'avais le droit")

@bot.command(pass_context=True)
async def espace(ctx, repeat = 1):
	if not bot.executing_repetitive_task and (repeat <= 5 or repeat > 5 and fn.has_perms(ctx)):
		if not fn.has_perms(ctx):
			logging.debug("Doesn't have perms")
			with open(db_filename, 'r+') as json_file:
				data = json.load(json_file)
				if str(ctx.author.id) not in data["servers"][str(ctx.guild.id)]["lastUsedEspace"]:
					logging.debug("user doesn't have a timestamp")
					data["servers"][str(ctx.guild.id)]["lastUsedEspace"][str(ctx.author.id)] = datetime.datetime.now().timestamp()
					fn.write_JSON(data, json_file)
					fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
				else:
					logging.debug("user has a timestamp")
					lastDate = data["servers"][str(ctx.guild.id)]["lastUsedEspace"][str(ctx.author.id)]
					dateDelta = datetime.datetime.now().timestamp() - lastDate
					logging.debug(f"dateDelta.seconds: {str(dateDelta)}")
					if dateDelta / 60 < 5:
						logging.debug("Delta < 5 min")
						await ctx.send(f"{ctx.author.mention} vous devez attendre {str(5 - math.trunc(dateDelta / 60))} minute(s) avant de pouvoir utiliser cette commande")
						return
					else:
						logging.debug("delta > min")
						data["servers"][str(ctx.guild.id)]["lastUsedEspace"] = datetime.datetime.now().timestamp()
						fn.write_JSON(data, json_file)
						fn.ftp_put(db_filename, remote_ftp_host, remote_ftp_path, remote_ftp_user, remote_ftp_pw)
		if not bot.executing_repetitive_task:
			bot.executing_repetitive_task = True
			for i in range(repeat):
				if not bot.cancelled_command:
					await ctx.channel.send(fn.gen_espace())
				else:
					bot.cancelled_command = False
					break
			if not bot.cancelled_command:
				bot.executing_repetitive_task = False
				bot.cancelled_command = False
		else:
			await ctx.send("Déjà en traîn d'exécuter une commande répétitive")
	elif guildHasThisPrefix(ctx.guild.id, ctx.prefix) and repeat > 5 and not fn.has_perms(ctx):
		await ctx.send(f"{ctx.author.mention} vous n'avez pas le droit de répéter cette commande plus de cinq fois")

@bot.command(pass_context=True)
async def repeat(ctx, repeat, *, arg):
	if not bot.executing_repetitive_task and fn.has_perms(ctx):
		logging.debug(f"bot.executing_repetitive_task is: {str(bot.executing_repetitive_task)}")
		bot.executing_repetitive_task = True
		logging.debug("setting bot.executing_repetitive_task True")
		for i in range(int(repeat)):
			if not bot.cancelled_command:
				await ctx.send(arg)
			else:
				bot.cancelled_command = False
				break
		if not bot.cancelled_command:
			bot.executing_repetitive_task = False
			bot.cancelled_command = False
			logging.debug("setting bot.executing_repetitive_task false")
	elif bot.executing_repetitive_task:
		await ctx.send("Déjà en traîn d'exécuter une commande répétitive")

@bot.command(pass_context=True)
async def cancel(ctx):
	if guildHasThisPrefix(ctx.guild.id, ctx.prefix):
		bot.cancelled_command = True
		bot.executing_repetitive_task = False
		await ctx.send("Commande répétitive précédente annulée")

@bot.command()
async def urban(ctx, *, arg):
	embed = discord.Embed(colour = discord.Color.blue())
	embed.set_thumbnail(url="https://antisemitism.uk/wp-content/uploads/2020/02/Urban-Dictionary.png")

	url = 'https://mashape-community-urban-dictionary.p.rapidapi.com/define'
	querystring = {"term":arg}
	headers = {
	    'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
	    'x-rapidapi-key': rapid_api_key
	    }
	response = requests.request("GET", url, headers=headers, params=querystring)
		
	if len(response.json()['list']) > 0:
		res = response.json()['list'][0]

		word = res['word']
		definition = fn.strip(fn.strip(res['definition'], '['), ']')
		example = fn.strip(fn.strip(res['example'], '['), ']')
		url = res['permalink']
		author = res['author']
		written_on = res['written_on'] #example: '2020-01-17T00:00:00.000Z'
		upvotes = res['thumbs_up']
		downvotes = res['thumbs_down']

		day = int(written_on[8:10])
		month = date_dict[written_on[5:7]]
		year = written_on[0:4]
		contributor = f"par {author}, le {day} {month} {year}"

		if 'bean' in word.lower() or 'bean' in definition.lower():
			embed.set_author(name = "Définition du Dictionnaire Urbean:")
		else:
			embed.set_author(name = "Définition du Dictionnaire Urbain:")
		
		embed.description = f"[**{word}**]({url})\n{definition}\n_{example}_\n\n{contributor}\n{upvotes}:thumbsup: {downvotes}:thumbsdown:"
		
		await ctx.send(embed=embed)
	else:
		url = f"https://www.urbandictionary.com/define.php?term={arg}"
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		tryThese = soup.find_all("div", class_="try-these")[0]
		w1 = tryThese.find_next("li")
		w2 = w1.find_next("li")
		w3 = w2.find_next("li")
		w4 = w3.find_next("li")
		embed.set_author(name="Le mot \"" + arg + "\" n'a pas été trouvé")
		embed.description = "**Vous vouliez peut-être rechercher un de ces mots:**\n‣ " + w1.getText() + "\n‣ " + w2.getText() + "\n‣ " + w3.getText() + "\n‣ " + w4.getText()
		#await ctx.send("Le mot \"**" + arg + "**\" n'a pas été trouvé")
		await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def dankmeme(ctx, url = None):
	await ctx.channel.send(embed=fn.random_meme(reddit))



#@bot.command(pass_context=True)
#async def s(ctx):


########---------
#RUN
########---------

token = os.getenv("TOKEN")
bot.run(token)
