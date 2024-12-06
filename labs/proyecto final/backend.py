from flask import Flask, jsonify
import subprocess
import os
import logging

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def home():
    return jsonify({"message": "Servidor funcionando. Usa /run-script para ejecutar el script."})

@app.route('/favicon.ico')
def favicon():
    return '', 204
@app.route('/run-script2', methods=['GET'])
def run_script2():
    try:
     
        # Validar el resultado de la ejecución
        if 0 == 0:
            # Verificar si el archivo JSON de salida existe
            output_file_path = os.path.join(os.getcwd(), 'stp_network_map.json')
            logging.debug(f"Ruta del archivo de salida: {output_file_path}")
            if os.path.exists(output_file_path):
                with open(output_file_path, 'r') as file:
                    json_data = file.read()
                    return jsonify({"status": "success", "data": json_data})
            else:
                logging.error("Archivo de salida JSON no encontrado.")
                return jsonify({"status": "error", "message": "Archivo de salida JSON no encontrado"}), 500
        else:
            logging.error(f"Error en la ejecución del script: {result.stderr}")
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        logging.error(f"Excepción capturada: {str(e)}")
        print(f"Excepción capturada: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        # Ruta del script
        script_path = os.path.join(os.getcwd(), '/home/wheliver/labs/proyecto final/main.py')
        logging.debug(f"Ruta del script: {script_path}")
        print(f"Ruta del script: {script_path}")

        # Verificar si el archivo existe
        if not os.path.exists(script_path):
            logging.error(f"El archivo {script_path} no existe.")
            return jsonify({"status": "error", "message": f"El archivo {script_path} no existe."}), 500

        # Ejecutar el script
        result = subprocess.run(
            ['python3', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        logging.debug(f"Salida del script: {result.stdout}")
        logging.debug(f"Errores del script: {result.stderr}")
        print(f"Salida del script: {result.stdout}")
        print(f"Errores del script: {result.stderr}")

        # Validar el resultado de la ejecución
        if result.returncode == 0:
            # Verificar si el archivo JSON de salida existe
            output_file_path = os.path.join(os.getcwd(), 'stp_network_map.json')
            logging.debug(f"Ruta del archivo de salida: {output_file_path}")
            if os.path.exists(output_file_path):
                with open(output_file_path, 'r') as file:
                    json_data = file.read()
                    return jsonify({"status": "success", "data": json_data})
            else:
                logging.error("Archivo de salida JSON no encontrado.")
                return jsonify({"status": "error", "message": "Archivo de salida JSON no encontrado"}), 500
        else:
            logging.error(f"Error en la ejecución del script: {result.stderr}")
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        logging.error(f"Excepción capturada: {str(e)}")
        print(f"Excepción capturada: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
