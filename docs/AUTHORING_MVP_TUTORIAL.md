# Tutorial: Westgard Authoring MVP (Local)

## 1) Requisitos

- Windows + PowerShell
- Python 3.11+
- Repositorio clonado localmente

## 2) Iniciar la interfaz

Opcion recomendada (launcher):

```powershell
.\run_authoring_ui.ps1
```

Opcion manual:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run scripts/authoring_mvp.py
```

## 3) Abrir un catalogo de autora

1. En la barra lateral, revisa `Catalogo de autora`.
2. Usa por defecto:
   - `content/authoring_catalog.example.json`
3. Haz clic en `Abrir catalogo`.

## 4) Editar experimentos y escenarios

### Experimentos

- `Nuevo experimento`: agrega uno nuevo con valores base.
- `Eliminar experimento`: elimina el seleccionado.
- `Subir experimento` / `Bajar experimento`: reordena.

### Escenarios

- `Nuevo escenario`: agrega uno nuevo en el experimento actual.
- `Eliminar escenario`: elimina el seleccionado.
- `Subir escenario` / `Bajar escenario`: reordena.

### Campos editables

- Experimento:
  - `ID`, `Titulo`, `Descripcion`, `Analito`, `config`
- Escenario:
  - `ID`, `Tipo`, `parameters`, `Bloque educativo`

## 5) Validar y guardar

1. Haz clic en `Validar catalogo`.
2. Si hay errores, revisa los bloques:
   - `Errores del experimento seleccionado`
   - `Errores del escenario seleccionado`
3. Haz clic en `Guardar cambios`.

## 6) Generar catalogo tecnico

1. Haz clic en `Build technical catalog`.
2. Se genera (por defecto):
   - `content/experiment_catalog.generated.json`
3. Veras una vista previa en pantalla.

## 7) Exportar datos estaticos web

1. Haz clic en `Export static web data`.
2. Se generan archivos web (por defecto):
   - `outputs/web_data_from_authoring_ui/index.json`
   - `outputs/web_data_from_authoring_ui/experiments/...`

## 8) Resultado final

Tu flujo local queda asi:

`authoring_catalog.json -> validate -> build technical catalog -> export static web data`
