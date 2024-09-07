# Pystray
import pystray
# Typing and utils
from typing import Callable
from dataclasses import dataclass

# Placeholder Image from pystray documentation
from PIL import Image, ImageDraw
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
  generate_resize_event: Callable[[str],None]
  generate_open_settings_event: Callable[[], None]

# Class for managing the tray icon
class TrayIcon:
  def __init__(self, callbacks: TrayCallbacks, size) -> None:
    self._callbacks = callbacks
    self._draggable = False
    self._size = size
    
    self._tray = pystray.Icon('Dextop', icon=create_image(64, 64, 'black', 'white'), menu=self._initialise_menu())
    
  def _initialise_menu(self):
    return pystray.Menu(
      pystray.MenuItem(
        'Size',
        pystray.Menu(
          pystray.MenuItem(
            'Normal',
            lambda: self._resize('NORMAL'),
            checked = lambda _: self._size == 'NORMAL'
          ),
          pystray.MenuItem(
            'Large',
            lambda: self._resize('LARGE'),
            checked = lambda _: self._size == 'LARGE'
          )
        )
      ),
      pystray.MenuItem(
        'Draggable',
        self._toggle_drag,
        checked= lambda _: self._draggable
    ),
      pystray.MenuItem(
        'Reset Position',
        self._callbacks.reset_window_position,
        checked=None
    ),
      pystray.MenuItem(
        'Settings',
        self._open_settings,
        checked=None
      ),
      pystray.MenuItem(
        'Close',
        self._close_tray,
        checked=None
      )
    )
  
  def _close_tray(self) -> None:
    self._callbacks.generate_close_event()
    self._tray.stop()
    
  def _open_settings(self) -> None:
    self._callbacks.generate_open_settings_event()
    self._tray.stop()
  
  def _toggle_drag(self) -> None:
    self._draggable = not self._draggable
    self._tray.update_menu()  
    
    if(self._draggable):
      self._callbacks.generate_enable_drag_event()
    else:
      self._callbacks.generate_disable_drag_event()
  
  def _resize(self,size) -> None:
    if(self._size == size): return
    self._size = size
    self._callbacks.generate_resize_event(size)
  
  def run_tray_icon(self) -> None:
    self._tray.run_detached()