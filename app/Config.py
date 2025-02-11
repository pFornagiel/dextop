# Utils
import os
from win32api import GetMonitorInfo, MonitorFromPoint
from configparser import ConfigParser
# Typing
from dataclasses import dataclass
from typing import Tuple, Literal
from enum import Enum

# ===== SIZING =====
class Size(str, Enum):
  NORMAL = "NORMAL"
  LARGE = "LARGE"

@dataclass
class Sizing:
  size: Literal['NORMAL', 'LARGE']
  font_glucose: int
  font_units: int
  svg: int
  window: Tuple[int,int]

class SizeConfig:
  SIZE_CONFIG = {
    Size.NORMAL: Sizing(
      size = 'NORMAL',
      font_glucose=30,
      font_units= 10,
      svg=40,
      window=(150,100)
    ),
    Size.LARGE: Sizing(
      size = 'LARGE',
      font_glucose=40,
      font_units= 15,
      svg=70,
      window=(220,140)
    )
  }
  
  @classmethod
  def get_size(cls, size: Size):
    return cls.SIZE_CONFIG[size]

# ===== DEFAULT SETTINGS =====
class DefaultSettings:
  DEFAULT_SETTINGS: dict[str, dict[str,str]] = {
    'credentials': {
        'login': ''
    },
    'position': {
        'x': '',
        'y': ''
    },
    'settings': {
        'interval': '1',
        'size': Size.NORMAL,
        'europe': 'False',
        'upper_threshold': '200',
        'bottom_threshold': '70',
        'mmol': 'False'
    }
  }
  
  @classmethod
  def get_settings(cls):
    return cls.DEFAULT_SETTINGS
  
  @classmethod
  def initialise_settings(cls, config_parser: ConfigParser):
    for section, keys in cls.DEFAULT_SETTINGS.items():
      if section not in config_parser:
        config_parser.add_section(section)
      for key, value in keys.items():
        if not config_parser.has_option(section, key) or not config_parser[section][key]:
          config_parser[section][key] = value
        
        # OPTION SPECIFIC ERROR CHECKS
        reset_to_default = False
        match key:
          case 'x' | 'y' | 'upper_threshold' | 'bottom_threshold':
            # EAFP
            try:
              float(config_parser[section][key])
            except ValueError:
              reset_to_default = True
          case 'interval':
            if(not config_parser[section][key].isdigit()):
              reset_to_default = True
          case 'size':
            if(config_parser[section][key] not in ('NORMAL', 'LARGE')):
              reset_to_default = True          
          case 'europe' | 'mmol':
            if(config_parser[section][key] not in ('True', 'False')):
              reset_to_default = True
                
        if(reset_to_default): 
          config_parser.set(section,key,value)
          
    with open(Paths.SETTINGS_PATH, 'w') as config_file:
      config_parser.write(config_file)

# ===== COLOURS =====
class Colours(str, Enum):
  WARNING_BOTTOM_COLOUR = 'red'
  WARNING_UPPER_COLOUR = '#ffce1f'
  TEXT_COLOUR = 'white'
  BACKGROUND_COLOUR = '#292929'
  
# ===== FILE PATHS =====
class Paths(str, Enum):
  _appdata_path = os.getenv('APPDATA')
  SETTINGS_PATH = os.path.join(_appdata_path, 'dextop', 'settings.ini')
  LOGGER_PATH = os.path.join(_appdata_path, 'dextop', 'logs')
  TRAY_IMAGE_PATH = os.path.join('assets','dextop_icon.png')
  TREND_SVG_PATH = os.path.join('assets', 'svg')
  
# ===== MMOL CONVERSION FACTOR =====
MMOL_FACTOR = 18.018 # mg/dl = 18.018 ∙ mmol/l

# ===== TASKBAR POSITIONING DETECTION (WINDOWS ONLY) =====
def get_taskbar_offset():
  try:
    monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
    monitor_area = monitor_info.get("Monitor")
    work_area = monitor_info.get("Work")
    return monitor_area[3] - work_area[3]
  except Exception:
    return 0  # Fallback for non-Windows OS or errors

TASKBAR_OFFSET = get_taskbar_offset()

# ===== LOGGER =====
ERROR_LOGGER_NAME = "error_logger"