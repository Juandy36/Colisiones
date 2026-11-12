import json
import sys
import math

def calcular_colision(datos):
    tipo = datos["tipo"]
    masa1 = float(datos["masa1"])
    masa2 = float(datos["masa2"])
    velocidad1 = float(datos["velocidad1"])
    velocidad2 = float(datos["velocidad2"])

    if tipo not in ["elastica", "inelastica"]:
        raise ValueError("Tipo de colision no valido.")

    if masa1 <= 0 or masa2 <= 0:
        raise ValueError("Las masas deben ser mayores que cero.")

    valores = [masa1, masa2, velocidad1, velocidad2]

    if not all(math.isfinite(valor) for valor in valores):
        raise ValueError("Todos los valores deben ser numeros validos.")

    if velocidad1 <= velocidad2:
        raise ValueError("Los cuerpos no se estan acercando.")

    suma_masas = masa1 + masa2

    if tipo == "elastica":
        velocidad1f = (
            (masa1 - masa2) * velocidad1 + 2 * masa2 * velocidad2
        ) / suma_masas

        velocidad2f = (
            2 * masa1 * velocidad1 + (masa2 - masa1) * velocidad2
        ) / suma_masas

    else:
        velocidad_final = (
            masa1 * velocidad1 + masa2 * velocidad2
        ) / suma_masas

        velocidad1f = velocidad_final
        velocidad2f = velocidad_final

    momento_antes = masa1 * velocidad1 + masa2 * velocidad2
    momento_despues = masa1 * velocidad1f + masa2 * velocidad2f

    energia_antes = (
        0.5 * masa1 * velocidad1 ** 2
        + 0.5 * masa2 * velocidad2 ** 2
    )

    energia_despues = (
        0.5 * masa1 * velocidad1f ** 2
        + 0.5 * masa2 * velocidad2f ** 2
    )

    conserva_momento = math.isclose(
        momento_antes, momento_despues, rel_tol=1e-9, abs_tol=1e-9
    )

    conserva_energia = math.isclose(
        energia_antes, energia_despues, rel_tol=1e-9, abs_tol=1e-9
    )

    resultados = {
        "tipo": tipo,
        "v1f": velocidad1f,
        "v2f": velocidad2f,
        "momentoAntes": momento_antes,
        "momentoDespues": momento_despues,
        "energiaAntes": energia_antes,
        "energiaDespues": energia_despues,
        "conservaMomento": conserva_momento,
        "conservaEnergia": conserva_energia
    }

    return resultados

def recibir_datos():
    try:
        datos = json.load(sys.stdin)
        resultados = calcular_colision(datos)
        print(json.dumps(resultados))

    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)

if __name__ == "__main__":
    recibir_datos()
