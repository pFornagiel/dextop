# Dextop Widget
## Desktop Dexcom Readings Display

Dextop is a Python-based Windows desktop widget which displays real-time Dexcom glucose readings using the Dexcom Share service API provided by [pydexcom](https://github.com/gagebenne/pydexcom). 

The app is a personal project, which was motivated by a need to keep an eye on my glucose levels while working, without having to constantly check the phone application. The project is still work in progress.

## Features

- Always-on-top, unobstructing widget
- Real-time Dexcom glucose readings
- Graphical settings interface
- Position, size customisation and configurability

## Prerequisites
- Python 3.x
- pip 24.1.1
- Windows operating system

## Installation

Note: At the moment, the project is developed and tested specifically for Windows. Unix system support may be added in the future.

1. Clone the repository:
  ```bash
   git clone https://github.com/pFornagiel/dextop.git
   cd dextop
  ```
2. Run the batch script to create a virtual environment and install dependencies:

  ```bash
  venv_setup.bat
  ```
3. Activate the virtual environment:
```bash
  .venv\Scripts\activate
  ```

4. Run `run.py` file

## Using the Widget

The [pydexcom's repository](https://github.com/gagebenne/pydexcom) goves detailed instruction about the user-end usage of Dexcom Share API and I highly encourage to read it through. 

A quick summary:
1. Download the [Dexcom G7 / G6 / G5 / G4 / One+ mobile app](https://www.dexcom.com/apps) and [enable the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow).

2. In the application, log in using **your** Dexcom Account credentials, **not the Dexcom Share follower's or manager's**.

3. Make sure to toggle the *Europe* checkbox in the app settings, if you happen to use the application outside of America. Note, that *Password not valid!* may also be caused by this option, if the user happens to be using the app in the wrong region.

After logging in, the widget itself can be configured using a tray icon associated with it. By right clicking, a set of options will be shown, allowing for changing the size of the widget, moving it around the screen, adjusting authentication settings and closing the app.

### Disclaimer:

*I am utilizing the Dexcom Share API solely for personal use and do not have any affiliation with Dexcom, Inc. This application is not endorsed, sponsored, or managed by Dexcom, and I do not take any responsibility for the accuracy or performance of the data provided through the API. Furthermore, I do not profit from, or claim ownership of, any Dexcom-related content or services. All trademarks, logos, and brand names belong to their respective owners.*