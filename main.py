import disnake
from disnake.ext import commands
from syncer import sync
import asyncio
from threading import Timer
from env import secure
from prestapyt import PrestaShopWebServiceDict
from xml.etree import ElementTree
import os
from datetime import datetime
import threading 
from database import *
import time
# Add comment to test something

# Prestashop
prestashop = PrestaShopWebServiceDict(secure.WEBSHOP_URL,
                                  secure.API_KEY,)

# Perms Discord
intents = disnake.Intents.all()
bot = commands.Bot(intents=intents)

# Getting things ready
@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening , name="/help"))
    print("The bot is ready now!")



# Loading cogs
bot.load_extension("cogs.tickets")  
bot.load_extension("cogs.help_menu")  
bot.load_extension("cogs.webstore-commands")  



# Keeping DB conn active
def thread_keeping_alive():
    while True:
        Database.cursor.execute("SELECT * FROM tickets")
        Database.cursor.fetchall()
        time.sleep(75)



# Running bot and threads 1 and 2
if __name__ == "__main__":
    thread_1= threading.Thread(target=thread_keeping_alive)
    thread_1.start()       
    bot.run(secure.BOT_TOKEN)

