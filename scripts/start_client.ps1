# Start the React client dev server from the project root
Set-Location -Path "$PSScriptRoot\client"
Write-Output "Starting client dev server in: $(Get-Location)"
npm run dev
