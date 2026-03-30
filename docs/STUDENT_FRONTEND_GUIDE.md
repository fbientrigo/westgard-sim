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

5. Build estático:

```powershell
.\student_web_ops.ps1 -Action build
```

## Estrategia de integración de datos (opción elegida)

Se implementó **Opción A**:

- Fuente: `outputs/web_data`
- Destino: `apps/student-web/public/web_data`
- Script de sync automatizado principal: `apps/student-web/scripts/run-sync.mjs`
- Script Python alternativo (CLI reutilizable): `scripts/sync_student_web_assets.py`

Razón:

- Mantiene separadas responsabilidades (simulación/export vs frontend).
- Permite preview local inmediato con Vite y assets estáticos.
- Simplifica el artefacto final de Pages.

## Contenido educativo

Decisión: integrar ahora de forma no invasiva con adapter opcional.

- El script de sync también copia:
  - `content/scenarios.json` -> `apps/student-web/public/educational/scenarios.json`
  - `content/lessons.json` -> `apps/student-web/public/educational/lessons.json`
- La app lo consume con `educationalAdapter`.
- Si faltan archivos o contrato no válido, el render principal del escenario no se rompe.

## Deploy en GitHub Pages

Workflow: `.github/workflows/student-pages.yml`.

- Build job:
  - instala Python deps,
  - exporta `outputs/web_data`,
  - instala frontend,
  - sincroniza datos,
  - compila Vite con `VITE_BASE_PATH`.
- Deploy job:
  - publica artefacto `apps/student-web/dist`.

Base path:

- Si el repo termina en `.github.io`, usa `/`.
- En caso contrario, usa `/<repo>/`.

## Tradeoffs técnicos

- Router en hash (`/#/...`) para compatibilidad robusta con Pages sin rewrites.
- `zod` agrega costo mínimo de runtime, pero protege contra drift del contrato JSON.
- No se incorporó estado global complejo (Redux/React Query) para mantener simplicidad y evitar sobreingeniería en fase inicial.

## Limitaciones abiertas

- No hay internacionalización activa aún (arquitectura preparada para crecer).
- No hay comparador entre escenarios todavía.
- La detección visual de triggers se basa en `first_trigger_run` por regla; se puede ampliar en futuras iteraciones a eventos por corrida/regla.
