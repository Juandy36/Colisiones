#Trabajo en conjunto con Juan Diego Ortiz y Paulo Claro
#Prueba animacion.html en el navegador con playwright (pip install playwright)
#Uso: python test_navegador.py
import os
import re
import sys
import subprocess
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

    #-------- PRUEBA DE TODO JUNTO: Python -> Java -> grafica -> navegador --------
    print()
    print("Prueba completa: colisiones.py, Main.java, grafica.py y la pagina")
    if os.path.exists("resultados.csv"):
        os.remove("resultados.csv")

    #tipo, m1, v1, m2, v2, e  (los dos ultimos son para Java, e=0)
    casosPy=[("elastica",2,3,1,0,0),("inelastica",5,2,3,1,0.5),("inelastica",2,3,1,0,0),
             ("elastica",1,5,1,0,0),("inelastica",2,-5,3,1,0.2)]
    casosJava=[("elastica",2,3,1,0,0),("inelastica",1,4,2,-1,0)]

    entrada=""
    for c in casosPy:
        t,m1,v1,m2,v2,e=c
        if t=="elastica":
            entrada+=f"1\n{m1}\n{v1}\n{m2}\n{v2}\n"
        else:
            entrada+=f"2\n{m1}\n{v1}\n{m2}\n{v2}\n{e}\n"
    entrada+="3\n4\n"
    r=subprocess.run([sys.executable,"colisiones.py"],input=entrada,text=True,encoding="utf-8",capture_output=True)
    revisar("colisiones.py termina sin errores", r.returncode==0 and "Traceback" not in r.stderr)
    revisar("colisiones.py crea resultados.csv", os.path.exists("resultados.csv"))

    r=subprocess.run(["javac","Main.java"],capture_output=True,text=True)
    revisar("Main.java compila", r.returncode==0)
    for c in casosJava:
        t,m1,v1,m2,v2,e=c
        opcion="1" if t=="elastica" else "2"
        r=subprocess.run(["java","Main"],input=f"{opcion}\n{m1}\n{v1}\n{m2}\n{v2}\n",text=True,encoding="utf-8",capture_output=True)
        revisar(f"Main.java corre el caso {t} {m1},{v1},{m2},{v2}", r.returncode==0 and "SI se conservo" in r.stdout)

    with open("resultados.csv","r",encoding="utf-8") as archivo:
        filas=archivo.readlines()
    todos=casosPy+casosJava
    revisar("el csv tiene una linea por colision (Python + Java)", len(filas)==len(todos))

    #cada linea del csv (Python o Java) se compara con lo que calcula la pagina
    for i in range(len(filas)):
        partes=filas[i].strip().split(",")
        v1f=float(partes[5])
        v2f=float(partes[6])
        t,m1,v1,m2,v2,e=todos[i]
        llenar(page,t,m1,v1,m2,v2,e)
        numeros=re.findall(r"v[12] = (-?\d+\.\d+)", page.inner_text("#resultado"))
        igual=len(numeros)==2 and abs(float(numeros[0])-v1f)<0.01 and abs(float(numeros[1])-v2f)<0.01
        origen="Python" if i<len(casosPy) else "Java"
        revisar(f"{origen} y la pagina dan lo mismo: {t} {m1},{v1},{m2},{v2}", igual)

    entorno=dict(os.environ)
    entorno["MPLBACKEND"]="Agg"   #sin ventana, solo guarda el png
    r=subprocess.run([sys.executable,"grafica.py"],capture_output=True,text=True,encoding="utf-8",env=entorno)
    revisar("grafica.py termina sin errores", r.returncode==0 and "Traceback" not in r.stderr)
    revisar("grafica.py crea grafica.png", os.path.exists("grafica.png"))

    #abrimos la grafica en el navegador y revisamos que cargue la imagen
    pagina2=navegador.new_page()
    pagina2.goto("file:///"+os.path.abspath("grafica.png").replace("\\","/"))
    ancho=pagina2.evaluate("document.images.length > 0 ? document.images[0].naturalWidth : 0")
    revisar("grafica.png se ve en el navegador", ancho>0)
    pagina2.screenshot(path="captura_grafica.png")

    navegador.close()

#limpiamos lo que generaron las pruebas
for nombre in ["resultados.csv","grafica.png","Main.class"]:
    if os.path.exists(nombre):
        os.remove(nombre)

revisar("sin errores en la consola del navegador", len(errores_consola)==0)
if len(errores_consola) > 0:
    print(errores_consola)

print()
if fallos == 0:
    print("Todas las pruebas pasaron")
else:
    print(f"Fallaron {fallos} pruebas")
    exit(1)
