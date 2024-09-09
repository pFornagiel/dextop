import os
from datetime import datetime

class Logger:
  def __init__(self, path: str) -> None:
    self._PATH = path
    self._check_valid_path(path)
    
  def _check_valid_path(self) -> None:
    if(not os.path.isdir(self._PATH)): os.mkdir(self._PATH)
    
  def add_entry(self, entry: str) -> None:
    self._check_valid_path(self._PATH)
    
    now = datetime.now()
    month = now.strftime('%m')
    year = now.strftime('%Y')
    filename = os.path.join(self._PATH, f'{month}-{year}-log.txt')
    
    if not os.path.exists(filename):
      with open(filename, 'w') as file:
        file.write('')
    
    time_stamp = now.strftime('[%H:%M %d-%m-%Y]')  # Format: [HH:MM DD-MM-YYYY]
    with open(filename, 'a') as file:
      file.write(f'{time_stamp} {entry}\n')
  
    
    
  
  



    
    