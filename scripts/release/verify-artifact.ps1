<#
.SYNOPSIS
  R6-01 Verify Git / Docker Image / Running Container provenance chain.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\.."))

$commit = (git rev-parse HEAD).Trim()
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
$dirty = -not [string]::IsNullOrWhiteSpace((git status --porcelain))
$treeState = if ($dirty) { "dirty" } else { "clean" }

Write-Host "=== Git ==="
Write-Host "branch=$branch commit=$commit tree_state=$treeState"

Write-Host "=== Images ==="
docker images "ecmp-backend" --format "backend {{.ID}} {{.Tag}} {{.CreatedAt}}"
docker images "ecmp-frontend" --format "frontend {{.ID}} {{.Tag}} {{.CreatedAt}}"

Write-Host "=== Containers ==="
docker compose ps

Write-Host "=== Backend container image labels ==="
docker inspect ecmp-backend --format "Image={{.Image}} Created={{.Created}}"
$imgId = docker inspect ecmp-backend --format "{{.Image}}"
$labels = docker image inspect $imgId --format "{{json .Config.Labels}}" | ConvertFrom-Json
Write-Host ("Id={0} Created={1} revision={2} tree={3}" -f $imgId, (docker image inspect $imgId --format "{{.Created}}"), $labels.'org.opencontainers.image.revision', $labels.'ecmp.git.tree_state')

Write-Host "=== GET /version ==="
try {
  $version = Invoke-RestMethod "http://127.0.0.1:8000/version" -TimeoutSec 10
  $version | ConvertTo-Json
} catch {
  Write-Host "FAIL: /version unreachable: $_"
  exit 1
}

$failures = @()
if ($version.git_commit -eq "unknown" -or [string]::IsNullOrWhiteSpace($version.git_commit)) {
  $failures += "git_commit is unknown (image not built with provenance)"
}
if ($version.git_commit -ne $commit) {
  $failures += "git_commit $($version.git_commit) != HEAD $commit"
}
if ($dirty) {
  $failures += "working tree dirty - RC must be built from committed code only"
}
if ($version.git_tree_state -eq "dirty") {
  $failures += "running artifact reports git_tree_state=dirty"
}

Write-Host "=== Verification Matrix ==="
Write-Host "Git              : $(if ($dirty) { 'FAIL (dirty)' } else { 'PASS' })"
Write-Host "Docker Image     : $(if ($version.git_commit -ne 'unknown') { 'PASS' } else { 'FAIL' })"
Write-Host "Running Container: $(if ($version.git_commit -eq $commit -and -not $dirty) { 'PASS' } else { 'FAIL' })"
Write-Host "Version Endpoint : PASS"
$running = docker compose ps --status running --services
Write-Host "Compose          : $(if ($running -match 'backend') { 'PASS' } else { 'FAIL' })"

if ($failures.Count -gt 0) {
  Write-Host "RESULT: FAIL"
  $failures | ForEach-Object { Write-Host " - $_" }
  exit 1
}

Write-Host "RESULT: PASS - Git == Image == Container == $commit"
