package eyeaf;

/**
 * Decide <b>cuándo</b> se manda el punto de AF, dentro de la cámara.
 *
 * <p>Misma semántica que <code>tools/eye-af/eyeaf/tracker.py</code> (el bucle del PC), para que
 * las dos implementaciones se comporten igual: suavizado EMA, salto limpio al cambiar de sujeto,
 * banda muerta, límite de órdenes por segundo y cancelación al perder el ojo.
 *
 * <p>Motivo de la banda muerta: el marco de AF es discreto y cada orden puede relanzar un ciclo de
 * enfoque en la cámara; mandar 30 órdenes por segundo sería contraproducente.
 *
 * <p>Java puro (sin Android): compila y se prueba sin cámara.
 */
public final class AfTracker {

    /** Orden a aplicar al punto de AF. */
    public static final class Command {
        public final boolean cancel;
        public final double xPercent;
        public final double yPercent;

        private Command(boolean cancel, double xPercent, double yPercent) {
            this.cancel = cancel;
            this.xPercent = xPercent;
            this.yPercent = yPercent;
        }

        static Command move(double xPercent, double yPercent) {
            return new Command(false, xPercent, yPercent);
        }

        static Command cancel() {
            return new Command(true, 0.0, 0.0);
        }

        @Override
        public String toString() {
            return cancel ? "cancel" : String.format(java.util.Locale.ROOT, "move(%.2f,%.2f)", xPercent, yPercent);
        }
    }

    private final double minMove;
    private final double periodS;
    private final double smooth;
    private final double lostAfterS;
    private final double jump;

    private double posX;
    private double posY;
    private boolean hasPos;
    private double sentX;
    private double sentY;
    private boolean hasSent;
    private double sentAtS;
    private double seenAtS;
    private boolean cancelled = true;

    public AfTracker(double minMove, double maxHz, double smooth, double lostAfterS, double jump) {
        if (minMove < 0 || maxHz <= 0 || smooth <= 0 || smooth > 1 || lostAfterS < 0 || jump <= 0) {
            throw new IllegalArgumentException("parámetros fuera de rango");
        }
        this.minMove = minMove;
        this.periodS = 1.0 / maxHz;
        this.smooth = smooth;
        this.lostAfterS = lostAfterS;
        this.jump = jump;
    }

    /** Valores por defecto del bucle del PC: 1 % de banda muerta, 3 Hz, EMA 0.4. */
    public static AfTracker defaults() {
        return new AfTracker(0.01, 3.0, 0.4, 1.5, 0.35);
    }

    /**
     * @param present si hay ojo en este cuadro
     * @param x       normalizado 0..1 del ojo elegido
     * @param y       normalizado 0..1 del ojo elegido
     * @param nowS    segundos monótonos
     * @return la orden a enviar, o {@code null} si no toca
     */
    public Command update(boolean present, double x, double y, double nowS) {
        if (!present) {
            if (!cancelled && nowS - seenAtS >= lostAfterS) {
                cancelled = true;
                hasSent = false;
                hasPos = false;
                return Command.cancel();
            }
            return null;
        }

        seenAtS = nowS;
        cancelled = false;

        double tx = AfPoint.clamp(x * 100.0);
        double ty = AfPoint.clamp(y * 100.0);

        boolean jumpNow = !hasPos || (tx - posX) * (tx - posX) + (ty - posY) * (ty - posY) > jump * jump * 10000.0;
        if (hasPos && !jumpNow) {
            posX = posX + smooth * (tx - posX);
            posY = posY + smooth * (ty - posY);
        } else {
            posX = tx;
            posY = ty;
            hasPos = true;
        }

        if (hasSent) {
            if (nowS - sentAtS < periodS) {
                return null;
            }
            double dx = posX - sentX;
            double dy = posY - sentY;
            if (dx * dx + dy * dy < (minMove * 100.0) * (minMove * 100.0)) {
                return null;
            }
        }

        sentX = posX;
        sentY = posY;
        sentAtS = nowS;
        hasSent = true;
        return Command.move(posX, posY);
    }

    public boolean hasPosition() {
        return hasPos;
    }
}
