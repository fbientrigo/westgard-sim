# Checklist de Piloto con Bea (usuaria no tecnica)

Objetivo: comprobar si Bea puede usar el MVP sola de principio a fin.

## Preparacion (5 min)

- [ ] Ejecutar preflight con `.\westgard_ops.ps1 -Action preflight`.
- [ ] Abrir la UI con `.\westgard_ops.ps1 -Action ui`.
- [ ] Cargar `content/authoring_catalog.example.json`.
- [ ] Confirmar que aparece mensaje de catalogo cargado.

## Tareas de Bea (sin ayuda tecnica)

- [ ] Crear 1 experimento nuevo.
- [ ] Cambiar titulo, descripcion y analito.
- [ ] Crear 2 escenarios dentro del experimento.
- [ ] Reordenar escenarios (subir/bajar).
- [ ] Eliminar 1 escenario y dejar 1 valido.
- [ ] Guardar cambios en archivo local.
- [ ] Validar catalogo y entender errores (si aparecen).
- [ ] Construir catalogo tecnico.
- [ ] Exportar datos estaticos web.
- [ ] Ejecutar `.\westgard_ops.ps1 -Action release`.
- [ ] Ejecutar `.\westgard_ops.ps1 -Action verify`.

## Que observar durante la prueba

- [ ] Entiende los nombres de botones sin explicacion adicional.
- [ ] Sabe distinguir que archivo esta cargado y donde se guarda.
- [ ] Puede corregir errores con los mensajes mostrados.
- [ ] Identifica cuando build/export fue exitoso.
- [ ] Puede repetir el flujo dos veces sin ayuda.

## Errores a registrar

- [ ] Mensajes ambiguos o poco accionables.
- [ ] Campos confusos (terminos tecnicos no entendidos).
- [ ] Pasos donde se pierde o duda del estado actual.
- [ ] Fallos al eliminar/reordenar.
- [ ] Casos donde cree que guardo/exporto pero no sabe donde quedo.

## Criterio de exito minimo para piloto

- [ ] Completa flujo completo en menos de 20 minutos.
- [ ] Repite export con una edicion adicional sin asistencia.
- [ ] No queda bloqueada por errores de validacion sin entender accion siguiente.
- [ ] Puede identificar en que carpeta quedaron los resultados (`outputs/web_data`).
