import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Apex Legends Status API
ALS_API_KEY = os.environ.get("ALS_API_KEY")

# Discord Token
DIS_API_KEY = os.environ.get("DIS_API_KEY")

# Steam Token
STEAM_API_KEY = os.environ.get("STEAM_API_KEY")

# Steam ID
STEAM_ID = os.environ.get("STEAM_ID")