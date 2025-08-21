Write-Host "🚀 Starting YouTube Transcript API with ngrok..." -ForegroundColor Green
Write-Host ""

Write-Host "📡 Starting API server..." -ForegroundColor Yellow
$env:NGROK = "1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py"

Write-Host "⏳ Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🌐 Starting ngrok tunnel..." -ForegroundColor Yellow
ngrok http 8000

Write-Host "✅ Both services started!" -ForegroundColor Green
Write-Host "📱 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🌐 Public: Check ngrok console above" -ForegroundColor Cyan
Read-Host "Press Enter to continue"
