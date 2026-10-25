# Especialización en IA - Skillnest

Repositorio con el código, proyectos, ejercicios y pruebas de evaluación de modelos de lenguaje (LLM) desarrollados durante el programa de **Especialización en Inteligencia Artificial** en Skillnest.

---

## 📌 Descripción del Proyecto

Este repositorio contiene la implementación paso a paso de canalizaciones (*pipelines*) para la interacción, automatización y validación de prompts estructurados utilizando APIs de IA Generativa. 

En este espacio se abordan conceptos fundamentales y avanzados como:
* **Diseño y automatización de prompts (Prompt Engineering):** Creación de un banco de prompts parametrizados con instrucciones del sistema y esquemas de respuesta estricta.
* **Salidas Estructuradas en JSON:** Validación de respuestas mediante esquemas JSON explícitos (`response_schema`).
* **Sistemas de Evaluación y Benchmarking:** Automatización de pruebas de estrés para medir la tasa de éxito (`éxitos/intentos`) en las respuestas de los modelos.
* **Procesamiento de Respuestas:** Limpieza y parseo de salidas que incluyen bloques de código Markdown u otros formatos devueltos por el modelo.

---

## 📁 Estructura del Repositorio

```text
Especializaci-n-IA-Skillnest/
├── MODULO_01/
│   ├── Bloque_10/
│   │   ├── Banco_Prompts.py        # Script principal de ejecución y evaluación de prompts
│   │   └── ...
│   ├── venv/                       # Entorno virtual de Python
│   └── ...
├── prompts/
│   └── registro_resultados.json    # Resultados acumulados de las evaluaciones
├── .gitignore
└── README.md