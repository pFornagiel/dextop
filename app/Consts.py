from dataclasses import dataclass
from typing import Tuple, Literal
import os

@dataclass
class Sizing:
  size: Literal['NORMAL', 'LARGE']
  font_glucose: int
  font_units: int
  svg: int
  window: Tuple[int,int]
  
SIZE = {
  'NORMAL': Sizing(
    size = 'NORMAL',
    font_glucose=30,
    font_units= 10,
    svg=40,
    window=(150,100)
  ),
  'LARGE': Sizing(
    size = 'LARGE',
    font_glucose=40,
    font_units= 15,
    svg=70,
    window=(220,140)
  )
}

# default settings
DEFAULT_SETTINGS = {
    'credentials': {
        'login': '',
        'password': ''
    },
    'position': {
        'x': '',
        'y': ''
    },
    'settings': {
        'interval': '1',
        'size': 'NORMAL',
        'europe': 'False'
    }
}

# Colours
WARNING_BOTTOM = 'red'
WARNING_UPPER = '#ffce1f'
TEXT = 'white'
BACKGROUND = '#292929'
# Positioning
TASKBAR_OFFSET = 50
# Treshold, constant for now
TRESHOLD_BOTTOM = 70
TRESHOLD_UPPER = 250
SETTINGS_PATH = os.path.join(os.getcwd(), 'app/settings.ini')