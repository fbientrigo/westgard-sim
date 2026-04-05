# Guia de Uso: Authoring Studio

## Objetivo

Permitir que Beatriz pueda trabajar desde una sola UI local para:

1. Crear y reordenar experimentos y escenarios.
2. Crear flashcards con tags propios y orden manual.
3. Validar, exportar y dejar la web local lista sin tocar codigo.

La UI sigue separada del nucleo cientifico en `qc_lab_simulator/`.

## Entrada recomendada

```powershell
.\run_authoring_ui.ps1
```

El launcher abre `scripts/authoring_mvp.py` con Streamlit.

## Estructura de la UI

### Barra lateral

- Catalogo de experimentos
- Guardado de experimentos
- Catalogo tecnico
- Salida web de experimentos
- Deck de flashcards
- Guardado del deck
- Salida export de flashcards
- Destinos de publicacion en `apps/student-web/public`

### Pestanas principales

- `Inicio`: explica que carpeta sirve para compartir y cual actualiza la web local.
- `Experimentos`: edicion de experimentos, escenarios y bloque educativo.
- `Flashcards`: edicion de deck, tarjetas, tags y vista previa rapida.
- `Publicar`: validacion, guardado, export y copia a la web local.

## Flujo recomendado para experimentos

1. Abrir catalogo de experimentos.
2. Editar experimento y escenarios.
3. Validar experimentos.
4. Guardar experimentos.
5. Generar y exportar dataset.
6. Compartir `outputs/...` o publicar en `apps/student-web/public/web_data`.

## Flujo recomendado para flashcards

1. Abrir deck de flashcards.
2. Crear o reordenar tarjetas.
3. Ajustar tags generales y tags por tarjeta.
4. Validar flashcards.
5. Guardar deck.
6. Exportar flashcards.
7. Compartir `outputs/...` o publicar en `apps/student-web/public/flashcards/<deck_id>`.

## Que significa cada destino

- `outputs/...`: carpeta lista para revision editorial, respaldo o envio a otra persona.
- `apps/student-web/public/...`: copia operativa para que la web local de estudiantes use los cambios.

## Operacion alternativa por script

Si se necesita un flujo tecnico separado:

```powershell
.\westgard_ops.ps1 -Action preflight
.\westgard_ops.ps1 -Action release
.\westgard_ops.ps1 -Action verify
```

## Limitaciones actuales

- No hay deshacer/rehacer.
- No hay control de versiones dentro de la UI.
- La vista previa de flashcards es editorial; la de experimentos sigue mostrando el catalogo tecnico en JSON.
