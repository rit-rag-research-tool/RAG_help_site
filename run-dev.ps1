# run-dev.ps1
# Launch Python (uvicorn) and React (npm start) dev servers in separate PowerShell windows.
# Usage: Right-click -> Run with PowerShell or run `.
# run-dev.ps1 -NoInstall` from PowerShell to skip installs after the first run.

# Adjust this path if your workspace is in a different location
$base = "C:\Users\Rae\Desktop\RAG_help_site"

param(
	[switch]$NoInstall
)

# Decide install steps based on flag
if ($NoInstall) {
	$pythonInstallPart = ".\\.venv\\Scripts\\Activate.ps1;"
	$clientInstallPart = "npm start"
} else {
	$pythonInstallPart = "if (-Not (Test-Path '.venv')) { python -m venv .venv }; .\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt;"
	$clientInstallPart = "npm install; npm start"
}

Write-Output "Starting Python server..."
$pythonChildCmd = "cd '$base\\server\\python'; $pythonInstallPart $env:OPENAI_API_KEY='YOUR_KEY_HERE'; uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$pythonChildCmd

Start-Sleep -Seconds 2
Write-Output "(Node layer archived; not starting)"

Start-Sleep -Seconds 2
Write-Output "Starting React client..."
$clientChildCmd = "cd '$base\\client'; $clientInstallPart"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$clientChildCmd

Write-Output "All processes started. Check the PowerShell windows that have opened."