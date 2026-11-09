import java.util.Scanner;
import java.io.FileWriter;
import java.io.IOException;
// Proyecto final Mecanica - Colisiones (version en Java)
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.println("Colisiones en una dimension");
        System.out.println("1. Elastica");
        System.out.println("2. Perfectamente inelastica");
        int opcion = sc.nextInt();

        System.out.println("Masa 1 (kg): ");
        double m1 = sc.nextDouble();
        System.out.println("Velocidad 1 (m/s): ");
        double v1 = sc.nextDouble();
        System.out.println("Masa 2 (kg): ");
        double m2 = sc.nextDouble();
        System.out.println("Velocidad 2 (m/s): ");
        double v2 = sc.nextDouble();

        double v1f = 0;
        double v2f = 0;
        String tipo = "";

        switch (opcion) {
            case 1:
                tipo = "Elastica";
                v1f = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2);
                v2f = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2);
                break;
            case 2:
                tipo = "Inelastica";
                v1f = (m1 * v1 + m2 * v2) / (m1 + m2);
                v2f = v1f;
                break;
            default:
                System.out.println("Opcion invalida.");
                return;
        }

        double pAntes = m1 * v1 + m2 * v2;
        double pDespues = m1 * v1f + m2 * v2f;
        double eAntes = 0.5 * m1 * v1 * v1 + 0.5 * m2 * v2 * v2;
        double eDespues = 0.5 * m1 * v1f * v1f + 0.5 * m2 * v2f * v2f;

        System.out.println("\nTipo: " + tipo);
        System.out.println("Velocidades finales: v1 = " + v1f + " | v2 = " + v2f);
        System.out.println("Momento antes: " + pAntes + " | despues: " + pDespues);
        System.out.println("Energia antes: " + eAntes + " | despues: " + eDespues);

        if (Math.abs(pAntes - pDespues) < 0.0001) {
            System.out.println("El momento SI se conservo");
        } else {
            System.out.println("El momento NO se conservo");
        }

        // Guardamos en el mismo formato que colisiones.py: tipo,m1,v1,m2,v2,v1f,v2f
        try {
            FileWriter fw = new FileWriter("resultados.csv", true);
            fw.write(tipo + "," + m1 + "," + v1 + "," + m2 + "," + v2 + "," + v1f + "," + v2f + "\n");
            fw.close();
            System.out.println("Se guardo en resultados.csv");
        } catch (IOException e) {
            System.out.println("No se pudo guardar el archivo");
        }
    }
}
