# Entorno de Python

Desde la raíz del proyecto, crea el entorno con Python 3.14 e instala las dependencias de ambos módulos:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r MODULO_01/src/requirements.txt -r MODULO_02/src/requirements.txt
```

En VS Code, selecciona `.venv/bin/python` con **Python: Select Interpreter**. Para ejecutar un archivo desde la terminal:

```bash
.venv/bin/python MODULO_02/Bloque_19/enrutamiento.py
```

Los ejemplos que usan Gemini requieren `GEMINI_API_KEY` en el entorno o en `MODULO_02/.env`. No subas el archivo `.env` al repositorio.
