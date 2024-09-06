# pydexcom
from pydexcom import Dexcom
from pydexcom import errors as dexcom_errors
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
    
    # Exception handling done in Setup.py component
    self._dexcom = Dexcom(self._username, self._password, ous=ous)
    
  def fetch_glucose_reading(self):
    if(not self._dexcom):
      raise Exception('Dexcom API not initialised.')
    
    # Exception handling done in Widget.py
    reading = self._dexcom.get_current_glucose_reading()
    return DexcomData(
      glucose_reading=reading.value, 
      trend=reading.trend
    )

# Class initiating periodical fetch loop
class GlucoseFetcher:
  def __init__(self, dex_api: DexcomApi, interval:int, generate_fail_event: Callable[[],None], generate_update_event: Callable[[str,int,int],None]) -> None:
    self._dex_api = dex_api
    self._interval = interval * 60
    self._generate_fail_event = generate_fail_event
    self._generate_update_event = generate_update_event
    self._stop_event = threading.Event()
    self._thread: Optional[threading.Thread] = None
    
  def _fetch_loop(self, interval: int):
    while(not self._stop_event.is_set()):
      try:
        reading = self._dex_api.fetch_glucose_reading()
        self._generate_update_event(reading.glucose_reading, reading.trend)
        
      except dexcom_errors.DexcomError as e:
        self._generate_fail_event(e)
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