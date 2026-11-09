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
- `grafica.py`: lee `resultados.csv` y grafica momento y energía (guarda `grafica.png`)
- `Main.java`: programa en Java que calcula una colisión (elástica o inelástica) y la agrega a `resultados.csv`
- `servidor.py`: servidor Flask de la página: manda los datos a `Main.java` (Java es el que calcula) y usa `grafica.py` (Python) para la gráfica
- `index.html`: la página con pestañas (Simulador, Historial, Gráfica, Informe)
- `notas.txt`: fórmulas y casos de prueba
- `informe.txt`: resultados y conclusiones

## Cómo correrlo
Desde la terminal:
```
pip install -r requirements.txt
python servidor.py
```
Se abre http://localhost:5050. Se puede cambiar el puerto con la variable `PUERTO` y evitar que abra el navegador con `NO_ABRIR=1`.
Cómo trabajan juntos: la página manda los datos a `Main.java`, que calcula la colisión y la agrega a `resultados.csv`; luego `grafica.py` (Python) lee ese archivo y genera la gráfica.
Hace falta tener `java` y `javac` instalados (el servidor compila `Main.java` solo al arrancar; sin Java la página no puede calcular).

Los programas también se pueden usar por separado:
```
python grafica.py
javac Main.java
java Main
```

Ojo: `Main.java` (también cuando lo usa la página) agrega una línea al final de `resultados.csv` en cada colisión.
