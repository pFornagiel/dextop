
# Dextop Widget
## Unofficial Desktop Dexcom Readings Display

![Github](https://github.com/user-attachments/assets/748f8352-61c6-49ba-9ece-68aa947b9654)

Dextop is a Python-based Windows desktop widget which displays real-time Dexcom glucose readings using the Dexcom Share service API provided by [pydexcom](https://github.com/gagebenne/pydexcom). 

The app is a personal project, which was motivated by a need to keep an eye on my glucose levels while working, without having to constantly check the phone application. The project is still work in progress.

## Features

- Always-on-top, unobstructing widget
- Real-time Dexcom glucose readings
- Graphical settings interface
- Position and size customisation and configurability

## Prerequisites
- Python 3.x
- pip 24.1.1
- Windows operating system

## Installation

> [!NOTE]
> At the moment, the project is developed and tested specifically for Windows. Unix system support may be added in the future. 

> [!IMPORTANT]
> If you choose to use the standalone executable installation, please be aware that **the executable files may be auto-detected as false positives** (harmless files seen as a viruses) by some security vendors, [which is a common case when using python-to-exe compilers](https://www.reddit.com/r/learnpython/comments/13igjrl/nuitka_hello_world_binary_detected_as_malware_why/). Currently, I am unable to do anything about this matter, so if this happens the reccomended fix is to add the file to anti-virus exceptions. I assure, that the installer distribution of the application is an exact build of the project as available in the repository. If you have any concerns about the files` integrity or security, it is encouraged to verify it by building the project from the source code yourself.

### Running Script Locally

1. Clone the repository:
  ```bash
   git clone https://github.com/pFornagiel/dextop.git
   cd dextop
  ```
2. Run the `venv_setup` batch script from the project`s root folder to create a virtual environment and install dependencies:

  ```bash
  scripts/venv_setup.bat
  ```
3. Activate the virtual environment:
```bash
  .venv\Scripts\activate
  ```

4. Run `Dextop.py` file

### Compiling Script Locally

[Nuitka](https://nuitka.net/) is the package of choice for the project, when it comes to compiling python files to an independent executable. I have provided a batch script to further simplify this process.

1. Clone the repository:
  ```bash
   git clone https://github.com/pFornagiel/dextop.git
   cd dextop
  ```
2. Run the `venv_setup` batch script from the project`s root folder to create a virtual environment and install dependencies:
  ```bash
  scripts/venv_setup.bat
  ```
3. Run the `nuitka_compile` batch script from the project`s root folder to compile the project into an executable file
  ```bash
  scripts/nuitka_compile.bat
  ```
4. `Dextop.dist` directory will be created, where an executable `Dextop.exe` file can be used to launch the application.

### Using the Installer

[The Releases tab](https://github.com/pFornagiel/dextop/releases) provides the windows installer download link. The installer itself was created using  [InstallForge](https://installforge.net/) and, as said above, it **installs an exact build of the project as available in the repository**. The installer provides step-by-step instructions and installs the compiled build in user's directory of choice. 

Note, that running the installer will probably trigger *Windows protected your PC* window. It is a standard windows security measure, which is triggered when unknown executable is run. In order to proceed with the installation, click the `More Info` button and choose `Run anyway` option.

#### Additional option: [Allowing the app to launch at startup](https://www.dell.com/support/kbdoc/en-us/000124550/how-to-add-app-to-startup-in-windows-10)

## Widget Usage Instructions

The [pydexcom's repository](https://github.com/gagebenne/pydexcom) gives detailed instructions about the user-end usage of Dexcom Share API and I highly encourage to read it through. 

A quick summary and step-by-step instructions:
1. Download the [Dexcom G7 / G6 / G5 / G4 / One+ mobile app](https://www.dexcom.com/apps) and [enable the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow).

2. In the application, log in using <ins>**your**</ins> Dexcom Account credentials, <ins>not the Dexcom Share follower's or manager's</ins>.

3. Make sure to toggle the *Europe* checkbox in the app settings, if you happen to use the application outside of America. Note, that *Password not valid!* error may be caused by this option, if the user happens to be using the app in the wrong region.

To access Dexcom readings, the app needs to be provided an internet connection. After logging in, the widget can be configured using a tray icon associated with it (an icon in the bottom-right corner of the taskbar). By right clicking the icon, a set of options will be shown:
- `Size`, allows for choosing one of available sizes for the widget.
- `Draggable`, allows for moving the widget around the screen. When the option is disactivated, the widget is semitransparent, uninteractable and click-trough. After toggling On the option, the widget stops being transparent and can be dragged around using the mouse. Position the widget on the screen while *Draggable* option is On and when you are satisfied, toggle it Off to save its new location.
- `Reset Position`, resets widget's position to default (bottom-right corner of the screen).
- `Settings`, opens *Settings* window, where user credentials and other options can be set.
- `Close`, closes the applicaiton.

The app makes use of `%appdata%/dextop` directory, which stores the following files:
- `settings.ini` configuration file
- logs of encountered errors

## Disclaimer:

>*I am utilizing the Dexcom Share API solely for personal use and do not have any affiliation with Dexcom, Inc. This application is not endorsed, sponsored, or managed by Dexcom, and I do not take any responsibility for the accuracy or performance of the data provided through the API. Furthermore, I do not profit from, or claim ownership of, any Dexcom-related content or services. All trademarks, logos, and brand names belong to their respective owners.*
