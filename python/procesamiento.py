import json
import sys

def recibir_datos():

    datos = json.load(sys.stdin)

    print("Datos recibidos correctamente:")
    print(json.dumps(datos, indent=4))

if __name__ == "__main__":
    recibir_datos()
