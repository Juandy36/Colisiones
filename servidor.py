#Servidor de la pagina web del proyecto. Usa de verdad colisiones.py, Main.java y grafica.py
#Trabajo en conjunto con Jefferson Useche, Andres Nichoy, Juan Diego Ortiz y Paulo Claro
#Uso: python servidor.py   (abre el navegador solo; NO_ABRIR=1 para que no lo abra, PUERTO=5000)
import os
import re
import sys
import math
import threading
import subprocess
import webbrowser
from flask import Flask, jsonify, request, send_file, send_from_directory
from colisiones import Elastica, Inelastica

CARPETA = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(CARPETA, "resultados.csv")
PNG = os.path.join(CARPETA, "grafica.png")
DOCUMENTOS = ["informe.txt", "notas.txt", "README.md"]
TOLERANCIA = 0.0001

app = Flask(__name__)
hayJava = False

def compilar_java():
    #compilamos Main.java al arrancar; si no hay java avisamos en vez de romper
    global hayJava
    try:
        r = subprocess.run(["javac", "Main.java"], cwd=CARPETA, capture_output=True, text=True, timeout=60)
        hayJava = r.returncode == 0
        if not hayJava:
            print("No se pudo compilar Main.java:", r.stderr)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        hayJava = False
        print("No se encontro java/javac, el motor Java no va a estar disponible")

def es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

def respuesta(tipo, m1, v1, m2, v2, v1f, v2f):
    pA = m1 * v1 + m2 * v2
    pD = m1 * v1f + m2 * v2f
    eA = 0.5 * m1 * v1 ** 2 + 0.5 * m2 * v2 ** 2
    eD = 0.5 * m1 * v1f ** 2 + 0.5 * m2 * v2f ** 2
    return {
        "tipo": tipo, "m1": m1, "v1": v1, "m2": m2, "v2": v2,
        "v1f": v1f, "v2f": v2f,
        "momentoAntes": pA, "momentoDespues": pD,
        "energiaAntes": eA, "energiaDespues": eD,
        "conservaMomento": abs(pA - pD) < TOLERANCIA,
        "conservaEnergia": abs(eA - eD) < TOLERANCIA,
    }

def error(texto, codigo=400):
    return jsonify({"error": texto}), codigo

@app.route("/")
def inicio():
    return send_from_directory(CARPETA, "index.html")

@app.route("/api/calcular", methods=["POST"])
def calcular():
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return error("Los datos llegaron mal, intente de nuevo.")
    motor = d.get("motor")
    tipo = d.get("tipo")
    if motor not in ("python", "java"):
        return error("El motor debe ser python o java.")
    if tipo not in ("elastica", "inelastica"):
        return error("El tipo debe ser elastica o inelastica.")
    datos = {}
    for k in ["m1", "v1", "m2", "v2"]:
        if not es_numero(d.get(k)):
            return error("Escriba numeros validos en m1, v1, m2 y v2.")
        datos[k] = float(d[k])
    e = 0.0
    if tipo == "inelastica":
        if not es_numero(d.get("e")):
            return error("Escriba un numero valido en e.")
        e = float(d["e"])
        if e < 0 or e > 1:
            return error("e debe estar entre 0 y 1.")
    if datos["m1"] <= 0 or datos["m2"] <= 0:
        return error("Las masas deben ser mayores a 0.")
    m1, v1, m2, v2 = datos["m1"], datos["v1"], datos["m2"], datos["v2"]

    if motor == "java" and tipo == "inelastica" and e != 0:
        return error("El motor Java solo calcula la inelastica perfecta (e = 0).")

    if motor == "python":
        if tipo == "elastica":
            c = Elastica(m1, v1, m2, v2)
        else:
            c = Inelastica(m1, v1, m2, v2, e)
        v1f, v2f = c.v1f, c.v2f
        if not (math.isfinite(v1f) and math.isfinite(v2f)):
            return error("Los numeros son demasiado grandes.")
        with open(CSV, "a", encoding="utf-8") as archivo:
            archivo.write(f"{c.tipo},{c.m1},{c.v1},{c.m2},{c.v2},{c.v1f},{c.v2f}\n")
        return jsonify(respuesta(c.tipo, m1, v1, m2, v2, v1f, v2f))

    #motor java: Main.java ya agrega su linea a resultados.csv
    if not hayJava:
        return error("El motor Java no esta disponible (no se encontro java o no compilo Main.java).", 503)
    opcion = "1" if tipo == "elastica" else "2"
    entrada = f"{opcion}\n{m1!r}\n{v1!r}\n{m2!r}\n{v2!r}\n"
    try:
        r = subprocess.run(["java", "Main"], input=entrada, cwd=CARPETA, capture_output=True,
                           text=True, encoding="utf-8", timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return error("No se pudo ejecutar Java.", 500)
    m = re.search(r"v1 = (\S+) \| v2 = (\S+)", r.stdout)
    if r.returncode != 0 or m is None:
        return error("Java no devolvio un resultado: " + (r.stdout + r.stderr).strip()[-200:], 500)
    v1f = float(m.group(1))
    v2f = float(m.group(2))
    nombre = "Elastica" if tipo == "elastica" else "Inelastica"
    return jsonify(respuesta(nombre, m1, v1, m2, v2, v1f, v2f))

@app.route("/api/historial")
def historial():
    filas = []
    if os.path.exists(CSV):
        with open(CSV, "r", encoding="utf-8") as archivo:
            for L in archivo.readlines():
                p = L.strip().split(",")
                if len(p) < 7:
                    continue
                try:
                    nums = [float(x) for x in p[1:7]]
                except ValueError:
                    continue
                filas.append(respuesta(p[0], *nums))
    return jsonify(filas)

@app.route("/api/limpiar", methods=["POST"])
def limpiar():
    for ruta in [CSV, PNG]:
        if os.path.exists(ruta):
            os.remove(ruta)
    return jsonify({"ok": True})

@app.route("/grafica.png")
def grafica():
    if os.path.exists(PNG):
        os.remove(PNG)
    entorno = dict(os.environ)
    entorno["MPLBACKEND"] = "Agg"
    try:
        subprocess.run([sys.executable, "grafica.py"], cwd=CARPETA, env=entorno,
                       capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        pass
    if not os.path.exists(PNG):
        return "No se pudo generar la grafica", 404
    resp = send_file(PNG, mimetype="image/png")
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/api/documento/<nombre>")
def documento(nombre):
    if nombre not in DOCUMENTOS:
        return error("Ese documento no existe.", 404)
    with open(os.path.join(CARPETA, nombre), "r", encoding="utf-8") as archivo:
        return jsonify({"nombre": nombre, "texto": archivo.read()})

if __name__ == "__main__":
    puerto = int(os.environ.get("PUERTO", "5000"))
    compilar_java()
    if os.environ.get("NO_ABRIR") != "1":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{puerto}")).start()
    print(f"Pagina en http://localhost:{puerto}  (Ctrl+C para cerrar)")
    app.run(host="127.0.0.1", port=puerto, threaded=True)
