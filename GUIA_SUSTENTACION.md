# Guía de sustentación – CollisionJP (MecanicaPJ)

Proyecto final de **Programación de Computadores**: simulador web de colisiones elásticas e inelásticas en 1D, hecho con **Java + Python + HTML/CSS/JavaScript**, comunicados con **JSON**.

> Los números de línea (`Servidor.java:18`, `index.html:314`, etc.) son los del código actual. Si editas un archivo pueden moverse unas líneas: busca con `Ctrl+F` el texto que se indica.
>
> Esta guía está enfocada en **programación** (arquitectura, flujo de datos, clases, funciones, librerías, errores). La física se resume en la sección 9, por si acaso, pero lo que se va a preguntar es el código.

---

## 0. Resumen en 30 segundos (para decirlo de entrada)

> "Hicimos un simulador de colisiones con interfaz web. **Java** es el servidor: usa `HttpServer` para atender la página, validar los datos, guardar el historial en JSON y coordinar todo. **Python** es el motor de procesamiento: Java lo ejecuta como un proceso externo, le pasa los datos en JSON por la entrada estándar y Python devuelve los resultados también en JSON. Python además genera la gráfica con matplotlib y el informe PDF con reportlab. La página en **HTML/CSS/JavaScript** envía los datos con `fetch`, anima los bloques en un `<canvas>` y muestra el historial en una tabla."

---

## 1. Mapa de archivos

| Archivo | Lenguaje | Qué hace | Líneas |
|---|---|---|---|
| `java/Main.java` | Java | Punto de entrada. Arranca el servidor y orquesta una colisión: JSON → Python → historial. | 75 |
| `java/Servidor.java` | Java | **Servidor HTTP** (`com.sun.net.httpserver`). Define las rutas y responde JSON, HTML, PNG y PDF. | 291 |
| `java/Colision.java` | Java | Clase `Colision`: guarda los datos de entrada y los **valida** en el constructor. | 50 |
| `java/JsonManager.java` | Java | Convierte un objeto `Colision` a JSON con Gson y lo guarda en `datos/colision.json`. | 24 |
| `java/HistorialManager.java` | Java | Lee, agrega y limpia el historial (`datos/historial.json`). | 42 |
| `java/lib/gson-2.15.0.jar` | librería | Gson, de Google, para manejar JSON en Java. | – |
| `python/procesamiento.py` | Python | **Motor de cálculo.** Lee JSON por stdin, calcula y devuelve JSON por stdout. | 91 |
| `python/grafica.py` | Python | Lee el historial y dibuja 2 gráficos de barras (momento y energía). Guarda `datos/grafica.png`. | 105 |
| `python/informe.py` | Python | Genera `datos/informe_colision.pdf` con reportlab (última simulación). | 125 |
| `web/index.html` | HTML+CSS+JS | **Interfaz:** formulario, animación en canvas, tabla de historial, botón de PDF. | 436 |
| `datos/` | carpeta | Se crea sola al simular. **Ignorada por git** (`.gitignore`). | – |
| `requirements.txt` | texto | Dependencias de Python (`matplotlib`, `numpy`, `reportlab`). Se instalan con `py -m pip install -r requirements.txt`. | 3 |
| `docs/informe.txt` | texto | Informe del proyecto (ver sección 8: está desactualizado). | 45 |
| `README.md` | texto | Descripción y cómo compilar/ejecutar. | 158 |

Archivos que genera el programa en `datos/`: `colision.json` (última entrada), `historial.json` (todas las simulaciones), `grafica.png`, `informe_colision.pdf`.

---

## 2. Arquitectura y flujo completo

```
NAVEGADOR (index.html)          JAVA (Servidor.java + Main.java)             PYTHON (procesamiento.py)
──────────────────────          ────────────────────────────────             ─────────────────────────
1. Usuario llena el form
   y pulsa "Simular"
2. JS valida (números,
   masas>0, v1>v2)
3. fetch POST /api/calcular ──► 4. manejarSolicitud() lee el cuerpo
   {tipo,m1,v1,m2,v2}              y lo parsea con JsonParser
                                5. new Colision(...)  → valida
                                6. Main.procesarColision():
                                   · JsonManager.convertirAJson
                                   · guarda datos/colision.json
                                   · ejecutarPython(json):
                                     ProcessBuilder("py", ...)
                                     escribe el JSON en stdin ────────────► 7. json.load(sys.stdin)
                                                                            8. calcular_colision()
                                                                            9. print(json.dumps(resultados))
                                10. Java lee stdout, lo parsea  ◄───────────
                                11. Arma el "registro" (fecha +
                                    parametros + resultados)
                                12. HistorialManager.agregar()
                                    → datos/historial.json
13. JS recibe resultados  ◄───── 14. responder(200, resultados)
15. animar(...) en el canvas
```

Otras rutas:

| Ruta | Método | Qué pasa |
|---|---|---|
| `/` y `/index.html` | GET | Java lee `../web/index.html` y lo envía. |
| `/api/calcular` | POST | Flujo de arriba. |
| `/api/historial` | GET | Java lee `historial.json` y manda al navegador una lista "plana" para la tabla. |
| `/api/limpiar` | POST | Java reemplaza el historial por un arreglo vacío. |
| `/grafica.png` | GET | Java ejecuta `python/grafica.py` y devuelve `datos/grafica.png`. |
| `/informe.pdf` | GET | Java ejecuta `python/informe.py` y devuelve `datos/informe_colision.pdf` como descarga. |
| cualquier otra | – | 404 `{"error":"Ruta no encontrada"}`. |

**Idea clave para defender:** *Java no calcula la física; Java es el servidor y el coordinador. Python hace el cálculo, la gráfica y el PDF.* Java y Python se hablan con **JSON por entrada/salida estándar**, no comparten memoria.

**¿Por qué dos lenguajes?** El proyecto pedía usar ambos: Java es fuerte para servidores y manejo de clases/validación; Python tiene las librerías de gráficas (matplotlib) y PDF (reportlab).

---

## 3. Explicación archivo por archivo

### 3.1 `Main.java`

| Líneas | Qué hace |
|---|---|
| 13-20 | `main`: crea un `Servidor` y llama `iniciar()`. Si no puede abrir el puerto captura `IOException` e imprime el error. |
| 22-41 | **`procesarColision(Colision)`** — orquesta todo: (1) convierte a JSON, (2) guarda `colision.json`, (3) llama a Python, (4) crea el registro con fecha, (5) lo agrega al historial, (6) devuelve los resultados. |
| 31-32 | La fecha se formatea con `LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss"))`. |
| 35 | `JsonParser.parseString(json).getAsJsonObject()` vuelve a convertir el texto JSON en un objeto Gson para meterlo dentro del registro. |
| 43-74 | **`ejecutarPython(json)`** — lanza Python y se comunica con él (explicado abajo). |

**`ejecutarPython` paso a paso:**
1. `new ProcessBuilder("py", "../python/procesamiento.py")` prepara el comando (`py` es el lanzador de Python en Windows).
2. `redirectErrorStream(true)` junta stderr con stdout, así si Python falla el mensaje llega por el mismo canal.
3. `proceso.start()` ejecuta el proceso.
4. Con un `try-with-resources` se abre un `OutputStreamWriter` hacia `python.getOutputStream()` (la **entrada** de Python) y se escribe el JSON. Al cerrarse el `try`, Python recibe el "fin de entrada".
5. Se lee `python.getInputStream()` línea por línea con `BufferedReader` y se acumula en un `StringBuilder`.
6. `waitFor()` espera a que Python termine y devuelve el código de salida. Si es distinto de 0 → `throw new IOException("Python termino con un error: ...")`.
7. Si todo bien, `JsonParser.parseString(...)` convierte la respuesta en `JsonObject`.

> Usa `StandardCharsets.UTF_8` en todos lados para que las tildes y caracteres no se dañen entre Java y Python.

### 3.2 `Servidor.java`

| Líneas | Qué hace |
|---|---|
| 15-23 | `iniciar()`: `HttpServer.create(new InetSocketAddress(8080), 0)` abre el **puerto 8080**; `createContext("/", this::manejarSolicitud)` manda **todas** las peticiones a un único método; `start()` lo enciende. |
| 25-27 | `manejarSolicitud`: obtiene la **ruta** (`getRequestURI().getPath()`) y el **método** HTTP (`getRequestMethod()`). Luego es una cadena de `if` por ruta. |
| 29-50 | `/` → sirve `../web/index.html` con `Files.readAllBytes`. Si no existe → 404. |
| 52-98 | `/api/calcular` (ver abajo). |
| 100-143 | `/api/historial`: recorre el JSON del historial con un `for` y arma, por cada registro, un objeto plano (`tipo, m1, v1, m2, v2, v1f, ...`). |
| 145-162 | `/api/limpiar`: `HistorialManager.limpiar()`. |
| 164-214 | `/grafica.png`: ejecuta `grafica.py`, espera, y si salió bien devuelve el PNG con `Content-Type: image/png`. |
| 216-273 | `/informe.pdf`: igual, con `Content-Type: application/pdf` y `Content-Disposition: attachment` (fuerza la descarga). |
| 275 | Si ninguna ruta coincide → 404. |
| 278-290 | **`responder(intercambio, estado, texto)`**: método auxiliar que evita repetir código. Fija `Content-Type: application/json`, manda el código HTTP con `sendResponseHeaders`, escribe el cuerpo y cierra. |

**`/api/calcular` (líneas 52-98):**
1. Si el método no es POST → 405 "Metodo no permitido".
2. Lee el cuerpo: `new String(getRequestBody().readAllBytes(), UTF_8)`.
3. `JsonParser.parseString(cuerpo).getAsJsonObject()` y extrae `tipo`, `m1`, `m2`, `v1`, `v2`.
4. Crea `new Colision(...)`. **Aquí se validan los datos** (el constructor lanza excepción si algo está mal).
5. `Main.procesarColision(colision)` → resultados.
6. `responder(200, resultados.toString())`.
7. Manejo de errores:
   - `IllegalArgumentException | IllegalStateException` → **400** con el mensaje (dato inválido del usuario).
   - cualquier otra `Exception` → **500** "Error al procesar la colision" y `e.printStackTrace()`.

**Códigos HTTP usados:** 200 (ok), 400 (datos inválidos), 404 (no existe), 405 (método no permitido), 500 (error interno).

**Importante:** el navegador manda `m1, v1, m2, v2` pero la clase `Colision` usa `masa1, velocidad1, ...`. Gson serializa con los **nombres de los campos de la clase**, así que Python recibe `masa1, velocidad1...`, y al armar el historial (línea 119-123) Java traduce de vuelta a `m1, v1...` para la tabla.

### 3.3 `Colision.java` (clase `Colision`)

Es una **clase modelo** (POJO): campos `private`, constructor y *getters*.

- **Constructor (líneas 8-29)** valida: tipo ∈ {"elastica","inelastica"}; masas > 0; todos los valores finitos (`Double.isFinite`, rechaza NaN e infinito). Si algo falla lanza `IllegalArgumentException`. Solo si todo está bien asigna los campos con `this.`
- **Encapsulamiento:** los campos son `private` y se leen con `getTipo()`, `getMasa1()`, etc.
- Gson no necesita los getters: lee los campos por **reflexión**.

### 3.4 `JsonManager.java`

- `convertirAJson(Colision)` (línea 13): `gson.toJson(colision)`. El `Gson` está creado con `GsonBuilder().setPrettyPrinting()` → JSON con sangría (legible).
- `guardar(json, ruta)` (línea 17): `Files.createDirectories` crea `datos/` si no existe y `Files.writeString` escribe el archivo.
- Todos los métodos son `static`: no hace falta crear un objeto `JsonManager`.

### 3.5 `HistorialManager.java`

- `ARCHIVO = Path.of("../datos/historial.json")` — **constante** (`static final`).
- `agregar(registro)`: lee el arreglo actual, le añade el registro y lo guarda completo.
- `obtener()`: si el archivo no existe, crea la carpeta y un arreglo vacío `[]`; luego lo lee y lo devuelve como `JsonArray`.
- `limpiar()`: guarda un arreglo vacío.
- **`synchronized`** en los métodos públicos: solo un hilo a la vez puede leer/escribir el historial, para que dos peticiones no se pisen el archivo.

**Formato de un registro en `historial.json`:**
```json
{
  "fecha": "11/11/2026 10:30:00",
  "parametros": { "tipo": "elastica", "masa1": 2.0, "masa2": 1.0, "velocidad1": 3.0, "velocidad2": 0.0 },
  "resultados": { "tipo": "elastica", "v1f": 1.0, "v2f": 4.0, "momentoAntes": 6.0, "momentoDespues": 6.0,
                  "energiaAntes": 9.0, "energiaDespues": 9.0, "conservaMomento": true, "conservaEnergia": true }
}
```

### 3.6 `procesamiento.py`

| Líneas | Qué hace |
|---|---|
| 5-10 | `calcular_colision(datos)`: lee el diccionario y convierte a `float`. |
| 12-24 | **Segunda validación** (tipo, masas > 0, valores finitos con `math.isfinite`) y además `velocidad1 <= velocidad2` → "Los cuerpos no se estan acercando". |
| 28-43 | Fórmulas: si es elástica, v1f y v2f distintas; si no, ambas iguales (quedan pegados). |
| 45-56 | Momento y energía antes y después. |
| 58-64 | `math.isclose(...)` compara con tolerancia (los `float` tienen error de redondeo, no se comparan con `==`). |
| 66-76 | Diccionario `resultados` con todo lo que se devuelve. |
| 80-88 | `recibir_datos()`: `json.load(sys.stdin)` → calcula → `print(json.dumps(resultados))`. Si hay error (`ValueError, KeyError, TypeError`) imprime `{"error": ...}` y termina con `sys.exit(1)`. |
| 90-91 | `if __name__ == "__main__":` → solo ejecuta `recibir_datos()` cuando se corre directo (no al importarlo). |

**Se puede probar sola, sin Java:**
```
echo {"tipo":"elastica","masa1":2,"masa2":1,"velocidad1":3,"velocidad2":0} | py python/procesamiento.py
```

### 3.7 `grafica.py`

| Líneas | Qué hace |
|---|---|
| 6-7 | `matplotlib.use("Agg")` → dibuja **sin abrir ventana** (necesario porque corre dentro del servidor). |
| 12-14 | Rutas con `pathlib`: `Path(__file__).resolve().parent.parent` = carpeta raíz del proyecto, así no depende de desde dónde se ejecute. |
| 16-25 | Lee `historial.json`; si no existe o está vacío lanza error. |
| 33-44 | Recorre el historial con `enumerate` y llena listas: nombres (`"1. Elastica"`), momento y energía antes/después. |
| 46-47 | `np.arange(len(nombres))` posiciones de las barras; `ancho = 0.35`. |
| 49 | `plt.subplots(1, 2, figsize=(12, 5))` → 1 fila, 2 gráficos lado a lado. |
| 51-70 | Gráfico izquierdo: barras de **momento** (Antes / Despues) con título, etiquetas, leyenda y cuadrícula. |
| 72-91 | Gráfico derecho: barras de **energía**. |
| 96-97 | `savefig(..., dpi=150)` guarda el PNG y `plt.close(figura)` libera memoria. |
| 99-105 | Si algo falla: escribe el mensaje a **stderr** y `sys.exit(1)` → Java lo detecta por el código de salida ≠ 0. |

### 3.8 `informe.py`

Usa **reportlab** (`canvas.Canvas`) para dibujar el PDF línea por línea con `drawString(x, y, texto)` y baja la posición `y` en cada línea. Secciones: encabezado, 1. Parámetros, 2. Resultados, 3. Análisis de conservación, 4. Gráfica (inserta `grafica.png` con `drawImage`). Toma solo `historial[-1]` (la **última** simulación).

> Este archivo tenía un error de indentación que impedía generar el PDF; ya está arreglado (ver sección 8, punto 1).

### 3.9 `index.html` (la interfaz)

Tiene 3 partes: **CSS** (líneas 8-191), **HTML** (194-240) y **JavaScript** (242-434).

**HTML:**
- `<nav>` (200-204): 3 botones de pestaña (Simulador, Historial, Grafica).
- `#panelSimulador` (206-222): `select#tipo`, inputs `m1 v1 m2 v2`, botón `#simular`, `<p id="mensaje">`, `<canvas id="lienzo">` de 720×150.
- `#panelHistorial` (224-230): `<table id="tabla">` y botón `#borrar`.
- `#panelGrafica` (232-238): botón `#generarPDF` y `<p id="mensajePDF">`.

**JavaScript – funciones y eventos:**

| Qué | Línea | Qué hace |
|---|---|---|
| `$(id)` | 247 | Atajo de `document.getElementById`. |
| `abrir(nombre)` | 251 | Cambia de pestaña: recorre el arreglo `pestanas` y pone clase `activa`/`visible` solo a la elegida. Si es Historial, llama `cargarHistorial()`. |
| bucle de `onclick` | 260-264 | Asigna a cada botón de pestaña su evento. Usa una **función autoejecutable (closure)** `(function(n){...})(pestanas[i])` para que cada botón "recuerde" su propio `n`. |
| `ancho(m)` | 266 | Ancho del bloque según la masa: `24 + m·10`, máximo 100. |
| `dibujar(x1,x2,m1,m2)` | 272 | Limpia el canvas y dibuja suelo, bloque azul, bloque rojo y etiquetas. |
| `fmt(n)` | 286 | `n.toFixed(2)`: dos decimales. |
| `animar(...)` | 288 | Animación con `setInterval` cada **20 ms**. Primero los bloques avanzan con v1 y v2; al tocarse (`choco = true`) siguen con v1f y v2f. Termina tras 200 pasos o al salir del canvas (`clearInterval`). |
| `$("simular").onclick` | 317 | Valida → `fetch` POST → muestra mensaje → `animar`. |
| `cargarHistorial()` | 367 | `fetch` GET `/api/historial`, arma el HTML de la tabla en un string con un `for` y lo asigna a `innerHTML`. |
| `$("borrar").onclick` | 379 | `confirm(...)` y POST a `/api/limpiar`, luego recarga la tabla. |
| `$("generarPDF").onclick` | 385 | Encadena promesas: primero `fetch("/grafica.png")`, luego `fetch("/informe.pdf")`, convierte a `blob`, crea un enlace `<a download>` temporal, lo "clickea" y libera la URL. Los errores se capturan con `.catch`. |

**El `fetch` de simular (líneas 342-363):**
```js
var datos = { tipo: tipo, m1: m1, v1: v1, m2: m2, v2: v2 };
fetch("/api/calcular", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(datos) })
  .then(resp => resp.json())      // convierte la respuesta a objeto
  .then(r => { if (r.error) {...} else { animar(...) } })
  .catch(() => "No se pudo hablar con el servidor.");
```
Mientras espera, el botón queda `disabled` para evitar dobles clics.

**Validaciones del navegador (328-340):** números válidos (`isNaN`), masas > 0 y `v1 > v2` (si no, no hay choque).

**Idea de diseño:** el bloque 1 (azul) empieza a la izquierda y el 2 (rojo) a la derecha; por eso se exige `v1 > v2`.

---

## 4. Conceptos de programación que usamos (para explicar con tus palabras)

| Concepto | Dónde se ve |
|---|---|
| **Cliente-servidor / HTTP** | El navegador pide, `Servidor.java` responde. |
| **API REST (endpoints)** | `/api/calcular`, `/api/historial`, `/api/limpiar`. |
| **JSON** | Formato de texto para intercambiar datos entre navegador↔Java y Java↔Python. |
| **Programación orientada a objetos** | Clase `Colision` (atributos privados, constructor, getters). |
| **Clases utilitarias estáticas** | `JsonManager`, `HistorialManager` (métodos `static`, sin crear objetos). |
| **Excepciones (try/catch, throw)** | `IllegalArgumentException` en `Colision`; `IOException` si Python falla; `ValueError` en Python. |
| **Procesos externos** | `ProcessBuilder` en Java lanza `py`. |
| **Entrada/salida estándar** | Java escribe en stdin de Python y lee su stdout. |
| **Archivos** | `Files.readString/writeString/readAllBytes`, `Path.of`. |
| **Concurrencia básica** | `synchronized` en `HistorialManager`. |
| **Validación en capas** | Navegador → `Colision` (Java) → `procesamiento.py`. |
| **Separación de responsabilidades** | Cada archivo hace una sola cosa. |
| **Asincronía en JS** | `fetch` + promesas (`.then/.catch`), `setInterval`. |
| **DOM** | `getElementById`, `innerText`, `innerHTML`, `className`. |
| **Canvas 2D** | `fillRect`, `fillText`, `clearRect`. |
| **Librerías** | Gson (Java); matplotlib, numpy, reportlab (Python). |

---

## 5. Preguntas probables del profesor (con respuesta corta)

**Arquitectura**
1. **¿Por qué usaron Java y Python juntos?** Java para el servidor y la validación orientada a objetos; Python para cálculo, gráficas (matplotlib) y PDF (reportlab).
2. **¿Cómo se comunican Java y Python?** Java ejecuta Python con `ProcessBuilder`, le manda un JSON por la entrada estándar y lee la respuesta JSON por la salida estándar. Si Python termina con código distinto de 0, Java lanza un error.
3. **¿Qué es un endpoint?** Una URL que el servidor atiende con una función. Ej.: `/api/calcular`.
4. **¿Qué es JSON y por qué lo usaron?** Texto estructurado `{"clave": valor}` que entienden JavaScript, Java y Python: es el "idioma común".
5. **¿Qué es Gson?** Librería de Google para convertir objetos Java ↔ JSON.
6. **¿Qué es `HttpServer`?** Clase incluida en el JDK (módulo `jdk.httpserver`) para crear un servidor web sin frameworks. Por eso se compila con `--add-modules jdk.httpserver`.
7. **¿Qué es `fetch`?** Función de JavaScript para hacer peticiones HTTP sin recargar la página.
8. **¿Dónde se guardan los datos?** En archivos JSON dentro de `datos/` (sin base de datos). El historial está en `historial.json`.
9. **¿Qué pasa si borras `datos/`?** `HistorialManager.obtener()` y `JsonManager.guardar()` la vuelven a crear. Solo se pierde el historial.
10. **¿Por qué el puerto 8080?** Es el puerto típico para servidores de desarrollo. Está en `Servidor.java:18`.

**Java**
11. **¿Por qué se valida en `Colision` y también en Python?** Defensa en capas: el navegador da respuesta rápida, Java protege al servidor y Python protege el cálculo si se ejecutara solo. Nunca se debe confiar en lo que llega del cliente.
12. **¿Qué hace `private` y por qué getters?** Encapsulamiento: los datos solo se cambian a través del constructor, que valida.
13. **¿Para qué sirve `synchronized`?** Evita que dos hilos modifiquen `historial.json` al mismo tiempo.
14. **¿Qué hace `try-with-resources`?** Cierra automáticamente el recurso (el `OutputStreamWriter`/`BufferedReader`) al terminar el bloque, aunque haya error. Cerrar la entrada además le avisa a Python que ya no hay más datos.
15. **¿Por qué `redirectErrorStream(true)`?** Para leer en un solo flujo la salida normal y los errores de Python.
16. **¿Qué es `static`?** El método pertenece a la clase, no a un objeto: se llama `JsonManager.guardar(...)` sin hacer `new`.
17. **¿Qué diferencia hay entre `IllegalArgumentException` e `IOException`?** La primera es dato inválido (devolvemos 400); la segunda es un fallo del sistema, como Python o archivos (devolvemos 500).
18. **¿Qué es `this::manejarSolicitud`?** Referencia a método: le dice al servidor "cuando llegue una petición, ejecuta este método".
19. **¿Se atienden varias peticiones a la vez?** Con la configuración por defecto de `HttpServer` (sin ejecutor propio) se atienden una por una. Para un proyecto de clase es suficiente.

**Python**
20. **¿Qué hace `if __name__ == "__main__"`?** Ejecuta el código solo si el archivo se corre directamente y no cuando se importa.
21. **¿Por qué `sys.exit(1)`?** Para indicarle a Java que hubo un error (código de salida ≠ 0).
22. **¿Qué hace `matplotlib.use("Agg")`?** Genera la imagen sin abrir ventana, necesario en un servidor.
23. **¿Por qué `Path(__file__).resolve().parent.parent`?** Para obtener la carpeta del proyecto sin importar desde dónde se ejecute el script.
24. **¿Por qué `math.isclose` en vez de `==`?** Los decimales (`float`/`double`) tienen error de redondeo.

**JavaScript / interfaz**
25. **¿Cómo funciona la animación?** `setInterval` ejecuta una función cada 20 ms: suma `velocidad × escala` a la posición de cada bloque y redibuja el canvas. Al detectar solapamiento cambia a las velocidades finales.
26. **¿La animación es a escala real?** No, es ilustrativa; el tamaño del bloque depende de la masa solo de forma visual.
27. **¿Qué es el `closure` del bucle de pestañas?** Una función que "recuerda" el valor de `n`; sin ella todos los botones abrirían la última pestaña.
28. **¿Cómo se descarga el PDF?** Se pide al servidor, se convierte a `blob`, se crea una URL temporal con `URL.createObjectURL` y se simula un clic en un `<a download>`.
29. **¿Por qué se deshabilita el botón al simular?** Para evitar peticiones duplicadas mientras responde el servidor.
30. **¿Por qué se muestra el mensaje en verde/rojo?** Se cambia `style.color` según sea éxito o error (línea 357).

---

## 6. Cambios cortos que podrían pedirte (con dónde tocar)

### 6.1 Colores (`index.html`)

| Qué | Dónde | Valor actual |
|---|---|---|
| Fondo de la página | línea 16 (`body`) | `#eef2f7` |
| Encabezado | línea 21 (`header`) | `#1e3a5f` |
| Botón de pestaña normal | línea 55 (`nav button`) | `#cbd5e1` |
| Pestaña activa | línea 61 (`nav button.activa`) | `#1e3a5f` |
| Botón "Simular" / "Descargar PDF" | línea 115 (`button.grande`) | `#2563eb` |
| Botón "Borrar historial" | línea 123 (`button.rojo`) | `#dc2626` |
| Mensaje de error | línea 127 (`#mensaje`) | `#b91c1c` |
| Mensaje de éxito | línea 357 (JS) | `#15803d` |
| Fondo del canvas | línea 138 | `#f8fafc` |
| Cabecera de la tabla | línea 161 (`th`) | `#e2e8f0` |
| **Bloque 1** | línea 276 (`ctx.fillStyle`) | `#2563eb` azul |
| **Bloque 2** | línea 278 | `#ef4444` rojo |
| Suelo del canvas | línea 274 | `#94a3b8` |
| Texto "m1"/"m2" | línea 280 | `white` |

Para cambiar todo el esquema azul: `Ctrl+F` de `#1e3a5f` y `#2563eb` y reemplazar. Se pueden usar nombres (`red`, `green`) o hex.

### 6.2 Textos (`index.html`)

| Qué | Dónde |
|---|---|
| Título de la pestaña del navegador | línea 7 (`<title>`) |
| Título grande | línea 196 (`<h1>`) |
| Subtítulo con integrantes | línea 197 |
| Nombres de las pestañas | líneas 201-203 (los `id` **no** se cambian: el JS los usa) |
| Etiquetas del formulario | líneas 208-217 |
| Mensajes de error del navegador | líneas 329, 333, 337 |
| Mensaje de éxito | línea 358 |
| Mensajes de error del servidor | `Servidor.java` (los `responder(...)`) y `Colision` líneas 12, 16, 21 |
| Texto del PDF | `informe.py` líneas 34-101 |

### 6.3 Valores por defecto del formulario
`index.html:214-217` → atributos `value="2"`, `"3"`, `"1"`, `"0"` (m1, v1, m2, v2). El dibujo inicial usa m1=2, m2=1 en la línea 365.

### 6.4 Animación (`index.html`)

| Qué | Dónde |
|---|---|
| Velocidad (ms entre cuadros) | línea 314 → `}, 20);` |
| Escala de velocidad | línea 291 → `var escala = 0.8;` |
| Tamaño del bloque según masa | líneas 267-268 → `24 + m * 10`, tope `100` |
| Posición y tamaño de los bloques | líneas 277-279 (`58` = y, `60` = alto) |
| Posición inicial del bloque 1 | línea 289 → `var x1 = 40;` |
| Duración tras el choque | línea 310 → `pasos > 200` |
| Tamaño del canvas | línea 221 → `width="720" height="150"` |

### 6.5 Decimales mostrados
`index.html:286` → `toFixed(2)`. Cambia el `2`. (Solo la web; el PDF usa `:.2f` en `informe.py:70-80`.)

### 6.6 Gráfica (`grafica.py`)

| Qué | Dónde |
|---|---|
| Tamaño de la figura | línea 49 → `figsize=(12, 5)` |
| Ancho de las barras | línea 47 → `ancho = 0.35` |
| Colores de las barras | líneas 51-63 y 72-84: agregar `color="green"` dentro de `ejes[0].bar(...)` |
| Títulos de cada gráfico | líneas 65 y 86 |
| Título general | línea 93 |
| Etiquetas del eje Y | líneas 66 y 87 |
| Cuadrícula | líneas 70 y 91 (`grid`) |
| Inclinación del eje X | `rotation=45` en líneas 68 y 89 |
| Calidad de la imagen | línea 96 → `dpi=150` |
| Nombre del archivo | línea 14 (si lo cambias, cámbialo también en `informe.py:14` y `Servidor.java:192`) |

### 6.7 Configuración

| Qué | Dónde |
|---|---|
| **Puerto** | `Servidor.java:18` (`8080`) **y** el mensaje de la línea 22. Cámbialo en ambos. |
| Ruta del historial | `HistorialManager.java:13` |
| Formato de la fecha | `Main.java:32` |
| Comando de Python (`py`) | `Main.java:46`, `Servidor.java:173` y `:225`. En Linux/Mac sería `python3`. |
| Tolerancia de conservación | `procesamiento.py:58-64` (`rel_tol`, `abs_tol`) |

### 6.8 Cambios de funcionalidad "cortos" (cómo hacerlos)

**a) "Agregar una nueva ruta/endpoint"** → en `Servidor.manejarSolicitud` copia el patrón de `/api/limpiar` (líneas 145-162): `if (ruta.equals("/api/nueva"))`, verifica método, haz la lógica y llama `responder(...)`.

**b) "Agregar un campo nuevo a la colisión (ej. nombre)"** → 4 sitios: input en `index.html` y su lectura en el `onclick` (línea 322-342); campo + parámetro + getter en `Colision`; lectura en `Servidor.java` (líneas 66-78); y si se usa en el cálculo, `procesamiento.py:6-10`.

**c) "Agregar una columna a la tabla del historial"** → `index.html:369` (encabezado `<th>`) y `:372` (celda `<td>`); si el dato no viaja aún, agregarlo en el `for` de `Servidor.java:117-130`.

**d) "Agregar un tipo de colisión nuevo"** → `<option>` en `index.html:209-212`; permitir el valor en `Colision.java:11` y `procesamiento.py:12`; y la rama en `procesamiento.py:28-43`.

**e) "Agregar otra pestaña"** → (1) botón en `<nav>`, (2) `<section id="panelNombre">`, (3) añadir `"Nombre"` al arreglo `pestanas` (línea 249). `abrir()` la maneja sola si los ids siguen el patrón `tabNombre` / `panelNombre`.

**f) "Mostrar la gráfica en la página"** → agregar `<img id="imgGrafica">` en `#panelGrafica` (el CSS ya existe en la línea 168) y en `abrir()` poner `$("imgGrafica").src = "/grafica.png?t=" + Date.now();` (el `?t=` evita la caché).

**g) "Que el historial muestre la fecha"** → el dato ya está en `historial.json` (`fecha`); falta agregarlo en el `for` de `Servidor.java:117-130` (`fila.add("fecha", registro.get("fecha"))`) y como columna en `index.html:369-372`.

**h) "Limitar a N registros del historial"** → en `HistorialManager.agregar`, después de `historial.add(...)`, borrar el primero con `historial.remove(0)` si `historial.size() > N`.

**i) "Cambiar las unidades"** → solo etiquetas (`index.html:214-217`, `informe.py`, `grafica.py:66,87`).

### 6.9 Probar piezas por separado

- **Python solo:** `echo {"tipo":"elastica","masa1":2,"masa2":1,"velocidad1":3,"velocidad2":0} | py python/procesamiento.py`
- **API con curl** (servidor encendido):
  `curl -X POST localhost:8080/api/calcular -d "{\"tipo\":\"elastica\",\"m1\":2,\"v1\":3,\"m2\":1,\"v2\":0}"`
- **Historial:** abre `http://localhost:8080/api/historial` en el navegador.

---

## 7. Demostración sugerida (3-5 min)

**Antes de sustentar verifica:** `java -version`, `javac -version`, `py --version`, que estén instaladas las librerías (`py -m pip install -r requirements.txt`), y que **nada más use el puerto 8080**.

1. **Compilar** (desde la carpeta `java`):
   ```powershell
   javac --add-modules jdk.httpserver -cp ".;lib/gson-2.15.0.jar" Main.java Colision.java JsonManager.java HistorialManager.java Servidor.java
   ```
2. **Ejecutar** (misma carpeta):
   ```powershell
   java --add-modules jdk.httpserver -cp ".;lib/gson-2.15.0.jar" Main
   ```
   Debe decir `Servidor iniciado en http://localhost:8080`. **Hay que ejecutarlo desde `java/`** porque las rutas son relativas (`../web`, `../datos`, `../python`).
3. Abre `http://localhost:8080`.
4. **Simulador:** elástica m1=2, v1=3, m2=1, v2=0 → se anima el choque. Una inelástica con los mismos datos.
5. **Historial:** aparecen las dos filas con sus resultados.
6. Muestra `datos/historial.json` y `datos/colision.json`: explica quién los escribe.
7. **Gráfica:** abre `http://localhost:8080/grafica.png` para mostrar el PNG generado con matplotlib.
8. Pestaña **Grafica** → botón **Descargar informe PDF**: descarga el informe de la última simulación con su gráfica.
9. Si piden ver el flujo en vivo: la consola de Java imprime "Archivo JSON guardado correctamente." en cada simulación.

---

## 8. Cosas flojas del proyecto (conócelas antes de que las encuentren)

1. **✅ Arreglado – `informe.py` no generaba el PDF.** Las últimas líneas (título "4. Grafica", `drawImage`, `showPage`, `save`) habían quedado **fuera de la función `generar_informe()`** por la sangría, y Python fallaba con `NameError: name 'pdf' is not defined`. Además `showPage()` y `save()` estaban después de un `raise` y nunca se ejecutaban. Se metió el bloque dentro de la función y se cambió el `if/else` por una validación previa (`if not archivo_grafica.exists(): raise ...`). Si preguntan: *"en Python la sangría define qué está dentro de una función; una sangría mal puesta saca el código de la función y las variables locales dejan de existir."*
2. **✅ Arreglado – el archivo se llamaba `colision.java` en minúscula.** Java exige que una clase `public` esté en un archivo con su mismo nombre exacto (`Colision.java`); con el comando del README daba `class Colision is public, should be declared in a file named Colision.java`. Se renombró el archivo y se actualizó el README.
3. **Rutas relativas (`../web`, `../python`, `../datos`):** el servidor solo funciona si se ejecuta **desde la carpeta `java/`**. Desde otra carpeta no encuentra nada.
4. **Se usa `py` (lanzador de Windows):** en Linux/Mac habría que cambiarlo por `python3` (3 lugares, ver 6.7).
5. **Si v1 ≤ v2 y se llama a la API directamente**, Python rechaza el caso ("Los cuerpos no se estan acercando") y Java responde un **500 genérico** en vez de un 400 con el mensaje. En la página no se nota porque el navegador valida antes.
6. **Mensajes de error con comillas:** en `Servidor.java:86-87` el JSON de error se arma concatenando texto; si el mensaje tuviera comillas rompería el JSON. Con los mensajes actuales no pasa.
7. **Código sobrante en `index.html`:** `cargarDoc()` y `$("doc").onchange` (líneas 428-433) y el CSS `#textoDoc` (175-185) son de una pestaña "Informe" que ya no existe. `$("doc")` es `null`, así que aparece un error en la consola (F12) al cargar; la página funciona igual porque es la última instrucción. Se pueden borrar.
8. **Nombre del proyecto inconsistente:** README dice "CollisionJP", `informe.py` dice "Collision Arena", el árbol del README dice `CollisionArena/` y `index.html` dice "Colisiones en una dimension".
9. **`docs/informe.txt` está desactualizado:** habla de Flask, `servidor.py`, `Main.java` con Scanner y `resultados.csv`, que ya no existen.
10. **El historial se lee/escribe completo en cada petición** (`HistorialManager.agregar`). Con pocos registros no importa.
11. **Cada simulación inicia un proceso Python nuevo** (tarda cientos de milisegundos). Aceptable para un proyecto de clase.
12. **Sin pruebas automáticas:** se probó a mano con casos calculados (ver sección 9).
13. **Se guarda `datos/colision.json` pero nadie lo lee:** solo es un archivo de depuración de la última entrada.

Si te preguntan por limitaciones, puedes decir con confianza: *"es 1D, solo dos cuerpos, sin fricción, solo colisiones elásticas y perfectamente inelásticas, y la animación es ilustrativa, no a escala real."*

---

## 9. La física, en lo mínimo (por si acaso)

- **Momento:** `p = m·v`. **Energía cinética:** `Ec = ½·m·v²`.
- **Elástica:** se conservan momento **y** energía. Fórmulas (`procesamiento.py:28-35`):
  `v1f = ((m1−m2)·v1 + 2·m2·v2)/(m1+m2)` y `v2f = (2·m1·v1 + (m2−m1)·v2)/(m1+m2)`.
- **Perfectamente inelástica:** quedan pegados, misma velocidad final `(m1·v1 + m2·v2)/(m1+m2)`. Se conserva el momento, se pierde energía.
- **Caso de prueba para la demo:** m1=2, v1=3, m2=1, v2=0.

| Tipo | v1f | v2f | Momento | Energía |
|---|---|---|---|---|
| Elástica | 1.0 | 4.0 | 6 → 6 ✅ | 9 → 9 ✅ |
| Inelástica | 2.0 | 2.0 | 6 → 6 ✅ | 9 → 6 ❌ |

Estos valores los verifiqué ejecutando el proyecto. Si preguntan algo más de física, la respuesta honesta es que el foco del proyecto es la programación y que las fórmulas son las estándar de colisiones en 1D.

---

## 10. Chuleta rápida (lo más importante)

- **Java = servidor y coordinador** (`Servidor.java`, `Main.java`). **Python = cálculo, gráfica y PDF.** **HTML/JS = interfaz.**
- Java ↔ Python: `ProcessBuilder` + JSON por stdin/stdout (`Main.java:43-74`).
- Navegador ↔ Java: `fetch` + JSON sobre HTTP, puerto **8080** (`Servidor.java:18`).
- Validación en 3 capas: navegador (`index.html:328-340`), `Colision` (`Colision.java:11-22`), Python (`procesamiento.py:12-24`).
- Datos en `datos/`: `historial.json`, `colision.json`, `grafica.png`, `informe_colision.pdf` (carpeta ignorada por git).
- Errores HTTP: 400 dato inválido, 404 no existe, 405 método incorrecto, 500 error interno.
- Compilar y ejecutar **desde `java/`** con `--add-modules jdk.httpserver` y `lib/gson-2.15.0.jar`.
- Colores de bloques: `index.html:276` y `278`. Velocidad de animación: `index.html:314`. Decimales: `index.html:286`.
- Errores que ya arreglamos: `informe.py` (el final estaba fuera de la función) y `colision.java` → `Colision.java`.
