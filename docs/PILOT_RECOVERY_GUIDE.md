# Westgard Pilot Recovery Guide

Objetivo: recuperar rapido el estado operativo si una ejecucion de release falla o deja salidas inconsistentes.

## Donde quedan los backups

Por defecto:

`outputs/backups`

Tipos de respaldo:
- `technical_catalog_YYYYMMDD_HHMMSS.json`
- `web_export_YYYYMMDD_HHMMSS.zip`

Se crean automaticamente al ejecutar:

```powershell
.\westgard_ops.ps1 -Action release
```

## Recovery rapido (3 pasos)

## 1) Identificar ultimo backup

```powershell
Get-ChildItem outputs/backups | Sort-Object LastWriteTime -Descending
```

## 2) Restaurar catalogo tecnico (si aplica)

```powershell
Copy-Item outputs/backups/technical_catalog_YYYYMMDD_HHMMSS.json `
  content/experiment_catalog.generated.json -Force
```

## 3) Restaurar export web

```powershell
Expand-Archive outputs/backups/web_export_YYYYMMDD_HHMMSS.zip `
  -DestinationPath outputs/web_data -Force
```

## Verificar recuperacion

```powershell
.\westgard_ops.ps1 -Action verify
```

Debe terminar con `Verification OK`.

## Si no hay backup util

Regenerar desde authoring:

```powershell
.\westgard_ops.ps1 -Action release
```

Si falla en validacion, corregir el catalogo en UI y volver a ejecutar.
