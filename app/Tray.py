# GUI
import pystray
# Image manipulation
from PIL import Image
# Typing 
from typing import Callable, Literal
from dataclasses import dataclass


def create_image() -> Image:
  return Image.open('./assets/dextop_icon.png')  # Replace with your image file path
  
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
  def __init__(self, callbacks: TrayCallbacks, size: Literal['LARGE', 'NORMAL']) -> None:
    self._callbacks = callbacks
    self._draggable = False
    self._size = size
    
    self._tray = pystray.Icon('Dextop', icon=create_image(64, 64), menu=self._initialise_menu())
    
  def _initialise_menu(self) -> pystray.Menu:
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