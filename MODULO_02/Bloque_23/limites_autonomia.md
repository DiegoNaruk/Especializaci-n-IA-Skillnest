# Límites de autonomía: agente de fletes y mudanzas

## Alcance

Este documento describe el agente de [agente.py](./agente.py), no una futura aplicación de fletes. Sus herramientas usan tarifas y disponibilidad de ejemplo en memoria: no reservan vehículos, no modifican registros y no cobran. La cotización es una estimación, no una confirmación de servicio.

## Herramientas y nivel de riesgo

| Herramienta | Categoría | Riesgo | Consecuencia |
|---|---|---|---|
| `consultar_disponibilidad_flete` | Solo lectura | Bajo | Consulta la disponibilidad de ejemplo por comuna; no modifica datos. Una respuesta equivocada puede desinformar al cliente. |
| `cotizar_flete` | Solo lectura y cálculo | Bajo | Calcula una tarifa estimada; no crea una reserva ni un cobro. Una estimación equivocada puede desinformar al cliente. |

El agente no tiene actualmente herramientas de escritura reversible ni de escritura irreversible con impacto económico.

## Aprobación humana

- Las dos herramientas actuales no requieren aprobación previa: solo consultan datos o calculan una estimación. Una persona debe verificar la disponibilidad y el precio antes de comprometer un servicio real.
- [aprobacion.py](./aprobacion.py) contiene un ejemplo **separado** de `generar_reembolso`, que no está registrado como herramienta del agente. Por su propósito tendría riesgo alto y requeriría aprobación previa; la función llama a `esperar_aprobacion`, acepta solo `s` y rechaza la operación si vence el plazo de 300 segundos. La decisión se guarda únicamente en la lista en memoria `registro_aprobaciones`.
- El reembolso es una simulación: devuelve un mensaje, pero no mueve dinero. No existe una aprobación de reembolso integrada en el agente ni una traza persistente de esa aprobación. Antes de incorporar una acción económica real, implementar y comprobar la aprobación y su registro persistente.

## Revisión de trazas

- **Frecuencia propuesta:** después de cada tanda de pruebas y, si el agente se utiliza regularmente, cada 50 interacciones o semanalmente, lo que ocurra primero. Revisar inmediatamente cualquier resultado sospechoso.
- **Qué revisar:** comparar `entrada`, `acciones` y `respuesta_final`; comprobar la herramienta y sus argumentos, la observación y la coherencia de la respuesta con esa observación.
- **Patrones sospechosos:** uso de herramientas para preguntas generales; llamadas repetidas o innecesarias; comunas sin cobertura o argumentos inválidos, extremos o inconsistentes; errores recurrentes; precios o disponibilidad inventados, distintos de la observación o presentados como confirmados.
- **Evidencia disponible:** [trazas_agente.jsonl](../../trazas_agente.jsonl) contiene dos registros JSON válidos: uno de `consultar_disponibilidad_flete` y otro de `cotizar_flete`. No hay una herramienta de alto riesgo en este agente que deba aparecer en esa muestra.
- **Limitaciones:** `registrar_traza` escribe en `trazas_agente.jsonl` relativo al directorio desde donde se ejecuta el programa, y solo se llama después de cada invocación exitosa y sus comprobaciones. Por tanto, fallos anteriores al registro no quedan reflejados; una lista de acciones vacía tampoco demuestra por sí sola que no haya habido acciones, ya que el código la deja vacía si faltan `intermediate_steps`. Las trazas pueden incluir entradas y respuestas: limitar su acceso antes de utilizarlas con datos reales.
- El archivo [trazas_agente.jsonl del Bloque 23](./trazas_agente.jsonl) contiene Markdown, no registros JSONL; no debe utilizarse como evidencia de ejecución.

## Qué hacer ante un comportamiento inesperado

1. Detener las pruebas y retirar la herramienta afectada de la lista `herramientas` de [agente.py](./agente.py) hasta resolver el problema. No confirmar reservas ni precios basándose en la respuesta afectada.
2. Revisar la entrada, los argumentos, la observación y la respuesta final de la traza correspondiente; si no existe registro, revisar también la salida y el error de la ejecución.
3. Corregir la causa: acotar el prompt o la descripción de la herramienta si se invoca fuera de contexto; ajustar la validación o los datos de ejemplo si los argumentos o resultados son incorrectos.
4. Probar nuevamente los casos afectados, una pregunta general y entradas inválidas; comprobar las acciones y registrar los resultados antes de volver a habilitar la herramienta.
5. Si se agrega una herramienta de impacto económico, mantenerla deshabilitada hasta comprobar la aprobación humana previa, el rechazo o vencimiento y el registro persistente de la decisión.
