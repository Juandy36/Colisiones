#Trabajo en conjunto con Juan Diego Ortiz y Paulo Claro
#Prueba animacion.html en el navegador con playwright (pip install playwright)
#Uso: python test_navegador.py
import os
from playwright.sync_api import sync_playwright

ruta="file:///"+os.path.abspath("animacion.html").replace("\\","/")
errores_consola=[]
fallos=0

def revisar(nombre, condicion):
    global fallos
    if condicion:
        print(f"OK     {nombre}")
    else:
        print(f"FALLO  {nombre}")
        fallos+=1

def llenar(page, tipo, m1, v1, m2, v2, e):
    page.select_option("#tipo", tipo)
    page.fill("#m1", str(m1))
    page.fill("#v1", str(v1))
    page.fill("#m2", str(m2))
    page.fill("#v2", str(v2))
    page.fill("#e", str(e))
    page.click("#simular")

with sync_playwright() as p:
    navegador=p.chromium.launch()
    page=navegador.new_page()
    page.on("console", lambda m: errores_consola.append(m.text) if m.type=="error" else None)
    page.on("pageerror", lambda err: errores_consola.append(str(err)))
    page.goto(ruta)

    #caso 1 de notas.txt: elastica m1=2 v1=3 m2=1 v2=0 -> v1f=1 v2f=4
    llenar(page,"elastica",2,3,1,0,0)
    texto=page.inner_text("#resultado")
    revisar("elastica: v1=1.00 y v2=4.00", "v1 = 1.00" in texto and "v2 = 4.00" in texto)
    revisar("elastica: se conserva el momento", "SI se conservo" in page.inner_text("#conservaP"))
    revisar("elastica: se conserva la energia", "SI se conservo" in page.inner_text("#conservaE"))

    #la animacion debe mover los bloques y mostrar el choque
    antes=page.evaluate("document.getElementById('lienzo').toDataURL()")
    page.wait_for_function("document.getElementById('mensaje').innerText.includes('Choque')", timeout=15000)
    revisar("elastica: aparece el mensaje de choque", True)
    despues=page.evaluate("document.getElementById('lienzo').toDataURL()")
    revisar("la animacion cambia el dibujo del canvas", antes!=despues)

    #caso 3 de notas.txt: inelastica e=0 -> v1f=v2f=2, se pierden 3 J
    llenar(page,"inelastica",2,3,1,0,0)
    texto=page.inner_text("#resultado")
    revisar("inelastica e=0: v1=2.00 y v2=2.00", "v1 = 2.00" in texto and "v2 = 2.00" in texto)
    revisar("inelastica e=0: energia NO se conserva", "NO se conservo" in page.inner_text("#conservaE"))
    revisar("inelastica e=0: se pierden 3.00 J", "3.00 J" in page.inner_text("#conservaE"))
    revisar("inelastica e=0: momento si se conserva", "SI se conservo" in page.inner_text("#conservaP"))

    #caso 4: inelastica e=1 igual a elastica
    llenar(page,"inelastica",2,3,1,0,1)
    texto=page.inner_text("#resultado")
    revisar("inelastica e=1: igual que elastica", "v1 = 1.00" in texto and "v2 = 4.00" in texto)

    #caso 2: masas iguales intercambian velocidades
    llenar(page,"elastica",1,5,1,0,0)
    texto=page.inner_text("#resultado")
    revisar("masas iguales: v1=0.00 y v2=5.00", "v1 = 0.00" in texto and "v2 = 5.00" in texto)

    #velocidades negativas: se conserva el momento
    llenar(page,"inelastica",2,-5,3,1,0.5)
    revisar("velocidades negativas: momento se conserva", "SI se conservo" in page.inner_text("#conservaP"))

    #errores de entrada
    llenar(page,"elastica",0,3,1,0,0)
    revisar("masa 0 muestra error", "mayores a 0" in page.inner_text("#mensaje"))
    revisar("masa 0 no muestra resultado", page.inner_text("#resultado")=="")

    llenar(page,"elastica","",3,1,0,0)
    revisar("campo vacio muestra error", "numeros" in page.inner_text("#mensaje"))

    llenar(page,"inelastica",2,3,1,0,1.5)
    revisar("e fuera de rango muestra error", "entre 0 y 1" in page.inner_text("#mensaje"))

    llenar(page,"elastica",2,1,1,3,0)
    revisar("v1<=v2: avisa que no hay choque", "no hay choque" in page.inner_text("#mensaje"))

    #si simulan dos veces seguidas no debe romperse nada
    llenar(page,"elastica",2,3,1,0,0)
    llenar(page,"elastica",2,3,1,0,0)
    revisar("doble simulacion seguida funciona", "v1 = 1.00" in page.inner_text("#resultado"))

    page.screenshot(path="captura_animacion.png")
    navegador.close()

revisar("sin errores en la consola del navegador", len(errores_consola)==0)
if len(errores_consola) > 0:
    print(errores_consola)

print()
if fallos == 0:
    print("Todas las pruebas pasaron")
else:
    print(f"Fallaron {fallos} pruebas")
    exit(1)
