import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpExchange;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class Servidor {
    private HttpServer servidor;

    public void iniciar() throws IOException {
        servidor = HttpServer.create(new InetSocketAddress(8080), 0);
        servidor.createContext("/", this::manejarSolicitud);
        servidor.start();

        System.out.println("Servidor iniciado en http://localhost:8080");
    }

    private void manejarSolicitud(HttpExchange intercambio) throws IOException {
        String ruta = intercambio.getRequestURI().getPath();
        String metodo = intercambio.getRequestMethod();

        if (ruta.equals("/") || ruta.equals("/index.html")) {
            if (!metodo.equals("GET")) {
                responder(intercambio, 405, "{\"error\":\"Metodo no permitido\"}");
                return;
            }

            Path archivo = Path.of("../web/index.html");

            if (!Files.exists(archivo)) {
                responder(intercambio, 404, "{\"error\":\"No se encontro index.html\"}");
                return;
            }

            byte[] contenido = Files.readAllBytes(archivo);

            intercambio.getResponseHeaders().set("Content-Type", "text/html; charset=UTF-8");
            intercambio.sendResponseHeaders(200, contenido.length);
            intercambio.getResponseBody().write(contenido);
            intercambio.close();

            return;
        }

        if (ruta.equals("/api/calcular")) {
            if (!metodo.equals("POST")) {
                responder(intercambio, 405, "{\"error\":\"Metodo no permitido\"}");
                return;
            }

            try {

                String cuerpo = new String(
                    intercambio.getRequestBody().readAllBytes(),
                    StandardCharsets.UTF_8
                );

                JsonObject datos = JsonParser.parseString(cuerpo).getAsJsonObject();

                String tipo = datos.get("tipo").getAsString();

                double masa1 = datos.get("m1").getAsDouble();
                double masa2 = datos.get("m2").getAsDouble();
                double velocidad1 = datos.get("v1").getAsDouble();
                double velocidad2 = datos.get("v2").getAsDouble();

                Colision colision = new Colision(
                    tipo,
                    masa1,
                    masa2,
                    velocidad1,
                    velocidad2
                );

                JsonObject resultados = Main.procesarColision(colision);

                responder(intercambio, 200, resultados.toString());

            } catch (IllegalArgumentException | IllegalStateException e) {

                responder(intercambio, 400,
                    "{\"error\":\"" + e.getMessage() + "\"}");

            } catch (Exception e) {

                responder(intercambio, 500,
                    "{\"error\":\"Error al procesar la colision\"}");

                e.printStackTrace();
            }

            return;
        }

        responder(intercambio, 404, "{\"error\":\"Ruta no encontrada\"}");
    }

    private void responder(HttpExchange intercambio, int estado, String respuesta)
            throws IOException {

        byte[] contenido = respuesta.getBytes(StandardCharsets.UTF_8);

        intercambio.getResponseHeaders().set(
            "Content-Type",
            "application/json; charset=UTF-8"
        );

        intercambio.sendResponseHeaders(estado, contenido.length);
        intercambio.getResponseBody().write(contenido);
        intercambio.close();
    }
}
