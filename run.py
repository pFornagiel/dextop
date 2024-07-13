from app.DexcomApi import DexcomApi
from app.Widget import Widget

# Testing initialisation
dex_api = DexcomApi(True)
test = Widget(dex_api)