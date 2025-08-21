Write-Host "🚀 Starting YouTube Transcript API with ngrok..." -ForegroundColor Green
Write-Host ""

Write-Host "📡 Starting API server..." -ForegroundColor Yellow
$env:NGROK = "1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py"

Write-Host "⏳ Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🌐 Starting ngrok tunnel (using ngrok.yml)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok start --config ngrok.yml youtube-api"

Write-Host "⏳ Waiting for ngrok to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
  $tunnels = Invoke-RestMethod -Uri http://127.0.0.1:4040/api/tunnels
  $public = ($tunnels.tunnels | Where-Object { $_.name -like '*youtube-api*' -or $_.public_url -like 'https*' } | Select-Object -First 1).public_url
} catch {
  $public = $null
}

Write-Host "✅ Both services started!" -ForegroundColor Green
Write-Host "📱 API: http://localhost:8000" -ForegroundColor Cyan
if ($public) {
  Write-Host "🌐 Public: $public" -ForegroundColor Cyan
} else {
  Write-Host "🌐 Public: Open http://127.0.0.1:4040/status and copy the https URL" -ForegroundColor Cyan
}
Read-Host "Press Enter to continue"
