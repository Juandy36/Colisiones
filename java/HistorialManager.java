import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class HistorialManager {
    private static final Path ARCHIVO = Path.of("../datos/historial.json");
    private static final Gson gson = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    public static synchronized void agregar(JsonObject registro) throws IOException {
        JsonArray historial = obtener();
        historial.add(registro);
        guardar(historial);
    }

    public static synchronized JsonArray obtener() throws IOException {
        if (!Files.exists(ARCHIVO)) {
            Files.createDirectories(ARCHIVO.getParent());
            guardar(new JsonArray());
        }

        String contenido = Files.readString(ARCHIVO, StandardCharsets.UTF_8);
        return JsonParser.parseString(contenido).getAsJsonArray();
    }

    public static synchronized void limpiar() throws IOException {
        guardar(new JsonArray());
    }

    private static void guardar(JsonArray historial) throws IOException {
        Files.createDirectories(ARCHIVO.getParent());
        Files.writeString(ARCHIVO, gson.toJson(historial), StandardCharsets.UTF_8);
    }
}
