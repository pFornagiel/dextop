from app.DexcomApi import DexcomApi
from app.Widget import Widget
# Environmental variables
import os
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
# Testing initialisation
dex_api = DexcomApi(True, USERNAME, PASSWORD)
test = Widget(dex_api)