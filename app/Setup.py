import tkinter as tk
import tkinter.messagebox as mb
from configparser import ConfigParser
from .DexcomApi import DexcomApi
from pydexcom import errors as dexcom_errors
from .Consts import *
import keyring
from .Widget import Widget

class SetupWindow:
  def __init__(self) -> None:
    self._root = tk.Tk()
    self._initialise_settings()
    self._initialize_window()
    if(self._check_logged_in()):
      self._root.withdraw()
      self._skip_setup()
    self._root.mainloop()
  
  def _initialise_settings(self) -> None:
    # TODO ADD ERRORS CHECK
    self._config = ConfigParser()
    self._config.read(SETTINGS_PATH)
    
    for section, keys in DEFAULT_SETTINGS.items():
      if section not in self._config:
        self._config.add_section(section)
      for key, value in keys.items():
        if not self._config.has_option(section, key) or not self._config[section][key]:
          self._config.set(section, key, value)
          
    with open(SETTINGS_PATH, 'w') as config_file:
      self._config.write(config_file)

  def _initialize_window(self) -> None:
    self._root.title("Setup Window")

    # Login field
    login = self._config['credentials']['login']
    tk.Label(self._root, text="Login:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    self._login_entry = tk.Entry(self._root)
    self._login_entry.insert(0,login)
    self._login_entry.grid(row=0, column=1, padx=10, pady=5)

    # Password field
    password = self._get_password(login)
    tk.Label(self._root, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    self._password_entry = tk.Entry(self._root, show="*")
    self._password_entry.insert(0,password)
    self._password_entry.grid(row=1, column=1, padx=10, pady=5)

    # Europe checkbox
    is_europe = self._config['settings']['europe']
    self._europe_var = tk.BooleanVar(value=is_europe)
    self._europe_checkbox = tk.Checkbutton(self._root, text="Europe", variable=self._europe_var)
    self._europe_checkbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    # Settings button
    self._settings_button = tk.Button(self._root, text="Settings ▼", command=self._toggle_more_settings)
    self._settings_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Frame for settings that can be shown/hidden
    self._settings_frame = tk.Frame(self._root, borderwidth=1)

    # Reading Interval field inside settings frame
    tk.Label(self._settings_frame, text="Reading Interval:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    validate_command = (self._root.register(self._validate_numeric),'%P')
    self._interval_entry = tk.Entry(self._settings_frame, width=3, validate="all", validatecommand=validate_command)
    self._insert_interval_value()
    self._interval_entry.grid(row=0, column=1, pady=5)
    
    # Minutes label
    self._minutes_label = tk.Label(self._settings_frame, width=3, text='min')
    self._minutes_label.grid(row=0,column=2)
    

    # Start with settings frame hidden
    self._settings_frame.grid(row=4, column=0, columnspan=2, sticky="we")
    self._settings_frame.grid_remove()

    # Button to submit or proceed (optional)
    self._submit_button = tk.Button(self._root, text="Submit", command=self._submit)
    self._submit_button.grid(row=5, column=0, columnspan=2, pady=10)
    
  def _initialise_dextop_widget(self, login, password, is_europe, interval):
    dex_api = None
    try:
      dex_api = DexcomApi(is_europe, login, password)
    except dexcom_errors.DexcomError as e:
      message_title = 'Error'
      if(type(e) == '<class \'pydexcom.errors.AccountError\'>'): message_title = 'Authentication Error'
      if(type(e) == '<class \'pydexcom.errors.SessionError\'>'): message_title = 'Session Error'
      if(type(e) == '<class \'pydexcom.errors.SessionError\'>'): message_title = 'Settings Error'
      tk.messagebox.showwarning(title=message_title, message=f'{str(e)}!')
      self._reset_settings()
      # The Setup Window is open
      if(self._root.state == 'normal'):
        self._password_entry.delete(0,'end')
        self._password_entry.focus()
      # Setup Window is withdrawn
      else:
        self._root.deiconify()

    if(dex_api): 
      self._save_settings(login,password,is_europe,interval)
      # Hide setup window and create the widget
      if(self._root.wm_state() == 'normal'):
        self._root.withdraw()
      Widget(self._root, dex_api)

  # Helper methods
  
  def _save_settings(self, login: str, password: str, europe: bool, interval: str):
    self._config['settings']['interval'] = str(interval)
    self._config['settings']['europe'] = str(europe)
    self._config['credentials']['login'] = login

    with open(SETTINGS_PATH, 'w') as configfile:
      self._config.write(configfile)
      
    # Store the password using keyring instead of plain text for security
    self._set_password(login,password)
  
  def _reset_settings(self):
    self._config['settings']['interval'] = ''
    self._config['settings']['europe'] = 'False'
    self._config['credentials']['login'] = ''
    with open(SETTINGS_PATH, 'w') as configfile:
      self._config.write(configfile)
  
  def _toggle_more_settings(self) -> None:
    # Toggle the visibility of the settings frame
    if self._settings_frame.winfo_ismapped():
      self._settings_frame.grid_remove()
      self._settings_button.config(text='Settings ▼')
    else:
      self._settings_frame.grid()
      self._settings_button.config(text='Settings ▲')
      # Unfocus entries in the settings
      self._root.focus()

  def _validate_numeric(self, text: str) -> bool:
    # Validate that the input is numeric
    if text.isdigit():
      return 0 < int(text) < 100
    return text == ""
  
  def _insert_interval_value(self):
    # Reads the interval value from settings.ini and inserts it into the input field
    value = self._config['settings']['interval']
    value = str(value)
    for i, digit in enumerate(value):
      self._interval_entry.insert(i, digit)
  
  def _submit(self) -> None:
    login = self._login_entry.get()
    password = self._password_entry.get()
    is_europe = self._europe_var.get()
    interval = self._interval_entry.get()
    self._initialise_dextop_widget(login,password,is_europe, interval)
      
  def _check_logged_in(self):
    login = self._config['credentials']['login']
    if(not login): return False
    
    password = self._get_password(login)
    if(not password): return False

    return True
  
  def _skip_setup(self):
    login = self._config['credentials']['login']
    password = self._get_password(login)
    is_europe = self._config['settings']['europe']
    interval = self._config['settings']['interval']
    self._initialise_dextop_widget(login,password,is_europe,interval)
  
  # Keyring helpers
  
  def _get_password(self, login):
    password = None
    if(login): password = keyring.get_password('dextop', login)
    return password if password is not None else ''

  def _set_password(self,login,password):
    if(login): keyring.set_password("dextop", login, password)
  