import tkinter as tk
import tkinter.messagebox as mb
from configparser import ConfigParser
from .DexcomApi import DexcomApi
from pydexcom import errors as dexcom_errors
from .Consts import *
import keyring
from .Widget import Widget
from .Logger import Logger
from PIL import Image, ImageTk


class SetupWindow:
  def __init__(self) -> None:
    self._root = tk.Tk()
    self._logger = Logger(LOGGER_PATH)
    self._initialise_settings()
    self._initialize_window()

    self._skip_setup() if self._check_logged_in() else self._root.deiconify()
    
    self._root.mainloop()
  
  def _initialise_settings(self) -> None:
    self._config = ConfigParser()
    self._config.read(SETTINGS_PATH)
    
    for section, keys in DEFAULT_SETTINGS.items():
      if section not in self._config:
        self._config.add_section(section)
      for key, value in keys.items():
        if not self._config.has_option(section, key) or not self._config[section][key]:
          self._config[section][key] = value
        
        # OPTION SPECIFIC ERROR CHECKS
        reset_to_default = False
        if(key in ('x', 'y', 'upper_threshold', 'bottom_threshold')):
          # EAFP
          try:
            float(self._config[section][key])
          except ValueError:
            reset_to_default = True
        
        if(key == 'interval'):
          if(not self._config[section][key].isdigit()):
            reset_to_default = True
            
        if(key == 'size'):
          if(self._config[section][key] not in ('NORMAL', 'LARGE')):
            reset_to_default = True
            
        if(key in ('europe', 'mmol')):
          if(self._config[section][key] not in ('True', 'False')):
            reset_to_default = True
              
        if(reset_to_default): self._config.set(section,key,value)
          
    with open(SETTINGS_PATH, 'w') as config_file:
      self._config.write(config_file)

  def _initialize_window(self) -> None:
    self._root.title("Settings")
    self._root.resizable(False,False)
    self._root.withdraw()
    
    image = Image.open('./assets/dextop_icon.png')  # Replace with your image file path
    icon_photo = ImageTk.PhotoImage(image)
    self._root.iconphoto(True, icon_photo)

    # Create a container frame for padding around the entire window
    self._main_frame = tk.Frame(self._root, padx=20, pady=20)  # Add 20px padding around the root
    self._main_frame.grid(row=0, column=0, sticky="nsew")
    self._main_frame.grid_columnconfigure(0, weight=1)
    self._main_frame.grid_columnconfigure(1, weight=1)

    # Login field
    login = self._config['credentials']['login']
    tk.Label(self._main_frame, text="Login:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    self._login_entry = tk.Entry(self._main_frame, width=25)
    self._login_entry.insert(0,login)
    self._login_entry.grid(row=0, column=1, padx=10, pady=5)

    # Password field
    password = self._get_password(login)
    tk.Label(self._main_frame, text="Password:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    self._password_entry = tk.Entry(self._main_frame, show="*", width=25)
    self._password_entry.insert(0,password)
    self._password_entry.grid(row=1, column=1, padx=10, pady=5)

    # Europe checkbox
    is_europe = self._config['settings']['europe']
    self._europe_var = tk.BooleanVar(value=is_europe)
    self._europe_checkbox = tk.Checkbutton(self._main_frame, text="Europe", variable=self._europe_var)
    self._europe_checkbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    # Settings button
    self._settings_button = tk.Button(self._main_frame, text="Settings ▼", command=self._toggle_more_settings, width=30)
    self._settings_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Frame for settings that can be shown/hidden
    self._settings_frame = tk.Frame(self._main_frame, borderwidth=1)
    
    # MMOL/L checkbox
    is_mmol = self._config['settings']['mmol']
    self._mmol_var = tk.BooleanVar(value=is_mmol)
    self._mmol_checkbox = tk.Checkbutton(self._settings_frame, text="Readings in mmol/L", variable=self._mmol_var, command=self._on_mmol_button_click)
    self._mmol_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
    self._unit_label_var = tk.StringVar(value='mmol/L' if is_mmol else 'mg/dL')

    # Reading Interval field inside settings frame
    tk.Label(self._settings_frame, text="Reading Fetch Interval:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    validate_command = (self._root.register(self._validate_numeric),'%P')
    self._interval_entry = tk.Entry(self._settings_frame, width=4, validate="all", validatecommand=validate_command)
    self._insert_interval_value()
    self._interval_entry.grid(row=1, column=1, pady=5)
    
    # Minutes label
    self._interval_label = tk.Label(self._settings_frame, width=8, text='minutes')
    self._interval_label.grid(row=1,column=2, sticky='w')

    # Upper Threshold field inside settings frame
    tk.Label(self._settings_frame, text="High Glucose Warning:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    validate_command = (self._root.register(self._validate_numeric),'%P')
    self._upper_threshold_entry = tk.Entry(self._settings_frame, width=4, validate="all", validatecommand=validate_command)
    self._insert_upper_threshold_value()
    self._upper_threshold_entry.grid(row=2, column=1, pady=5)
    
    # mg/dL label
    self._upper_threshold_label = tk.Label(self._settings_frame, width=7, textvariable=self._unit_label_var)
    self._upper_threshold_label.grid(row=2,column=2, sticky="w")
    
    # Bottom Threshold field inside settings frame
    tk.Label(self._settings_frame, text="Low Glucose Warning:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    validate_command = (self._root.register(self._validate_numeric),'%P')
    self._bottom_threshold_entry = tk.Entry(self._settings_frame, width=4, validate="all", validatecommand=validate_command)
    self._insert_bottom_threshold_value()
    self._bottom_threshold_entry.grid(row=3, column=1, pady=5)
    
    # mg/dL label
    self._bottom_threshold_label = tk.Label(self._settings_frame, width=7, textvariable=self._unit_label_var)
    self._bottom_threshold_label.grid(row=3,column=2, sticky="w")

    # Start with settings frame hidden
    self._settings_frame.grid(row=4, column=0, columnspan=2, sticky="we")
    self._settings_frame.grid_remove()

    # Confirm button
    self._submit_button = tk.Button(self._main_frame, text="Confirm", command=self._on_submit, width=30)
    self._submit_button.grid(row=5, column=0, columnspan=2, pady=10)
    
    # Center the window on the screen
    self._root.update_idletasks()  # Ensure window is updated with its final size
    window_width = self._root.winfo_width()
    window_height = self._root.winfo_height()
    screen_width = self._root.winfo_screenwidth()
    screen_height = self._root.winfo_screenheight()
    x_coordinate = (screen_width // 2) - (window_width // 2)
    y_coordinate = (screen_height // 2) - (window_height // 2)
    self._root.geometry(f"+{x_coordinate}+{y_coordinate}")

    
  def _initialise_dextop_widget(self, login: str, password: str, is_europe: bool, interval:str, upper_threshold: str, bottom_threshold: str, mmol: bool) -> None:
    dex_api = None
    try:
      dex_api = DexcomApi(is_europe, login, password)
    except dexcom_errors.DexcomError as e:
      message_title = 'Error'
      if(isinstance(e,dexcom_errors.AccountError)): message_title = 'Authentication Error'
      if(isinstance(e,dexcom_errors.SessionError)): message_title = 'Session Error'
      if(isinstance(e,dexcom_errors.ArgumentError)): message_title = 'Settings Error'
      self._logger.add_entry(entry=f'{message_title}: {e}')
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
      self._save_settings(login,password,is_europe,interval, upper_threshold, bottom_threshold, mmol)
      # Hide setup window and create the widget
      if(self._root.wm_state() == 'normal'):
        self._root.withdraw()
      Widget(self._root, dex_api)
  
  # Saving and reseting settings
  
  def _save_settings(self, login: str, password: str, europe: bool, interval: str, upper_threshold: str, bottom_threshold: str, mmol: str) -> None:
    self._config['settings']['interval'] = str(interval)
    self._config['settings']['europe'] = str(europe)
    self._config['settings']['upper_threshold'] = str(upper_threshold)
    self._config['settings']['bottom_threshold'] = str(bottom_threshold)
    self._config['settings']['mmol'] = str(mmol)
    self._config['credentials']['login'] = login

    with open(SETTINGS_PATH, 'w') as configfile:
      self._config.write(configfile)
      
    # Store the password using keyring instead of plain text for security
    self._set_password(login,password)
  
  def _reset_settings(self) -> None:
    self._config['settings']['interval'] = DEFAULT_SETTINGS['settings']['interval']
    self._config['settings']['europe'] = DEFAULT_SETTINGS['settings']['europe']
    self._config['settings']['upper_threshold'] = DEFAULT_SETTINGS['settings']['upper_threshold']
    self._config['settings']['bottom_threshold'] = DEFAULT_SETTINGS['settings']['bottom_threshold']
    self._config['credentials']['login'] = DEFAULT_SETTINGS['credentials']['login']
    with open(SETTINGS_PATH, 'w') as configfile:
      self._config.write(configfile)
  
  # Helper methods
  
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
    # EAFP
    try:
      return 0 < float(text) < 1000
    except ValueError:
      return text == ''
  
  def _insert_interval_value(self) -> None:
    # Reads the interval value from settings.ini and inserts it into the input field
    value = self._config['settings']['interval']
    value = str(value)
    for i, digit in enumerate(value):
      self._interval_entry.insert(i, digit)
      
  def _insert_upper_threshold_value(self) -> None:
    # Reads the upper_threshold value from settings.ini and inserts it into the input field
    value = self._config['settings']['upper_threshold']
    value = str(value)
    for i, digit in enumerate(value):
      self._upper_threshold_entry.insert(i, digit)
      
  def _insert_bottom_threshold_value(self) -> None:
    # Reads the bottom_threshold value from settings.ini and inserts it into the input field
    value = self._config['settings']['bottom_threshold']
    value = str(value)
    for i, digit in enumerate(value):
      self._bottom_threshold_entry.insert(i, digit)
      
  def _check_logged_in(self) -> bool:
    login = self._config['credentials']['login']
    if(not login): return False
    
    password = self._get_password(login)
    if(not password): return False

    return True
  
  def _skip_setup(self) -> None:
    login = self._config['credentials']['login']
    password = self._get_password(login)
    is_europe = self._config['settings'].getboolean('europe')
    interval = self._config['settings']['interval']
    upper_threshold = self._config['settings']['upper_threshold']
    bottom_threshold = self._config['settings']['bottom_threshold']
    mmol = self._config['settings'].getboolean('mmol')
    
    self._initialise_dextop_widget(login,password,is_europe,interval, upper_threshold, bottom_threshold, mmol)
    
  # Event handlers
  
  def _on_mmol_button_click(self):
    is_mmol = self._mmol_var.get()
    self._unit_label_var.set('mmol/L' if is_mmol else 'mg/dL')
    
    upper_threshold = self._upper_threshold_entry.get()
    bottom_threshold = self._bottom_threshold_entry.get()
    if(not upper_threshold): upper_threshold = 0
    if(not bottom_threshold): bottom_threshold = 0
    upper_threshold = float(upper_threshold)
    bottom_threshold = float(bottom_threshold)
    
    if(is_mmol):
      upper_threshold =  str(round(upper_threshold / MMOL_FACTOR, 1))
      bottom_threshold = str(round(bottom_threshold / MMOL_FACTOR, 1))
    else:
      upper_threshold =  str(round(upper_threshold * MMOL_FACTOR))
      bottom_threshold = str(round(bottom_threshold * MMOL_FACTOR))
      
    self._upper_threshold_entry.delete(0,'end')
    self._bottom_threshold_entry.delete(0,'end')
    
    for i, digit in enumerate(upper_threshold):
      self._upper_threshold_entry.insert(i, digit)
    for i, digit in enumerate(bottom_threshold):
      self._bottom_threshold_entry.insert(i, digit)
      
  def _on_submit(self) -> None:
    login = self._login_entry.get()
    password = self._password_entry.get()
    is_europe = self._europe_var.get()
    interval = self._interval_entry.get()
    upper_threshold = self._upper_threshold_entry.get()
    bottom_threshold = self._bottom_threshold_entry.get()
    mmol = self._mmol_var.get()
    self._initialise_dextop_widget(login,password,is_europe, interval, upper_threshold, bottom_threshold, mmol)
  
  # Keyring helpers
  
  def _get_password(self, login) -> str:
    password = None
    if(login): password = keyring.get_password('dextop', login)
    return password if password is not None else ''

  def _set_password(self,login,password) -> None:
    if(login): keyring.set_password("dextop", login, password)
  