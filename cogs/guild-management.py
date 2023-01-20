import disnake
from disnake.ext import commands
from database import *


class guild_management(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


        # Ticket Mother Of All Commands
        @commands.default_member_permissions(moderate_members=True)
        @bot.slash_command()
        async def guild(inter):
            pass


        # Making new ticket command        
        @guild.sub_command(description="Open een ticket")
        async def purge(inter, aantal:int):
            await inter.channel.purge(limit=aantal)


# Adding code to main file
def setup(bot: commands.Bot):
    bot.add_cog(guild_management(bot))        