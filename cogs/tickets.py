import disnake
from disnake.ext import commands
from database import *
from datetime import datetime
import random
import asyncio

TICKET_ROLE_ID = 1055220848874750063

class tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


        # Ticket Mother Of All Commands
        @bot.slash_command()
        async def ticket(inter):
            pass


        # Making new ticket command        
        @ticket.sub_command(description="Open een ticket")
        async def aanmaken(inter: disnake.CommandInteraction):
            now = datetime.now()
            id_gen = random.randint(1, 2000)
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            await inter.response.send_modal(
                title="Ticket aanmaken",
                custom_id="ticket_making",
                components=[
                    disnake.ui.TextInput(
                        label="Probleem",
                        placeholder="Beschrijf hier het probleem waar je tegenaan loopt",
                        custom_id="issue",
                        style=disnake.TextInputStyle.paragraph,
                        min_length=5,
                        max_length=50,
                    ),
                    disnake.ui.TextInput(
                        label="url",
                        placeholder="De website url waar het probleem is",
                        custom_id="url",
                        style=disnake.TextInputStyle.paragraph,
                        min_length=5,
                        max_length=1024,
                    ),
                ],
            )

            try:
                modal_inter: disnake.ModalInteraction = await bot.wait_for(
                    "modal_submit",
                    check=lambda i: i.custom_id == "ticket_making" and i.author.id == inter.author.id,
                    timeout=600,
                )
            except asyncio.TimeoutError:
                return

            issue = modal_inter.text_values["issue"]
            url = modal_inter.text_values["url"]
            new_ticket(inter, issue, url, id_gen, dt_string)
            embed = ticket_embed(type="aangemaakt", id= id_gen)
            bot.loop.create_task(ticket_handler_notify(inter, type="Nieuwe-ticket", id=id_gen, issue=issue, url=url))
            await modal_inter.response.send_message(embed=embed, ephemeral=True)


        # Get ticket info command    
        @ticket.sub_command(description="Krijg informatie over je ticket")
        async def informatie(inter, id:int):
            if validate_ticket_id(id) != True:
                inter.response.send_message("ID is niet bij ons bekend!", ephemeral=True)
            else:
                embed = ticket_embed(type="informatie", id=id)
                inter.response.send_message(embed=embed, ephemeral=True)


        # Get ticket info command    
        @ticket.sub_command(description="Zie al jouw tickets! met de status 'Open/wordt aan gewerkt'")
        async def al_jouw_tickets(inter):
            if validate_user_in_db(inter) != True:
                inter.response.send_message("Je hebt geen tickets momenteel bij ons!", ephemeral=True)
            else:
                embed = get_all_open_or_wop_tickets(inter)
                await inter.response.send_message(embed=embed, ephemeral=True)


        # Delete a ticket
        @ticket.sub_command(description="Verwijder een ticket als je ticket-maken of ticket-handler bent!")
        async def verwijder(inter, id:int):
            if validate_ticket_id(id) !=  True:
                inter.response.send_message("ID is niet bij ons bekend!", ephemeral=True)
            else:
                if validate_permissions(inter, id=id) != 1 or 0:
                    await inter.response.send_message("Ongeldige permissies!", ephemeral=True)
                    return

                delete_ticket(id)
                await inter.response.send_message(f"Ticket met ID: '{id}' is verwijderd!", ephemeral=True)


        # Change a ticket status as a assigned user
        @ticket.sub_command(description="Verander de ticket status (ticket-handler only)")
        async def status(inter, id:int):
            if validate_ticket_id(id) !=  True:
                inter.response.send_message("ID is niet bij ons bekend!", ephemeral=True)
            else:
                if validate_permissions(inter, id=id) != 1:
                    await inter.response.send_message("Ongeldige permissies! Dit command is voor ticket-behandelaars!", ephemeral=True)
                    return
                await change_status_ticket(inter, id)


        # Assign a ticket
        @ticket.sub_command(description="Wijs een ticket aan jezelf toe (ticket-handler only)")
        async def toewijzen(inter, id:int):
            if validate_ticket_id(id) !=  True:
                inter.response.send_message("ID is niet bij ons bekend!", ephemeral=True)
            else:
                if ticket_handler_validate(inter):
                    await inter.response.send_message("Ongeldige permissies! Dit command is voor ticket-behandelaars!", ephemeral=True)
                    return

                assign_a_ticket(inter, id)
                await ticket_status_msg(inter, id)
                await inter.response.send_message(f"Ticket is met ID: '{id}' is aan je toegewezen!", ephemeral=True)


        # See assigned tickets
        @ticket.sub_command(description="Zie alle toegewezen tickets (ticket-handler only)")
        async def toegewezen(inter):
                if ticket_handler_validate(inter) != True:
                    await inter.response.send_message("Ongeldige permissies! Dit command is voor ticket-behandelaars!", ephemeral=True)
                    return
                else:
                    embed = get_assigned_tickets(inter)
                    await inter.response.send_message(embed=embed, ephemeral=True)







        # Defining
        # Inserting new ticket into the database
        def new_ticket(inter, issue, url, id_gen, dt_string):
            Database.cursor.execute(f"INSERT INTO tickets (probleem, site_url, status, aanmaker, tijd_aanmaak, id) VALUES ('{issue}', '{url}', 'Open', '{inter.author.id}', '{dt_string}', '{id_gen}')")
            Database.db.commit()
            


        # Making and returning a embed
        def ticket_embed(type, id):
            Database.cursor.execute(f"SELECT * FROM tickets WHERE id={id}")
            res = Database.cursor.fetchall()[0]

            user_maker = bot.get_user(res[4])
            if res[5] != "Geen":
                ticket_handler = bot.get_user(res[5]).mention
            else:
                ticket_handler = "Geen"

            embed = disnake.Embed(title=f"Ticket {type}", description=f"**ID: {id}**", color=0x4793FF)
            embed.add_field(name="Probleem:", value=res[1], inline=False)  
            embed.add_field(name="URL:", value=res[2], inline=False)  
            embed.add_field(name="Status:", value=res[3], inline=False)  
            embed.add_field(name="Ticket maker:", value=user_maker.mention, inline=False)  
            embed.add_field(name="Ticket behandelaar:", value=ticket_handler, inline=False)  
            embed.set_footer(text="Let op, onthoudt je ticket-id goed!",icon_url="https://handbuildcomputers.nl/img/logo-1668156510.jpg")
            return embed



        # Get all open or wop tickets 
        def get_all_open_or_wop_tickets(inter):
            Database.cursor.execute(f"SELECT probleem, id, status FROM tickets WHERE aanmaker='{inter.author.id}' AND status='Open' OR status='Wordt aan gewerkt'")
            res = Database.cursor.fetchall()

            embed = disnake.Embed(title=f"Alle tickets van jou!", description=f"**Totaal: {len(res)}**", color=0x4793FF)
            for entry in res:
                embed.add_field(name=f"Probleem: {entry[0]}", value=f"ID: {entry[1]} - Status: {entry[2]}", inline=False)  

            embed.set_footer(text="Door het HBC team",icon_url="https://handbuildcomputers.nl/img/logo-1668156510.jpg")
            return embed




        def get_assigned_tickets(inter):
            Database.cursor.execute(f"SELECT probleem, id, status FROM tickets WHERE behandelaar='{inter.author.id}' AND status='Open' OR status='Wordt aan gewerkt'")
            res = Database.cursor.fetchall()

            embed = disnake.Embed(title=f"Alle tickets van jou!", description=f"**Totaal: {len(res)}**", color=0x4793FF)
            for entry in res:
                embed.add_field(name=f"Probleem: {entry[0]}", value=f"ID: {entry[1]} - Status: {entry[2]}", inline=False)  

            embed.set_footer(text="Door het HBC team",icon_url="https://handbuildcomputers.nl/img/logo-1668156510.jpg")
            return embed            



        # Checks if a ticket id excist
        def validate_ticket_id(id):
            Database.cursor.execute(f"SELECT id FROM tickets WHERE id={id}")
            res = Database.cursor.fetchall()[0]
            if res == []:
                return False
            else:
                return True



        # Checks if a user has any tickets
        def validate_user_in_db(inter):
            Database.cursor.execute(f"SELECT id FROM tickets WHERE aanmaker={inter.author.id}")
            res = Database.cursor.fetchall()[0]
            if res == []:
                return False
            else:
                return True                



        # validate perms
        def validate_permissions(inter, id):
            Database.cursor.execute(f"SELECT aanmaker FROM tickets WHERE id={id};")
            result = Database.cursor.fetchall()[0][0]

            for role in inter.author.roles:
                if TICKET_ROLE_ID == role.id:
                    return 1            
            if result == inter.author.id:
                return 0
            else:
                return False



        # Validate just role ticket-handler
        def ticket_handler_validate(inter):
                for role in inter.author.roles:
                    if TICKET_ROLE_ID == role.id:
                        return True
                return False              

        # Get all ticket infomation
        def get_ticket(id):
            Database.cursor.execute(f"SELECT * FROM tickets WHERE id={id};")
            result = Database.cursor.fetchall()
            if result != None:
                return result
            else:
                return False


        
        # Assign a ticket to the slash author
        def assign_a_ticket(inter, id):
            Database.cursor.execute(f"UPDATE tickets SET behandelaar='{inter.author.id}' WHERE id={id}")
            Database.db.commit()



        # Deletes a ticket from the database
        def delete_ticket(id):
            Database.cursor.execute(f"DELETE * FROM tickets WHERE id={id}")
            Database.db.commit()



        # Change status ticket
        async def change_status_ticket(inter, id):
                class Dropdown(disnake.ui.StringSelect):
                    def __init__(self):

                            options = [
                            disnake.SelectOption(
                                    label="Open", description="Open", emoji="🟥"
                            ),
                            disnake.SelectOption(
                                    label="Gesloten", description="Gesloten", emoji="🟩"
                            ),
                            disnake.SelectOption(
                                    label="Wordt aan gewerkt", description="Wordt aan gewerkt", emoji="🛠️"
                            ),
                            ]

                            super().__init__(
                            placeholder="Kies een status voor je ticket...",
                            min_values=1,
                            max_values=1,
                            options=options,
                            )

                    async def callback(self, inter: disnake.MessageInteraction):

                            Database.cursor.execute(f"UPDATE tickets SET status='{self.values[0]}' WHERE id={id}")
                            Database.cursor.execute(f"UPDATE tickets SET behandelaar='{inter.author.name}' WHERE id={id}")
                            Database.db.commit()
                            Database.db.commit()

                            await inter.response.send_message(f"Ik heb de status van ticket : {id} aangepast naar: {self.values[0]}", ephemeral=True)
                            await ticket_status_msg(inter, id=id, type=None)

                class DropdownView(disnake.ui.View):
                        def __init__(self):
                                super().__init__()

                                self.add_item(Dropdown())

                view = DropdownView()
                await inter.response.send_message(view=view, ephemeral=True)



        # Send DM to ticket handler
        async def ticket_handler_notify(inter, type, id, issue, url):
            ticket_handlr_person_list = []

            guild = await bot.fetch_guild(1036956401102237717)
            members = await guild.fetch_members(limit=1000).flatten()     

            for member in members:
                if member.get_role(TICKET_ROLE_ID) != None:
                    ticket_handlr_person_list.append(member.id)

            for user in ticket_handlr_person_list:
                user_to_send = bot.get_user(user)
                
                if type == "Nieuwe-ticket":
                    embed = disnake.Embed(title=f"Nieuwe ticket!", description=f"**ID: {id}**", color=0x4793FF)
                    embed.add_field(name="Probleem:", value=f'{issue}', inline=False)  
                    embed.add_field(name="URL:", value=f'{url}', inline=False)  
                    embed.add_field(name="Aangemaakt door:", value=f'{inter.author.name}', inline=False)  
                    embed.set_footer(text="Door het HBC team",icon_url="https://handbuildcomputers.nl/img/logo-1668156510.jpg")

                    await user_to_send.send(embed=embed)

            ticket_handlr_person_list.clear()



        # Send dm for ticket status change to ticket-owner
        async def ticket_status_msg(inter, id):
            result = get_ticket(id)[0]
            user_to_send = bot.get_user(result[4])
            embed = disnake.Embed(title=f"Ticket wijziging!", description=f"**ID: {id}**", color=0x4793FF)
            embed.add_field(name="Probleem:", value=result[1], inline=False)  
            embed.add_field(name="Nieuwe status:", value=result[3], inline=False)  
            embed.add_field(name="Ticket behandelaar:", value=bot.get_user(result[5]).name, inline=False)  
            embed.set_footer(text="Door het HBC team",icon_url="https://handbuildcomputers.nl/img/logo-1668156510.jpg")
            await user_to_send.send(embed=embed)


# Adding code to main file
def setup(bot: commands.Bot):
    bot.add_cog(tickets(bot))        