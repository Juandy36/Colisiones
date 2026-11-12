import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

carpeta = Path(__file__).resolve().parent.parent
archivo_historial = carpeta / "datos" / "historial.json"
archivo_pdf = carpeta / "datos" / "informe_colision.pdf"
archivo_grafica = carpeta / "datos" / "grafica.png"

def generar_informe():
    with open(archivo_historial, "r", encoding="utf-8") as archivo:
        historial = json.load(archivo)

    if not historial:
        raise ValueError("No hay simulaciones en el historial.")

    registro = historial[-1]

    parametros = registro["parametros"]
    resultados = registro["resultados"]

    pdf = canvas.Canvas(str(archivo_pdf), pagesize=letter)

    ancho, alto = letter
    y = alto - 50

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, y, "Collision Arena")

    y -= 35

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, "Informe de simulacion de colisiones")

    y -= 30
    pdf.drawString(50, y, f"Fecha: {registro['fecha']}")

    y -= 45

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "1. Parametros de entrada")

    y -= 25

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Tipo de colision: {parametros['tipo']}")
    y -= 20
    pdf.drawString(50, y, f"Masa del cuerpo 1: {parametros['masa1']} kg")
    y -= 20
    pdf.drawString(50, y, f"Masa del cuerpo 2: {parametros['masa2']} kg")
    y -= 20
    pdf.drawString(50, y, f"Velocidad inicial del cuerpo 1: {parametros['velocidad1']} m/s")
    y -= 20
    pdf.drawString(50, y, f"Velocidad inicial del cuerpo 2: {parametros['velocidad2']} m/s")

    y -= 35

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "2. Resultados")

    y -= 25

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Velocidad final del cuerpo 1: {resultados['v1f']:.2f} m/s")
    y -= 20
    pdf.drawString(50, y, f"Velocidad final del cuerpo 2: {resultados['v2f']:.2f} m/s")
    y -= 20
    pdf.drawString(50, y, f"Momento inicial: {resultados['momentoAntes']:.2f} kg*m/s")
    y -= 20
    pdf.drawString(50, y, f"Momento final: {resultados['momentoDespues']:.2f} kg*m/s")
    y -= 20
    pdf.drawString(50, y, f"Energia inicial: {resultados['energiaAntes']:.2f} J")
    y -= 20
    pdf.drawString(50, y, f"Energia final: {resultados['energiaDespues']:.2f} J")

    y -= 35

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "3. Analisis de conservacion")

    y -= 25

    pdf.setFont("Helvetica", 11)

    if resultados["conservaMomento"]:
        pdf.drawString(50, y, "El momento lineal se conserva.")
    else:
        pdf.drawString(50, y, "El momento lineal no se conserva.")

    y -= 20

    if resultados["conservaEnergia"]:
        pdf.drawString(50, y, "La energia cinetica se conserva.")
    else:
        pdf.drawString(50, y, "La energia cinetica no se conserva.")

    y -= 40

pdf.setFont("Helvetica-Bold", 14)
pdf.drawString(50, y, "4. Grafica de la colision")

if archivo_grafica.exists():
    pdf.drawImage(
        ImageReader(str(archivo_grafica)),
        50,
        20,
        width=420,
        height=175,
        preserveAspectRatio=True
    )
else:
    raise FileNotFoundError("No se encontro la grafica.")

    pdf.showPage()
    pdf.save()

if __name__ == "__main__":
    generar_informe()
    print("Informe PDF generado correctamente.")
