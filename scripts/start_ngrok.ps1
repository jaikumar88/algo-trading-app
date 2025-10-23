# start_ngrok.ps1
# Helper to start ngrok and print the public URL to expose local Flask /webhook endpoint.
# Requires ngrok to be installed and on PATH. Starts ngrok on port 5000.

param(
    [int]$Port = 5000
)

function Get-NgrokPublicUrl {
    try {
        $api = Invoke-RestMethod -Uri http://127.0.0.1:4040/api/tunnels -Method Get -ErrorAction Stop
        foreach ($t in $api.tunnels) {
            if ($t.public_url -and $t.config -and $t.config.addr -match ":$Port$") {
                return $t.public_url
            }
        }
        return $null
    } catch {
        return $null
    }
}

Write-Output "Starting ngrok http $Port..."
# Ensure ngrok is available
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Warning "ngrok executable not found on PATH. Please install ngrok and ensure it's on PATH."
    return
}

# Start ngrok; avoid using -NoNewWindow together with -WindowStyle (incompatible)
Start-Process -FilePath $ngrokPath -ArgumentList "http $Port" -WindowStyle Hidden

# Wait up to 10 seconds for ngrok to become available
$timeout = 10
for ($i=0; $i -lt $timeout; $i++) {
    Start-Sleep -Seconds 1
    $url = Get-NgrokPublicUrl -ErrorAction SilentlyContinue
    if ($url) {
        Write-Output "ngrok tunnel ready: $url/webhook"
        return
    }
}

Write-Warning "ngrok did not respond on http://127.0.0.1:4040 within $timeout seconds. Is ngrok installed and able to run?"
Write-Output "You can manually run: ngrok http $Port"
