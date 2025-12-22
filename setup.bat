@echo off
echo Starting Travel Assistant...
echo.

echo Setting up Python environment...
cd backend
python -m venv venv 2>nul
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo To start the backend server:
echo cd backend
echo venv\Scripts\activate
echo python app.py
echo.

echo To start the frontend (in a new terminal):
echo cd frontend
echo npm install
echo npm start
echo.

echo Make sure to create .env file in backend/ with your OPENAI_API_KEY
pause