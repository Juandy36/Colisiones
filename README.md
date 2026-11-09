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
- `servidor.py`: servidor Flask que une los programas: Python calcula, Java verifica leyendo el csv de Python, y `grafica.py` grafica lo que dejó Java
- `index.html`: la página con pestañas (Simulador, Historial, Gráfica, Informe)
- `iniciar.bat`: instala lo que falta y abre la página con doble clic
- `test_navegador.py`: prueba automática con playwright: arranca el servidor, usa la página y compara Python con Java
- `notas.txt`: fórmulas y casos de prueba
- `informe.txt`: resultados y conclusiones

## Cómo correrlo
Lo más fácil: doble clic en `iniciar.bat` (instala lo que falta y abre la página en el navegador).

O desde la terminal:
```
pip install -r requirements.txt
python servidor.py
```
Se abre http://localhost:5050. Se puede cambiar el puerto con la variable `PUERTO` y evitar que abra el navegador con `NO_ABRIR=1`.
Cómo trabajan juntos: Python (`colisiones.py`) calcula la colisión y la guarda en `resultados.csv`; luego `java Main verificar` lee esa línea, la calcula por su cuenta, la compara y deja la línea con sus valores; por último `grafica.py` y el historial leen lo que dejó Java.
Para la parte de Java hace falta tener `java` y `javac` instalados (el servidor compila `Main.java` solo al arrancar; sin Java la página solo muestra lo de Python).

Los programas también se pueden usar por separado:
```
python colisiones.py
python grafica.py
javac Main.java
java Main
```

Prueba automática de la página (necesita `python -m playwright install chromium`):
```
python test_navegador.py
```

Ojo: `colisiones.py` crea `resultados.csv` desde cero cada vez que se sale del menú de consola, y `Main.java` y la página agregan líneas al final del archivo.
