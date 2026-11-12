import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class Main {
    public static void main(String[] args) {
        try {
            Servidor servidor = new Servidor();
            servidor.iniciar();
        } catch (IOException e) {
            System.out.println("Error al iniciar el servidor: " + e.getMessage());
        }
    }

    public static JsonObject procesarColision(Colision colision)
            throws IOException, InterruptedException {

        String json = JsonManager.convertirAJson(colision);

        JsonManager.guardar(json, "../datos/colision.json");
        JsonObject resultados = ejecutarPython(json);
        JsonObject registro = new JsonObject();

        String fecha = LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss"));

        registro.addProperty("fecha", fecha);
        registro.add("parametros", JsonParser.parseString(json).getAsJsonObject());
        registro.add("resultados", resultados);

        HistorialManager.agregar(registro);

        return resultados;
    }

    public static JsonObject ejecutarPython(String json)
            throws IOException, InterruptedException {

        ProcessBuilder proceso = new ProcessBuilder("py", "../python/procesamiento.py");

        proceso.redirectErrorStream(true);
        Process python = proceso.start();

        try (OutputStreamWriter entrada = new OutputStreamWriter(python.getOutputStream(), StandardCharsets.UTF_8)) {
            entrada.write(json);
        }

        StringBuilder respuesta = new StringBuilder();

        try (BufferedReader salida = new BufferedReader(
                new InputStreamReader(python.getInputStream(), StandardCharsets.UTF_8))) {

            String linea;

            while ((linea = salida.readLine()) != null) {
                respuesta.append(linea);
            }
        }

        int resultado = python.waitFor();

        if (resultado != 0) {
            throw new IOException("Python termino con un error: " + respuesta);
        }

        return JsonParser.parseString(respuesta.toString()).getAsJsonObject();
    }
}
