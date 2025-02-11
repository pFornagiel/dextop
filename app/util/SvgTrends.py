# Util
import os
# Config
from app.Config import Paths

TREND_LIST: list[str] = []

def load_svgs():
  global TREND_LIST
  for i in range(len(os.listdir(Paths.TREND_SVG_PATH))):
    with open(os.path.join(Paths.TREND_SVG_PATH, f'trend_{i}.svg'), 'r') as file:
      TREND_LIST.append(file.read())

def get_trend_SVG(number: int, colour: str, size: int) -> str:
  if number == 0:
    return TREND_LIST[0]
  if number == 7 or number == 1:
    return TREND_LIST[number].format(size, size, colour, colour)
  return TREND_LIST[number].format(size, size, colour)

# Load SVGs on startup
load_svgs()
