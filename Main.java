import java.util.Scanner;
import java.util.Locale;
import java.util.InputMismatchException;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.BufferedReader;
import java.util.ArrayList;
import java.io.IOException;
// Proyecto final Mecanica - Colisiones (version en Java)
// Trabajo en conjunto con Andres Nichoy, Juan Diego Ortiz y Paulo Claro
public class Main {
    // Modo verificar: java Main verificar [e]
    // Lee la ultima colision que dejo colisiones.py en resultados.csv, la calcula por su cuenta,
    // la compara con lo de Python y deja esa linea con los valores de Java (y la palabra Java al final)
    static void verificar(String[] args) {
        double e = 0;
        if (args.length > 1) {
            e = Double.parseDouble(args[1]);
        }
        ArrayList<String> lineas = new ArrayList<String>();
        try {
            BufferedReader br = new BufferedReader(new FileReader("resultados.csv"));
            String linea = br.readLine();
            while (linea != null) {
                if (linea.trim().length() > 0) {
                    lineas.add(linea);
                }
                linea = br.readLine();
            }
            br.close();
        } catch (IOException ex) {
            System.out.println("Error: no se pudo leer resultados.csv");
            return;
        }
        if (lineas.size() == 0) {
            System.out.println("Error: resultados.csv esta vacio");
            return;
        }
        String[] p = lineas.get(lineas.size() - 1).split(",");
        if (p.length < 7) {
            System.out.println("Error: la ultima linea no tiene el formato esperado");
            return;
        }
        String tipo = p[0];
        double m1 = Double.parseDouble(p[1]);
        double v1 = Double.parseDouble(p[2]);
        double m2 = Double.parseDouble(p[3]);
        double v2 = Double.parseDouble(p[4]);
        double v1Py = Double.parseDouble(p[5]);
        double v2Py = Double.parseDouble(p[6]);

        double v1f = 0;
        double v2f = 0;
        if (tipo.equals("Elastica")) {
            v1f = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2);
            v2f = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2);
        } else {
            double pTotal = m1 * v1 + m2 * v2;
            v1f = (pTotal + m2 * e * (v2 - v1)) / (m1 + m2);
            v2f = (pTotal + m1 * e * (v1 - v2)) / (m1 + m2);
        }

        System.out.println("Java leyo de resultados.csv: " + tipo + " m1=" + m1 + " v1=" + v1 + " m2=" + m2 + " v2=" + v2);
        System.out.println("Python calculo: v1 = " + v1Py + " | v2 = " + v2Py);
        System.out.println("Java calculo: v1 = " + v1f + " | v2 = " + v2f);
        if (Math.abs(v1f - v1Py) < 0.0001 && Math.abs(v2f - v2Py) < 0.0001) {
            System.out.println("Coinciden: SI");
        } else {
            System.out.println("Coinciden: NO");
        }

        // dejamos la linea con los valores de Java para que grafica.py y la pagina usen lo de Java
        lineas.set(lineas.size() - 1, tipo + "," + m1 + "," + v1 + "," + m2 + "," + v2 + "," + v1f + "," + v2f + ",Java");
        try {
            FileWriter fw = new FileWriter("resultados.csv", false);
            for (int i = 0; i < lineas.size(); i++) {
                fw.write(lineas.get(i) + "\n");
            }
            fw.close();
        } catch (IOException ex) {
            System.out.println("Error: no se pudo guardar resultados.csv");
        }
    }

    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("verificar")) {
            verificar(args);
            return;
        }
        Scanner sc = new Scanner(System.in);
        sc.useLocale(Locale.US);   // en Windows en español Scanner pedia coma decimal y fallaba con 2.5

        System.out.println("==================================================");
        System.out.println("Colisiones en una dimension");
        System.out.println("1. Elastica");
        System.out.println("2. Perfectamente inelastica");
        int opcion = 0;
        try {
            opcion = sc.nextInt();
        } catch (InputMismatchException ex) {
            System.out.println("Opcion invalida.");
            return;
        }

        double m1 = 0;
        double v1 = 0;
        double m2 = 0;
        double v2 = 0;

        try {
            while (m1 <= 0) {
                System.out.println("Masa 1 (kg), debe ser mayor a 0: ");
                m1 = sc.nextDouble();
            }
            System.out.println("Velocidad 1 (m/s): ");
            v1 = sc.nextDouble();
            while (m2 <= 0) {
                System.out.println("Masa 2 (kg), debe ser mayor a 0: ");
                m2 = sc.nextDouble();
            }
            System.out.println("Velocidad 2 (m/s): ");
            v2 = sc.nextDouble();
        } catch (InputMismatchException ex) {
            System.out.println("Error: tenia que escribir un numero.");
            return;
        }

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

        System.out.println("\n--------------Resultados--------------");
        System.out.println("Tipo: " + tipo);
        System.out.println("Velocidades finales: v1 = " + v1f + " | v2 = " + v2f);
        System.out.println("Momento antes: " + pAntes + " | despues: " + pDespues);
        System.out.println("Energia antes: " + eAntes + " | despues: " + eDespues);

        if (Math.abs(pAntes - pDespues) < 0.0001) {
            System.out.println("El momento SI se conservo");
        } else {
            System.out.println("El momento NO se conservo");
        }

        if (Math.abs(eAntes - eDespues) < 0.0001) {
            System.out.println("La energia cinetica SI se conservo");
        } else {
            System.out.println("La energia cinetica NO se conservo, se perdieron " + (eAntes - eDespues) + " J");
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
