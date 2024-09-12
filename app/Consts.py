# Utils
import os
from win32api import GetMonitorInfo, MonitorFromPoint
# Typing
from dataclasses import dataclass
from typing import Tuple, Literal

# SIZING PROPERTIES
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

# DEFAULT SETTINGS
DEFAULT_SETTINGS = {
    'credentials': {
        'login': ''
    },
    'position': {
        'x': '',
        'y': ''
    },
    'settings': {
        'interval': '1',
        'size': 'NORMAL',
        'europe': 'False',
        'upper_threshold': '200',
        'bottom_threshold': '70',
        'mmol': 'False'
    }
}

# COLOURS
WARNING_BOTTOM = 'red'
WARNING_UPPER = '#ffce1f'
TEXT = 'white'
BACKGROUND = '#292929'

# MMOL CONVERSION
# mg/dl = 18.018 ∙ mmol/l
MMOL_FACTOR = 18.018

# POSITIONING
# Get the taskbar height at the start of the application
monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
monitor_area = monitor_info.get("Monitor")
work_area = monitor_info.get("Work")
TASKBAR_OFFSET = monitor_area[3]-work_area[3]

# PATH
appdata_path = os.getenv('APPDATA')
SETTINGS_PATH = os.path.join(appdata_path, 'dextop', 'settings.ini')
LOGGER_PATH = os.path.join(appdata_path, 'dextop', 'logs')