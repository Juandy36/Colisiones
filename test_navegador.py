#Trabajo en conjunto con Juan Diego Ortiz y Paulo Claro
#Prueba toda la pagina con playwright: arranca servidor.py, usa la pagina y compara Python con Java
#Uso: python test_navegador.py   (necesita: pip install -r requirements.txt y python -m playwright install chromium)
import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

PUERTO = 5055
URL = f"http://localhost:{PUERTO}"
errores_consola = []
llamadas_calcular = []
fallos = 0

def revisar(nombre, condicion):
    global fallos
    if condicion:
        print(f"OK     {nombre}")
    else:
        print(f"FALLO  {nombre}")
        fallos += 1

def limpiar_archivos():
    for nombre in ["resultados.csv", "grafica.png", "Main.class"]:
        if os.path.exists(nombre):
            os.remove(nombre)

def llenar(page, tipo, m1, v1, m2, v2, e=0):
    page.select_option("#tipo", tipo)
    page.fill("#m1", str(m1))
    page.fill("#v1", str(v1))
    page.fill("#m2", str(m2))
    page.fill("#v2", str(v2))
    if page.is_enabled("#e"):
        page.fill("#e", str(e))
    page.click("#simular")
    #esperamos un resultado o un mensaje de error
    page.wait_for_function("document.getElementById('resultado').innerText != '' || document.getElementById('mensaje').innerText != ''", timeout=20000)

def finales(page):
    #devuelve (v1f, v2f) de la pagina o None si no hay resultado
    if page.inner_text("#resultado") == "":
        return None
    return (float(page.inner_text("#v1f")), float(page.inner_text("#v2f")))

def python_java(page):
    #lo que calculo Python y lo que calculo Java (leyendo el csv de Python)
    if page.locator("#jaV1").count() == 0:
        return None, None
    py = (float(page.inner_text("#pyV1")), float(page.inner_text("#pyV2")))
    ja = (float(page.inner_text("#jaV1")), float(page.inner_text("#jaV2")))
    return py, ja

def casi(a, b):
    return a is not None and abs(a[0] - b[0]) < 0.01 and abs(a[1] - b[1]) < 0.01

def filas_tabla(page, esperadas):
    #esperamos a que la tabla tenga las filas esperadas (mas el encabezado) y devolvemos cuantas hay
    page.click("#tabHistorial")
    try:
        page.wait_for_function(f"document.getElementById('tabla').rows.length == {esperadas + 1}", timeout=5000)
    except Exception:
        pass
    return page.evaluate("document.getElementById('tabla').rows.length") - 1   #sin el encabezado

def borrar_historial(page):
    page.click("#tabHistorial")
    page.click("#borrar")
    page.wait_for_function("document.getElementById('tabla').rows.length == 1")
    page.click("#tabSimulador")

def esperar_servidor():
    for i in range(120):
        try:
            urllib.request.urlopen(URL + "/", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False

limpiar_archivos()

#-------- el menu de consola de colisiones.py sigue funcionando --------
entrada = "1\n2\n3\n1\n0\n2\n2\n3\n1\n0\n0\n3\nabc\n4\n"
r = subprocess.run([sys.executable, "colisiones.py"], input=entrada, text=True, encoding="utf-8", capture_output=True)
revisar("consola: colisiones.py termina sin errores", r.returncode == 0 and "Traceback" not in r.stderr)
revisar("consola: muestra v1 = 1.00 y v2 = 4.00", "v1 = 1.00" in r.stdout and "v2 = 4.00" in r.stdout)
revisar("consola: la inelastica pierde 3.00 J", "se perdieron 3.00 J" in r.stdout)
revisar("consola: guarda resultados.csv con 2 lineas", os.path.exists("resultados.csv") and len(open("resultados.csv", encoding="utf-8").readlines()) == 2)
limpiar_archivos()

#-------- servidor --------
entorno = dict(os.environ)
entorno["PUERTO"] = str(PUERTO)
entorno["NO_ABRIR"] = "1"
servidor = subprocess.Popen([sys.executable, "servidor.py"], env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    listo = esperar_servidor()
    revisar("el servidor arranca y responde", listo)
    if not listo:
        raise SystemExit(1)

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 900, "height": 900})
        page.on("console", lambda m: errores_consola.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda err: errores_consola.append(str(err)))
        page.on("dialog", lambda d: d.accept())
        page.on("request", lambda rq: llamadas_calcular.append(rq.url) if "/api/calcular" in rq.url else None)
        page.goto(URL)

        revisar("la pagina tiene el titulo y las 4 pestañas", "Colisiones" in page.title() and page.locator("nav button").count() == 4)

        #campo e: solo habilitado en inelastica
        page.select_option("#tipo", "elastica")
        revisar("e deshabilitado en elastica", page.is_disabled("#e"))
        page.select_option("#tipo", "inelastica")
        revisar("e habilitado en inelastica", page.is_enabled("#e"))
        revisar("ya no hay selector de motor (Python y Java trabajan juntos)", page.locator("#motor").count() == 0)
        page.select_option("#tipo", "elastica")

        borrar_historial(page)

        #-------- casos de notas.txt en Python y en Java --------
        casos = [
            ("elastica 2,3,1,0", "elastica", 2, 3, 1, 0, 0, (1.0, 4.0)),
            ("elastica masas iguales 1,5,1,0", "elastica", 1, 5, 1, 0, 0, (0.0, 5.0)),
            ("inelastica e=0 2,3,1,0", "inelastica", 2, 3, 1, 0, 0, (2.0, 2.0)),
        ]
        for nombre, tipo, m1, v1, m2, v2, e, esperado in casos:
            llenar(page, tipo, m1, v1, m2, v2, e)
            revisar(f"{nombre} da {esperado}", casi(finales(page), esperado))
            revisar(f"{nombre}: se conserva el momento", "SI se conservo" in page.inner_text("#conservaP"))
            py, ja = python_java(page)
            revisar(f"{nombre}: Java leyo el csv de Python y dio lo mismo", py is not None and ja is not None and casi(py, ja))
            revisar(f"{nombre}: la pagina dice que coinciden", "Coinciden Python y Java" in page.inner_text("#coinciden"))
            if nombre == "elastica 2,3,1,0":
                revisar("elastica conserva la energia", "SI se conservo" in page.inner_text("#conservaE"))
            if tipo == "inelastica":
                revisar("inelastica e=0: se pierden 3.00 J", "3.00 J" in page.inner_text("#conservaE"))
        page.screenshot(path="captura_simulador.png")

        llenar(page, "inelastica", 2, 3, 1, 0, 1)
        revisar("inelastica e=1 igual a elastica (1 y 4)", casi(finales(page), (1.0, 4.0)))
        llenar(page, "inelastica", 2, 3, 1, 0, 0.5)
        f = finales(page)
        revisar("inelastica e=0.5 conserva momento y pierde energia", f is not None and "SI se conservo" in page.inner_text("#conservaP") and "NO se conservo" in page.inner_text("#conservaE"))

        #-------- velocidades negativas y decimales --------
        llenar(page, "elastica", 2, -1, 3, -4)
        py, ja = python_java(page)
        revisar("velocidades negativas: conserva momento y Java coincide", "SI se conservo" in page.inner_text("#conservaP") and casi(py, ja))
        llenar(page, "elastica", 2.5, 3.5, 1.5, 0.5)
        py, ja = python_java(page)
        revisar("Java entiende decimales como 2.5 y coincide con Python", py is not None and ja is not None and casi(py, ja))
        llenar(page, "inelastica", 2.5, 3.5, 1.5, 0.5, 0.3)
        py, ja = python_java(page)
        revisar("inelastica con e=0.3 y decimales: Java coincide con Python", py is not None and ja is not None and casi(py, ja))

        #-------- errores de entrada (no deben llegar al servidor) --------
        antes = len(llamadas_calcular)
        llenar(page, "elastica", 0, 3, 1, 0)
        revisar("masa 0 muestra error y no hay resultado", "mayores a 0" in page.inner_text("#mensaje") and page.inner_text("#resultado") == "")
        llenar(page, "elastica", "", 3, 1, 0)
        revisar("campo vacio muestra error", "numeros" in page.inner_text("#mensaje"))
        llenar(page, "inelastica", 2, 3, 1, 0, 1.5)
        revisar("e fuera de rango muestra error", "entre 0 y 1" in page.inner_text("#mensaje"))
        llenar(page, "elastica", 2, 1, 1, 3)
        revisar("v1<=v2 avisa que no hay choque", "no hay choque" in page.inner_text("#mensaje"))
        revisar("errores y no-choque no llaman al servidor", len(llamadas_calcular) == antes)
        page.screenshot(path="captura_error.png")

        #el servidor tambien valida por su cuenta (probamos la API directo)
        for cuerpo, texto in [
            ({"tipo": "elastica", "m1": 0, "v1": 1, "m2": 1, "v2": 0}, "masa 0"),
            ({"tipo": "elastica", "m1": "a", "v1": 1, "m2": 1, "v2": 0}, "texto en vez de numero"),
            ({"tipo": "inelastica", "m1": 1, "v1": 1, "m2": 1, "v2": 0, "e": 2}, "e fuera de rango"),
            ({"tipo": "cobol", "m1": 1, "v1": 1, "m2": 1, "v2": 0}, "tipo desconocido"),
        ]:
            resp = page.request.post(URL + "/api/calcular", data=cuerpo)
            revisar(f"API rechaza con 400: {texto}", resp.status == 400 and "error" in resp.json())
        revisar("API: documento no permitido da 404", page.request.get(URL + "/api/documento/servidor.py").status == 404)

        #-------- animacion --------
        page.reload()
        llenar(page, "elastica", 2, 3, 1, 0)
        dibujo1 = page.evaluate("document.getElementById('lienzo').toDataURL()")
        page.wait_for_function("document.getElementById('mensaje').innerText.includes('Choque')", timeout=15000)
        dibujo2 = page.evaluate("document.getElementById('lienzo').toDataURL()")
        revisar("la animacion cambia el canvas y avisa el choque", dibujo1 != dibujo2)
        page.screenshot(path="captura_choque.png")

        #-------- historial y grafica --------
        borrar_historial(page)

        #grafica con historial vacio: mensaje y sin pedir la imagen
        page.click("#tabGrafica")
        page.wait_for_function("document.getElementById('mensajeGrafica').innerText != ''")
        revisar("grafica vacia muestra mensaje", "No hay colisiones" in page.inner_text("#mensajeGrafica"))
        revisar("grafica vacia no muestra la imagen", not page.is_visible("#imgGrafica"))
        page.screenshot(path="captura_grafica_vacia.png")
        page.click("#tabSimulador")

        llenar(page, "elastica", 2, 3, 1, 0)
        llenar(page, "inelastica", 1, 4, 2, -1, 0)
        llenar(page, "inelastica", 2, 3, 1, 0, 0.5)
        revisar("el historial cuenta 3 filas", filas_tabla(page, 3) == 3)
        revisar("el historial marca las filas como verificadas por Java", page.inner_text("#tabla").count("verificado") == 3)
        page.screenshot(path="captura_historial.png")

        page.click("#tabGrafica")
        page.wait_for_function("document.getElementById('imgGrafica').naturalWidth > 0", timeout=60000)
        revisar("la grafica carga (naturalWidth > 0)", page.is_visible("#imgGrafica"))
        page.screenshot(path="captura_grafica.png")

        page.click("#tabHistorial")
        page.click("#borrar")
        page.wait_for_function("document.getElementById('tabla').rows.length == 1")
        revisar("Borrar historial deja la tabla vacia", filas_tabla(page, 0) == 0)
        revisar("Borrar elimina resultados.csv y grafica.png", not os.path.exists("resultados.csv") and not os.path.exists("grafica.png"))

        #-------- informe --------
        page.click("#tabInforme")
        page.wait_for_function("document.getElementById('textoDoc').textContent != ''")
        revisar("informe muestra informe.txt", "INFORME" in page.inner_text("#textoDoc"))
        page.select_option("#doc", "notas.txt")
        page.wait_for_function("document.getElementById('textoDoc').textContent.includes('FORMULAS')")
        revisar("informe muestra notas.txt", True)
        page.select_option("#doc", "README.md")
        page.wait_for_function("document.getElementById('textoDoc').textContent.includes('MecanicaPJ')")
        revisar("informe muestra README.md", True)
        page.screenshot(path="captura_informe.png")

        #-------- celular --------
        movil = navegador.new_page(viewport={"width": 375, "height": 800})
        movil.on("console", lambda m: errores_consola.append(m.text) if m.type == "error" else None)
        movil.goto(URL)
        llenar(movil, "elastica", 2, 3, 1, 0)
        ancho_pagina = movil.evaluate("document.documentElement.scrollWidth")
        revisar("en celular no hay scroll horizontal", ancho_pagina <= 376)
        movil.screenshot(path="captura_celular.png", full_page=True)

        navegador.close()
finally:
    servidor.terminate()
    try:
        servidor.wait(timeout=10)
    except subprocess.TimeoutExpired:
        servidor.kill()
    limpiar_archivos()

revisar("sin errores en la consola del navegador", len(errores_consola) == 0)
if len(errores_consola) > 0:
    print(errores_consola)

print()
if fallos == 0:
    print("Todas las pruebas pasaron")
else:
    print(f"Fallaron {fallos} pruebas")
    sys.exit(1)
