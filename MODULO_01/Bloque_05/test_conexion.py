import requests
 
def obtener_datos(url):
	respuesta = requests.get(url)
	return respuesta.json()
 
url_rota = "https://esta-direccion-no-existe.ejemplo/datos"

try:
	datos = obtener_datos(url_rota)
	print(datos)
except requests.exceptions.RequestException as e:
	print(f"Error al obtener los datos: {e}")