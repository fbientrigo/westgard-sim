# Student Web Frontend

Frontend para estudiantes que consume datasets estaticos exportados por el motor Python.

## Requisitos

- Node.js 20+ (en este repo ya se detecta Node 24)
- Dataset exportado en `outputs/web_data`
- Flashcards exportadas en `outputs/flashcards`

## Comandos

Desde la raiz del repo:

```powershell
# instalar dependencias
.\student_web_ops.ps1 -Action install

# sincronizar assets estaticos
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

Para Vercel, usa:

```powershell
cd apps/student-web
npm run build:vercel
```

Ese comando exporta datos estaticos desde `content/experiment_catalog.json`, exporta el deck de
flashcards, sincroniza `public/web_data`, `public/educational` y `public/flashcards`, y luego ejecuta
`vite build`.

## Flashcards interactivas

La ruta `/#/flashcards` muestra un MVP de estudio con tres pilas. Sin Supabase usa
`localStorage`; con una sesion autenticada sincroniza el progreso a Supabase.

Antes de abrirla:

```powershell
cd ..
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics
cd apps/student-web
npm run sync:data
```

Archivos esperados:

- `public/flashcards/westgard_qc_basics/study_deck.json`
- `public/flashcards/westgard_qc_basics/preview.html`

## Arquitectura

```text
src/
  app/        # bootstrap, layout, router
  pages/      # HomePage, ExperimentPage, ScenarioPage, FlashcardsPage
  features/   # slices de UI y estudio
  entities/   # modelos de dominio
  shared/     # api, config, utilidades, ui base, types
```

## Datos y contrato

- `public/web_data/index.json`
- `public/web_data/experiments/<experiment-id>/manifest.json`
- `public/web_data/experiments/<experiment-id>/<scenario-id>.json`
- `public/flashcards/<deck-id>/study_deck.json`

La app valida contratos en runtime con `zod` antes de renderizar.

Estos archivos siguen siendo assets estaticos. Escenarios, decks, contenido educativo y datos
generados no se leen desde Supabase.

## Contenido educativo

Integracion no invasiva y opcional via adapter:

- `public/educational/scenarios.json`
- `public/educational/lessons.json`

Si faltan o fallan, la vista de escenario sigue funcionando sin bloquearse.

## Deploy a GitHub Pages

El workflow `.github/workflows/student-pages.yml`:

1. Exporta dataset desde Python.
2. Exporta flashcards desde Python.
3. Sincroniza assets al frontend.
4. Compila Vite con base configurable.
5. Publica `apps/student-web/dist` en GitHub Pages.

## Deploy a Vercel

Configura el proyecto Vercel con:

- Root Directory: `apps/student-web`
- Install Command: `npm install`
- Build Command: `npm run build:vercel`
- Output Directory: `dist`

El build de Vercel necesita Python disponible para ejecutar los scripts de export estatico. El
build no requiere Supabase para compilar ni para servir contenido educativo.

Variables opcionales de entorno:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Si faltan, la app entra en modo local y guarda progreso en `localStorage`. No uses ni expongas una
service-role key en el frontend.

## Supabase

Supabase se usa solo para identidad y progreso de flashcards. Ejecuta manualmente:

- `supabase/001_identity_and_progress.sql`

Ese SQL crea:

- `public.westgard_profiles`
- `public.westgard_flashcard_progress`
- politicas RLS para que cada usuario lea, inserte, actualice y elimine solo sus propias filas

No se agrego tabla de progreso de escenarios porque la app actual no tiene un estado de escenario
editable o persistible claro; las paginas de escenarios son lectura de JSON estatico.

Para magic links, habilita Email Auth en Supabase y agrega la URL de Vercel a los redirect URLs del
proyecto Supabase.
