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
    
    self._tray = pystray.Icon('Dextop', icon=create_image(), menu=self._initialise_menu())
    
  def _initialise_menu(self) -> pystray.Menu:
    return pystray.Menu(
      pystray.MenuItem(
        'Size',
        pystray.Menu(
          pystray.MenuItem(
            'Normal',
            lambda: self._on_resize('NORMAL'),
            checked = lambda _: self._size == 'NORMAL'
          ),
          pystray.MenuItem(
            'Large',
            lambda: self._on_resize('LARGE'),
            checked = lambda _: self._size == 'LARGE'
          )
        )
      ),
      pystray.MenuItem(
        'Draggable',
        self._on_toggle_drag,
        checked= lambda _: self._draggable
    ),
      pystray.MenuItem(
        'Reset Position',
        self._callbacks.reset_window_position,
        checked=None
    ),
      pystray.MenuItem(
        'Settings',
        self._on_open_settings,
        checked=None
      ),
      pystray.MenuItem(
        'Close',
        self._on_close_tray,
        checked=None
      )
    )
  
  def _on_close_tray(self) -> None:
    self._callbacks.generate_close_event()
    self._tray.stop()
    
  def _on_open_settings(self) -> None:
    self._callbacks.generate_open_settings_event()
    self._tray._hide()
  
  def _on_toggle_drag(self) -> None:
    self._draggable = not self._draggable
    self._tray.update_menu()  
    
    if(self._draggable):
      self._callbacks.generate_enable_drag_event()
    else:
      self._callbacks.generate_disable_drag_event()
  
  def _on_resize(self,size) -> None:
    if(self._size == size): return
    self._size = size
    self._callbacks.generate_resize_event(size)
    
  # Public methods
  
  def show_tray(self) -> None:
    # if(not self._tray.visible):
    self._tray._show()
  
  def run_tray_icon(self) -> None:
    self._tray.run_detached()
  
  # to use, when the closing happens, becuase parent of widget was closed
  def close_tray(self) -> None:
    self._tray.stop()
  
  def hide_tray(self) -> None:
    self._tray._hide()
  
  def set_size(self, size) -> None:
    self._size = size