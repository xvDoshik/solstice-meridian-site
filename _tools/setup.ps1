$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$EnvFile = Join-Path $Root "deploy\config.env"
Get-Content $EnvFile | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)=(.*)$') {
    Set-Variable -Name $matches[1].Trim() -Value $matches[2].Trim() -Scope Script
  }
}
$Nginx = Get-Content (Join-Path $Root "deploy\nginx.conf") -Raw
$Remote = @"
set -euo pipefail
mkdir -p '$REMOTE_DIR'
apt-get update -qq
apt-get install -y nginx rsync
cat > /etc/nginx/sites-available/$DOMAIN <<'NGX'
$Nginx
NGX
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
nginx -t
systemctl enable nginx
systemctl restart nginx
"@
$Remote | ssh -o ConnectTimeout=15 $SSH_HOST "bash -s"
if ($LASTEXITCODE -ne 0) { throw "server setup failed" }
Write-Host "SERVER OK $DOMAIN -> $REMOTE_DIR"
