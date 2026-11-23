# Alcance y límites de la evaluación por palabras

## Qué evalúa

El [pipeline del bloque 16](../Bloque_16/pipeline_texto.py) compara una respuesta con un texto de referencia. Convierte ambos a minúsculas, elimina la puntuación y cuenta las palabras compartidas, respetando la cantidad de veces que aparecen.

- **Precisión:** proporción de palabras de la respuesta que coinciden con la referencia.
- **Cobertura:** proporción de palabras de la referencia presentes en la respuesta.
- **F1:** media armónica de precisión y cobertura.

Estas medidas describen coincidencias de palabras, no garantizan que la respuesta sea correcta.

## Casos donde puede fallar

Los siguientes ejemplos usan la implementación del bloque 16; los valores están redondeados a dos decimales.

| Referencia | Respuesta | F1 | Limitación |
|---|---|---:|---|
| El coche es rápido | El automóvil es veloz | 0,50 | Una respuesta equivalente puede perder puntos por usar sinónimos. |
| La reunión será en 2025 | La reunión será en 2026 | 0,80 | Una fecha incorrecta puede recibir una puntuación alta. |
| El sistema no guarda datos | El sistema guarda datos | 0,89 | Omitir una negación cambia el sentido, aunque la puntuación sea alta. |

Además, el orden de las palabras no afecta el resultado, y las tildes o distintas formas de una palabra pueden reducir las coincidencias.

## Resultados disponibles

El archivo [resultados_metricas.json](../../resultados_metricas.json) contiene tres respuestas sobre Python evaluadas con esta métrica. Es una muestra pequeña y no consta en el archivo una revisión humana de su exactitud; no basta por sí sola para generalizar los resultados.

## Uso recomendado

Utilizar las puntuaciones para comparar versiones sobre los mismos casos y detectar respuestas que merecen revisión. Complementarlas con una evaluación humana, especialmente para negaciones, fechas, cifras y nombres propios.
