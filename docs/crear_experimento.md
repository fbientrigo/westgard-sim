# Crear Experimento (authoring catalog)

Guia practica para editar `content/authoring_catalog.example.json` sin romper validacion.

## Estructura minima

```json
{
  "experiments": [
    {
      "id": "glucose_intro_course",
      "title": "Glucose Intro Course",
      "description": "Set inicial para practicar identificacion de errores de control de calidad.",
      "analyte": "Glucose",
      "config": {
        "mean": 100.0,
        "sd": 2.0,
        "n_runs": 30,
        "seed": 42
      },
      "scenarios": [
        {
          "id": "syst_bias_early",
          "type": "systematic_error",
          "parameters": {
            "start_run": 10,
            "shift_sd": 3.0
          },
          "education": {
            "description": "Que deberia observar el estudiante.",
            "learning_objective": "Objetivo pedagogico del escenario.",
            "questions": ["Pregunta 1"],
            "explanation": "Explicacion esperada."
          }
        }
      ]
    }
  ]
}
```

## Que significa cada campo

### Nivel catalogo

- `experiments`: lista de experimentos. Minimo 1.

### Nivel experimento

- `id`: identificador unico del experimento. Evita espacios; usa `snake_case`.
- `title`: nombre visible para la UI.
- `description`: contexto del experimento.
- `analyte`: analito (ejemplo: `Glucose`, `Creatinine`).
- `config`: parametros base de simulacion.
- `scenarios`: lista de escenarios del experimento. Minimo 1.

### `config`

- `mean`: media objetivo del control.
- `sd`: desviacion estandar base. Debe ser mayor a 0.
- `n_runs`: cantidad de corridas simuladas (minimo 5).
- `seed`: semilla para reproducibilidad.

### Nivel escenario

- `id`: identificador unico del escenario dentro del experimento.
- `type`: tipo de falla.
  - `systematic_error`: sesgo abrupto.
  - `trend`: tendencia gradual.
  - `random_error`: aumento de dispersion.
- `parameters`: parametros numericos del comportamiento.
- `education`: bloque pedagogico que consume la UI.

### `parameters`

Campos posibles (dependen del `type`):

- `start_run`: corrida desde donde inicia el problema.
- `shift_sd`: magnitud de sesgo en unidades SD.
- `drift_per_run`: pendiente por corrida (para `trend`).
- `sd_multiplier`: multiplicador de dispersion (para `random_error`).

Recomendacion practica por tipo:

- `systematic_error`: usar `start_run` + `shift_sd`.
- `trend`: usar `start_run` + `drift_per_run`.
- `random_error`: usar `start_run` + `sd_multiplier`.

### `education`

- `description`: texto corto de lo que se observa.
- `learning_objective`: habilidad/concepto a entrenar.
- `questions`: preguntas para estudiante (minimo 1).
- `explanation`: respuesta esperada o guia docente.

## Flujo recomendado para crear/subir experimentos

1. Editar en UI (`.\westgard_ops.ps1 -Action ui`) o directo en JSON.
2. Validar (`Validar catalogo` en UI o `preflight` por CLI).
3. Generar dataset (`.\westgard_ops.ps1 -Action release`).
4. Publicar `outputs/web_data` en el frontend de estudiantes (`public/web_data` o equivalente).

## Validacion por CLI

```powershell
.\westgard_ops.ps1 -Action preflight
.\westgard_ops.ps1 -Action verify
```

## Errores comunes

- IDs repetidos: rompe navegacion por rutas.
- `questions` vacio: invalida el schema.
- `sd` en 0: invalido por definicion estadistica.
- editar solo UI sin exportar: no aparecen cambios en la web de estudiantes.
