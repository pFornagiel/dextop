import tkinter as tk
from PIL import Image, ImageDraw
import pystray
from typing import Callable
from dataclasses import dataclass

# Placeholder Image from pystray documentation
def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image
  
@dataclass
class TrayCallbacks:
  generate_close_event: Callable[[],None]
  generate_enable_drag_event: Callable[[],None]
  generate_disable_drag_event: Callable[[],None]
  reset_window_position: Callable[[], None]

# Class for managing the tray icon
class TrayIcon:
  def __init__(self, callbacks: TrayCallbacks) -> None:
    self._callbacks = callbacks
    self._draggable = False
    
    menu = pystray.Menu(
      pystray.MenuItem(
        'Draggable',
        self._toggle_drag,
        checked= lambda item: self._draggable
    ),
      pystray.MenuItem(
        'Reset Position',
        self._callbacks.reset_window_position,
        checked=None
    ),
      pystray.MenuItem(
        'Close',
        self._close_tray,
        checked=None
      ) 
    )
    
    self._tray = pystray.Icon('Dextop', icon=create_image(64, 64, 'black', 'white'), menu=menu)
  
  def _close_tray(self):
    self._callbacks.generate_close_event()
    self._tray.stop()
  
  def _toggle_drag(self):
    self._draggable = not self._draggable
    self._tray.update_menu()  
    
    if(self._draggable):
      self._callbacks.generate_enable_drag_event()
    else:
      self._callbacks.generate_disable_drag_event()
  
  def run_tray_icon(self):
    self._tray.run_detached()