import disnake
from disnake.ext import commands
from database import *
from datetime import datetime


class help_menu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Help Mother Of All Commands
        @bot.slash_command()
        async def help(inter):
            pass


        # Help command tickets
        @help.sub_command(description="Maak een ticket aan!")
        async def tickets(inter):
            help_function= "Tickets"
            item_list = ["/ticket aanmaken-Maakt een nieuwe ticket aan", "/ticket informatie-Krijg alle info van je ticket te zien!", 
            "/ticket sluiten-Sluit een ticket!"
            ]
            embed = embed_help_menu(help_function, item_list)
            await inter.response.send_message(embed=embed, ephemeral=True)



def embed_help_menu(help_function, item_list):

    embed=disnake.Embed(title="Command help menu", description=f"**For: {help_function}**", color=disnake.Color.blue())

    for item in item_list:
        splt_list = str(item).split("-")
        embed.add_field(name=f"{splt_list[0]}", value=f"{splt_list[1]}", inline=False)    

    embed.set_footer(text="By </Kelvin>",icon_url="https://itkelvin.nl/CustomCPULOGO.png")
    return embed
        



def setup(bot: commands.Bot):
    bot.add_cog(help_menu(bot))        