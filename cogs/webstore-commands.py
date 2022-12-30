import disnake
from disnake.ext import commands
from database import *
from prestapyt import PrestaShopWebServiceDict
from env import secure


TICKET_ROLE_ID = 1055220848874750063

class webstore_commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Prestashop
        prestashop = PrestaShopWebServiceDict(secure.WEBSHOP_URL,
                                        secure.API_KEY,)


        # Ticket Mother Of All Commands
        @commands.default_member_permissions(moderate_members=True)
        @bot.slash_command()
        async def winkel(inter):
            pass

        # Order count
        @winkel.sub_command(description="Zie het aantal orders!")
        async def order_aantal(inter):
            # Counting how many orders ther are.
            orders_json_data1 = prestashop.get("orders")
            count1 = 0

            for item in orders_json_data1["orders"]["order"]:
                count1 = count1 + 1
                
            embed=disnake.Embed(title="Orders:", description=f"{count1}", color=0x00FF00)
            await inter.response.send_message(embed=embed)  


        @winkel.sub_command(description="Zie het aantal klanten accounts!")
        async def klanten_aantal(inter):
            count_customers1 = 0
            customers_json_data1 = prestashop.get("customers")

            for customer in customers_json_data1["customers"]["customer"]:
                count_customers1 = count_customers1 + 1
                
            embed=disnake.Embed(title="Aantal klanten:", description=f"{count_customers1}", color=0x00FF00)
            await inter.response.send_message(embed=embed)  



# Adding code to main file
def setup(bot: commands.Bot):
    bot.add_cog(webstore_commands(bot))        