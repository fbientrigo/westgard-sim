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
            } catch {
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

Write-Host "Iniciando Westgard Authoring MVP..." -ForegroundColor Cyan
Write-Host "Repositorio: $repoRoot"
Write-Host "Python: $pythonCmd"
Write-Host "Nota: abrir la UI no genera export automaticamente." -ForegroundColor Yellow
Write-Host "Para generar datos web usa 'Build technical catalog' + 'Export static web data'" -ForegroundColor Yellow
Write-Host "o ejecuta: .\westgard_ops.ps1 -Action release" -ForegroundColor Yellow

try {
    & $pythonCmd -m streamlit --version | Out-Null
} catch {
    Write-Host "Streamlit no esta instalado. Instalando dependencias..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -r requirements.txt
}

& $pythonCmd -m streamlit run scripts/authoring_mvp.py
