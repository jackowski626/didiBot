#invite: https://discordapp.com/api/oauth2/authorize?client_id=659120033519108115&permissions=2147482867&scope=bot
import os
import discord
import random
from discord.ext import commands
from discord.utils import get
from random import randint
#from bs4 import BeautifulSoup
import requests
import json
import pprint
import copy
import http.client
import paramiko
import logging
#import youtube_dl
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from variables import *
from functions import *

from bs4 import BeautifulSoup
from selenium import webdriver

import sys
import praw

#logging.basicConfig(level=logging.DEBUG)

########---------
#some functions that can't really go into functions.py
########---------

##


#Getting prefixes from all registered guilds
prefixesDict = {};
prefixesList = ["!"]
grabDB(DB_FILENAME)
with open(DB_FILENAME) as json_file:
	data = json.load(json_file)
	for server in data["servers"]: #returns a dict where key is server id and value is its prefix
		prefixesDict[server] = data["servers"][server]["prefix"]
		prefixesList.append(data["servers"][server]["prefix"])

#client = discord.Client()
bot = commands.Bot(command_prefix=prefixesList)

bot.remove_command("help")

driver = webdriver.Chrome(CHROMEDRIVER_PATH,options=options)
print("driver: "+pp.pformat(driver))


########---------
#EVENTS
########---------

@bot.event
async def on_ready():
	if DEBUG:print(f'{bot.user} shall serve his master!'); return
	print(f'{bot.user} has connected to Discord!')


@bot.event
async def on_guild_join(guild):
	if DEBUG:
		for channel in guild.text_channels:
			print("channel perms: "+pp.pformat(channel.permissions_for(guild.me))) 
			print("send_messages: "+pp.pformat(channel.permissions_for(guild.me).send_messages))

	grabDB(DB_FILENAME)
	with open(DB_FILENAME, 'r+') as json_file:
		data = json.load(json_file)
		#Add a new server entry to the json
		data["servers"][str(guild.id)] = {"server_id":guild.id,"prefix":DEFAULT_PREFIX,"privileged_roles":[],"voice_channel":"none"}
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
		writeJSON(data, json_file)
	placeDB(DB_FILENAME)

@bot.event
async def on_guild_remove(guild):
	grabDB(DB_FILENAME)
	with open(DB_FILENAME, 'r+') as json_file:
		data = json.load(json_file)
		del data["servers"][str(guild.id)]
		writeJSON(data, json_file)
	placeDB(DB_FILENAME)

@bot.event
async def on_message(message):
	#print("message.guild.id: "+str(message.guild.id))
	#print("message.author.id: "+str(message.author.id))
	print("message.content: "+message.content)
	#print("bot.user.mention: "+bot.user.mention)
	# we do not want the bot to reply to itself
	if message.author == bot.user:
		return
	#changer de prefixe avec le ping
	print("usableMention: "+usableMention(bot.user.mention))
	if len(usableMention(message.content)) == len(bot.user.mention) and stringBeginsWith(usableMention(message.content), bot.user.mention):
		print("bot has been pinged")
		prefix = "[Error while fetching prefix]" + random.choice(errorMessages)
		grabDB(DB_FILENAME)
		with open(DB_FILENAME) as json_file:
			data = json.load(json_file)
			prefix = data["servers"][str(message.guild.id)]["prefix"]
		await message.channel.send("Mon préfixe est:\n> " + prefix)
	elif stringBeginsWith(usableMention(message.content), bot.user.mention):
		pingMessage = message.content[len(bot.user.mention)+1:len(message.content)]
		pingMessageNoSpaces = strip(pingMessage)
		#await message.channel.send("Vous avez dit \n" + pingMessage)
		print("pingMessageNoSpaces: "+pingMessageNoSpaces)
		if stringBeginsWith(pingMessageNoSpaces, "prefix"):
			newPrefix = pingMessageNoSpaces[6:len(pingMessageNoSpaces)]
			#await message.channel.send("le nouveau préfixe serait: \n> " + newPrefix)
			if len(newPrefix) > 0 and not isMessageFromDM(message) and hasPerms(message):
				async with message.channel.typing():
					if not grabDB(DB_FILENAME):
						print("bruh")
						await message.channel.send("[FTP error] " + random.choice(errorMessages))
					with open(DB_FILENAME, 'r+') as json_file:
						data = json.load(json_file)
						bot.command_prefix.remove(data["servers"][str(message.guild.id)]["prefix"])
						data["servers"][str(message.guild.id)]["prefix"] = newPrefix
						writeJSON(data, json_file)
					placeDB(DB_FILENAME)
					bot.command_prefix.append(newPrefix)
					if DEBUG: print("bot prefixes: " + pp.pformat(bot.command_prefix))
					await message.channel.send("Le préfixe a été changé en " + newPrefix)
	#reagir aux msg de arlind
	if message.author.id == 309052661569814528 and message.guild.id == 445983404832587805:
		await message.add_reaction("<:bescherelle:694172190282874961>")
	#reagir aux msg de jacek
	#if message.author.id == 435446721485733908 and message.guild.id == 445983404832587805:
	#	await message.add_reaction("<:bescherelle:694172190282874961>")
	if message.content.lower().startswith('salut'):
		#channel = client.get_channel(-)
		await message.channel.send(random.choice(randomGreet))
	if message.content.lower().startswith('je suis'):
		#channel = client.get_channel(-)
		await message.channel.send("Salut "+message.content[8:]+", je suis papa")
	if message.content.lower().startswith("i'm"):
		#channel = client.get_channel(-)
		await message.channel.send("Hello "+message.content[4:]+", I'm dad")
	if message.content.lower() == "nice":
		await message.channel.send("nice")
		if randint(0,20)<20:
			#updoot
			await message.add_reaction("⬆️")
		else:
			#downdoot
			await message.add_reaction("⬇")
	if message.author.id == authorID and isMessageFromDM(message) and stringBeginsWith(message.content, "relay"):
		await bot.get_channel(defaultChannelID).send(message.content[5:len(message.content)])
	await bot.process_commands(message)
	#technologie mee6 word filter pass
	if message.author.id == authorID and message.channel.guild.id == barID and "mec" in message.content.lower():
		await message.channel.send("[" + message.author.display_name + "]: \n> " + message.content + "\n_MecPass™_")


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
	embed.add_field(name="addPrivileged", value="Donne aux rôles mentionnés les permissions pour les fonctions avancées du bot", inline=False)
	embed.add_field(name="removePrivileged", value="Enlève aux rôles mentionnés les permissions pour les fonctions avancées du bot", inline=False)
	embed.add_field(name="complimente", value="Affirme qui est le patron", inline=False)
	embed.add_field(name="corona", value="Affiche les statistiques sur le coronavirus en Suisse. Si invoqué avec un nom de pays en anglais, les statistiques seront pour ce pays. Exemples d'utilisation:\n_.corona_\n_.corona italy_\nCette commande est aussi disponible sous les alias suivants: coronal, plague", inline=False)
	embed.add_field(name="motd", value="Invoqué sans arguments, affiche le message du jour. Si invoqué avec un message, ce message sera mis comme nouveau message du jour.\nExemple d'utilisation:\n_.motd il fait beau aujourd'hui_", inline=False)
	embed.add_field(name="prefix", value="Si invoqué sans arguments, affiche le préfixe du bot. Si invoqué avec un préfixe, met le préfixe à jour.\nExemple d'utilisation:\n_.prefix !_\nNote: si le préfixe est le même pour un autre bot et cette commande change le préfixe pour les deux, vous pouvez mentionner le bot comme ceci pour changer son préfixe:\n_@Didier prefix !_\nSimplement mentionner le bot affiche son préfixe actuel", inline=False)
	embed.add_field(name="say", value="Fait répéter le bot ce qui suit la commande", inline=False)
	embed.add_field(name="repeat", value="Fait répéter le bot ce qui suit la commande plusieurs fois\nExemple d'utilisation:\n_.repeat tg 420_", inline=False)
	embed.add_field(name="espace", value="Remplit le chat d'étoiles ✦\nCette commande peut aussi être répétée comme ceci:\n_.espace 69_", inline=False)
	embed.add_field(name="urban", value="Cherche le mot donné dans Urban Dictionnary\nExemple d'utilisation:\n_.urban hanus_", inline=False)
	embed.add_field(name="dankmeme", value="Affiche un meme aléatoire parmi les 100 memes les plus hot de r/dankmemes", inline=False)
	await ctx.author.send(embed=embed)

@bot.command(pass_context=True)
async def perms(ctx):
	if DEBUG and not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix) and hasPerms(ctx):
		for channel in ctx.guild.text_channels:
			print("channel perms: "+pp.pformat(channel.permissions_for(ctx.guild.me)))
			print("send_messages: "+pp.pformat(channel.permissions_for(ctx.guild.me).send_messages))

@bot.command()
async def say(ctx, *, arg):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix):
		await ctx.send(arg)

@bot.command()
async def motd(ctx, *, motd=None):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix):
		if motd:
			motd = motd.replace("'", "\\'").replace('"', '\\"')
			ftpGrab("motd.json")
			with open("motd.json", 'r+') as json_file:
				motd_data = json.load(json_file)
				motd_data["motd"] = motd
				writeJSON(motd_data, json_file)
			ftpPlace("motd.json")
			await ctx.send("Le message du jour a été mis à jour: http://jacques.ml/didiBot/motd.php")
		else:
			ftpGrab("motd.json")
			with open("motd.json") as json_file:
				motd_data = json.load(json_file)
				motd = motd_data["motd"]
				await ctx.channel.send("Le message du jour est: "+motd)

@bot.command()
async def complimente(ctx):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix):
		await ctx.send("Cédric, t'es beau")

@bot.command(pass_context=True)
async def addPrivileged(ctx, *, message):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix) and hasPerms(ctx):
		grabDB(DB_FILENAME)
		with open(DB_FILENAME, 'r+') as json_file:
			data = json.load(json_file)
			print("message "+message)
			addedRoles = []
			for role in ctx.guild.roles:
				#print("hmm role")
				print("mention "+role.mention)
				if role.mention in message:
					data["servers"][str(ctx.guild.id)]["privileged_roles"].append(role.id)
					addedRoles.append(role.name)
			joinSeparator = ", "
			await ctx.channel.send("Le(s) rôle(s) "+joinSeparator.join(removedRoles)+" a(ont) été supprimé(s) de la liste des rôles avec accès privilégié au bot")
			writeJSON(data, json_file)
		placeDB(DB_FILENAME)
@addPrivileged.error
async def info_error(ctx, error):
	if isinstance(error, commands.errors.MissingRequiredArgument):
		await ctx.channel.send("Veuillez mentionner au moins un rôle")

#Command used to remove roles from the privileged_roles list
@bot.command(pass_context=True)
async def removePrivileged(ctx, *, message):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix) and hasPerms(ctx):
		grabDB(DB_FILENAME)
		with open(DB_FILENAME, 'r+') as json_file:
			data = json.load(json_file)
			removedRoles = []
			for role in ctx.guild.roles:
				if role.mention in message and role.id in data["servers"][str(ctx.guild.id)]["privileged_roles"]:
					data["servers"][str(ctx.guild.id)]["privileged_roles"].remove(role.id)
					removedRoles.append(role.name)
			joinSeparator = ", "
			await ctx.channel.send("Le(s) rôle(s) "+joinSeparator.join(removedRoles)+" a(ont) été supprimé(s) de la liste des rôles avec accès privilégié au bot")
			writeJSON(data, json_file)
		placeDB(DB_FILENAME)
@removePrivileged.error
async def info_error(ctx, error):
	if isinstance(error, commands.errors.MissingRequiredArgument):
		await ctx.channel.send("Veuillez mentionner au moins un rôle")

@bot.command(pass_context=True)
async def prefix(ctx, message):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix) and hasPerms(ctx):
		if not " " in message:
			bot.command_prefix.remove(ctx.prefix)
			bot.command_prefix.append(message)
			if DEBUG: print("bot prefixes: "+pp.pformat(bot.command_prefix))
			grabDB(DB_FILENAME)
			with open(DB_FILENAME, 'r+') as json_file:
				data = json.load(json_file)
				data["servers"][str(ctx.guild.id)]["prefix"] = message
				writeJSON(data, json_file)
			placeDB(DB_FILENAME)
			await ctx.channel.send("Le préfixe a été changé en "+message)
		else:
			await ctx.channel.send("Le nouveau préfixe ne doit pas comporter d'espaces")
	else:
		await ctx.channel.send("Vous n'avez pas les permissions nécessaires pour exécuter cette commande")
@prefix.error
async def info_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		print("Bad argument(s) for prefix command")

@bot.command(pass_context=True, aliases=['coronal', 'plague'])
async def corona(ctx, *, country=None):
	#countries = ['China','Italy','USA','Spain','Germany','Iran','France','Switzerland','S. Korea','UK','Netherlands','Austria','Belgium','Norway','Canada','Portugal','Sweden','Australia','Brazil','Malaysia','Denmark','Ireland','Poland','Greece','Indonesia','Philippines','Hong Kong','Iraq','Algeria','China','Italy','USA','Spain','Germany','Iran','France','S. Korea','Switzerland','UK','Netherlands','Austria','Belgium','Norway','Canada','Portugal','Sweden','Brazil','Australia','Malaysia','Denmark','Ireland','Poland','Greece','Indonesia','Philippines','Hong Kong','Iraq','Algeria']
	#countryDict = {'china':'china','italy':'italy','usa':'us','spain':'spain','germany':'germany','iran':'iran','france':'france','switzerland':'switzerland','s. korea':'south-korea','uk':'uk','netherlands':'netherlands','austria':'austria','belgium':'belgium','norway':'norway','canada':'canada','portugal':'portugal','sweden':'sweden','australia':'brazil','brazil':'australia','malaysia':'malaysia','denmark':'denmark','ireland':'ireland','poland':'poland','greece':'greece','indonesia':'indonesia','philippines':'philippines','hong kong':'china-hong-kong-sar','iraq':'iraq','algeria':'algeria','china':'china','italy':'italy','usa':'us','spain':'spain','germany':'germany','iran':'iran','france':'france','s. korea':'south-korea','switzerland':'switzerland','uk':'uk','netherlands':'netherlands','austria':'austria','belgium':'belgium','norway':'norway','canada':'canada','portugal':'portugal','sweden':'sweden','brazil':'brazil','australia':'australia','malaysia':'malaysia','denmark':'denmark','ireland':'ireland','poland':'poland','greece':'greece','indonesia':'indonesia','philippines':'philippines','hong kong':'china-hong-kong-sar','iraq':'iraq','algeria':'algeria','america':'us','united kingdom':'uk', 'amerique':'us'}
	countryDict = {'usa':'USA','america':'USA','amerique':'USA','china':'China','germany':'Germany','france':'France','switzerland':'Switzerland','suisse':'Switzerland','netherlands':'Netherlands','belgium':'Belgium','canada':'Canada','norway':'Norway','sweden':'Sweden','brazil':'Brazil','malaysia':'Malaysia','ireland':'Ireland','luxembourg':'Luxembourg','japan':'Japan','pakistan':'Pakistan','south africa':'South Africa','saudi arabia':'Saudi Arabia','finland':'Finland','greece':'Greece','india':'India','singapore':'Singapore','panama':'Panama','argentina':'Argentina','mexico':'Mexico','peru':'Peru','qatar':'Qatar','hong kong':'Hong Kong','colombia':'Colombia','iraq':'Iraq','lebanon':'Lebanon','lithuania':'Lithuania','uae':'UAE','hungary':'Hungary','latvia':'Latvia','andorra':'Andorra','uruguay':'Uruguay','costa rica':'Costa Rica','ukraine':'Ukraine','san marino':'San Marino','jordan':'Jordan','albania':'Albania','azerbaijan':'Azerbaijan','cyprus':'Cyprus','faeroe islands':'Faeroe Islands','kazakhstan':'Kazakhstan','oman':'Oman','brunei':'Brunei','sri lanka':'Sri Lanka','ivory coast':'Ivory Coast','mauritius':'Mauritius','palestine':'Palestine','uzbekistan':'Uzbekistan','georgia':'Georgia','channel islands':'Channel Islands','guadeloupe':'Guadeloupe','trinidad and tobago':'Trinidad and Tobago','bolivia':'Bolivia','liechtenstein':'Liechtenstein','paraguay':'Paraguay','mayotte':'Mayotte','bangladesh':'Bangladesh','macao':'Macao','french polynesia':'French Polynesia','polynesie francaise':'French Polynesia','aruba':'Aruba','jamaica':'Jamaica','togo':'Togo','madagascar':'Madagascar','uganda':'Uganda','bermuda':'Bermuda','maldives':'Maldives','tanzania':'Tanzania','equatorial guinea':'Equatorial Guinea','mali':'Mali','saint martin':'Saint Martin','greenland':'Greenland','eswatini':'Eswatini','guinea':'Guinea','namibia':'Namibia','curaçao':'Curaçao','antigua and barbuda':'Antigua and Barbuda','mozambique':'Mozambique','benin':'Benin','laos':'Laos','guyana':'Guyana','fiji':'Fiji','myanmar':'Myanmar','syria':'Syria','angola':'Angola','vatican city':'Vatican City','sudan':'Sudan','car':'CAR','liberia':'Liberia','saint lucia':'Saint Lucia','somalia':'Somalia','anguilla':'Anguilla','british virgin islands':'British Virgin Islands','saint kitts and nevis':'Saint Kitts and Nevis','libya':'Libya','st. vincent grenadines':'St. Vincent Grenadines','italy':'Italy','spain':'Spain','iran':'Iran','uk':'UK','united kingdom':'UK','s. korea':'S. Korea','south corea':'S. Korea','austria':'Austria','turkey':'Turkey','portugal':'Portugal','australia':'Australia','israel':'Israel','czechia':'Czechia','denmark':'Denmark','chile':'Chile','ecuador':'Ecuador','poland':'Poland','romania':'Romania','thailand':'Thailand','indonesia':'Indonesia','russia':'Russia','iceland':'Iceland','philippines':'Philippines','diamond princess':'Diamond Princess','slovenia':'Slovenia','croatia':'Croatia','dominican republic':'Dominican Republic','estonia':'Estonia','serbia':'Serbia','egypt':'Egypt','bahrain':'Bahrain','algeria':'Algeria','new zealand':'New Zealand','morocco':'Morocco','armenia':'Armenia','bulgaria':'Bulgaria','slovakia':'Slovakia','taiwan':'Taiwan','bosnia and herzegovina':'Bosnia and Herzegovina','tunisia':'Tunisia','kuwait':'Kuwait','north macedonia':'North Macedonia','moldova':'Moldova','burkina faso':'Burkina Faso','vietnam':'Vietnam','réunion':'Réunion','malta':'Malta','ghana':'Ghana','senegal':'Senegal','venezuela':'Venezuela','cambodia':'Cambodia','afghanistan':'Afghanistan','belarus':'Belarus','cameroon':'Cameroon','martinique':'Martinique','cuba':'Cuba','montenegro':'Montenegro','honduras':'Honduras','nigeria':'Nigeria','kyrgyzstan':'Kyrgyzstan','gibraltar':'Gibraltar','drc':'DRC','rwanda':'Rwanda','monaco':'Monaco','kenya':'Kenya','isle of man':'Isle of Man','french guiana':'French Guiana','guatemala':'Guatemala','barbados':'Barbados','zambia':'Zambia','ethiopia':'Ethiopia','new caledonia':'New Caledonia','el salvador':'El Salvador','djibouti':'Djibouti','dominica':'Dominica','mongolia':'Mongolia','niger':'Niger','bahamas':'Bahamas','cayman islands':'Cayman Islands','haiti':'Haiti','suriname':'Suriname','gabon':'Gabon','grenada':'Grenada','seychelles':'Seychelles','eritrea':'Eritrea','cabo verde':'Cabo Verde','zimbabwe':'Zimbabwe','montserrat':'Montserrat','st. barth':'St. Barth','nepal':'Nepal','congo':'Congo','gambia':'Gambia','bhutan':'Bhutan','chad':'Chad','mauritania':'Mauritania','sint maarten':'Sint Maarten','nicaragua':'Nicaragua','belize':'Belize','guinea-bissau':'Guinea-Bissau','turks and caicos':'Turks and Caicos','papua new guinea':'Papua New Guinea','timor-leste':'Timor-Leste'}
	async with ctx.typing():
		if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix):
			worldoMeterUrl = "https://www.worldometers.info/coronavirus/"
			driver.get(worldoMeterUrl)
			print("initialized driver")
			odds = driver.find_elements_by_class_name('odd')
			evens = driver.find_elements_by_class_name('even')
			print("got odds and events")
			#print("stages: "+pp.pformat(stages))
			d = {"total_cases":"./td[2]","new_cases":"./td[3]","total_deaths":"./td[4]","new_deaths":"./td[5]","total_recovered":"./td[6]","active_cases":"./td[7]", "critical_cases":"./td[8]"}
			embed = discord.Embed(colour = discord.Color.blue())
			embed.set_thumbnail(url="https://lh3.googleusercontent.com/proxy/1eWPPTYWMw6cn2_JnJ2TDzinXP5D8cC_Ho62z1N8pDurodNDKw5d1Z6rWmK9EfZSGRXfAZ1bdyA7FY9PEj_81h_6Btv0tGMsiav-TPCI9XTqXXSo9SxF3WOKPLhlR_-57g")
			if country:
				selectedCountry = None
				for key in countryDict:
					if not selectedCountry:
						selectedCountry = countryDict[key]
					if fuzz.ratio(country.lower(), key.lower()) > fuzz.ratio(country.lower(), selectedCountry.lower()):
						selectedCountry = countryDict[key]
				print("selectedCountry is: "+selectedCountry)
				for odd in odds:
					if odd.find_element_by_xpath('./td[1]').text == selectedCountry:
						await ctx.channel.send(embed=fetchCoronaInfo(d, odd, selectedCountry, embed))
						break
				print("Searching in evens")
				for even in evens:
					if even.find_element_by_xpath('./td[1]').text == selectedCountry:
						await ctx.channel.send(embed=fetchCoronaInfo(d, even, selectedCountry, embed))
						break
			elif not country:
				for odd in odds:
					if odd.find_element_by_xpath('./td[1]').text == "Switzerland":
						await ctx.channel.send(embed=fetchCoronaInfo(d, odd, "Suisse", embed))
						break
				print("Searching in evens")
				for even in evens:
					if even.find_element_by_xpath('./td[1]').text == "Switzerland":
						await ctx.channel.send(embed=fetchCoronaInfo(d, even, "Suisse", embed))
						break
			#driver.close()

@bot.command(pass_context=True)
async def s(ctx):
    if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix) and ctx.author.id == 435446721485733908:
        await ctx.channel.send(random.choice(["Arrivederci", "Goodnight girl, I'll see you tomorrow", "last seen online: 6 years ago", "stop! you can't ju"]))
        await bot.logout()
    elif ctx.author.id != 435446721485733908:
    	await ctx.channel.send("T'as cru t'avais le droit")

@bot.command(pass_context=True)
async def espace(ctx, repeat = 1):
	for i in range(repeat):
		await ctx.channel.send(genEspace())
	#await ctx.channel.send(random.choice(espaceEmojiList))

@bot.command()
async def repeat(ctx, repeat, *, arg):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix):
		for i in range(int(repeat)):
			await ctx.send(arg)

@bot.command()
async def urban(ctx, *, arg):
	if not isMessageFromDM(ctx) and guildHasThisPrefix(ctx.guild.id, ctx.prefix):
		url = "https://www.urbandictionary.com/define.php?term=" + parseWordForUrbanDictLink(arg)
		print("url is: " + url)
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		panels = soup.find_all("div", class_="def-panel")
		embed = discord.Embed(colour = discord.Color.blue())
		embed.set_thumbnail(url="https://antisemitism.uk/wp-content/uploads/2020/02/Urban-Dictionary.png")
		if len(panels) > 0:
			panel = panels[0]
			word = panel.find_next("a", class_="word").getText()
			definition = panel.find_next("div", class_="meaning").getText()
			example = panel.find_next("div", class_="example").getText()
			contributor = panel.find_next("div", class_="contributor").getText()
			contributor = urbanDictParseContributor(contributor)
			thumbs = panel.find_next("div", class_="left thumbs")
			upvotes = thumbs.find_next("a", class_="up").getText()
			downvotes = thumbs.find_next("a", class_="down").getText()
			if "bean" in word.lower() or "bean" in definition.lower():
				embed.set_author(name = "Définition du Dictionnaire Urbean:")
			else:
				embed.set_author(name = "Définition du Dictionnaire Urbain:")
			embed.description = "**" + word + "**\n" + definition + "\n_" + example + "_\n\n" + contributor + "\n" + upvotes + ":thumbsup: " + downvotes + ":thumbsdown:"
			await ctx.send(embed=embed)
		else:
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
	await ctx.channel.send(embed=randomMeme(reddit))



#@bot.command(pass_context=True)
#async def s(ctx):


########---------
#RUN
########---------

#client.run(TOKEN)
bot.run(TOKEN)
