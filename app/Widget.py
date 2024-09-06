# GUI
import tkinter as tk
import tksvg
from .SvgTrends import get_trend_arrow_SVG
# Dexcom Api
from .DexcomApi import DexcomApi, GlucoseFetcher
# Clicktrough-hacking - win32
import win32gui
import win32con
# Config Parser
from configparser import ConfigParser
# Tray icon
from .Tray import TrayIcon, TrayCallbacks
# Typing and utility

from dataclasses import dataclass

# Constants
from .Consts import *

@dataclass
class Position:
  x: int
  y: int

class Widget:
  def __init__(self, parent_root: tk.Tk, dex_api: DexcomApi) -> None:
    self._parent_root = parent_root
    self._root = tk.Toplevel()
    self._dex_api = dex_api
    self._initialise_settings()
    self._initialise_GUI_value_display()
    self._initialise_glucose_fetching()
    self._initialise_widget()
    self._initialise_tray()
    self._root.mainloop()
  
  def _initialise_settings(self) -> None:
    self._config = ConfigParser()
    self._config.read(SETTINGS_PATH)
    self._size_config: Sizing = SIZE[self._config['settings']['size']]
    self._interval: int = int(self._config['settings']['interval'])
    self._position: Position = Position(
      x = int(self._config['position']['x']),
      y = int(self._config['position']['y'])
    )
    self._moveable: bool = False
  
  def _initialise_glucose_fetching(self) -> None:
    self._glucose_fetcher = GlucoseFetcher(self._dex_api, self._interval ,self._generate_failed_event, self._generate_udpate_event)
    self._glucose_fetcher.start_fetch_loop()
  
  def _initialise_GUI_value_display(self) -> None:
    self._glucose_value = tk.StringVar(value='---')
    self._trend = tk.IntVar(value=0)
    self._units = tk.StringVar(value='mg/dL')
    
  def _initialise_tray(self):
    callbacks = TrayCallbacks(
      self._generate_close_event,
      self._generate_enable_drag_event,
      self._generate_disable_drag_event,
      self._reset_window_position,
      self._generate_resize_event
    )
    self._tray_icon = TrayIcon(callbacks, self._size_config.size)
    self._tray_icon.run_tray_icon()
    

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
    # self._root.bind("<<Resize>>", lambda event: event_handler(event, event.widget.event_info["data"].arg1, event.widget.event_info["data"].arg2))
    self._root.bind("<<Resize>>", self._on_resize)

    
    # Position the window
    screen_width, screen_height = self._root.winfo_screenwidth(), self._root.winfo_screenheight()
    window_width, window_height =  self._size_config.window
      
    if(self._position.x == '' or self._position.y == ''):
      self._position.x, self._position.y = screen_width - window_width, screen_height - window_height - TASKBAR_OFFSET
      self._config['position'] = {
        'x': str(self._position.x),
        'y': str(self._position.y)
      }
      with open(SETTINGS_PATH, 'w') as configfile:
        self._config.write(configfile)
        
    self._root.geometry(f'{window_width}x{window_height}+{self._position.x}+{self._position.y}')
    
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
    
    # svg = ImageTk.getimage(svg)
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
  
  def _enable_clicktrough(self,init=False):
    hwnd = self._root.winfo_id() if init else win32gui.FindWindow(None, self._root.title())
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    styles = styles | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
    self._root.attributes('-transparentcolor', '#000000')

  def _disable_clicktrough(self,init=False):
    hwnd = self._root.winfo_id() if init else win32gui.FindWindow(None, self._root.title())
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    styles = styles & ~win32con.WS_EX_LAYERED  # Remove the layered style
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)  # Set new styles
  
  # Event handlers
  
  def _on_close(self,_=None):
    self._glucose_fetcher.stop_fetch_loop()
    self._root.destroy()
    self._parent_root.destroy()
  
  def _on_update(self, _):
    trend = self._trend.get()
    colour = self._get_colour()
    
    self._glucose_value_label.config(fg=colour)
    
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(trend,colour,self._size_config.svg))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
  
  def _on_fail(self,_):
    self._glucose_value_label.config(fg=TEXT)
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(0,TEXT, self._size_config.svg))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
  
  def _on_enable_drag(self,_):
    self._disable_clicktrough()
    self._moveable = True
  
  def _on_disable_drag(self,_):
    self._enable_clicktrough()
    self._moveable = False
    
  def _on_start_drag(self,event):
    if(self._moveable):
      self._root.x = event.x
      self._root.y = event.y

  def _on_stop_drag(self,_):
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
    
  def _on_drag(self,event):
    if(self._moveable):
      delta_x = event.x - self._root.x
      delta_y = event.y - self._root.y
      x = self._root.winfo_x() + delta_x
      y = self._root.winfo_y() + delta_y
      window_width,window_height =self._size_config.window
      self._root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
  def _on_resize(self,_):
    window_width, window_height = self._size_config.window
    self._root.geometry(f'{window_width}x{window_height}')
    self._glucose_value_label.configure(font=('Inter',self._size_config.font_glucose))
    self._unit_label.configure(font=('Inter',self._size_config.font_units))
    
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG((self._trend.get()),self._get_colour(),self._size_config.svg))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
    
    self._config['settings']['size'] = self._size_config.size
    with open(SETTINGS_PATH, 'w') as config_file:
      self._config.write(config_file)
  
  # Event generating methods
  
  def _generate_udpate_event(self,glucose_value:str, trend:int):
    self._glucose_value.set(glucose_value)
    self._trend.set(trend)
    self._root.event_generate("<<Update>>",when='now')

  def _generate_failed_event(self,e):
    self._glucose_value.set('---')
    self._trend.set(0)
    self._root.event_generate("<<Failed>>",when='now')
    
    # TODO add log files
    message_title = 'Error'
    if(type(e) == '<class \'pydexcom.errors.AccountError\'>'): message_title = 'Authentication Error'
    if(type(e) == '<class \'pydexcom.errors.SessionError\'>'): message_title = 'Session Error'
    if(type(e) == '<class \'pydexcom.errors.SessionError\'>'): message_title = 'Settings Error'
    print(f'{message_title} has occured: {e}')
  
  def _generate_close_event(self):
    self._root.event_generate("<<Close>>", when='now')
    
  def _generate_enable_drag_event(self):
    self._root.event_generate('<<Start_Drag>>', when='now')
    
  def _generate_disable_drag_event(self):
    self._root.event_generate('<<Stop_Drag>>', when='now')
  
  def _generate_resize_event(self, size):
    self._size_config = SIZE[size]
    self._root.event_generate('<<Resize>>', when='now')
  
  # Helper methods
  
  def _reset_window_position(self):
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
      
  def _get_colour(self):
    glucose_value = self._glucose_value.get()
    colour = TEXT
    if(glucose_value != '---' and int(glucose_value) <= TRESHOLD_BOTTOM):
      colour = WARNING_BOTTOM
    if(glucose_value != '---' and int(glucose_value) >= TRESHOLD_UPPER):
      colour = WARNING_UPPER
    return colour