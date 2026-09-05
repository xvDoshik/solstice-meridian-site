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
ssh -o ConnectTimeout=15 -o BatchMode=yes $SSH_HOST "mkdir -p '$REMOTE_DIR'"
if ($LASTEXITCODE -ne 0) { throw "ssh failed: $SSH_HOST" }
scp -r public/. "${SSH_HOST}:${REMOTE_DIR}/"
if ($LASTEXITCODE -ne 0) { throw "upload failed" }
ssh $SSH_HOST "nginx -t && systemctl reload nginx"
if ($LASTEXITCODE -ne 0) { throw "nginx reload failed" }
Write-Host "LIVE https://$DOMAIN"
