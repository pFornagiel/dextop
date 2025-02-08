# pydexcom
from pydexcom import Dexcom
from pydexcom import errors as dexcom_errors
# Utils
import threading
from .util.Logger import Logger
import requests
import time
# Config
from app.Consts import LOGGER_PATH
# Typing
from typing import Callable, Optional
from dataclasses import dataclass
# Exceptions
from app.Exceptions import NoGlucoseDataError, DexcomApiNotInitialisedError

# Dexcom Data Object Class
@dataclass
class DexcomData:
    glucose_reading: str
    trend: str
    
# Class providing connection to Dexcom Share API
class DexcomClient:
  def __init__(self, ous:bool, username: str, password: str) -> None:
    self._username = username
    self._password = password
    self._dexcom: Optional[Dexcom] = None
    
    # Exception handling done in Setup.py component
    self._dexcom = Dexcom(self._username, self._password, ous=ous)
    
  def fetch_glucose_reading(self) -> DexcomData | None:
    if(not self._dexcom):
      raise DexcomApiNotInitialisedError()
    
    # Exception handling done in GlucoseFetcher
    reading = self._dexcom.get_latest_glucose_reading()
    return DexcomData(
      glucose_reading=reading.value, 
      trend=reading.trend
    ) if reading else None

# Class initiating periodical fetch loop
class GlucoseFetcher:
  def __init__(self, interval:int, generate_fail_event: Callable[[],None], generate_update_event: Callable[[str,int,int],None]) -> None:
    self._interval = interval * 60
    self._generate_fail_event = generate_fail_event
    self._generate_update_event = generate_update_event
    self._stop_event = threading.Event()
    self._thread: Optional[threading.Thread] = None
    self._logger = Logger(LOGGER_PATH)
    
    self._dex_api: Optional[DexcomClient] = None

  def _fetch_and_update(self):
    reading = self._dex_api.fetch_glucose_reading()
    if(reading is None):
      raise NoGlucoseDataError()
    self._generate_update_event(reading.glucose_reading, reading.trend)
 
  def _handle_fetch_error(self, error_messege: str, retry=False, max_retries = 5) -> None:
    attempt = 0
    while(retry and attempt < max_retries):
      try:
        time.sleep(50 * (min(2**(attempt+1), 100)))
        self._fetch_and_update()
        return # Exit on success
      except Exception:
        attempt += 1
        
    self._generate_fail_event(error_messege)
    
    if(retry):
      self._logger.add_entry(error_messege)
    else:
      self._logger.add_entry(f'Failed after {max_retries} retries. {error_messege}')
  
  def _fetch_loop(self, interval: int) -> None:
    while(not self._stop_event.is_set()):
      try:
        self._fetch_and_update()
      except dexcom_errors.AccountError as e:
        self._handle_fetch_error(f'Authentication Error: {e}')
      except dexcom_errors.SessionError as e:
        self._handle_fetch_error(f'Session Error: {e}')
      except dexcom_errors.ArgumentError as e:
        self._handle_fetch_error(f'Settings Error: {e}')
      except (requests.exceptions.ConnectionError, requests.exceptions.RetryError) as e:
        self._handle_fetch_error(f'Connection Error: {e}', retry=True)
      except requests.exceptions.RequestException as e:
        self._handle_fetch_error(f'General HTTP Error: {e}', retry=True)
      except NoGlucoseDataError as e:
        self._handle_fetch_error(f'Data error: {e}', retry=True)
      except Exception as e:
        self._handle_fetch_error('Unexpected Error')
        
      self._stop_event.wait(interval)

  def setDexcomApi(self, dex_api: DexcomClient) -> None:
    self._dex_api = dex_api
         
  def start_fetch_loop(self) -> None:
    if(self._dex_api is None):
      raise DexcomApiNotInitialisedError()
    
    if(not self._thread or not self._thread.is_alive()):
      self._stop_event.clear()
      self._thread = threading.Thread(target=self._fetch_loop, args=([self._interval]))
      self._thread.start()
  
  def stop_fetch_loop(self) -> None:
    if(self._thread and self._thread.is_alive()):
      self._stop_event.set()
      self._thread.join()
      self._thread = None