# cliente_api

Proyecto listo para abrir en Visual Studio (o VS Code) y correr directo.

## Pasos

1. Descomprime la carpeta y ábrela en Visual Studio / VS Code.
2. Abre una terminal dentro de la carpeta e instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

3. Renombra `.env.example` a `.env` y pega tu clave real de Gemini adentro:

   ```
   GEMINI_API_KEY=tu_clave_real_aqui
   ```

4. Corre el script:

   ```
   python cliente_api.py
   ```

   Si la clave es válida, imprime la respuesta de Gemini.

## Para provocar el error a propósito (paso de práctica del documento)

Cambia el valor de `GEMINI_API_KEY` en tu `.env` por algo inválido, por ejemplo:

```
GEMINI_API_KEY=clave_invalida
```

Corre de nuevo `python cliente_api.py`. Deberías ver un traceback terminando en:

```
ValueError: Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.
```

Después restaura tu clave real en el `.env` antes de seguir.

## Contenido

- `cliente_api.py` — el código de la lección (versión final, con `try/except` para timeouts y clasificación de errores 401/403/429/5xx), más `load_dotenv()` agregado para que el `.env` se lea automáticamente y una llamada al final para que el script haga algo al correrlo.
- `requirements.txt` — `requests` y `python-dotenv`.
- `.env.example` — plantilla del archivo de variables de entorno; renómbralo a `.env`.
- `.gitignore` — evita subir tu `.env` real a un repositorio.
