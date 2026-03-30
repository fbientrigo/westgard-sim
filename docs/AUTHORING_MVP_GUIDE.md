# Guia de Uso: Authoring MVP

## Objetivo de esta UI

Permitir que una autora no tecnica pueda editar contenido y escenarios sin tocar codigo de simulacion.

La UI no modifica el motor ni el exportador. Solo orquesta:

1. Edicion de contrato de autora
2. Validacion
3. Adaptacion a catalogo tecnico
4. Export de archivos web estaticos

## Controles principales

## Archivos (barra lateral)

- `Catalogo de autora`: archivo JSON editable de entrada.
- `Guardar cambios en`: ruta de salida del catalogo de autora.
- `Catalogo tecnico salida`: JSON tecnico generado.
- `Directorio web estatico`: carpeta final para GitHub Pages u otro hosting estatico.

## Botones globales

- `Validar catalogo`
- `Guardar cambios`
- `Build technical catalog`
- `Export static web data`

## Gestion de listas (nuevo)

## Experimentos

- `Nuevo experimento`
- `Eliminar experimento`
- `Subir experimento`
- `Bajar experimento`

## Escenarios

- `Nuevo escenario`
- `Eliminar escenario`
- `Subir escenario`
- `Bajar escenario`

## Errores y validacion

La UI muestra errores amigables por alcance:

- experimento seleccionado
- escenario seleccionado
- lista completa de validacion

Si hay errores, no se ejecuta build/export.

## Launcher recomendado

```powershell
.\run_authoring_ui.ps1
```

Que hace:

1. Detecta Python local (`.venv` o `python` global).
2. Verifica Streamlit.
3. Si falta, instala dependencias (`requirements.txt`).
4. Levanta la app.

## Operacion de piloto (recomendado)

Comando unico para operaciones frecuentes:

```powershell
.\westgard_ops.ps1 -Action preflight
.\westgard_ops.ps1 -Action release
.\westgard_ops.ps1 -Action verify
```

`release` incluye backup automatico antes de sobrescribir salidas.

## Flujo de trabajo recomendado

1. Abrir catalogo
2. Editar experimento/escenario
3. Validar
4. Guardar
5. Build technical catalog
6. Export static web data

## Limitaciones actuales (MVP)

- No hay deshacer/rehacer.
- No hay control de versiones dentro de la UI.
- No hay preview grafica de curvas o reglas (solo JSON tecnico).
