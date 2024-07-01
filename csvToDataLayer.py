import csv
import json
import subprocess
import argparse

def csv_to_json(csv_file_path):
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

def upload_to_datalayer(data_layer_id, data):
    # Guardar los datos JSON en un archivo temporal
    json_file_path = 'temp_data.json'
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
    
    # Subir el archivo JSON al data layer usando el comando de Chia
    command = [
        'chia', 'data_layer', 'add',
        '--id', data_layer_id,
        '--data', '@' + json_file_path
    ]
    subprocess.run(command, check=True)
    print(f'Datos subidos exitosamente al data layer {data_layer_id}.')

def main():
    parser = argparse.ArgumentParser(description='Subir datos desde un archivo CSV a un data layer de Chia.')
    parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV.')
    parser.add_argument('data_layer_id', type=str, help='ID del data layer de Chia.')
    
    args = parser.parse_args()
    
    # Convertir CSV a JSON
    data = csv_to_json(args.csv_file_path)
    
    # Subir JSON al data layer
    upload_to_datalayer(args.data_layer_id, data)

if __name__ == "__main__":
    main()
