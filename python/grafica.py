
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

carpeta_proyecto = Path(__file__).resolve().parent.parent
archivo_historial = carpeta_proyecto / "datos" / "historial.json"
archivo_grafica = carpeta_proyecto / "datos" / "grafica.png"

def generar_grafica():

    if not archivo_historial.exists():
        raise FileNotFoundError("No se encontro el historial.")

    with open(archivo_historial, "r", encoding="utf-8") as archivo:
        historial = json.load(archivo)

    if not historial:
        raise ValueError("No hay simulaciones para graficar.")

    nombres = []
    momento_antes = []
    momento_despues = []
    energia_antes = []
    energia_despues = []

    for i, registro in enumerate(historial):

        parametros = registro["parametros"]
        resultados = registro["resultados"]

        nombres.append(f"{i + 1}. {parametros['tipo'].capitalize()}")

        momento_antes.append(resultados["momentoAntes"])
        momento_despues.append(resultados["momentoDespues"])

        energia_antes.append(resultados["energiaAntes"])
        energia_despues.append(resultados["energiaDespues"])

    posiciones = np.arange(len(nombres))
    ancho = 0.35

    figura, ejes = plt.subplots(1, 2, figsize=(12, 5))

    ejes[0].bar(
        posiciones - ancho / 2,
        momento_antes,
        ancho,
        label="Antes"
    )

    ejes[0].bar(
        posiciones + ancho / 2,
        momento_despues,
        ancho,
        label="Despues"
    )

    ejes[0].set_title("Conservacion del momento lineal")
    ejes[0].set_ylabel("Momento (kg*m/s)")
    ejes[0].set_xticks(posiciones)
    ejes[0].set_xticklabels(nombres, rotation=45, ha="right")
    ejes[0].legend()
    ejes[0].grid(axis="y", alpha=0.3)

    ejes[1].bar(
        posiciones - ancho / 2,
        energia_antes,
        ancho,
        label="Antes"
    )

    ejes[1].bar(
        posiciones + ancho / 2,
        energia_despues,
        ancho,
        label="Despues"
    )

    ejes[1].set_title("Conservacion de la energia cinetica")
    ejes[1].set_ylabel("Energia (J)")
    ejes[1].set_xticks(posiciones)
    ejes[1].set_xticklabels(nombres, rotation=45, ha="right")
    ejes[1].legend()
    ejes[1].grid(axis="y", alpha=0.3)

    figura.suptitle("Analisis de las colisiones", fontsize=15)
    figura.tight_layout()

    figura.savefig(archivo_grafica, dpi=150, bbox_inches="tight")
    plt.close(figura)

if __name__ == "__main__":
    try:
        generar_grafica()
        print("Grafica generada correctamente.")
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
