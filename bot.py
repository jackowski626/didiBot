import mysql.connector
from mysql.connector import Error
import os
import discord
from dotenv import load_dotenv
import random
from discord.ext import commands
from random import randint

#code still veeeeery messy

def changeMOTD(motd):
	try:
	    connection = mysql.connector.connect(host='-',
                                         database='-',
                                         user='-',
                                         password='-')
	    if connection.is_connected():
	        db_Info = connection.get_server_info()
	        print("Connected to MySQL Server version ", db_Info)
	        cursor = connection.cursor()
	        cursor.execute("select database();")
	        record = cursor.fetchone()
	        print("You're connected to database: ", record)
	        cursor.execute("SELECT motd FROM motd WHERE id LIKE 69 LIMIT 1")
	        query = cursor.fetchall()
	        print(query)
	        cursor.execute("UPDATE motd SET motd = '"+motd+"' WHERE id LIKE 69 LIMIT 1")
	        connection.commit()
	        cursor.execute("SELECT motd FROM motd WHERE id LIKE 69 LIMIT 1")
	        query = cursor.fetchall()
	        print(query)

	except Error as e:
	    print("Error while connecting to MySQL", e)
	finally:
	    if (connection.is_connected()):
	        cursor.close()
	        connection.close()
	        print("MySQL connection is closed")
def getPrefix(serverId):
	try:
	    connection = mysql.connector.connect(host='remotemysql.com',
                                         database='9TOxaV1q24',
                                         user='9TOxaV1q24',
                                         password='XJsdO215Kh')
	    if connection.is_connected():
	        db_Info = connection.get_server_info()
	        print("Connected to MySQL Server version ", db_Info)
	        cursor = connection.cursor()
	        cursor.execute("select database();")
	        record = cursor.fetchone()
	        print("You're connected to database: ", record)
	        cursor.execute("SELECT prefix FROM prefixes WHERE serverid LIKE "+serverId+" LIMIT 1")
	        query = cursor.fetchall()
	        print(query)
	        if len(query) == 0:
	        	cursor.execute("INSERT INTO prefixes(serverid, prefix) VALUES ("+serverId+", '!')")
	        	connection.commit()
	        	print("Server",serverId,"was not in db, setting default '!' prefix")
	        	return "!"
	        else:
	        	print("Server",serverId,"was in db with prefix'",query,"'")
	        	return query
	        return "$"
	except Error as e:
	    print("Error while connecting to MySQL", e)
	    #channel.send("Error connecting to database")
	finally:
	    if (connection.is_connected()):
	        cursor.close()
	        connection.close()
	        print("MySQL connection is closed")
def setPrefix(serverId, ctx, prefix):
	try:
	    connection = mysql.connector.connect(host='remotemysql.com',
                                         database='9TOxaV1q24',
                                         user='9TOxaV1q24',
                                         password='XJsdO215Kh')
	    if connection.is_connected():
	        db_Info = connection.get_server_info()
	        print("Connected to MySQL Server version ", db_Info)
	        cursor = connection.cursor()
	        cursor.execute("select database();")
	        record = cursor.fetchone()
	        print("You're connected to database: ", record)
	        cursor.execute("UPDATE prefixes SET prefix = '"+prefix+"' WHERE serverid LIKE "+serverId+" LIMIT 1")
	        connection.commit()
	        return prefix
	except Error as e:
	    print("Error while connecting to MySQL", e)
	    #ctx.send("Error connecting to database")
	finally:
	    if (connection.is_connected()):
	        cursor.close()
	        connection.close()
	        print("MySQL connection is closed")

#changeMOTD("Epstein didnt kill Epstein")

#bot
load_dotenv()
TOKEN = "-"#os.getenv('DISCORD_TOKEN')
#Donjons et creepers
#GUILD = "-"
#bar
GUILD = "-"
botchannel = "-"

#client = discord.Client()
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    #print(f'{client.user} has connected to Discord!')
    #PREFIX = "!"
    bot.command_prefix = getPrefix(GUILD)[0][0]
    channel = bot.get_channel(botchannel)
    await channel.send('hello')
    print("prefix is:",bot.command_prefix)
    #await channel.send("my prefix is"+bot.command_prefix)
    for guild in bot.guilds:
    	if guild.name == GUILD:
    		break
    print(f'{bot.user} is connected to the following guild:\n'f'{guild.name}(id: {guild.id})')
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


randomGreet = ["*", "*", "*", "*", "bonsoeir", "bonjour, ici c'est le COFOP", "yo mec", "bonjour, *", "bsoir, tu me dois un cône"]
randomBye = ["Goodnight girl, I'll see you tomorrow", "last seen online: 6 years ago", "stop! you can't ju"]

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	# we do not want the bot to reply to itself
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
	if message.content.lower() == "prefix":
		if bot.command_prefix[len(bot.command_prefix)-1] == " ":
			await message.channel.send("mon préfixe est "+bot.command_prefix+" (avec un espace à la fin)")
		else:
			await message.channel.send("mon préfixe est "+bot.command_prefix)
	await bot.process_commands(message)

@bot.command()
async def say(ctx, *, arg):
    await ctx.send(arg)
@bot.command()
async def motd(ctx, *, motd):
	changeMOTD(motd.replace("'", "\\'").replace('"', '\\"'))
	await ctx.send("MOTD has been updated. Check it out here: http://jacques.ml")
@bot.command()
async def changePrefix(ctx, prefix):
	bot.command_prefix = prefix
	setPrefix(GUILD, ctx.channel, prefix.replace("'", "\\'").replace('"', '\\"'))
	await ctx.send("Prefix changed successfully")
@bot.command()
async def stop(ctx):
	await ctx.channel.send(random.choice(randomBye))
	await bot.logout()
@bot.command()
async def complimente(ctx):
    await ctx.send("Cédric, t'es beau")

#client.run(TOKEN)
bot.run(TOKEN)
