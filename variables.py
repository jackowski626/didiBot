import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

DEBUG = True
LOCAL = False
REMOTEFTPDB = True
DEFAULT_PREFIX = "!"
on_raspberry = False
DB_FILENAME = ""
#By default the bot is on heroku. However, if it finds a "local" file, it switches to local setup
on_heroku = True

if os.path.isfile('local'):
    print ("\"local\" file exists")
    LOCAL = True
    on_raspberry = False
    on_heroku = False
else:
    print ("\"local\" file does not exist")

if on_raspberry:
	DB_FILENAME = "/home/pi/didibot/dididb.json"
else:
	DB_FILENAME = "./dididb.json"
pp = pprint.PrettyPrinter(indent=4)

if not LOCAL and not on_heroku and not on_raspberry:
	print("not local")
	#GOOGLE_CHROME_PATH = '/home/pi/Downloads/chromium_80.0.3987.149-1_deb10u1_armhf.deb'
	CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
	
	#GOOGLE_CHROME_PATH = os.getenv("CHROMEDRIVER_PATH")
	#CHROMEDRIVER_PATH = os.getenv("GOOGLE_CHROME_BIN")
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	#options.binary_location = GOOGLE_CHROME_PATH
	#driver / browser = webdriver.Chrome(execution_path=CHROMEDRIVER_PATH, options=options)
elif LOCAL:
	print("local")
	options = Options()  
	options.add_argument("--headless")  
	options.binary_location = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
	CHROMEDRIVER_PATH = './chromedriver.exe'
	#driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
else:
	CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')



randomGreet = ["bonsoeir", "bonsoir, ici c'est le COFOP", "yo mec", "bonjour", "bsoir, tu me dois une girafe"]
errorMessages = ["Je pense que mon foie a lâché cette fois", "Ambulance! vite!", "Aidez-moi! je ne sens plus ma byte"]

authorID = 435446721485733908
defaultChannelID = 445985682410831882
barID = 445983404832587805

espaceEmojis = "˚　　　　　　　　　　　　　　*　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　. 　　 　　　　　　　 ✦ 　　　　　　　　　　 　 ‍ ‍ ‍ ‍ 　　　　 　　　　　　　　　　　　,　　   　\n.　　　　　　　　　　　　　.　　　ﾟ　  　　　.　　　　　　　　　　　　　.\n　　　　　　,　　　　　　　.　　　　　　    　　　　 　　　　　　　　　　　　　　　　　　 :sunny: 　　　　　　　　　　　　　　　　　　    　      　　　　　        　　　　　　　　　　　　　. 　　　　　　　　　　.　　　　　　　　　　　　　. 　　　　　　　　　　　　　　　　       　   　　　　 　　　　　　　　　　　　　　　　       　   　　　　　　　　　　　　　　　　       　    ✦ 　   　　　,　　　　　　　　　　　    :rocket: 　　　　 　　,　　　 ‍ ‍ ‍ ‍ 　 　　　　　　　　　　　　.　　　　　 　　 　　　.　　　　　　　　　　　　　 　           　　　　　　　　　　　　　　　　　　　˚　　　 　   　　　　,　　　　　　　　　　　       　    　　　　　　　　　　　　　　　　.　　　  　　    　　　　　 　　　　　.　　　　　　　　　　　　　.　　　　　　　　　　　　　　　* 　　   　　　　　 ✦ 　　　　　　　         　        　　　　 　　 　　　　　　　 　　　　　.　　　　　　　　　　　　　　　　　　.　　　　　    　　. 　 　　　　　.　　　　    :new_moon:  　　　　　   　　　　　.　　　　　　　　　　　.　　　　　　　　　　   　\n˚　　　　　　　　　　　　　　　　　　　　　ﾟ　　　　　.　　　　　　　　　　　　　　　. 　　 　 :earth_americas: ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ,　 　　　　　　　　　　　　　　* .　　　　　 　　　　　　　　　　　　　　.　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　. .　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　. 　　 　　　　　　　 ✦ 　　　　　　　　　　 　 ‍ ‍ ‍ ‍ 　　　　 　　　　　　　　　　　　,　　   　\n.　　　　　　　　　　　　　.　　　ﾟ　  　　　.　　　　　　　　　　　　　."
espaceEmojis2 = "✦ 　　　　　　　         　        　　　　 　　 　　　　　　　 　　　　　.　　　　　　　　　　　　　　　　　　.　　　 　　　˚　　　　　　　　　　　　　　    　　. 　 　　　　　.　　　　 　　　　　   　　　　　.　　　　　　　　　　　.　　　　　　　　　　  　　　* .　　　　　 　　　　　　　　　　　　　　.　　　　　　　　　　 ✦ 　　　　 　 　˚　　 . ✦ ✦　　　　　　　　　　　　　　　　　　　ﾟ　　　　　.　　　　　　　　　　　　　　　. 　　 　 :earth_americas: ,　 　　　　　　　　　　　　　　  　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　 ✦ .　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　　　　　　　   　　　　　　　　　　　　　.　　　:comet:　　　　　　　　 　　　. 　　 　　　　　　　 ✦ 　　　　　　　　　　 　 　　　　 　　　　　　　　　　　　,　　   　 .　　　　　　　　　　　　　.　　　ﾟ　  　　　.　　　　　　　　　　　　　✦ 　　　　　　,　　　　　　　.　　　　　　    　　　　 　　　　　　　　　　　　　　　　　　  . :sunny: 　　　　　　　　　　　　　　　　　　    　      　　　　　        　　　　　　　　　　　　　. 　　　　　　　　.　　　　　　　　　　　　　.　　　　　　       　   　　　　 　　　　　　　　　　　　　　　　       　   　　　　　　　　　　　　　　　　       　    ✦ 　   　　　,　　　　　　　　　　　  　　　　 　　,　　　 　 　　　　　　　　　　　　.　　　　　 　　 　　　.　　　　　　　　　　　　　 　           　　　　　　　　　　　　　　　　　　　. ˚　　　 　   . ,　　　　　　　　　　　       　    　　　　　　　　　　　　　. .　　　  　　    ✦　 ✦　　　　 　　　　　.　　　　　　　　　　　　　.　　　　　　　　　　　　　　　 　　   　　　　　 ✦ 　　　　　　　         　        　　　　 　　 　　　　　　　 　　　　　.　　　　　　　　　　　　　　　　　　.　　　　　    　　. 　 　　　　　.　　　　 　　　　　   　　　　　.　　　　　　　　　　　.　　　　　　　　　　  .　　　　　 　　　　　　　　　　　　　　.　　　　　　　　　　 ✦"
espaceEmojiList = [espaceEmojis, espaceEmojis2]