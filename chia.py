import subprocess
import logging
import time
from tqdm import tqdm
import colorlog
import json
from termcolor import colored

# Configuración del log con colorlog
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors=log_colors
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Configuración del log para consola y archivo
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

file_handler = logging.FileHandler('ejecucion_comando.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Función para mostrar mensajes con colores y emojis
def mostrar_mensaje(mensaje, color, emoji):
    mensaje_color = colored(mensaje, color, attrs=['bold'])
    print(f"{emoji} {mensaje_color} {emoji}")

# Función para ejecutar el comando y obtener la salida
def ejecutar_comando(comando, descripcion):
    try:
        # Registrar el comando que se va a ejecutar
        logger.info("Inicio de la ejecución del comando")
        logger.info(f"Descripción: {descripcion}")
        logger.info(f"Ejecutando comando: {comando}")
        mostrar_mensaje(f"Descripción: {descripcion}", 'cyan', '🔍')
        mostrar_mensaje(f"Ejecutando comando: {comando}", 'cyan', '⚙️')
        
        # Mostrar una animación de carga antes de ejecutar el comando
        mostrar_mensaje("Preparando para ejecutar el comando...", 'yellow', '⌛')
        for _ in tqdm(range(100), desc="Cargando", unit="tick", ncols=100, ascii=' ░▒▓█'):
            time.sleep(0.05)

        # Ejecutar el comando
        proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Capturar la salida en tiempo real
        salida_completa = ""
        while True:
            salida = proceso.stdout.readline()
            if salida == '' and proceso.poll() is not None:
                break
            if salida:
                mostrar_mensaje(salida.strip(), 'green', '✅')
                logger.info(salida.strip())
                salida_completa += salida.strip()
        
        # Registrar la salida de error en tiempo real
        error = proceso.stderr.read()
        if error:
            mostrar_mensaje(f"Error: {error.strip()}", 'red', '❌')
            logger.error(f"Error: {error.strip()}")
        
        # Verificar el código de salida del comando
        retorno = proceso.poll()
        if retorno == 0:
            mostrar_mensaje("Comando ejecutado exitosamente.", 'green', '🎉')
            logger.info("Comando ejecutado exitosamente.")
        else:
            mostrar_mensaje(f"El comando finalizó con el código de salida: {retorno}", 'red', '⚠️')
            logger.error(f"El comando finalizó con el código de salida: {retorno}")
            
        return salida_completa
        
    except Exception as e:
        mostrar_mensaje(f"Excepción al ejecutar el comando: {str(e)}", 'red', '💥')
        logger.error(f"Excepción al ejecutar el comando: {str(e)}")
        return None

if __name__ == "__main__":
    # Comando para crear una base de datos en Chia
    comando_creacion_bd = "chia data create_data_store -m 0.00001"
    descripcion_creacion_bd = "Creación de la base de datos en Chia"
    salida_creacion_bd = ejecutar_comando(comando_creacion_bd, descripcion_creacion_bd)
    
    # Extraer el ID generado del comando de creación de la base de datos
    id_bd = None
    if salida_creacion_bd:
        try:
            id_bd = json.loads(salida_creacion_bd)["id"]
            mostrar_mensaje(f"ID de la base de datos creada: {id_bd}", 'blue', '🆔')
            logger.info(f"ID de la base de datos creada: {id_bd}")
        except (json.JSONDecodeError, KeyError) as e:
            mostrar_mensaje(f"Error al extraer el ID de la base de datos: {str(e)}", 'red', '❌')
            logger.error(f"Error al extraer el ID de la base de datos: {str(e)}")
    
    # Continuar solo si se ha obtenido un ID válido
    if id_bd:
        # Esperar un momento antes de ejecutar el siguiente comando
        mostrar_mensaje("Esperando un momento antes de la inserción de datos...", 'yellow', '⌛')
        time.sleep(10)

        # Comando para insertar datos en la base de datos
        comando_insercion_datos = f"chia rpc data_layer batch_update '{{\"id\":\"{id_bd}\", \"changelist\":[{{\"action\":\"insert\", \"key\":\"0003\", \"value\":\"abc1\"}}]}}'"
        descripcion_insercion_datos = "Inserción de datos en la base de datos en Chia"
        salida_insercion_datos = ejecutar_comando(comando_insercion_datos, descripcion_insercion_datos)
        
        # Esperar un momento antes de ejecutar el siguiente comando
        mostrar_mensaje("Esperando un momento antes de la consulta de datos...", 'yellow', '⌛')
        time.sleep(10)

        # Comando para consultar datos en la base de datos
        comando_consulta_datos = f"chia rpc data_layer get_keys_values '{{\"id\":\"{id_bd}\"}}'"
        descripcion_consulta_datos = "Consulta de datos en la base de datos en Chia"
        ejecutar_comando(comando_consulta_datos, descripcion_consulta_datos)
