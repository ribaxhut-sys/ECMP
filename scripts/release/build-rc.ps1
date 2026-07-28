<#
.SYNOPSIS
  R6-01 Build Release Candidate images with Git provenance.

.DESCRIPTION
  Captures Git SHA / branch / tree state, refuses dirty trees by default
  (RC must be built from committed code), then runs docker compose build
  and recreates app containers. Verifies GET /version matches the build SHA.

.PARAMETER AllowDirty
  Permit building from a dirty working tree (DEV only). Marks GIT_TREE_STATE=dirty
  and fails the post-build RC gate that requires clean.

.PARAMETER UseCache
  Allow Docker layer cache. Default is --no-cache for RC builds.

.PARAMETER SkipUp
  Build only; do not recreate running containers.
#>
[CmdletBinding()]
param(
  [switch]$AllowDirty,
  [switch]$UseCache,
  [switch]$SkipUp
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\.."))

function Get-GitCommit { (git rev-parse HEAD).Trim() }
function Get-GitBranch { (git rev-parse --abbrev-ref HEAD).Trim() }
function Get-GitTreeState {
  $porcelain = git status --porcelain
  if ([string]::IsNullOrWhiteSpace($porcelain)) { "clean" } else { "dirty" }
}

$commit = Get-GitCommit
$branch = Get-GitBranch
$treeState = Get-GitTreeState
$buildTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$appVersion = if ($env:APP_VERSION) { $env:APP_VERSION } else { "1.0.0" }
$imageTag = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "rc-$($commit.Substring(0,12))" }

Write-Host "R6-01 build-rc"
Write-Host "  branch      = $branch"
Write-Host "  commit      = $commit"
Write-Host "  tree_state  = $treeState"
Write-Host "  build_time  = $buildTime"
Write-Host "  image_tag   = $imageTag"

if ($treeState -eq "dirty" -and -not $AllowDirty) {
  throw "REFUSING RC BUILD: working tree is dirty. Commit or stash changes, or pass -AllowDirty for a non-RC diagnostic build."
}

$env:GIT_COMMIT = $commit
$env:GIT_BRANCH = $branch
$env:BUILD_TIME = $buildTime
$env:GIT_TREE_STATE = $treeState
$env:APP_VERSION = $appVersion
$env:IMAGE_TAG = $imageTag

$buildArgs = @("compose", "build")
if (-not $UseCache) { $buildArgs += "--no-cache" }
$buildArgs += @("backend", "frontend")

Write-Host "Running: docker $($buildArgs -join ' ')"
& docker @buildArgs
if ($LASTEXITCODE -ne 0) { throw "docker compose build failed ($LASTEXITCODE)" }

if (-not $SkipUp) {
  Write-Host "Recreating application containers from freshly built images..."
  & docker compose up -d --force-recreate --no-deps backend frontend
  if ($LASTEXITCODE -ne 0) { throw "docker compose up failed ($LASTEXITCODE)" }

  Write-Host "Waiting for backend health..."
  $deadline = (Get-Date).AddMinutes(3)
  do {
    Start-Sleep -Seconds 3
    try {
      $health = Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 5
      if ($health.status -eq "ok") { break }
    } catch { }
  } while ((Get-Date) -lt $deadline)

  $version = Invoke-RestMethod "http://127.0.0.1:8000/version" -TimeoutSec 10
  Write-Host ($version | ConvertTo-Json -Compress)

  if ($version.git_commit -ne $commit) {
    throw "PROVENANCE MISMATCH: /version.git_commit=$($version.git_commit) != git HEAD=$commit"
  }
  if ($treeState -eq "dirty") {
    Write-Warning "Built with dirty tree - NOT a valid Release Candidate (GIT_TREE_STATE=dirty)."
    exit 2
  }
  Write-Host "R6-01 OK: Git commit == container /version.git_commit == $commit"
}
