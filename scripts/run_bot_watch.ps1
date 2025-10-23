# Simple PowerShell watchdog to keep telegram_bot.py running
# Usage: run this from the project root (where telegram_bot.py sits)
# It will restart the bot whenever it exits (crash or normal exit).
# Requires PowerShell. Run in background with Start-Process or create a scheduled task.

$venvPython = Join-Path -Path $PSScriptRoot -ChildPath ".venv\Scripts\python.exe"
$logFile = Join-Path -Path $PSScriptRoot -ChildPath "bot_watch.log"

Write-Output "Starting bot watchdog. Logging to $logFile"
while ($true) {
    $ts = (Get-Date).ToString('u')
    "$ts - Starting bot" | Out-File -FilePath $logFile -Append -Encoding utf8
    try {
        & $venvPython -u "$PSScriptRoot\telegram_bot.py"
    } catch {
        $err = $_.Exception.Message
        $ts = (Get-Date).ToString('u')
        "$ts - Bot crashed with exception: $err" | Out-File -FilePath $logFile -Append -Encoding utf8
    }
    $ts = (Get-Date).ToString('u')
    "$ts - Bot exited (restart in 2s). ExitCode=$LASTEXITCODE" | Out-File -FilePath $logFile -Append -Encoding utf8
    Start-Sleep -Seconds 2
}
