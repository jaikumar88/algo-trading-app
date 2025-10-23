<# start_all.ps1

Starts the Flask app using the project's venv, starts ngrok to expose port 5000,
waits for a ngrok tunnel, prints the public webhook URL, and tails the Flask log.

Usage (PowerShell):
  .\start_all.ps1

Notes:
- Requires ngrok on PATH.
- Does not run as a service; intended for local/dev use.
#>

param(
    [int]$Port = 5000,
    [string]$FlaskScript = "app.py"
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$flaskLog = Join-Path $projectRoot "flask.log"

if (-not (Test-Path $venvPython)) {
    Write-Warning "venv python not found at $venvPython. Activate your venv or adjust the script."
}

# Start Flask app
Write-Output "Starting Flask app ($FlaskScript) with venv python..."
$startInfo = @{ FilePath = $venvPython; ArgumentList = '-u', "$projectRoot\\$FlaskScript"; WorkingDirectory = $projectRoot }
Start-Process @startInfo -NoNewWindow -PassThru | Out-Null
Start-Sleep -Seconds 1

# Start (or reuse) ngrok
Write-Output "Starting ngrok http $Port..."
# Ensure ngrok is available
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Warning "ngrok executable not found on PATH. Please install ngrok and ensure it's on PATH."
} else {
    # Start ngrok without using incompatible Start-Process flags
    Start-Process -FilePath $ngrokPath -ArgumentList "http $Port" -WindowStyle Hidden
}

# Wait up to 15s for ngrok to expose the tunnel
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

$timeout = 15
$url = $null
for ($i=0; $i -lt $timeout; $i++) {
    Start-Sleep -Seconds 1
    $url = Get-NgrokPublicUrl
    if ($url) { break }
}

if ($url) {
    $webhookUrl = $url.TrimEnd('/') + "/webhook"
    Write-Output "Public webhook URL: $webhookUrl"
    try { Start-Process $webhookUrl } catch {}
} else {
    Write-Warning "ngrok did not publish a tunnel within $timeout seconds. You can run 'ngrok http $Port' manually or check ngrok logs."
}

# Tail the flask log if present, otherwise show running python processes for debugging
if (Test-Path $flaskLog) {
    Write-Output "Tailing $flaskLog (Ctrl+C to stop)..."
    Get-Content $flaskLog -Wait -Tail 50
} else {
    Write-Output "No $flaskLog found; listing python processes:"
    Get-Process -Name python | Select-Object Id,ProcessName,Path
}
