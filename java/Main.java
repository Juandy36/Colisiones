import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

public class Main {

    public static void main(String[] args) {
        try {
            Colision colision = new Colision(
                "elastica",
                2.0,
                3.0,
                5.0,
                -2.0
            );

            String json = JsonManager.convertirAJson(colision);
            JsonManager.guardar(json, "../datos/colision.json");

            JsonObject resultados = ejecutarPython(json);

            System.out.println("Resultados de la colision:");
            System.out.println("Velocidad final 1: " + resultados.get("v1f").getAsDouble());
            System.out.println("Velocidad final 2: " + resultados.get("v2f").getAsDouble());
            System.out.println("Momento antes: " + resultados.get("momentoAntes").getAsDouble());
            System.out.println("Momento despues: " + resultados.get("momentoDespues").getAsDouble());
            System.out.println("Energia antes: " + resultados.get("energiaAntes").getAsDouble());
            System.out.println("Energia despues: " + resultados.get("energiaDespues").getAsDouble());
            System.out.println("Conserva momento: " + resultados.get("conservaMomento").getAsBoolean());
            System.out.println("Conserva energia: " + resultados.get("conservaEnergia").getAsBoolean());

        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }

    public static JsonObject ejecutarPython(String json) throws IOException, InterruptedException {

        ProcessBuilder proceso = new ProcessBuilder(
            "py",
            "../python/procesamiento.py"
        );

        proceso.redirectErrorStream(true);
        Process python = proceso.start();

        try (OutputStreamWriter entrada = new OutputStreamWriter(
                python.getOutputStream(), StandardCharsets.UTF_8)) {
            entrada.write(json);
        }

        StringBuilder respuesta = new StringBuilder();

        try (BufferedReader salida = new BufferedReader(
                new InputStreamReader(
                    python.getInputStream(), StandardCharsets.UTF_8))) {

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
