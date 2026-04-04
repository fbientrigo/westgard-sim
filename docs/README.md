# Documentacion Authoring MVP

Este directorio contiene la documentacion operativa del flujo local de authoring y publicacion de datos estaticos.

## Punto de entrada recomendado

1. Ejecutar `..\westgard_ops.ps1 -Action preflight`.
2. Seguir `PILOT_QUICKSTART_5_MIN.md`.
3. Correr `..\westgard_ops.ps1 -Action ui` para editar.
4. Correr `..\westgard_ops.ps1 -Action release` para generar datos reales.
5. Confirmar con `..\westgard_ops.ps1 -Action verify`.

## Mapa de documentos

- `PILOT_QUICKSTART_5_MIN.md`: arranque en 5 minutos (ideal primera ejecucion).
- `AUTHORING_MVP_TUTORIAL.md`: tutorial guiado de uso de la UI.
- `AUTHORING_MVP_GUIDE.md`: referencia funcional de la UI y pipeline.
- `crear_experimento.md`: significado de cada campo del catalogo y como cargar nuevos experimentos.
- `BEA_PILOT_CHECKLIST.md`: checklist de ejecucion de piloto.
- `PILOT_TROUBLESHOOTING.md`: errores comunes y resolucion.
- `PILOT_RECOVERY_GUIDE.md`: recuperacion desde backups y restauracion.
- `STUDENT_FRONTEND_PLAN.md`: plan incremental de implementacion del frontend estudiante.
- `STUDENT_FRONTEND_GUIDE.md`: guia operativa del frontend estudiante (local + Pages).
- `FLASHCARDS_GUIDE.md`: authoring y export de decks de flashcards para Anki + preview HTML.

## Nota importante

Abrir la UI (`-Action ui`) no exporta datos por si solo. La generacion de payloads en `outputs/web_data` ocurre al ejecutar `release` o al usar en UI las acciones de build + export.
