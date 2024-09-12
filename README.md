
# Dextop Widget
## Desktop Dexcom Readings Display

![Github](https://github.com/user-attachments/assets/a9e00921-b8a5-4687-97dc-b9e6387c1552)

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

4. Run `run.py` file

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

[The Releases tab](https://github.com/pFornagiel/dextop/releases/tag/latest) provides the windows installer download link. The installer itself was created using  [InstallForge](https://installforge.net/) and, as said above, it **installs an exact build of the project as available in the repository**. The installer provides step-by-step instructions and installs the compiled build in user's directory of choice.

## Using the Widget

The [pydexcom's repository](https://github.com/gagebenne/pydexcom) gives detailed instructions about the user-end usage of Dexcom Share API and I highly encourage to read it through. 

A quick summary:
1. Download the [Dexcom G7 / G6 / G5 / G4 / One+ mobile app](https://www.dexcom.com/apps) and [enable the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow).

2. In the application, log in using **your** Dexcom Account credentials, **not the Dexcom Share follower's or manager's**.

3. Make sure to toggle the *Europe* checkbox in the app settings, if you happen to use the application outside of America. Note, that *Password not valid!* may also be caused by this option, if the user happens to be using the app in the wrong region.

After logging in, the widget itself can be configured using a tray icon associated with it. By right clicking, a set of options will be shown, allowing for changing the size of the widget, moving it around the screen, adjusting authentication settings and closing the app.

### Disclaimer:

*I am utilizing the Dexcom Share API solely for personal use and do not have any affiliation with Dexcom, Inc. This application is not endorsed, sponsored, or managed by Dexcom, and I do not take any responsibility for the accuracy or performance of the data provided through the API. Furthermore, I do not profit from, or claim ownership of, any Dexcom-related content or services. All trademarks, logos, and brand names belong to their respective owners.*
