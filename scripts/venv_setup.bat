:: Create the virtual environment
python -m venv .venv

:: Activate the virtual environment
CALL ".venv\Scripts\activate" 

:: Install dependencies from requirements.txt
".venv\Scripts\python.exe" -m pip install -r requirements.txt
