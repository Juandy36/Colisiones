#Lee resultados.csv (hecho por colisiones.py o por Main.java) y grafica
import matplotlib.pyplot as plt

nombres=[]
p_antes=[]
p_despues=[]
e_antes=[]
e_despues=[]

with open("resultados.csv", "r", encoding="utf-8") as archivo:
    lineas=archivo.readlines()
    for L in lineas:
        partes=L.strip().split(",")
        if len(partes) < 7:
            continue
        tipo=partes[0]
        m1=float(partes[1])
        v1=float(partes[2])
        m2=float(partes[3])
        v2=float(partes[4])
        v1f=float(partes[5])
        v2f=float(partes[6])

        nombres.append(f"{len(nombres)+1}. {tipo}")
        p_antes.append(m1*v1 + m2*v2)
        p_despues.append(m1*v1f + m2*v2f)
        e_antes.append(0.5*m1*v1**2 + 0.5*m2*v2**2)
        e_despues.append(0.5*m1*v1f**2 + 0.5*m2*v2f**2)

if len(nombres) == 0:
    print("No hay colisiones en resultados.csv, corre primero colisiones.py")
else:
    x=list(range(len(nombres)))
    ancho=0.35

    plt.figure(figsize=(10,4))

    #grafica de momento
    plt.subplot(1,2,1)
    plt.bar([i-ancho/2 for i in x], p_antes, ancho, label="Antes")
    plt.bar([i+ancho/2 for i in x], p_despues, ancho, label="Despues")
    plt.xticks(x, nombres)
    plt.ylabel("Momento (kg*m/s)")
    plt.title("Momento lineal")
    plt.legend()

    #grafica de energia
    plt.subplot(1,2,2)
    plt.bar([i-ancho/2 for i in x], e_antes, ancho, label="Antes")
    plt.bar([i+ancho/2 for i in x], e_despues, ancho, label="Despues")
    plt.xticks(x, nombres)
    plt.ylabel("Energia cinetica (J)")
    plt.title("Energia cinetica")
    plt.legend()

    plt.tight_layout()
    plt.show()
