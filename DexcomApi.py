# Environmental variables
import os
from dotenv import load_dotenv
load_dotenv()
# pydexcom
from pydexcom import Dexcom
# Threading
import threading
# Types
from typing import Callable
# Error Handling
from urllib.error import HTTPError


USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# Dexcom Data Object Class
class DexcomData:
  def __init__(self, glucose_reading, trend) -> None:
    self.glucose_reading = glucose_reading
    self.trend = trend
    
# Class providing connection to Dexcom Share API
class DexcomApi:
  def __init__(self, ous:bool) -> None:
    self._username =  USERNAME
    self._password = PASSWORD
    self._dexcom: None | Dexcom = None
    
    try:
      self._dexcom = Dexcom(self._username, self._password, ous=ous)
    except Exception as error:
      raise Exception(f'An error has occured: {error}')
    
  def fetch_glucose_reading(self):
    try:
      reading = self._dexcom.get_current_glucose_reading()
      return DexcomData(reading.value,reading.trend)
    except Exception as error:
      raise Exception(f'An error has occured: {error}')

# Class establishing periodical fetch loop
class GlucoseFetcher:
  def __init__(self, dex_api: DexcomApi, interval:int, generate_fail_event: Callable[[],None], generate_update_event: Callable[[str,int,int],None]) -> None:
    self._dex_api = dex_api
    self._stop_event = threading.Event()
    self._thread: None | threading.Thread = None
    self._interval = interval
    self._generate_fail_event = generate_fail_event
    self._generate_update_event = generate_update_event
    
  def _fetch_loop(self, interval: int):
    while(not self._stop_event.is_set()):
      try:
        reading = self._dex_api.fetch_glucose_reading()
        self._generate_update_event(str(reading.glucose_reading), reading.trend)
      except Exception as error:
        self._generate_fail_event(error)
      self._stop_event.wait(interval)
         
  def start_fetch_loop(self):
    self._thread = threading.Thread(target=self._fetch_loop, args=([self._interval]))
    self._thread.start()
  
  def stop_fetch_loop(self):
    if(self._thread):
      self._stop_event.set()
      self._thread.join()