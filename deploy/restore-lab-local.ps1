# Restore ECMP lab export on Windows (Docker Desktop).
# Run from PowerShell:
#   powershell -ExecutionPolicy Bypass -File D:\ecmp\deploy\restore-lab-local.ps1
param(
    [string]$Pack = "D:\lab-local-export-20260830T120410Z",
    [string]$Target = "D:\ecmp",
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"
$env:COMPOSE_PROJECT_NAME = "ecmp"

if (-not (Test-Path (Join-Path $Pack "MANIFEST.txt"))) {
    throw "Paket export tidak ada: $Pack"
}
if (-not (Test-Path $Target)) {
    New-Item -ItemType Directory -Path $Target | Out-Null
}

$envLocal = Join-Path $Pack "secrets\env.local"
if (-not (Test-Path $envLocal)) {
    throw "secrets\env.local tidak ada di paket"
}

$tree = Join-Path $Pack "app\ECMP-working-tree.tar.gz"
if (Test-Path $tree) {
    Write-Host "==> working tree -> $Target"
    tar -xzf $tree -C $Target --strip-components=1
}

Copy-Item -Force $envLocal (Join-Path $Target ".env")

Set-Location $Target
Write-Host "==> postgres"
docker compose --env-file .env up -d postgres

$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    docker compose --env-file .env exec -T postgres pg_isready -U ecmp -d ecmp 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    throw "postgres tidak siap"
}

Write-Host "==> kosongkan skema (hindari bentrok FK init compose)"
docker compose --env-file .env exec -T postgres psql -U ecmp -d ecmp -v ON_ERROR_STOP=1 `
    -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO ecmp; GRANT ALL ON SCHEMA public TO public;"

$dump = Get-ChildItem (Join-Path $Pack "data\ecmp_*.sql.gz") | Select-Object -First 1
if ($null -eq $dump) {
    throw "dump SQL tidak ada di $Pack\data"
}
Write-Host "==> restore SQL $($dump.Name)"
docker cp $dump.FullName "ecmp-postgres:/tmp/ecmp_restore.sql.gz"
docker exec ecmp-postgres sh -c "gzip -dc /tmp/ecmp_restore.sql.gz > /tmp/ecmp_restore.sql && psql -U ecmp -d ecmp -v ON_ERROR_STOP=1 -f /tmp/ecmp_restore.sql && rm -f /tmp/ecmp_restore.sql /tmp/ecmp_restore.sql.gz"

docker compose --env-file .env up -d --no-start backend | Out-Null
Write-Host "==> restore lampiran"
$packData = Join-Path $Pack "data"
docker run --rm `
    -v ecmp_ecmp_attachments:/data `
    -v "${packData}:/backup:ro" `
    alpine:3.20 `
    sh -c "rm -rf /data/* /data/.[!.]* 2>/dev/null || true; tar -xzf /backup/ecmp_attachments.tar.gz -C /data"

Write-Host "==> backend + frontend"
if ($NoBuild) {
    docker compose --env-file .env up -d backend frontend
}
else {
    docker compose --env-file .env up -d --build backend frontend
}

Write-Host ""
Write-Host "RESTORE_OK"
Write-Host "  UI : http://localhost:3000"
Write-Host "  API: http://localhost:8000/health"
Write-Host "Password lab: $Pack\secrets\ecmp-credentials.host"
