# Westgard Pilot Troubleshooting

## 1) `Preflight failed. Missing Python dependencies`

Sintoma:
- falta `jsonschema` o `streamlit`.

Accion:
```powershell
.\.venv\python.exe -m pip install -r requirements.txt
```

Reintentar:
```powershell
.\westgard_ops.ps1 -Action preflight
```

Si solo necesitas build/export sin UI (modo headless):
```powershell
.\westgard_ops.ps1 -Action preflight -SkipStreamlitCheck
```

## 2) `Authoring catalog invalid`

Sintoma:
- error de esquema o reglas de negocio.

Accion:
1. Abrir UI (`.\westgard_ops.ps1 -Action ui`)
2. Cargar el archivo
3. Corregir errores mostrados por seccion
4. Guardar

Validar de nuevo:
```powershell
.\westgard_ops.ps1 -Action preflight
```

## 3) `Export verification failed`

Sintoma:
- faltan manifests/payloads o inconsistencia de conteos.

Accion:
1. Ejecutar release completo otra vez:
```powershell
.\westgard_ops.ps1 -Action release
```
2. Si persiste, restaurar backup (ver guia de recovery).

## 4) No abre la UI

Accion:
1. Validar streamlit:
```powershell
.\.venv\python.exe -m streamlit --version
```
2. Lanzar directo:
```powershell
.\.venv\python.exe -m streamlit run scripts/authoring_mvp.py
```

## 5) Quiero usar rutas personalizadas

Ejemplo:
```powershell
.\westgard_ops.ps1 -Action release `
  -Input content/authoring_catalog.example.json `
  -TechnicalOutput outputs/pilot/experiment_catalog.generated.json `
  -ExportDir outputs/pilot/web_data `
  -BackupsDir outputs/pilot/backups
```
