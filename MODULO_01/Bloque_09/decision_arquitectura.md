# Decisión de arquitectura: elección de modelo
  
 ## Modelo elegido
  MOdelo A: Gemini 3.5 Flash-Lite, este será el modelo base de mi miniApp

  Modelo B: Gemini 3.8 Flash

 ## Diagrama de arquitectura
  Diagrama de arquitecura (está en el repositorio)
El diagrama parte con la peticion de la psersona de "necesito un flete" a la interface de la app. Luego pasa a traves del flujo, llegando a de nuevo hasta la interface del usuario. El flujo pasa por api Rquest, procesa la request, llega hasta el backend de de la app, entra en la base de datos de los fletes, se devuelve y entra a RATE APi , donde calula los costos del flete. COn la ruta estimada y los costos estimados llega finalmente a la interfaz del usuario 

 ## Comparación de candidatos

 
  
 ## Justificación
  
 ## Alternativa descartada y por qué