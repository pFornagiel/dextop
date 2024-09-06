from app.DexcomApi import DexcomApi
from app.Widget import Widget
# from app.Setup import SetupWindow
# Environmental variables
import os
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv('_USERNAME')
PASSWORD = os.getenv('_PASSWORD')
# Testing initialisation
dex_api = DexcomApi(True, USERNAME, PASSWORD)
test = Widget(dex_api)