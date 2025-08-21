@echo off
echo 🚀 Starting YouTube Transcript API with ngrok...
echo.

echo 📡 Starting API server...
start "API Server" cmd /k "set NGROK=1 && python main.py"

echo ⏳ Waiting for API to start...
timeout /t 5 /nobreak > nul

echo 🌐 Starting ngrok tunnel...
ngrok http 8000

echo ✅ Both services started!
echo 📱 API: http://localhost:8000
echo 🌐 Public: Check ngrok console above
pause
