param(
    [ValidateSet("install", "dev", "sync", "build", "test")]
    [string]$Action = "dev"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Join-Path $repoRoot "apps/student-web"

if (-not (Test-Path $appDir)) {
    throw "No se encontro apps/student-web"
}

Set-Location $appDir

if ($Action -eq "install") {
    npm install
    exit $LASTEXITCODE
}

if ($Action -eq "sync") {
    npm run sync:data
    exit $LASTEXITCODE
}

if ($Action -eq "dev") {
    npm run dev
    exit $LASTEXITCODE
}

if ($Action -eq "build") {
    npm run build
    exit $LASTEXITCODE
}

if ($Action -eq "test") {
    npm run test:run
    exit $LASTEXITCODE
}
