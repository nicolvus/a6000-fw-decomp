package eyeaf;

/**
 * Pruebas del núcleo del Eye AF de cámara, sin Android y sin cámara.
 *
 * <p>Se ejecuta con <code>javac</code> + <code>java</code> (ver
 * <code>tools/eye-af/camera/run_selftest.sh</code>) y también desde
 * <code>tests/test_eye_af_camera_core.py</code>. Cada comprobación cita la evidencia que la
 * fija: si la evidencia cambia, el test debe cambiar con ella.
 */
public final class SelfTest {

    private static int checks;
    private static int failures;

    public static void main(String[] args) {
        percent();
        packing();
        message();
        trackerDeadbandAndRate();
        trackerJumpAndCancel();
        System.out.println(checks + " comprobaciones, " + failures + " fallos");
        if (failures > 0) {
            System.exit(1);
        }
    }

    // -- AfPoint -------------------------------------------------------------

    private static void percent() {
        check("0.25 normalizado -> 25 %", AfPoint.toPercent(0.25) == 25.0);
        check("0.5 -> 50 %", AfPoint.toPercent(0.5) == 50.0);
        check("recorte inferior", AfPoint.toPercent(-0.4) == 0.0);
        check("recorte superior", AfPoint.toPercent(1.7) == 100.0);
        check("rango cerrado admite extremos", AfPoint.isValid(0.0, 100.0) && AfPoint.isValid(100.0, 0.0));
        check("rango rechaza 100.5", !AfPoint.isValid(100.5, 0.0));
        check("NaN rechazado", throwsIllegalArgument());
    }

    private static boolean throwsIllegalArgument() {
        try {
            AfPoint.clamp(Double.NaN);
            return false;
        } catch (IllegalArgumentException expected) {
            return true;
        }
    }

    // -- empaquetado (evidencia: orb-server 0x2150dc..0x215124) ---------------

    private static void packing() {
        // El informe cita dos ejemplos medidos en el binario.
        check("[50,50] -> 0x13881388", AfPoint.pack(50.0, 50.0) == 0x13881388);
        check("[100,0] -> 0x27100000", AfPoint.pack(100.0, 0.0) == 0x27100000);
        check("[0,100] -> 0x00002710", AfPoint.pack(0.0, 100.0) == 0x00002710);
        check("[12.34,56.78] trunca a centésimas",
                AfPoint.pack(12.34, 56.78) == ((1234 << 16) | 5678));
    }

    // -- mensaje WebApiIntMsg (evidencia: setEvtParamId 0x18773c) -------------

    private static void message() {
        byte[] msg = WebApiMsg.setTouchAf(50.0, 50.0);
        check("tamaño 1568 B", msg.length == 1568);
        check("msgid 0x192 en +0x00", WebApiMsg.intAt(msg, WebApiMsg.OFF_MSGID) == 0x192);
        check("paramid 0x8d en +0x08", WebApiMsg.intAt(msg, WebApiMsg.OFF_PARAMID) == 0x8d);
        check("payload en +0x10 = pack", WebApiMsg.intAt(msg, WebApiMsg.OFF_PAYLOAD) == 0x13881388);
        check("resto a cero", WebApiMsg.restIsZero(msg));

        byte[] cancel = WebApiMsg.cancelTouchAf();
        check("cancel msgid 0x195", WebApiMsg.intAt(cancel, WebApiMsg.OFF_MSGID) == 0x195);
        check("cancel paramid 0x90", WebApiMsg.intAt(cancel, WebApiMsg.OFF_PARAMID) == 0x90);

        byte[] get = WebApiMsg.getTouchAf();
        check("get msgid 0x198", WebApiMsg.intAt(get, WebApiMsg.OFF_MSGID) == 0x198);
        check("get paramid 0x93", WebApiMsg.intAt(get, WebApiMsg.OFF_PARAMID) == 0x93);

        byte[] response = new byte[WebApiMsg.SIZE];
        response[WebApiMsg.OFF_FLAG] = 1;
        check("AFResult se lee de +0x14", WebApiMsg.afResult(response));
        check("sin AFResult -> false", !WebApiMsg.afResult(new byte[WebApiMsg.SIZE]));
        check("respuesta corta -> false", !WebApiMsg.afResult(new byte[10]));
    }

    // -- AfTracker -----------------------------------------------------------

    private static void trackerDeadbandAndRate() {
        AfTracker t = new AfTracker(0.01, 10.0, 1.0, 1.5, 0.35);
        AfTracker.Command first = t.update(true, 0.50, 0.50, 0.0);
        check("primer ojo mueve el punto", first != null && !first.cancel);
        check("primer punto = 50 %", first.xPercent == 50.0 && first.yPercent == 50.0);

        // 0.5 % de movimiento: por debajo de la banda muerta del 1 %
        check("banda muerta ignora 0.5 %", t.update(true, 0.505, 0.50, 0.50) == null);

        // movimiento grande pero demasiado pronto para el límite de 10 Hz
        check("límite de Hz frena", t.update(true, 0.70, 0.50, 0.05) == null);
        AfTracker.Command later = t.update(true, 0.70, 0.50, 0.20);
        check("pasado el período, manda", later != null && Math.abs(later.xPercent - 70.0) < 0.01);
    }

    private static void trackerJumpAndCancel() {
        AfTracker t = AfTracker.defaults();
        t.update(true, 0.20, 0.20, 0.0);
        AfTracker.Command jump = t.update(true, 0.90, 0.90, 1.0);
        check("salto de sujeto sin barrido", jump != null && Math.abs(jump.xPercent - 90.0) < 0.01);

        check("sin ojo no manda nada al principio", t.update(false, 0, 0, 1.2) == null);
        AfTracker.Command cancel = t.update(false, 0, 0, 2.6);
        check("cancelación tras perder el ojo", cancel != null && cancel.cancel);
        check("cancelación sólo una vez", t.update(false, 0, 0, 4.0) == null);
    }

    // -- utilidades ----------------------------------------------------------

    private static void check(String what, boolean ok) {
        checks++;
        if (!ok) {
            failures++;
            System.out.println("FALLO: " + what);
        }
    }
}
