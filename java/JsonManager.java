import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class JsonManager {
    private static final Gson gson = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    public static String convertirAJson(Colision colision) {
        return gson.toJson(colision);
    }

    public static void guardar(String json, String ruta) throws IOException {
        Path archivo = Path.of(ruta);
        Files.createDirectories(archivo.getParent());
        Files.writeString(archivo, json);

        System.out.println("Archivo JSON guardado correctamente.");
    }
}
