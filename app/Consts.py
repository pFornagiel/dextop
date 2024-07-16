from dataclasses import dataclass
from typing import Tuple
import os

@dataclass
class Sizing:
  font_glucose: int
  font_units: int
  svg: int
  window: Tuple[int,int]
  
SIZE = {
  'SMALL': Sizing(
    font_glucose=30,
    font_units= 10,
    svg=40,
    window=(180,108)
  ),
  'NORMAL': Sizing(
    font_glucose=40,
    font_units= 15,
    svg=70,
    window=(250,150)
  ),
  'LARGE': Sizing(
    font_glucose=50,
    font_units= 20,
    svg=90,
    window=(250,150)
  )
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