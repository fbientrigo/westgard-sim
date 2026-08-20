# Student Next — práctica Westgard

Aplicación estática e independiente para estudiantes de Bioquímica Clínica.
La práctica siempre sigue el mismo ciclo: observar el gráfico de
Levey–Jennings → marcar evidencia → identificar la regla → decidir la acción
→ revelar la evidencia validada → probar un contrafactual.

## Ejecutar localmente

Desde la raíz del repositorio:

```powershell
python scripts/export_student_next_data.py --output-dir apps/student-next/data
python -m http.server 8000 -d apps/student-next
```

Abre <http://localhost:8000>. Se requiere un servidor HTTP porque el navegador
carga los JSON generados mediante `fetch`; `file://` no es suficiente.

## Validar

```powershell
python -m pytest tests/test_evidence.py tests/test_student_next_export.py -q
node --test "apps/student-next/test/*.test.js"
node --check apps/student-next/app.js
```

`apps/student-next/data/` se genera a partir de las fuentes canónicas y está
ignorado por Git. No se edita ni se confirma manualmente.

## Revisión manual antes de publicar

- Desktop: abrir Home, completar los seis escenarios, probar los
  contrafactuales de `warning-1-2s-01` y `reject-2-2s-01`, expandir una regla y
  abrir tarjetas desde ella.
- 360 px, 390 px y 430 px: completar evidencia, regla y acción sin desplazarse
  entre el gráfico y los controles; verificar revelado y contrafactual; revisar
  la sesión de tarjetas.
- Solo teclado: completar un escenario, usar `Esc` para volver al inicio y usar
  `Espacio`, `←` y `→` en una sesión de tarjetas.
- Lector de pantalla: confirmar que la tabla adyacente enumera los diez
  controles y que el resumen del gráfico no revela una regla antes del bloqueo.
