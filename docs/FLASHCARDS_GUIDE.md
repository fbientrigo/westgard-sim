# Guia de Flashcards

Esta guia explica como editar, validar, exportar y publicar decks de flashcards para Westgard y laboratorio clinico.

## Donde estan los decks

- Decks JSON: `content/flashcards/`
- Esquema JSON: `content/flashcards/flashcard_deck.schema.json`
- Tokens visuales: `content/flashcards/theme_tokens.json`
- Codigo de exportacion: `qc_lab_simulator/flashcards/`
- Script CLI: `scripts/export_flashcards.py`
- Salida generada: `outputs/flashcards/`

## Deck actual de ejemplo

La fuente de verdad de esta fase es:

- `content/flashcards/westgard_qc_basics.deck.json`

Mantener estables:

- `deck_id`
- `cards[].id`

## Que se puede editar con seguridad

- Titulo, subtitulo, descripcion, tags y notas del deck
- Texto de `front` y `back`
- `card_type`
- Tags de cada tarjeta
- Colores y tipografias en `theme_tokens.json`

## Formato soportado dentro de las tarjetas

Usa este subconjunto pequeno de marcado:

- `**negrita**`
- `*cursiva*`
- `` `monoespaciado` ``
- `[[rule:1-2s]]`
- `[[warning:advertencia]]`
- `[[rejection:rechazar la ejecucion]]`
- `[[specimen:muestra de suero]]`
- `[[instrument:analizador]]`
- `[[qc:control interno]]`

El mismo texto fuente se usa para:

- la vista previa HTML
- los campos HTML del CSV para Anki
- el JSON web consumido por la pagina de estudio

No escribas HTML crudo dentro de las tarjetas. El exportador lo escapa.

## Flujo operativo recomendado

### Opcion UI local para Beatriz

La forma mas simple ahora es abrir:

```powershell
.\run_authoring_ui.ps1
```

Y trabajar en la pestaña `Flashcards`:

1. Abrir el deck desde la barra lateral.
2. Crear o reordenar tarjetas.
3. Editar tags del deck y de cada tarjeta.
4. Revisar la vista previa rapida.
5. Exportar y publicar desde la pestaña `Publicar`.

### Opcion CLI

### 1. Activar el entorno

En Windows PowerShell, desde la raiz del repo:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si ya existe `.venv`, puedes invocar el Python del entorno sin activarlo:

```powershell
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics
```

### 2. Editar o agregar tarjetas

1. Copia un objeto existente dentro del arreglo `cards`.
2. Asigna un `id` nuevo y estable.
3. Define un `sort_order` unico.
4. Escribe `front` y `back` en espanol.
5. Ejecuta la exportacion y revisa la vista previa.

### 3. Exportar el deck

```powershell
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics
```

Archivos esperados:

- `outputs/flashcards/westgard_qc_basics/westgard_qc_basics.csv`
- `outputs/flashcards/westgard_qc_basics/preview.html`
- `outputs/flashcards/westgard_qc_basics/flashcards.css`
- `outputs/flashcards/westgard_qc_basics/manifest.json`
- `outputs/flashcards/westgard_qc_basics/study_deck.json`

### 4. Revisar el resultado

- `preview.html`: vista legible para revision editorial
- `westgard_qc_basics.csv`: archivo importable en Anki
- `manifest.json`: resumen determinista del deck exportado
- `study_deck.json`: contrato estatico para la web

## Publicar las flashcards en la web

La web de estudiantes ya puede consumir el deck exportado sin backend.

Desde la raiz del repo:

```powershell
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics
cd apps/student-web
npm run sync:data
npm run dev
```

Luego abre:

- `/#/flashcards`

Detalles operativos:

- La web lee `public/flashcards/westgard_qc_basics/study_deck.json`
- El progreso se guarda localmente con `localStorage`
- El MVP usa tres pilas: nuevas, en practica y repaso
- Los botones de estudio son `Repetir` y `La supe`

## Notas de desarrollo

- El subsistema de flashcards esta separado del nucleo cientifico del simulador.
- La validacion combina JSON Schema con chequeos de ids duplicados, `sort_order` duplicado y marcado invalido.
- La exportacion es determinista y compatible con un flujo estatico futuro.
