public class Colision {
    private String tipo;
    private double masa1;
    private double masa2;
    private double velocidad1;
    private double velocidad2;
    private double e;

    public Colision(String tipo, double masa1, double masa2,
                    double velocidad1, double velocidad2, double e) {

        if (!tipo.equals("elastica") && !tipo.equals("inelastica")) {
            throw new IllegalArgumentException("Tipo de colision no valido.");
        }

        if (masa1 <= 0 || masa2 <= 0) {
            throw new IllegalArgumentException("Las masas deben ser mayores que cero.");
        }

        if (e < 0 || e > 1) {
            throw new IllegalArgumentException("El coeficiente de restitucion debe estar entre 0 y 1.");
        }

        if (!Double.isFinite(masa1) || !Double.isFinite(masa2)
                || !Double.isFinite(velocidad1) || !Double.isFinite(velocidad2)
                || !Double.isFinite(e)) {
            throw new IllegalArgumentException("Los valores deben ser numeros validos.");
        }

        if (tipo.equals("elastica") && e != 1.0) {
            throw new IllegalArgumentException("Una colision elastica debe tener e = 1.");
        }

        this.tipo = tipo;
        this.masa1 = masa1;
        this.masa2 = masa2;
        this.velocidad1 = velocidad1;
        this.velocidad2 = velocidad2;
        this.e = e;
    }

    public String getTipo() {
        return tipo;
    }

    public double getMasa1() {
        return masa1;
    }

    public double getMasa2() {
        return masa2;
    }

    public double getVelocidad1() {
        return velocidad1;
    }

    public double getVelocidad2() {
        return velocidad2;
    }

    public double getE() {
        return e;
    }
}
