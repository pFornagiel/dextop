# pydexcom
from pydexcom import Dexcom
# Threading
import threading
# Types and dataclasses
from typing import Callable, Optional
from dataclasses import dataclass
# # Error Handling
# from urllib.error import HTTPError



# Dexcom Data Object Class
@dataclass
class DexcomData:
    glucose_reading: str
    trend: str
    
# Class providing connection to Dexcom Share API
class DexcomApi:
  def __init__(self, ous:bool, username: str, password: str) -> None:
    self._username = username
    self._password = password
    self._dexcom: Optional[Dexcom] = None
    
    try:
      self._dexcom = Dexcom(self._username, self._password, ous=ous)
    except Exception as error:
      raise Exception(f'An error has occured during Dexcom API initialization: {error}')
    
  def fetch_glucose_reading(self):
    if(not self._dexcom):
      raise Exception('Dexcom API not initialised.')
    
    try:
      reading = self._dexcom.get_current_glucose_reading()
      return DexcomData(
        glucose_reading=reading.value, 
        trend=reading.trend
      )
    except Exception as error:
      raise Exception(f'An error has occurred while fetching glucose reading: {error}')

# Class establishing periodical fetch loop
class GlucoseFetcher:
  def __init__(self, dex_api: DexcomApi, interval:int, generate_fail_event: Callable[[],None], generate_update_event: Callable[[str,int,int],None]) -> None:
    self._dex_api = dex_api
    self._interval = interval
    self._generate_fail_event = generate_fail_event
    self._generate_update_event = generate_update_event
    self._stop_event = threading.Event()
    self._thread: Optional[threading.Thread] = None
    
  def _fetch_loop(self, interval: int):
    while(not self._stop_event.is_set()):
      try:
        reading = self._dex_api.fetch_glucose_reading()
        self._generate_update_event(reading.glucose_reading, reading.trend)
      except Exception as error:
        self._generate_fail_event(error)
      self._stop_event.wait(interval)
         
  def start_fetch_loop(self):
    if(not self._thread or not self._thread.is_alive()):
      self._stop_event.clear()
      self._thread = threading.Thread(target=self._fetch_loop, args=([self._interval]))
      self._thread.start()
  
  def stop_fetch_loop(self):
    if(self._thread and self._thread.is_alive()):
      self._stop_event.set()
      self._thread.join()