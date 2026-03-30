# Student Web Frontend

Frontend para estudiantes que consume datasets estaticos exportados por el motor Python.

## Requisitos

- Node.js 20+ (en este repo ya se detecta Node 24)
- Dataset exportado en `outputs/web_data` (generado por pipeline Python)

## Comandos

Desde la raiz del repo:

```powershell
# instalar dependencias
.\student_web_ops.ps1 -Action install

# sincronizar dataset exportado y contenido educativo opcional
.\student_web_ops.ps1 -Action sync

# correr en local
.\student_web_ops.ps1 -Action dev

# tests frontend
.\student_web_ops.ps1 -Action test

# build para Pages
.\student_web_ops.ps1 -Action build
```

Tambien puedes usar npm directo:

```powershell
cd apps/student-web
npm install
npm run sync:data
npm run dev
```

## Arquitectura

```text
src/
  app/        # bootstrap, layout, router
  pages/      # HomePage, ExperimentPage, ScenarioPage
  features/   # slices de UI (listado, detalle, viewer, chart)
  entities/   # modelos de dominio
  shared/     # api, config, utilidades, ui base, types
```

## Datos y contrato

- `public/web_data/index.json`
- `public/web_data/experiments/<experiment-id>/manifest.json`
- `public/web_data/experiments/<experiment-id>/<scenario-id>.json`

La app valida contratos en runtime con `zod` antes de renderizar.

## Contenido educativo

Integracion no invasiva y opcional via adapter:

- `public/educational/scenarios.json`
- `public/educational/lessons.json`

Si faltan o fallan, la vista de escenario sigue funcionando sin bloquearse.

## Deploy a GitHub Pages

El workflow `.github/workflows/student-pages.yml`:

1. Exporta dataset desde Python.
2. Sincroniza assets al frontend.
3. Compila Vite con base configurable.
4. Publica `apps/student-web/dist` en GitHub Pages.
