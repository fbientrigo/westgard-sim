param(
    [ValidateSet("preflight", "release", "verify", "smoke", "ui")]
    [string]$Action = "preflight",
    [string]$AuthoringInput = "content/authoring_catalog.example.json",
    [string]$TechnicalOutput = "content/experiment_catalog.generated.json",
    [string]$ExportDir = "outputs/web_data",
    [string]$BackupsDir = "outputs/backups",
    [switch]$SkipBackup,
    [switch]$SkipStreamlitCheck
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

function Resolve-PythonPath {
    $candidates = @(
        ".\.venv\Scripts\python.exe",
        ".\.venv\python.exe",
        "python"
    )
    foreach ($candidate in $candidates) {
        if ($candidate -eq "python") {
            try {
                $null = & python --version
                return "python"
            }
            catch {
                continue
            }
        }
        if (Test-Path $candidate) {
            return $candidate
        }
    }
    throw "No se encontro Python. Instala Python o crea .venv en la raiz del proyecto."
}

$pythonCmd = Resolve-PythonPath
Write-Host "Westgard ops | action=$Action | python=$pythonCmd" -ForegroundColor Cyan

if ($Action -eq "ui") {
    & .\run_authoring_ui.ps1
    exit $LASTEXITCODE
}

if ($Action -eq "preflight") {
    if ($SkipStreamlitCheck) {
        & $pythonCmd scripts/authoring_ops.py preflight --input $AuthoringInput --skip-streamlit-check
    }
    else {
        & $pythonCmd scripts/authoring_ops.py preflight --input $AuthoringInput
    }
    exit $LASTEXITCODE
}

if ($Action -eq "smoke") {
    & $pythonCmd scripts/authoring_ops.py smoke
    exit $LASTEXITCODE
}

if ($Action -eq "verify") {
    & $pythonCmd scripts/authoring_ops.py verify --export-dir $ExportDir
    exit $LASTEXITCODE
}

if ($Action -eq "release") {
    if ($SkipBackup) {
        & $pythonCmd scripts/authoring_ops.py release `
            --input $AuthoringInput `
            --technical-output $TechnicalOutput `
            --export-dir $ExportDir `
            --backups-dir $BackupsDir `
            --skip-backup
    }
    else {
        & $pythonCmd scripts/authoring_ops.py release `
            --input $AuthoringInput `
            --technical-output $TechnicalOutput `
            --export-dir $ExportDir `
            --backups-dir $BackupsDir
    }
    exit $LASTEXITCODE
}
