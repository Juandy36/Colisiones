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

            ejecutarPython(json);

        } catch (Exception e) {

            System.out.println("Error: " + e.getMessage());

        }
    }

    public static void ejecutarPython(String json) throws IOException, InterruptedException {

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

        try (BufferedReader salida = new BufferedReader(
                new InputStreamReader(
                    python.getInputStream(), StandardCharsets.UTF_8))) {

            String linea;

            while ((linea = salida.readLine()) != null) {
                System.out.println(linea);
            }
        }

        int resultado = python.waitFor();

        if (resultado == 0) {
            System.out.println("Comunicacion Java - Python exitosa.");
        } else {
            System.out.println("Python termino con un error. Codigo: " + resultado);
        }
    }
}
