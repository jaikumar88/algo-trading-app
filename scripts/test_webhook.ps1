$url = 'https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook'
$body = @{ message = 'TEST ALERT from TradingView' } | ConvertTo-Json
try {
    $resp = Invoke-RestMethod -Uri $url -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 15
    $resp | ConvertTo-Json -Depth 5
} catch {
    Write-Output "Request failed: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        try { $_.Exception.Response | ConvertTo-Json -Depth 5 } catch {}
    }
}
