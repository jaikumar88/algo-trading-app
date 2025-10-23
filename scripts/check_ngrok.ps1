$max = 15
for ($i=0; $i -lt $max; $i++) {
    Start-Sleep -Seconds 1
    try {
        $api = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -Method Get -ErrorAction Stop
        if ($api.tunnels) {
            $api.tunnels | ForEach-Object { $_.public_url }
            exit 0
        }
    } catch {
        # ignore and retry
    }
}
Write-Output "No tunnels found"
exit 1
