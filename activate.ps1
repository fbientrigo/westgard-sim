# Activation script for Westgard QC Simulator virtual environment
# Usage: .\activate.ps1

Write-Host "`nActivating Westgard QC Simulator environment..." -ForegroundColor Cyan

# Activate conda environment
& C:\ProgramData\miniconda3\Scripts\conda.exe activate C:\Users\Asus\Documents\code\westgard\.venv

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Environment activated!" -ForegroundColor Green
    Write-Host "`nYou can now run:" -ForegroundColor Yellow
    Write-Host "  python -m pytest                    # Run tests"
    Write-Host "  python scripts/run_demo.py          # Run demo"
    Write-Host "  python scripts/export_web_data.py   # Export web data"
    Write-Host "  python content/validate_content.py  # Validate content"
    Write-Host ""
} else {
    Write-Host "✗ Failed to activate environment" -ForegroundColor Red
}
