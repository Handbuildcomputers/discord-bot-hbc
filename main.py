import disnake
from disnake.ext import commands
import secrets
from secrets import secure
from syncer import sync
import asyncio
import threading
from threading import Timer

from prestapyt import PrestaShopWebServiceDict
from xml.etree import ElementTree
import os



# Prestashop
prestashop = PrestaShopWebServiceDict(secure.WEBSHOP_URL,
                                  secure.API_KEY,)


intents = disnake.Intents.all()
bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening , name="/hbc"))
    print("The bot is ready now!")
    await notify_discord()


# Slash commands:
# Order count
@bot.slash_command(description="Order aantal")
async def order_aantal(inter):
    # Counting how many orders ther are.
    orders_json_data1 = prestashop.get("orders")
    count1 = 0

    for item in orders_json_data1["orders"]["order"]:
        count1 = count1 + 1
        
    embed=disnake.Embed(title="Orders:", description=f"{count}", color=0x00FF00)
    await inter.response.send_message(embed=embed)  

count_customers1 = 0
@bot.slash_command(description="Klanten accounts aantal")
async def klanten_aantal(inter):
    customers_json_data1 = prestashop.get("customers")

    for customer in customers_json_data1["customers"]["customer"]:
        count_customers1 = count_customers1 + 1
        
    embed=disnake.Embed(title="Aantal klanten:", description=f"{count_customers}", color=0x00FF00)
    await inter.response.send_message(embed=embed)  




# Counting how many orders ther are.
orders_json_data = prestashop.get("orders")
count = [0]

for item in orders_json_data["orders"]["order"]:
    count[0] = count[0] + 1


# Counting how many customers account there are
customers_json_data = prestashop.get("customers")
count_customers = [0]

for customer in customers_json_data["customers"]["customer"]:
    count_customers[0] = count_customers[0] + 1
    
    
# Counting how many messages ther are.
messages_json_data_loop = prestashop.get("customer_messages")
count_messages = [0]     

for msg in messages_json_data_loop["customer_messages"]["customer_message"]:
    count_messages[0] = count_messages[0] + 1
    
    
async def notify_discord():
    while True:
        # Counting how many customers account there are and if new account, send discord message
        customers_json_data = prestashop.get("customers")
        count_customers_loop = [0]

        for customer in customers_json_data["customers"]["customer"]:
            count_customers_loop[0] = count_customers_loop[0] + 1
        
        if count_customers_loop[0] > count_customers[0]:
            
            print("Er is een customer erbij gekomen!")            
            count_customers[0] = count_customers_loop[0]
            
            # Sending to Discord
            channel = bot.get_channel(1037018534590558288)
            await channel.send("Er is een customer erbij gekomen!")
        
            
        # Counting how many orders ther are.
        orders_json_data_loop = prestashop.get("orders")
        count_orders_loop = [0]

        for item in orders_json_data_loop["orders"]["order"]:
            count_orders_loop[0] = count_orders_loop[0] + 1
            
        if count_orders_loop[0] > count[0]:
            print("Er is een order binnen gekomen!")
            count[0] = count_orders_loop[0]
            
            # Sending to Discord            
            channel = bot.get_channel(1037018534590558288)
            await channel.send("Er is een order binnengekomen op HBC!")
            
            
        # Counting how many messages ther are.
        messages_json_data_loop = prestashop.get("customer_messages")
        
        count_messages_loop = [0]     
        
        for msg in messages_json_data_loop["customer_messages"]["customer_message"]:
            count_messages_loop[0] = count_messages_loop[0] + 1
            
        if count_messages_loop[0] > count_messages[0]:
            count_messages[0] = count_messages_loop[0]
            
            # Sending to Discord            
            channel = bot.get_channel(1037018534590558288)
            await channel.send("Er is een bericht binnengekomen op HBC!")
        
        await asyncio.sleep(20)


bot.run(secure.BOT_TOKEN)