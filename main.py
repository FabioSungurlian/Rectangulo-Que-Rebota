import experimento
import dials
import json
# Importaciones arriba

def iterfaz_usuario_maquina():
    with open('data.json', encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
