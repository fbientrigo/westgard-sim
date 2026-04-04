# westgard-sim

Simulador reproducible de control de calidad interno (QC) para laboratorio clinico + flujo local de authoring para generar datos estaticos consumidos por UI/web.

## TL;DR (flujo minimo que funciona)

En PowerShell, desde la raiz del repo:

```powershell
# 1) Crear/activar entorno (solo primera vez)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) Validar entorno y catalogo
.\westgard_ops.ps1 -Action preflight

# 3) Abrir UI de authoring
.\westgard_ops.ps1 -Action ui

# 4) Generar salida estatica real
.\westgard_ops.ps1 -Action release

# 5) Verificar estructura exportada
.\westgard_ops.ps1 -Action verify
```

Si solo ejecutas `-Action ui`, no se generan automaticamente payloads en `outputs/web_data` hasta correr export/release.

## 1. Requisitos

- Python `>=3.11` (definido en `pyproject.toml`)
- PowerShell 7+ recomendado en Windows
- `pip` operativo

Verifica version:

```powershell
python --version
```

## 2. Setup del entorno (paso a paso)

### Windows (PowerShell)

```powershell
# en la raiz del repo
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux (bash/zsh)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Comandos principales

### UI local de authoring

```powershell
.\run_authoring_ui.ps1
```

O por wrapper operativo:

```powershell
.\westgard_ops.ps1 -Action ui
```

### Pipeline operativo reproducible

```powershell
.\westgard_ops.ps1 -Action preflight
.\westgard_ops.ps1 -Action release
.\westgard_ops.ps1 -Action verify
```

### Simulacion y export tecnico (sin UI)

```powershell
python scripts/run_demo.py
python scripts/export_web_data.py --output-dir outputs/web_data
```

Con catalogo completo:

```powershell
python scripts/export_web_data.py --catalog content/experiment_catalog.json --output-dir outputs/web_data
```

### Tests

```powershell
pytest
```

### Flashcards: edicion y export

Deck editable actual:

- `content/flashcards/westgard_qc_basics.deck.json`

Guia detallada:

- `docs/FLASHCARDS_GUIDE.md`

Comando recomendado usando el `.venv` del repo:

```powershell
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics
```

Salida esperada:

- `outputs/flashcards/westgard_qc_basics/westgard_qc_basics.csv`
- `outputs/flashcards/westgard_qc_basics/preview.html`
- `outputs/flashcards/westgard_qc_basics/flashcards.css`
- `outputs/flashcards/westgard_qc_basics/manifest.json`
- `outputs/flashcards/westgard_qc_basics/study_deck.json`

Punto de revision visual inmediato:

- abrir `outputs/flashcards/westgard_qc_basics/preview.html`
- para llevarlas a la web: `cd apps/student-web && npm run sync:data`

### Flashcards en la web

La web de estudiantes ahora incluye una sesion interactiva de flashcards con tres pilas y progreso local.

Flujo recomendado:

```powershell
# 1) exportar el deck
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics

# 2) sincronizar assets estaticos al frontend
cd apps/student-web
npm run sync:data

# 3) correr la web local
npm run dev
```

Ruta dentro de la web:

- `/#/flashcards`

Archivos que consume la web:

- `public/flashcards/westgard_qc_basics/study_deck.json`

Comportamiento del MVP:

- tres pilas: nuevas, en practica y repaso
- sin backend; el progreso se guarda en `localStorage`
- controles minimos: `Mostrar respuesta`, `Repetir`, `La supe`
- si una tarjeta falla, vuelve a la pila 1
- si una tarjeta acierta, avanza una pila

## 4. Flujo correcto para generar datos de UI

El flujo recomendado para authoring es:

1. `preflight`: valida archivos, dependencias y schema.
2. `ui`: edita/valida catalogo de authoring.
3. `release`: build catalogo tecnico + export estatico + verificacion + backups.
4. `verify`: chequeo independiente de la salida exportada.

Rutas por defecto del flujo operativo:

- input authoring: `content/authoring_catalog.example.json`
- catalogo tecnico generado: `content/experiment_catalog.generated.json`
- export web: `outputs/web_data`
- backups: `outputs/backups`

Salida esperada minima despues de `release`:

- `outputs/web_data/index.json`
- `outputs/web_data/experiments/<experiment-id>/manifest.json`
- `outputs/web_data/experiments/<experiment-id>/<scenario-id>.json`

## 5. Frontend de estudiantes (incluido en este repo)

El frontend vive en `apps/student-web` y consume directamente el contrato exportado por Python.

### Flujo local rapido

1. Generar dataset:

```powershell
.\westgard_ops.ps1 -Action release
```

2. Instalar frontend (primera vez):

```powershell
.\student_web_ops.ps1 -Action install
```

3. Sincronizar dataset + contenido educativo opcional:

```powershell
.\student_web_ops.ps1 -Action sync
```

4. Ejecutar frontend:

```powershell
.\student_web_ops.ps1 -Action dev
```

### Build y deploy en GitHub Pages

- Workflow: `.github/workflows/student-pages.yml`
- El workflow:
  - exporta dataset con Python,
  - exporta flashcards con Python,
  - sincroniza `outputs/web_data` en `apps/student-web/public/web_data`,
  - sincroniza `outputs/flashcards` en `apps/student-web/public/flashcards`,
  - compila el frontend con base path de Pages,
  - publica `apps/student-web/dist`.

URL final esperada para estudiantes:

- `https://<org-o-usuario>.github.io/<repo>/`
- si el repo es `<org-o-usuario>.github.io`, la URL queda `https://<org-o-usuario>.github.io/`

## 6. Guia para crear experimentos

Para entender cada campo del catalogo y editarlo correctamente, revisa:

- [docs/crear_experimento.md](docs/crear_experimento.md)

## 7. Estructura del proyecto

```text
qc_lab_simulator/   # motor de simulacion, reglas, metricas, export
content/            # catalogos y contratos de authoring
apps/student-web/   # frontend React + TS para estudiantes
docs/               # guias operativas del piloto
scripts/            # scripts CLI para demo/build/export/ops
tests/              # pruebas automaticas
```

## 8. Documentacion conectada (leer segun necesidad)

Indice general:

- `docs/README.md`

Arranque y operacion:

- `docs/PILOT_QUICKSTART_5_MIN.md`
- `docs/BEA_PILOT_CHECKLIST.md`

Uso de UI authoring:

- `docs/AUTHORING_MVP_TUTORIAL.md`
- `docs/AUTHORING_MVP_GUIDE.md`
- `docs/crear_experimento.md`
- `docs/FLASHCARDS_GUIDE.md`

Frontend estudiante:

- `apps/student-web/README.md`
- `docs/STUDENT_FRONTEND_PLAN.md`
- `docs/STUDENT_FRONTEND_GUIDE.md`

Incidentes y recuperacion:

- `docs/PILOT_TROUBLESHOOTING.md`
- `docs/PILOT_RECOVERY_GUIDE.md`

## 9. Troubleshooting rapido

- Error `No se encontro Python` en scripts `.ps1`:
  - crea `.venv` en la raiz o instala Python 3.11 y agrega a PATH.
- UI abre pero no aparecen archivos exportados:
  - ejecutar `Build technical catalog` y `Export static web data` en UI, o correr `westgard_ops.ps1 -Action release`.
- Error por dependencias faltantes:
  - `pip install -r requirements.txt` con el entorno activo.
- `verify` falla:
  - revisar `outputs/web_data/index.json` y manifests/payloads faltantes indicados por el error.
- Frontend no muestra experimentos:
  - ejecutar `.\student_web_ops.ps1 -Action sync` y confirmar `apps/student-web/public/web_data/index.json`.

## 10. Licencia

MIT (`LICENSE`).
