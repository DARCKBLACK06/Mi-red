from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import json
import time
import threading
import os
import GPUtil
import string
import socket  # Importar la biblioteca socket para obtener la IP

app = Flask(__name__)
CORS(app)

# Crear el archivo performance.json si no existe
if not os.path.exists('performance.json'):
    with open('performance.json', 'w') as f:
        json.dump({
            'cpu': 0,
            'memory': 0,
            'c_disk': '0 GB/0 GB',
            'd_disk': '0 GB/0 GB',
            'gpu_usage': 0,
            'vram_usage': 0,
            'ip_address': '0.0.0.0'  # Agregar un campo para la dirección IP
        }, f)

# Función para obtener la dirección IP
def get_ip_address():
    try:
        # Crear un socket para obtener la dirección IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conectar a un servidor externo (Google DNS)
        ip_address = s.getsockname()[0]  # Obtener la dirección IP local
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error obteniendo la dirección IP: {e}")
        return "0.0.0.0"  # Retornar una dirección IP por defecto en caso de error

# Función para obtener los datos de rendimiento
def get_performance_data():
    gpu_usage, vram_usage = 0, 0
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            gpu_usage = gpu.load * 100
            vram_usage = gpu.memoryUsed / gpu.memoryTotal * 100
    except Exception as e:
        print(f"Error getting GPU data: {e}")

    return {
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'gpu_usage': gpu_usage,
        'vram_usage': vram_usage,
        'ip_address': get_ip_address()  # Agregar la dirección IP al diccionario
    }

# Función para actualizar los datos de rendimiento en un archivo JSON
def update_performance_data():
    while True:
        try:
            data = get_performance_data()
            drives = [f"{drive}:\\" for drive in string.ascii_uppercase if os.path.exists(f"{drive}:\\")]
            for drive in drives:
                usage = psutil.disk_usage(drive)
                data[f"{drive[0].lower()}_disk"] = f"{usage.used / (1024 ** 3):.1f} GB/{usage.total / (1024 ** 3):.1f} GB"

            with open('performance.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error updating performance data: {e}")
        time.sleep(1)

# Iniciar el hilo para actualizar los datos de rendimiento
threading.Thread(target=update_performance_data, daemon=True).start()

# Ruta para obtener los datos de rendimiento
@app.route('/performance', methods=['GET'])
def get_performance():
    try:
        with open('performance.json') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': f"Error reading performance data: {e}"}), 500

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)