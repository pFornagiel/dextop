# GUI
import tkinter as tk
import tksvg
from .SvgTrends import get_trend_arrow_SVG
from .Tray import TrayIcon, TrayCallbacks
# Dexcom Api
from .DexcomApi import DexcomApi, GlucoseFetcher
from pydexcom import DexcomError
# Clicktrough-hacks - win32
import win32gui
import win32con
# Config
from configparser import ConfigParser
from .Consts import *
# Typing
from dataclasses import dataclass
from typing import Optional

@dataclass
class Position:
  x: int
  y: int

class Widget:
  def __init__(self, parent_root: tk.Tk, config: ConfigParser) -> None:
    self._parent_root = parent_root
    self._root = tk.Toplevel()
    self._config = config
    self._initialise_settings()
    self._glucose_fetcher = GlucoseFetcher(self._interval, self._generate_fail_event, self._generate_udpate_event)
    self._initialise_GUI_value_display()
    self._initialise_widget()
    self._initialise_tray()
  
  def _initialise_settings(self) -> None:
    self._size_config: Sizing = SIZE[DEFAULT_SETTINGS['settings']['size']]
    self._interval: int = int(DEFAULT_SETTINGS['settings']['interval'])
    self._upper_threshold: float = float(DEFAULT_SETTINGS['settings']['upper_threshold'])
    self._bottom_threshold: float = float(DEFAULT_SETTINGS['settings']['bottom_threshold'])
    self._mmol: bool = DEFAULT_SETTINGS['settings']['mmol'] == 'True'
    self._moveable: bool = False
    self._position: Position = Position(
      x = DEFAULT_SETTINGS['position']['x'],
      y = DEFAULT_SETTINGS['position']['y']
    )
  
  def _initialise_GUI_value_display(self) -> None:
    self._glucose_value = tk.StringVar(value='---')
    self._trend = tk.IntVar(value=0)
    self._units = tk.StringVar(value='mg/dL' if not self._mmol else 'mmol/L')
    
  def _initialise_tray(self) -> None:
    callbacks = TrayCallbacks(
      self._generate_close_event,
      self._generate_enable_drag_event,
      self._generate_disable_drag_event,
      self._reset_window_position,
      self._generate_resize_event,
      self._generate_open_settings_event
    )
    self._tray_icon = TrayIcon(callbacks, self._size_config.size)
    self._tray_icon.run_tray_icon()
    self._tray_icon.hide_tray()
    

  def _initialise_widget(self) -> None:
    '''initialise widget's attributes'''
    self._root.title("Dextop")
    self._root.configure(background=BACKGROUND)
    self._root.attributes('-alpha',0.7,"-topmost", True)
    self._root.overrideredirect(True)
    self._enable_clicktrough(init=True)
    
    # Protocols and binds
    self._root.protocol("WM_DELETE_WINDOW", self._on_close)
    self._root.bind('<<Close>>', self._on_close)
    self._root.bind('<<Update>>', self._on_update)
    self._root.bind('<<Failed>>', self._on_fail)
    self._root.bind('<<Start_Drag>>', self._on_enable_drag)
    self._root.bind('<<Stop_Drag>>', self._on_disable_drag)
    self._root.bind("<ButtonPress-1>", self._on_start_drag)
    self._root.bind("<ButtonRelease-1>", self._on_stop_drag)
    self._root.bind("<B1-Motion>", self._on_drag)
    self._root.bind("<<Resize>>", self._on_resize)
    self._root.bind("<<Settings>>", self._on_open_settings)

    
    # withdraw window upon, so it does not showup right away
    self._root.withdraw()
    
    # Set text colour
    colour = self._get_colour()
    # Get text-related size configs
    glucose_size, unit_size, svg_size = self._size_config.font_glucose, self._size_config.font_units, self._size_config.svg
    
    # Frames
    self._frame_wrapper = tk.Frame(self._root, background=BACKGROUND)
    self._frame1 = tk.Frame(self._frame_wrapper, background=BACKGROUND)
    self._frame2 = tk.Frame(self._frame_wrapper, background=BACKGROUND)
    
    # Glucose value label
    self._glucose_value_label = tk.Label(
      self._frame1,
      textvariable=self._glucose_value, 
      padx=10, 
      font=('Inter',glucose_size),
      fg=colour,
      background=BACKGROUND
    )
    
    # Trend arrow label displaying SVG
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(self._trend.get(), colour, svg_size))
    
    self._trend_label = tk.Label(
      self._frame1, 
      image=svg, 
      background=BACKGROUND,
      padx=10, 
      )
    # Has to be done, in order for the image to display correctly
    self._trend_label.image = svg
  
    # Unit label
    self._unit_label = tk.Label(
      self._frame2,
      textvariable=self._units,
      padx=15, 
      font=('Inter',unit_size),
      fg=colour,
      background=BACKGROUND)
    
    # Packing
    self._glucose_value_label.pack(side='left')
    self._trend_label.pack(side='left')
    self._frame1.pack()
    self._unit_label.pack(side='top')
    self._frame2.pack(side='left',anchor='nw')
    self._frame_wrapper.pack(expand=True)
    
  # Windows specific click-trough hacks
  
  def _enable_clicktrough(self,init=False) -> None:
    hwnd = self._root.winfo_id() if init else win32gui.FindWindow(None, self._root.title())
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    styles = styles | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
    self._root.attributes('-transparentcolor', '#000000')

  def _disable_clicktrough(self,init=False) -> None:
    hwnd = self._root.winfo_id() if init else win32gui.FindWindow(None, self._root.title())
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    styles = styles & ~win32con.WS_EX_LAYERED  # Remove the layered style
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)  # Set new styles
  
  # Event handlers
  
  def _on_close(self,_) -> None:
    self._glucose_fetcher.stop_fetch_loop()
    self._root.destroy()
    if(self._parent_root):
      self._parent_root.destroy()
  
  def _on_update(self, _) -> None:
    trend = self._trend.get()
    colour = self._get_colour()
    
    self._glucose_value_label.config(fg=colour)
    
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(trend,colour,self._size_config.svg))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
  
  def _on_fail(self,_) -> None:
    self._glucose_value_label.config(fg=TEXT)
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(0,TEXT, self._size_config.svg))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
  
  def _on_enable_drag(self,_) -> None:
    self._disable_clicktrough()
    self._moveable = True
  
  def _on_disable_drag(self,_) -> None:
    self._enable_clicktrough()
    self._moveable = False
    
  def _on_start_drag(self,event: tk.Event) -> None:
    if(self._moveable):
      self._root.x = event.x
      self._root.y = event.y

  def _on_stop_drag(self,_) -> None:
    if(self._moveable):
      self._position.x, self._position.y = self._root.winfo_x(), self._root.winfo_y()
      self._config['position'] = {
        'x': str(self._position.x),
        'y': str(self._position.y)
      }
      with open(SETTINGS_PATH, 'w') as configfile:
        self._config.write(configfile)
      
      self._root.x = None
      self._root.y = None
    
  def _on_drag(self,event: tk.Event) -> None:
    if(self._moveable):
      delta_x = event.x - self._root.x
      delta_y = event.y - self._root.y
      x = self._root.winfo_x() + delta_x
      y = self._root.winfo_y() + delta_y
      window_width,window_height =self._size_config.window
      self._root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
  def _on_resize(self,_) -> None:
    window_width, window_height = self._size_config.window
    self._root.geometry(f'{window_width}x{window_height}')
    self._glucose_value_label.configure(font=('Inter',self._size_config.font_glucose))
    self._unit_label.configure(font=('Inter',self._size_config.font_units))
    
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG((self._trend.get()),self._get_colour(),self._size_config.svg))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._config['settings']['size'] = self._size_config.size
    with open(SETTINGS_PATH, 'w') as config_file:
      self._config.write(config_file)
      
  def _on_open_settings(self, _) -> None:
    if(self._parent_root.wm_state() != 'normal'):
      self._parent_root.deiconify()
    self._glucose_fetcher.stop_fetch_loop()
    self._root.withdraw()

  # Event generating methods
  
  def _generate_udpate_event(self,glucose_value:str, trend:int) -> None:
    self._glucose_value.set(glucose_value if not self._mmol else str(round(float(glucose_value) / 18,1)))
    self._trend.set(trend)
    self._root.event_generate("<<Update>>",when='now')

  def _generate_fail_event(self,e: DexcomError) -> None:
    self._glucose_value.set('---')
    self._trend.set(0)
    self._root.event_generate("<<Failed>>",when='now')
  
  def _generate_close_event(self) -> None:
    self._root.event_generate("<<Close>>", when='now')
    
  def _generate_enable_drag_event(self) -> None:
    self._root.event_generate('<<Start_Drag>>', when='now')
    
  def _generate_disable_drag_event(self) -> None:
    self._root.event_generate('<<Stop_Drag>>', when='now')
  
  def _generate_resize_event(self, size) -> None:
    self._size_config = SIZE[size]
    self._root.event_generate('<<Resize>>', when='now')
    
  def _generate_open_settings_event(self) -> None:
    self._root.event_generate('<<Settings>>', when='now')
  
  # Helper methods
  
  def _reset_window_position(self) -> None:
    screen_width, screen_height = self._root.winfo_screenwidth(), self._root.winfo_screenheight()
    window_width, window_height = self._size_config.window
    self._position.x,self._position.y = screen_width - window_width, screen_height- window_height - TASKBAR_OFFSET
    
    self._root.geometry(f'+{self._position.x}+{self._position.y}')
    self._config['position'] = {
      'x': self._position.x,
      'y': self._position.y
    }
    
    with open(SETTINGS_PATH, 'w') as configfile:
      self._config.write(configfile)
      
  def _get_colour(self) -> str:
    glucose_value = self._glucose_value.get()
    colour = TEXT
    if(glucose_value != '---' and float(glucose_value) <= self._bottom_threshold):
      colour = WARNING_BOTTOM
    if(glucose_value != '---' and float(glucose_value) >= self._upper_threshold):
      colour = WARNING_UPPER
    return colour

  def _update_widget(self) -> None:
    self._units.set('mg/dL' if not self._mmol else 'mmol/L')
    glucose_size, unit_size = self._size_config.font_glucose, self._size_config.font_units
    self._glucose_value_label.config(font=('Inter', glucose_size))
    self._unit_label.config(font=('Inter', unit_size))
    
    try:
      # Check whether window position is not set to ''
      self._position.x = int(self._position.x)
      self._position.y = int(self._position.y)
      
      # Position the window
      window_width, window_height =  self._size_config.window
          
      self._root.geometry(f'{window_width}x{window_height}+{self._position.x}+{self._position.y}')
    except ValueError:
      self._reset_window_position()
  
  # Public methods
  
  def read_settings(self) -> None:
    self._size_config: Sizing = SIZE[self._config['settings']['size']]
    self._tray_icon.set_size(self._config['settings']['size'])
    self._interval: int = int(self._config['settings']['interval'])
    self._upper_threshold: float = float(self._config['settings']['upper_threshold'])
    self._bottom_threshold: float = float(self._config['settings']['bottom_threshold'])
    self._mmol: bool = self._config['settings'].getboolean('mmol')
    
    self._moveable: bool = False
    self._position: Position = Position(
      x = self._config['position']['x'],
      y = self._config['position']['y']
    )
    self._update_widget()
    
  def set_glucose_fetcher(self, dex_api: DexcomApi) -> None:
    self._glucose_fetcher.setDexcomApi(dex_api)
      
  def start_glucose_fetching(self) -> None:
    if(self._glucose_fetcher is None):
      raise Exception('The glucose fetcher not set!')
    # exception handling done in Setup.py
    self._glucose_fetcher.start_fetch_loop()
  
  def configure_widget(self) -> None:
    self.read_settings()
    self.start_glucose_fetching()
    self._tray_icon.show_tray()
  
  def close_widget(self) -> None:
    self._glucose_fetcher.stop_fetch_loop()
    self._tray_icon.close_tray()
    self._root.destroy()