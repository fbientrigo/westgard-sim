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

Write-Host "Iniciando Westgard Authoring Studio..." -ForegroundColor Cyan
Write-Host "Repositorio: $repoRoot"
Write-Host "Python: $pythonCmd"
Write-Host "La UI ahora integra experimentos, flashcards y publicacion local." -ForegroundColor Yellow
Write-Host "Usa la pestaña 'Publicar' para generar carpetas listas para compartir" -ForegroundColor Yellow
Write-Host "o para copiar datos a apps/student-web/public en tu PC local." -ForegroundColor Yellow

try {
    & $pythonCmd -m streamlit --version | Out-Null
} catch {
    Write-Host "Streamlit no esta instalado. Instalando dependencias..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -r requirements.txt
}

& $pythonCmd -m streamlit run scripts/authoring_mvp.py
