# Decks de Flashcards

Esta carpeta contiene los decks editables de flashcards para Westgard y educación de laboratorio clínico.

## Archivos

- `westgard_qc_basics.deck.json`: deck de ejemplo y fuente de verdad actual.
- `flashcard_deck.schema.json`: esquema JSON usado para validar la estructura.
- `theme_tokens.json`: tokens visuales compartidos para la vista previa HTML.

## Flujo seguro de edición

1. Edita el deck JSON.
2. Mantén estable cada `id` de tarjeta una vez que haya sido exportado o compartido.
3. Ejecuta desde la raíz del repo:

```powershell
.\.venv\python.exe scripts\export_flashcards.py --deck content/flashcards/westgard_qc_basics.deck.json --output-dir outputs/flashcards/westgard_qc_basics
```

4. Si el script termina bien, revisa `preview.html` y el CSV generado.

## Formato inline soportado

- `**negrita**`
- `*cursiva*`
- `` `monoespaciado` ``
- `[[rule:1-2s]]`
- `[[warning:revisar control]]`
- `[[rejection:rechazar la ejecucion]]`
- `[[specimen:suero]]`
- `[[instrument:analizador químico]]`
- `[[qc:control nivel 2]]`

Los tokens semánticos se renderizan como resaltados en la vista previa HTML y como spans HTML seguros dentro del CSV para Anki.
