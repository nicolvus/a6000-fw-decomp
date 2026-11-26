package eyeaf;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

/**
 * Mensaje <code>WebApiIntMsg</code> que la app de la cámara envía a la capa de cámara.
 *
 * <p>Layout verificado en <code>orb-server</code> fw3.21
 * (<code>WebApiAddonUipc::setEvtParamId</code> <code>0x18773c</code>,
 * <code>sendMsgToServer</code> <code>0x18767c</code>):
 *
 * <pre>
 *   tamaño        1568 B (0x620)
 *   +0x00  u32    id de mensaje
 *   +0x08  u32    id de parámetro
 *   +0x0c  u32    relay
 *   +0x10  u32    payload (para setTouchAFPosition, el valor empaquetado de AfPoint.pack)
 *   +0x14  u8     bool (AFResult / currentSet en las respuestas)
 * </pre>
 *
 * <p>La tabla de ids está en <code>liborbEvtCmdTbl</code> (<code>0x2d5d4</code>): petición,
 * respuesta y confirmación por familia. Ver <code>analysis/eyeaf/orb_touchaf.md</code> §2.
 */
public final class WebApiMsg {

    public static final int SIZE = 1568;

    public static final int OFF_MSGID = 0x00;
    public static final int OFF_PARAMID = 0x08;
    public static final int OFF_RELAY = 0x0c;
    public static final int OFF_PAYLOAD = 0x10;
    public static final int OFF_FLAG = 0x14;

    public static final int MSGID_SET_TOUCH_AF = 0x192;
    public static final int PARAMID_SET_TOUCH_AF = 0x8d;
    public static final int MSGID_SET_TOUCH_AF_CMP = 0x194;
    public static final int PARAMID_SET_TOUCH_AF_CMP = 0x8f;

    public static final int MSGID_CANCEL_TOUCH_AF = 0x195;
    public static final int PARAMID_CANCEL_TOUCH_AF = 0x90;
    public static final int MSGID_CANCEL_TOUCH_AF_CMP = 0x197;
    public static final int PARAMID_CANCEL_TOUCH_AF_CMP = 0x92;

    public static final int MSGID_GET_TOUCH_AF = 0x198;
    public static final int PARAMID_GET_TOUCH_AF = 0x93;
    public static final int MSGID_GET_TOUCH_AF_CMP = 0x19a;
    public static final int PARAMID_GET_TOUCH_AF_CMP = 0x95;

    private WebApiMsg() {
    }

    public static byte[] build(int msgid, int paramid, int relay, int payload, boolean flag) {
        byte[] msg = new byte[SIZE];
        ByteBuffer b = ByteBuffer.wrap(msg).order(ByteOrder.LITTLE_ENDIAN);
        b.putInt(OFF_MSGID, msgid);
        b.putInt(OFF_PARAMID, paramid);
        b.putInt(OFF_RELAY, relay);
        b.putInt(OFF_PAYLOAD, payload);
        msg[OFF_FLAG] = (byte) (flag ? 1 : 0);
        return msg;
    }

    /** Petición de punto de AF y enfoque en ese punto (porcentaje 0..100). */
    public static byte[] setTouchAf(double xPercent, double yPercent) {
        return build(MSGID_SET_TOUCH_AF, PARAMID_SET_TOUCH_AF, 0, AfPoint.pack(xPercent, yPercent), false);
    }

    public static byte[] cancelTouchAf() {
        return build(MSGID_CANCEL_TOUCH_AF, PARAMID_CANCEL_TOUCH_AF, 0, 0, false);
    }

    public static byte[] getTouchAf() {
        return build(MSGID_GET_TOUCH_AF, PARAMID_GET_TOUCH_AF, 0, 0, false);
    }

    /** Lectura defensiva de un campo u32 del mensaje recibido. */
    public static int intAt(byte[] msg, int offset) {
        if (msg == null || msg.length < SIZE) {
            throw new IllegalArgumentException("mensaje incompleto: " +
                    (msg == null ? "null" : String.valueOf(msg.length)));
        }
        return ByteBuffer.wrap(msg).order(ByteOrder.LITTLE_ENDIAN).getInt(offset);
    }

    /** AFResult de la respuesta (byte en +0x14). */
    public static boolean afResult(byte[] response) {
        if (response == null || response.length < SIZE) {
            return false;
        }
        return response[OFF_FLAG] != 0;
    }

    /** Copia para pruebas: comprueba que todo lo que no se escribe queda a cero. */
    static boolean restIsZero(byte[] msg) {
        byte[] copy = Arrays.copyOf(msg, msg.length);
        ByteBuffer b = ByteBuffer.wrap(copy).order(ByteOrder.LITTLE_ENDIAN);
        b.putInt(OFF_MSGID, 0);
        b.putInt(OFF_PARAMID, 0);
        b.putInt(OFF_RELAY, 0);
        b.putInt(OFF_PAYLOAD, 0);
        copy[OFF_FLAG] = 0;
        for (byte v : copy) {
            if (v != 0) {
                return false;
            }
        }
        return true;
    }
}
