<#
Run the Telegram bot using the project's virtualenv Python.

Usage:
  1) Make sure you have created the venv and installed requirements once:
       .venv\Scripts\python.exe -m pip install -r requirements.txt

  2) Put your token into a local `.env` file (TELEGRAM_BOT_TOKEN=...) or
     set the environment variable in the shell:
       $env:TELEGRAM_BOT_TOKEN = "<YOUR_TOKEN>"

  3) Run this script from the project root:
       .\run_bot.ps1

This script avoids using the system Python by explicitly invoking the
project venv python executable.
#>
param()

try {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
} catch {
    $scriptDir = Get-Location
}

$venvPython = Join-Path $scriptDir '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Error "Project venv python not found at $venvPython. Create the venv or run using the correct interpreter."
    exit 1
}

# Load TELEGRAM_BOT_TOKEN from .env if not already set
if (-not $env:TELEGRAM_BOT_TOKEN) {
    $envFile = Join-Path $scriptDir '.env'
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
                if ($_ -match '^[ \t]*TELEGRAM_BOT_TOKEN\s*=\s*(.+)\s*$') {
                $env:TELEGRAM_BOT_TOKEN = $matches[1].Trim()
            }
        }
    }
}

# If .env didn't provide a token, try .env.example automatically (no prompt)
if (-not $env:TELEGRAM_BOT_TOKEN) {
    $envExample = Join-Path $scriptDir '.env.example'
    if (Test-Path $envExample) {
        $exampleToken = $null
        Get-Content $envExample | ForEach-Object {
            if ($_ -match '^[ \t]*TELEGRAM_BOT_TOKEN\s*=\s*(.+)\s*$') {
                $exampleToken = $matches[1].Trim()
            }
        }
        if ($exampleToken) {
            Write-Host "Using TELEGRAM_BOT_TOKEN from .env.example (consider placing a real token in .env and adding .env to .gitignore)."
            $env:TELEGRAM_BOT_TOKEN = $exampleToken
        }
    }
}

if (-not $env:TELEGRAM_BOT_TOKEN) {
    Write-Host "TELEGRAM_BOT_TOKEN is not set."
    Write-Host "Set it for this session with:`n  $env:TELEGRAM_BOT_TOKEN = '<YOUR_TOKEN>'"
    Write-Host "Or create a .env file with the line: TELEGRAM_BOT_TOKEN=<YOUR_TOKEN>"
    exit 1
}

Write-Host "Using venv python: $venvPython"
Write-Host "Starting telegram_bot.py (press Ctrl+C to quit)"
& $venvPython (Join-Path $scriptDir 'telegram_bot.py')