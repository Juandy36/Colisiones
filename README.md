# MecanicaPJ

Proyecto final de programación - Mecánica
Tema: colisiones elásticas e inelásticas y conservación del momento lineal.

Integrantes:
- Jefferson Steven Useche Duarte (líder)
- Vismar Andrés Méndez Romero
- Andrés Felipe Nichoy Calderón
- Juan Diego Ortiz Mora
- Paulo Cesar Claro

## Archivos
- `colisiones.py`: programa principal en Python (menú, clases, guarda `resultados.csv`)
- `grafica.py`: lee `resultados.csv` y grafica momento y energía (guarda `grafica.png`)
- `Main.java`: versión en Java, calcula una colisión y la agrega a `resultados.csv`
- `animacion.html`: simulación en el navegador (se abre con doble clic)
- `test_navegador.py`: prueba automática de la página con playwright
- `notas.txt`: fórmulas y casos de prueba
- `informe.txt`: resultados y conclusiones

## Cómo correrlo
Primero instalar lo necesario:
```
pip install -r requirements.txt
python -m playwright install chromium
```

Programa en Python (el principal):
```
python colisiones.py
python grafica.py
```

Programa en Java:
```
javac Main.java
java Main
```

Página en el navegador y su prueba:
```
python test_navegador.py
```

Ojo: `colisiones.py` crea `resultados.csv` desde cero cada vez que se sale del programa, y `Main.java` agrega una línea al final del archivo.
