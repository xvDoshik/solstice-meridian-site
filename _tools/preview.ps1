$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$EnvFile = Join-Path $Root "deploy\config.env"
Get-Content $EnvFile | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)=(.*)$') {
    Set-Variable -Name $matches[1].Trim() -Value $matches[2].Trim() -Scope Script
  }
}
Set-Location $Root
python build.py | Out-Null
if (-not (Test-Path "public\index.html")) { throw "build failed" }
Set-Location public
Write-Host "PREVIEW http://127.0.0.1:$PREVIEW_PORT"
python -m http.server $PREVIEW_PORT
