package eyeaf;

/**
 * Punto de AF de la A6000 expresado como la cámara lo espera: <b>porcentaje del
 * encuadre, 0..100</b> en x e y, con origen arriba-izquierda.
 *
 * <p>Evidencia (fw3.21, <code>orb-server</code>): <code>SetTouchAFPosition::invoke</code>
 * (<code>0x214ec8</code>) rechaza fuera de <code>[0,100]</code> comparando con la constante
 * <code>100.0</code> (<code>0x215308</code>), y empaqueta las dos coordenadas en un solo
 * <code>u32</code> <code>val = (u16)(x*100) &lt;&lt; 16 | (u16)(y*100)</code>
 * (<code>0x2150dc..0x215124</code>; ejemplo verificado: <code>[50,50] -&gt; 0x13881388</code>).
 *
 * <p>Este fichero es Java puro (sin Android) para poder compilarlo y probarlo sin cámara.
 */
public final class AfPoint {

    public static final double MIN_PERCENT = 0.0;
    public static final double MAX_PERCENT = 100.0;

    private AfPoint() {
    }

    /** Normalizado 0..1 (detector) a porcentaje 0..100 (cámara), recortando al rango válido. */
    public static double toPercent(double normalized) {
        double pct = normalized * 100.0;
        return clamp(pct);
    }

    public static double clamp(double pct) {
        if (Double.isNaN(pct)) {
            throw new IllegalArgumentException("coordenada NaN");
        }
        if (pct < MIN_PERCENT) {
            return MIN_PERCENT;
        }
        if (pct > MAX_PERCENT) {
            return MAX_PERCENT;
        }
        return pct;
    }

    /** ¿Es (x,y) un punto que la cámara aceptaría? El rango es cerrado. */
    public static boolean isValid(double xPercent, double yPercent) {
        return xPercent >= MIN_PERCENT && xPercent <= MAX_PERCENT
                && yPercent >= MIN_PERCENT && yPercent <= MAX_PERCENT;
    }

    /**
     * Empaqueta el punto tal y como lo hace la cámara:
     * <code>(u16)(x*100) &lt;&lt; 16 | (u16)(y*100)</code>.
     */
    public static int pack(double xPercent, double yPercent) {
        if (!isValid(xPercent, yPercent)) {
            throw new IllegalArgumentException("fuera de 0..100: " + xPercent + "," + yPercent);
        }
        int x = (int) Math.round(xPercent * 100.0) & 0xFFFF;
        int y = (int) Math.round(yPercent * 100.0) & 0xFFFF;
        return (x << 16) | y;
    }
}
