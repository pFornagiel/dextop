# GUI
import tkinter as tk
import tksvg
from SvgTrends import get_trend_arrow_SVG
# Dexcom Api
from DexcomApi import DexcomApi, GlucoseFetcher
# Clicktrough-hacking
import win32gui
import win32con
# Tray icon
from Tray import TrayIcon

# Constants - Colours
WARNING = 'red'
TEXT = 'white'
BACKGROUND = '#292929'
# Treshold = constant for now
TRESHOLD = 70

class Widget:
  def __init__(self, dex_api: DexcomApi) -> None:
    self._root = tk.Tk()
    
    self._moveable = False

    # Dexcom API
    self._dex_api = dex_api
    # Initialise default reading values
    self._glucose_value = tk.StringVar(value='---')
    self._trend = tk.IntVar(value=0)
    self._units = tk.StringVar(value='mg/dL')
    # Initialise glucose fetching loop
    self._glucose_fetcher = GlucoseFetcher(self._dex_api, 60 ,self._generate_failed_event, self._generate_udpate_event)
    self._glucose_fetcher.start_fetch_loop()
    # Initialise the widget and start mainloop
    self._setup_widget()
    self._tray_icon = TrayIcon(self._generate_close_event, self._generate_enable_drag_event, self._generate_disable_drag_event)
    self._tray_icon.run_tray_icon()
    self._root.mainloop()

  def _setup_widget(self) -> None:
    '''initialise widget's attributes'''
    self._root.title("Dextop")
    self._root.configure(background=BACKGROUND)
    self._root.attributes('-alpha',0.7,"-topmost", True)
    self._root.overrideredirect(True)
    
    # Protocols and binds
    self._root.protocol("WM_DELETE_WINDOW", self._on_close)
    self._root.bind('<<Close>>', self._on_close)
    self._root.bind('<<Update>>', self._on_update)
    self._root.bind('<<Failed>>', self._on_fail)
    self._root.bind('<<Start_Drag>>', self._on_enable_drag)
    self._root.bind('<<Stop_Drag>>', self._on_disable_drag)
    self._root.bind("<ButtonPress-1>", self._on_start_move)
    self._root.bind("<ButtonRelease-1>", self._on_stop_move)
    self._root.bind("<B1-Motion>", self._on_drag)
    
    # Unclickability
    self._enable_clicktrough(init=True)
    
    # Position the window
    windowWidth = self._root.winfo_width()
    windowHeight = self._root.winfo_height()
    x = windowWidth + 15
    y = 75
    
    self._root.geometry(f'250x150-{x}-{y}')
    
    # If the glucose level is below the treshold, make it display in the warning colour
    colour = TEXT if self._glucose_value.get() == '---' or int(self._glucose_value.get()) > TRESHOLD else WARNING
    
    # Frames
    self._frame_wrapper = tk.Frame(self._root, background=BACKGROUND)
    self._frame1 = tk.Frame(self._frame_wrapper, background=BACKGROUND)
    self._frame2 = tk.Frame(self._frame_wrapper, background=BACKGROUND)
    
    # Glucose value label
    self._glucose_value_label = tk.Label(
      self._frame1,
      textvariable=self._glucose_value, 
      padx=10, 
      font=('Inter',45),
      fg=colour,
      background=BACKGROUND)
    
    # Trend arrow label displaying SVG
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(self._trend.get(),colour))
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
      font=('Inter',15),
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
  
  def _on_update(self, _):
    glucose_value = self._glucose_value.get()
    trend = self._trend.get()
    colour = TEXT if int(glucose_value) > TRESHOLD else WARNING
    
    self._glucose_value_label.config(fg=colour)
    
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(trend,colour))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
  
  def _on_fail(self,_):
    self._glucose_value_label.config(fg=TEXT)
    svg = tksvg.SvgImage(data=get_trend_arrow_SVG(0,TEXT))
    self._trend_label.config(image=svg)
    self._trend_label.image = svg
    
    self._root.update_idletasks()
  
  def _on_enable_drag(self,_):
    self._disable_clicktrough()
    self._moveable = True
  
  def _on_disable_drag(self,_):
    self._enable_clicktrough()
    self._moveable = False
    
  def _on_start_move(self,event):
    if(self._moveable):
      self._root.x = event.x
      self._root.y = event.y

  def _on_stop_move(self,_):
    if(self._moveable):
      self._root.x = None
      self._root.y = None
    
  def _on_drag(self,event):
    if(self._moveable):
      deltax = event.x - self._root.x
      deltay = event.y - self._root.y
      x = self._root.winfo_x() + deltax
      y = self._root.winfo_y() + deltay
      self._root.geometry(f"+{x}+{y}")
  
  # Event generating methods
  def _generate_udpate_event(self,glucose_value:str, trend:int):
    self._glucose_value.set(glucose_value)
    self._trend.set(trend)
    self._root.event_generate("<<Update>>",when='now')

  def _generate_failed_event(self,error):
    self._glucose_value.set('---')
    self._trend.set(0)
    self._root.event_generate("<<Failed>>",when='now')
    
    print(f'An error has occured: {error}')
  
  def _generate_close_event(self):
    self._root.event_generate("<<Close>>",when='now')
    
  def _generate_enable_drag_event(self):
    self._root.event_generate('<<Start_Drag>>',when='now')
    
  def _generate_disable_drag_event(self):
    self._root.event_generate('<<Stop_Drag>>',when='now')


# Testing initialisation
dex_api = DexcomApi(True)
test = Widget(dex_api)