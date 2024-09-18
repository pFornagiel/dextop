# pydexcom
from pydexcom import Dexcom
from pydexcom import errors as dexcom_errors
# Utils
import threading
from .Logger import Logger
import requests
# Config
from .Consts import LOGGER_PATH
# Typing
from typing import Callable, Optional
from dataclasses import dataclass

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
    
  def fetch_glucose_reading(self) -> DexcomData:
    if(not self._dexcom):
      raise Exception('Dexcom API not initialised.')
    
    # Exception handling done in GlucoseFetcher
    reading = self._dexcom.get_current_glucose_reading()
    return DexcomData(
      glucose_reading=reading.value, 
      trend=reading.trend
    )

# Class initiating periodical fetch loop
class GlucoseFetcher:
  def __init__(self, interval:int, generate_fail_event: Callable[[],None], generate_update_event: Callable[[str,int,int],None]) -> None:
    self._interval = interval * 60
    self._generate_fail_event = generate_fail_event
    self._generate_update_event = generate_update_event
    self._stop_event = threading.Event()
    self._thread: Optional[threading.Thread] = None
    self._logger = Logger(LOGGER_PATH)
    
    self._dex_api: Optional[DexcomApi] = None
    
  def _fetch_loop(self, interval: int) -> None:
    while(not self._stop_event.is_set()):
      try:
        reading = self._dex_api.fetch_glucose_reading()
        self._generate_update_event(reading.glucose_reading, reading.trend)
        
      except Exception as e:
        self._generate_fail_event(e)
        
        message_title = 'Error'
        if(isinstance(e,dexcom_errors.AccountError)): message_title = 'Authentication Error'
        if(isinstance(e,dexcom_errors.SessionError)): message_title = 'Session Error'
        if(isinstance(e,dexcom_errors.ArgumentError)): message_title = 'Settings Error'
        if(isinstance(e,requests.exceptions.RequestException)): message_title = 'General HTTP Error'
        if(
          isinstance(e,requests.exceptions.ConnectionError) or 
          isinstance(e,requests.exceptions.RetryError)
        ): message_title = 'Connection Error'
        
        self._logger.add_entry(f'{message_title}: {e}')
        
      self._stop_event.wait(interval)

  def setDexcomApi(self, dex_api: DexcomApi) -> None:
    self._dex_api = dex_api
         
  def start_fetch_loop(self) -> None:
    if(self._dex_api is None):
      raise Exception('DexcomApi not set!')
    
    if(not self._thread or not self._thread.is_alive()):
      self._stop_event.clear()
      self._thread = threading.Thread(target=self._fetch_loop, args=([self._interval]))
      self._thread.start()
  
  def stop_fetch_loop(self) -> None:
    if(self._thread and self._thread.is_alive()):
      self._stop_event.set()
      self._thread.join()
      self._thread = None