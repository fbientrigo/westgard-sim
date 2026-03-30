# Westgard Pilot Quickstart (5 minutos)

Objetivo: ejecutar el flujo completo local para Bea sin pasos manuales frágiles.

## 1) Abrir terminal en la raiz del repo

PowerShell en:

`C:\Users\Asus\Documents\code\westgard`

## 2) Preflight (30-60s)

```powershell
.\westgard_ops.ps1 -Action preflight
```

Debe terminar con `Preflight OK`.

## 3) Abrir UI de autora

```powershell
.\westgard_ops.ps1 -Action ui
```

En la UI:
1. Abrir catalogo.
2. Editar.
3. Validar.
4. Guardar.

## 4) Build + Export + Verify (release local)

```powershell
.\westgard_ops.ps1 -Action release
```

Este comando ejecuta:
1. preflight
2. backup automatico (si ya existian salidas)
3. build del catalogo tecnico
4. export estatico
5. verificacion estructural de salida

## 5) Verificacion independiente (opcional)

```powershell
.\westgard_ops.ps1 -Action verify
```

## Rutas por defecto

- Input autora: `content/authoring_catalog.example.json`
- Catalogo tecnico: `content/experiment_catalog.generated.json`
- Export web: `outputs/web_data`
- Backups: `outputs/backups`

## Salida minima esperada

- `outputs/web_data/index.json`
- `outputs/web_data/experiments/<experiment-id>/manifest.json`
- `outputs/web_data/experiments/<experiment-id>/<scenario-id>.json`
