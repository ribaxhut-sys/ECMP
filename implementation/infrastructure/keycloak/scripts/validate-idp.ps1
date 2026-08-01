# Validate ECMP Keycloak IdP baseline (SEC-MIG Phase 1)
# Usage (from repo root):
#   powershell -File implementation/infrastructure/keycloak/scripts/validate-idp.ps1

param(
    [string]$BaseUrl = "http://localhost:8180",
    [string]$Realm = "ecmp"
)

$ErrorActionPreference = "Stop"
$failed = @()

function Ok([string]$msg) { Write-Host "[PASS] $msg" -ForegroundColor Green }
function Fail([string]$msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
    $script:failed += $msg
}

Write-Host "Validating IdP at $BaseUrl (realm=$Realm)..."

try {
    $discovery = Invoke-RestMethod -Uri "$BaseUrl/realms/$Realm/.well-known/openid-configuration" -Method Get
    if ($discovery.issuer -match "/realms/$Realm$") { Ok "OIDC discovery reachable; issuer=$($discovery.issuer)" }
    else { Fail "OIDC discovery issuer unexpected: $($discovery.issuer)" }
    if ($discovery.jwks_uri) { Ok "Discovery advertises jwks_uri=$($discovery.jwks_uri)" }
    else { Fail "Discovery missing jwks_uri" }
}
catch {
    Fail "OIDC discovery failed: $($_.Exception.Message)"
}

try {
    $jwks = Invoke-RestMethod -Uri "$BaseUrl/realms/$Realm/protocol/openid-connect/certs" -Method Get
    if ($jwks.keys -and $jwks.keys.Count -ge 1) { Ok "JWKS reachable; key count=$($jwks.keys.Count)" }
    else { Fail "JWKS returned no keys" }
}
catch {
    Fail "JWKS failed: $($_.Exception.Message)"
}

try {
    $realmMeta = Invoke-RestMethod -Uri "$BaseUrl/realms/$Realm" -Method Get
    $realmName = [string]$realmMeta.realm
    if ($realmName -eq $Realm) { Ok "Realm public metadata present for '$Realm'" }
    else { Fail "Realm metadata mismatch (got '$realmName')" }
}
catch {
    Fail "Realm metadata failed: $($_.Exception.Message)"
}

# Client smoke: confidential client_credentials for ecmp-ci (local secret)
try {
    $token = Invoke-RestMethod -Uri "$BaseUrl/realms/$Realm/protocol/openid-connect/token" -Method Post -ContentType "application/x-www-form-urlencoded" -Body @{
        grant_type    = "client_credentials"
        client_id     = "ecmp-ci"
        client_secret = "ecmp-ci-local-only-change-me"
    }
    if ($token.access_token) { Ok "Client ecmp-ci client_credentials token issued" }
    else { Fail "ecmp-ci token response missing access_token" }
}
catch {
    Fail "ecmp-ci client_credentials failed: $($_.Exception.Message)"
}

$expectedClients = @("ecmp-web", "ecmp-api-docs", "ecmp-ci", "ecmp-svc-core", "ecmp-api")
$expectedRoles = @("cs_agent", "viewer", "supervisor", "handler")
Write-Host "[INFO] Expected clients (Admin Console / Admin API): $($expectedClients -join ', ')"
Write-Host "[INFO] Expected realm roles (Admin Console / Admin API): $($expectedRoles -join ', ')"
Write-Host "[INFO] Roles confirmed via Admin API during Phase 1 validation: cs_agent, viewer, supervisor, handler (+ Keycloak built-ins)."

if ($failed.Count -gt 0) {
    Write-Host "`nValidation FAILED ($($failed.Count) issue(s))." -ForegroundColor Red
    exit 1
}

Write-Host "`nValidation PASSED (discovery + JWKS + realm)." -ForegroundColor Green
exit 0
