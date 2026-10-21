from dotenv import load_dotenv # importando la funcion load_datenv del modulo dotenv
import os # importando el modulo os para acceder a las variables de entorno

load_dotenv()
# Cargar las varialbes de entorno 
load_dotenv() # cargando las variables de entorno desde el archivo .env

AI_API_KEY = os.getenv("AI_API_KEY") # obteniendo el valor de la variable de entorno AI_API_KEY
AI_MODEL = os.getenv("AI_MODEL") # obteniendo el valor de la variable de entorno AI_MODEL


print(AI_API_KEY)
print(AI_MODEL)

