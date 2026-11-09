#Proyecto final Mecanica - Colisiones y conservacion del momento lineal
#Trabajo en conjunto con Jefferson Useche, Vismar Mendez, Andres Nichoy, Juan Diego Ortiz y Paulo Claro

#CLASE COLISION (SUPERCLASE)###############
class Colision:
    def __init__(self, m1, v1, m2, v2):
        self.m1=m1
        self.v1=v1
        self.m2=m2
        self.v2=v2
        self.v1f=0
        self.v2f=0
        self.tipo="Colision"

    def momento_antes(self):
        return self.m1*self.v1 + self.m2*self.v2

    def momento_despues(self):
        return self.m1*self.v1f + self.m2*self.v2f

    def energia_antes(self):
        return 0.5*self.m1*self.v1**2 + 0.5*self.m2*self.v2**2

    def energia_despues(self):
        return 0.5*self.m1*self.v1f**2 + 0.5*self.m2*self.v2f**2

    def mostrar(self):
        print("-"*50)
        print(f"Tipo de colision: {self.tipo}")
        print(f"Antes:   v1 = {self.v1:.2f} m/s   v2 = {self.v2:.2f} m/s")
        print(f"Despues: v1 = {self.v1f:.2f} m/s   v2 = {self.v2f:.2f} m/s")

        pA=self.momento_antes()
        pD=self.momento_despues()
        eA=self.energia_antes()
        eD=self.energia_despues()

        print(f"Momento antes:   {pA:.2f} kg*m/s")
        print(f"Momento despues: {pD:.2f} kg*m/s")
        print(f"Energia antes:   {eA:.2f} J")
        print(f"Energia despues: {eD:.2f} J")

        #comparamos con una tolerancia porque los decimales no son exactos
        if abs(pA-pD) < 0.0001:
            print("El momento SI se conservo")
        else:
            print("El momento NO se conservo (hay un error)")

        if abs(eA-eD) < 0.0001:
            print("La energia cinetica SI se conservo")
        else:
            print(f"La energia cinetica NO se conservo, se perdieron {eA-eD:.2f} J")

#CLASES DE COLISIONES (SUBCLASES)############
class Elastica(Colision):
    def __init__(self, m1, v1, m2, v2):
        super().__init__(m1, v1, m2, v2)
        self.tipo="Elastica"
        self.calcular()

    def calcular(self):
        self.v1f=((self.m1-self.m2)*self.v1 + 2*self.m2*self.v2)/(self.m1+self.m2)
        self.v2f=((self.m2-self.m1)*self.v2 + 2*self.m1*self.v1)/(self.m1+self.m2)

class Inelastica(Colision):
    def __init__(self, m1, v1, m2, v2, e):
        super().__init__(m1, v1, m2, v2)
        self.tipo="Inelastica"
        self.e=e   #coeficiente de restitucion, e=0 es perfectamente inelastica
        self.calcular()

    def calcular(self):
        p=self.m1*self.v1 + self.m2*self.v2
        self.v1f=(p + self.m2*self.e*(self.v2-self.v1))/(self.m1+self.m2)
        self.v2f=(p + self.m1*self.e*(self.v1-self.v2))/(self.m1+self.m2)

#FUNCIONES############
def pedir_numero(texto):
    #sigue preguntando hasta que escriban un numero, si ponen letras no se cae
    while True:
        try:
            return float(input(texto))
        except ValueError:
            print("Eso no es un numero, escriba bien ese dato (ejemplo: 2.5)")

def pedir_datos():
    m1=pedir_numero("Masa 1 (kg): ")
    while m1 <= 0:
        m1=pedir_numero("La masa tiene que ser mayor a 0, intente de nuevo: ")
    v1=pedir_numero("Velocidad inicial 1 (m/s): ")
    m2=pedir_numero("Masa 2 (kg): ")
    while m2 <= 0:
        m2=pedir_numero("La masa tiene que ser mayor a 0, intente de nuevo: ")
    v2=pedir_numero("Velocidad inicial 2 (m/s): ")
    return m1,v1,m2,v2

def guardar_archivo(historial):
    #una colision por linea: tipo,m1,v1,m2,v2,v1f,v2f
    with open("resultados.csv", "w", encoding="utf-8") as archivo:
        for c in historial:
            archivo.write(f"{c.tipo},{c.m1},{c.v1},{c.m2},{c.v2},{c.v1f},{c.v2f}\n")

#PROGRAMA PRINCIPAL#####################
historial=[]
opcion=0

while opcion != 4:
    print()
    print("="*50)
    print("COLISIONES EN UNA DIMENSION")
    print("="*50)
    print("1. Colision elastica")
    print("2. Colision inelastica")
    print("3. Ver historial")
    print("4. Salir")

    try:
        opcion=int(input("\nSeleccione una opcion (1-4): "))
    except ValueError:
        opcion=0   #cae en el else de abajo (opcion invalida)

    if opcion == 1:
        m1,v1,m2,v2=pedir_datos()
        c=Elastica(m1,v1,m2,v2)
        c.mostrar()
        historial.append(c)

    elif opcion == 2:
        m1,v1,m2,v2=pedir_datos()
        e=pedir_numero("Coeficiente de restitucion e (0 = se quedan pegados, 1 = elastica): ")
        while e < 0 or e > 1:
            e=pedir_numero("e tiene que estar entre 0 y 1, escriba bien ese dato: ")
        c=Inelastica(m1,v1,m2,v2,e)
        c.mostrar()
        historial.append(c)

    elif opcion == 3:
        if len(historial) == 0:
            print("\nAun no hay colisiones en el historial.")
        else:
            for i in range(len(historial)):
                c=historial[i]
                print(f"{i+1}. {c.tipo}: m1={c.m1} v1={c.v1} | m2={c.m2} v2={c.v2} -> v1f={c.v1f:.2f} v2f={c.v2f:.2f}")

    elif opcion == 4:
        guardar_archivo(historial)
        print("\nSe guardo resultados.csv. Saliendo del programa")

    else:
        print("\nOpcion invalida. Debe ingresar un numero entre 1 y 4.")
