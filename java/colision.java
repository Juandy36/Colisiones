public class Colision {

    private String tipo;
    private double masa1;
    private double masa2;
    private double velocidad1;
    private double velocidad2;

    public Colision(String tipo, double masa1, double masa2,
                    double velocidad1, double velocidad2) {

        if (!tipo.equals("elastica") && !tipo.equals("inelastica")) {
            throw new IllegalArgumentException("Tipo de colision no valido.");
        }

        if (masa1 <= 0 || masa2 <= 0) {
            throw new IllegalArgumentException("Las masas deben ser mayores que cero.");
        }

        if (!Double.isFinite(masa1) || !Double.isFinite(masa2)
                || !Double.isFinite(velocidad1) || !Double.isFinite(velocidad2)) {
            throw new IllegalArgumentException("Los valores deben ser numeros validos.");
        }

        this.tipo = tipo;
        this.masa1 = masa1;
        this.masa2 = masa2;
        this.velocidad1 = velocidad1;
        this.velocidad2 = velocidad2;
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
}
