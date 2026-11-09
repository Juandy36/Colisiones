#Proyecto final Mecanica - Colisiones y conservacion del momento lineal
#Jefferson Useche, Vismar Mendez, Andres Nichoy, Juan Diego Ortiz, Paulo Claro

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
        print(f"Momento antes:   {self.momento_antes():.2f} kg*m/s")
        print(f"Momento despues: {self.momento_despues():.2f} kg*m/s")
        print(f"Energia antes:   {self.energia_antes():.2f} J")
        print(f"Energia despues: {self.energia_despues():.2f} J")

        #comparamos con una tolerancia pequeña por los decimales
        if abs(self.momento_antes()-self.momento_despues()) < 0.0001:
            print("El momento SI se conservo")
        else:
            print("El momento NO se conservo (hay un error)")

        if abs(self.energia_antes()-self.energia_despues()) < 0.0001:
            print("La energia cinetica SI se conservo")
        else:
            perdida = self.energia_antes()-self.energia_despues()
            print(f"La energia cinetica NO se conservo, se perdieron {perdida:.2f} J")

#CLASES DE COLISIONES (SUBCLASES)############
class Elastica(Colision):
    def __init__(self, m1, v1, m2, v2):
        super().__init__(m1, v1, m2, v2)
        self.tipo="Elastica"
        self.calcular()

    def calcular(self):
        self.v1f = ((self.m1-self.m2)*self.v1 + 2*self.m2*self.v2)/(self.m1+self.m2)
        self.v2f = ((self.m2-self.m1)*self.v2 + 2*self.m1*self.v1)/(self.m1+self.m2)

class Inelastica(Colision):
    def __init__(self, m1, v1, m2, v2, e):
        super().__init__(m1, v1, m2, v2)
        self.tipo="Inelastica"
        self.e=e   #coeficiente de restitucion, e=0 es perfectamente inelastica
        self.calcular()

    def calcular(self):
        p = self.m1*self.v1 + self.m2*self.v2
        self.v1f = (p + self.m2*self.e*(self.v2-self.v1))/(self.m1+self.m2)
        self.v2f = (p + self.m1*self.e*(self.v1-self.v2))/(self.m1+self.m2)

#FUNCIONES############
def pedir_datos():
    m1=float(input("Masa 1 (kg): "))
    while m1 <= 0:
        m1=float(input("La masa debe ser mayor a 0, intente de nuevo: "))
    v1=float(input("Velocidad inicial 1 (m/s): "))
    m2=float(input("Masa 2 (kg): "))
    while m2 <= 0:
        m2=float(input("La masa debe ser mayor a 0, intente de nuevo: "))
    v2=float(input("Velocidad inicial 2 (m/s): "))
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

    opcion=int(input("\nSeleccione una opcion (1-4): "))

    if opcion == 1:
        m1,v1,m2,v2=pedir_datos()
        c=Elastica(m1,v1,m2,v2)
        c.mostrar()
        historial.append(c)

    elif opcion == 2:
        m1,v1,m2,v2=pedir_datos()
        e=float(input("Coeficiente de restitucion e (0 = se quedan pegados, 1 = elastica): "))
        while e < 0 or e > 1:
            e=float(input("e debe estar entre 0 y 1, intente de nuevo: "))
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
