@echo off
echo 🚀 Starting YouTube Transcript API with ngrok...
echo.

echo 📡 Starting API server...
start "API Server" cmd /k "set NGROK=1 && python main.py"

echo ⏳ Waiting for API to start...
timeout /t 5 /nobreak > nul

echo 🌐 Starting ngrok tunnel (using ngrok.yml)...
start "ngrok" cmd /k "ngrok start --config ngrok.yml youtube-api"

echo ⏳ Waiting for ngrok to initialize...
timeout /t 5 /nobreak > nul

for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "try { ($t=(Invoke-RestMethod -Uri http://127.0.0.1:4040/api/tunnels).tunnels | Where-Object { $_.name -like '*youtube-api*' -or $_.public_url -like 'https*' } | Select-Object -First 1).public_url; if(!$t){$t=''}; Write-Output $t } catch { '' }"`) do set PUBLIC_URL=%%A

echo ✅ Both services started!
echo 📱 API: http://localhost:8000
if defined PUBLIC_URL (
  echo 🌐 Public: %PUBLIC_URL%
) else (
  echo 🌐 Public: Open http://127.0.0.1:4040/status and copy the https URL
)
echo:
pause
