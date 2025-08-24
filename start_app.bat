@echo off
echo Starting YouTube Transcript API Server...
echo.
echo The API server will start on http://127.0.0.1:8000
echo The HTML interface will open automatically in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the API server in the background
start /B python main.py

REM Wait a moment for the server to start
timeout /t 3 /nobreak > nul

REM Open the HTML file in the default browser
start index.html

echo.
echo Server is running! You can now use the HTML interface.
echo To stop the server, close this window or press Ctrl+C
echo.

REM Keep the window open
pause
