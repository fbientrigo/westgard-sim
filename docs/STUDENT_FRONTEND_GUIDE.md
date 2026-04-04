# Student Frontend Guide

## Objetivo

Publicar una web de estudiantes que consume el export estatico del simulador sin acoplarse al backend Python ni a la UI de authoring.

## Flujo operativo completo

1. Generar dataset desde Python:

```powershell
.\westgard_ops.ps1 -Action release
```

2. Instalar frontend (primera vez):

```powershell
.\student_web_ops.ps1 -Action install
```

3. Sincronizar dataset hacia frontend:

```powershell
.\student_web_ops.ps1 -Action sync
```

4. Correr local:

```powershell
.\student_web_ops.ps1 -Action dev
```

5. Build estatico:

```powershell
.\student_web_ops.ps1 -Action build
```

## Estrategia de integracion de datos

Se implemento la opcion de consumir assets estaticos sincronizados:

- Fuente: `outputs/web_data`
- Destino: `apps/student-web/public/web_data`
- Script de sync principal: `apps/student-web/scripts/run-sync.mjs`
- Script Python alternativo: `scripts/sync_student_web_assets.py`

Razon:

- Mantiene separadas responsabilidades.
- Permite preview local inmediato con Vite y assets estaticos.
- Simplifica el artefacto final de Pages.

## Contenido educativo

El script de sync tambien copia:

- `content/scenarios.json` -> `apps/student-web/public/educational/scenarios.json`
- `content/lessons.json` -> `apps/student-web/public/educational/lessons.json`

La app lo consume con `educationalAdapter`. Si faltan archivos o el contrato falla, el render principal del escenario no se rompe.

## Deploy en GitHub Pages

Workflow: `.github/workflows/student-pages.yml`.

- Build job:
  - instala dependencias Python
  - exporta `outputs/web_data`
  - exporta `outputs/flashcards`
  - instala frontend
  - sincroniza datos
  - compila Vite con `VITE_BASE_PATH`
- Deploy job:
  - publica `apps/student-web/dist`

Base path:

- Si el repo termina en `.github.io`, usa `/`
- En caso contrario, usa `/<repo>/`

## Tradeoffs tecnicos

- Router en hash (`/#/...`) para compatibilidad robusta con Pages sin rewrites.
- `zod` agrega costo minimo de runtime, pero protege contra drift del contrato JSON.
- No se incorporo estado global complejo para mantener simplicidad.

## Limitaciones abiertas

- No hay internacionalizacion activa aun.
- No hay comparador entre escenarios todavia.
- La deteccion visual de triggers se basa en `first_trigger_run` por regla; se puede ampliar en futuras iteraciones a eventos por ejecucion y regla.
