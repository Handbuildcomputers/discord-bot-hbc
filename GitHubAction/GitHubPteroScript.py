# Importing the modules
from pydactyl import PterodactylClient
import os
from dotenv import load_dotenv
import time

# Loading envirement keys
load_dotenv()

# Get the gamemanager URL and API key
gamemanager_url = os.getenv("gamemanager_ptero_url")
gamemanager_client_password = os.getenv("client_api_key")

# Create a client to connect to the panel by URL and authenticate with your API key
api = PterodactylClient(gamemanager_url, gamemanager_client_password)

# Assigning server ID
SERVER_ID = "8ec73c19"

# Killing the individual server
api.client.servers.send_power_action(SERVER_ID, "kill")
# Wait 10 seconds
time.sleep(10)
# Starting the server up again
api.client.servers.send_power_action(SERVER_ID, "start")
