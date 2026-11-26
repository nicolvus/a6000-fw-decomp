package eyeaf;

import android.app.Activity;
import android.hardware.Camera;
import android.net.LocalSocket;
import android.net.LocalSocketAddress;
import android.os.Bundle;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.OutputStream;
import java.lang.reflect.Method;
import java.util.Locale;

/**
 * Eye AF en tiempo real <b>dentro de la cámara</b>: la actividad abre la cámara por
 * {@code CameraEx} (misma reflexión que {@code tools/remote-shutter}), pide la detección de caras
 * del propio firmware, elige un ojo y manda el punto de AF por la misma orden que usa la app
 * remota de Sony ({@link WebApiMsg}).
 *
 * <p>No hay visión artificial aquí: el detector de caras/ojos es el de la cámara
 * ({@code Camera.Face.leftEye/rightEye}). Si el firmware no rellena los ojos, el respaldo es la
 * heurística del tercio superior de la cara, marcada como {@code shortcut}.
 *
 * <p>El envío del punto va por {@link TouchAfSender}; por defecto sólo escribe en el log
 * ({@link LogSender}) porque el nombre del socket de la cámara se fija por extra:
 * <pre>adb shell am start -n ar.eyeaf/.EyeAfActivity --es socket &lt;nombre&gt;</pre>
 * Así una sesión física puede probar el canal sin recompilar.
 */
public final class EyeAfActivity extends Activity implements SurfaceHolder.Callback, Camera.FaceDetectionListener {

    private static final String TAG = "EyeAF";

    private final AfTracker tracker = AfTracker.defaults();
    private SurfaceView view;
    private Object cameraEx;
    private Camera camera;
    private TouchAfSender sender = new LogSender();
    private volatile boolean running;
    private int previewWidth = 640;
    private int previewHeight = 480;
    private int frames;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        String socket = getIntent() == null ? null : getIntent().getStringExtra("socket");
        if (socket != null && socket.length() > 0) {
            sender = new UipcSender(socket);
        }
        view = new SurfaceView(this);
        view.getHolder().addCallback(this);
        setContentView(view);
        Log.i(TAG, "Eye AF listo; envío=" + sender.name());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stop();
        sender.close();
        android.os.Process.killProcess(android.os.Process.myPid());
    }

    // -- ciclo de vida del preview -------------------------------------------

    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        start(holder);
    }

    @Override
    public void surfaceChanged(SurfaceHolder holder, int format, int w, int h) {
        previewWidth = Math.max(w, 1);
        previewHeight = Math.max(h, 1);
    }

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        stop();
    }

    private void start(SurfaceHolder holder) {
        if (running) {
            return;
        }
        try {
            Class<?> c = Class.forName("com.sony.scalar.hardware.CameraEx");
            Method open = null;
            for (Method m : c.getMethods()) {
                if (m.getName().equals("open")) {
                    open = m;
                }
            }
            cameraEx = open.invoke(null, 0, null);
            camera = (Camera) c.getMethod("getNormalCamera").invoke(cameraEx);
            camera.setPreviewDisplay(holder);
            Camera.Parameters p = camera.getParameters();
            Log.i(TAG, "preview " + p.getPreviewSize().width + "x" + p.getPreviewSize().height
                    + " formato=" + p.getPreviewFormat());
            previewWidth = p.getPreviewSize().width;
            previewHeight = p.getPreviewSize().height;
            camera.startPreview();
            camera.setFaceDetectionListener(this);
            camera.startFaceDetection();
            running = true;
            Log.i(TAG, "preview y detección de caras activos");
        } catch (Throwable t) {
            Log.e(TAG, "no se pudo arrancar la cámara", t);
        }
    }

    private void stop() {
        running = false;
        try {
            if (camera != null) {
                camera.stopFaceDetection();
                camera.stopPreview();
                camera.setFaceDetectionListener(null);
            }
        } catch (Throwable ignored) {
            // el preview puede estar ya caído
        }
        try {
            if (cameraEx != null) {
                cameraEx.getClass().getMethod("release").invoke(cameraEx);
            }
        } catch (Throwable t) {
            Log.e(TAG, "release", t);
        }
        camera = null;
        cameraEx = null;
    }

    // -- bucle ---------------------------------------------------------------

    @Override
    public void onFaceDetection(Camera.Face[] faces, Camera cam) {
        frames++;
        double now = android.os.SystemClock.elapsedRealtime() / 1000.0;
        Camera.Face face = largest(faces);
        if (face == null) {
            apply(tracker.update(false, 0, 0, now));
            return;
        }
        double[] eye = eyeOf(face);
        AfTracker.Command cmd = tracker.update(true, eye[0], eye[1], now);
        apply(cmd);
    }

    private void apply(AfTracker.Command cmd) {
        if (cmd == null) {
            return;
        }
        sender.send(cmd);
        Log.i(TAG, String.format(Locale.ROOT, "cuadro %d -> %s", frames, cmd));
    }

    /** Cara de mayor área (el sujeto principal). */
    private static Camera.Face largest(Camera.Face[] faces) {
        if (faces == null) {
            return null;
        }
        Camera.Face best = null;
        long bestArea = -1;
        for (Camera.Face f : faces) {
            if (f == null || f.rect == null) {
                continue;
            }
            long area = (long) f.rect.width() * f.rect.height();
            if (area > bestArea) {
                bestArea = area;
                best = f;
            }
        }
        return best;
    }

    /**
     * Ojo elegido, en normalizado 0..1 con origen arriba-izquierda.
     *
     * <p>{@code Camera.Face} usa el sistema de coordenadas del sensor con el rango −1000..1000, así
     * que se remapea. Si el firmware no rellena {@code leftEye}/{@code rightEye} se usa el centro
     * del tercio superior de la cara.
     *
     * <p>shortcut: sin ojos del firmware, el tercio superior de la cara no distingue izquierda de
     * derecha ni sigue al ojo real; se sustituye cuando se verifique que {@code leftEye/rightEye}
     * llegan rellenos en la A6000.
     */
    private static double[] eyeOf(Camera.Face face) {
        if (face.leftEye != null && face.rightEye != null) {
            int x = (face.leftEye.x + face.rightEye.x) / 2;
            int y = (face.leftEye.y + face.rightEye.y) / 2;
            return normalized(x, y);
        }
        if (face.leftEye != null) {
            return normalized(face.leftEye.x, face.leftEye.y);
        }
        if (face.rightEye != null) {
            return normalized(face.rightEye.x, face.rightEye.y);
        }
        int x = face.rect.centerX();
        int y = face.rect.top + face.rect.height() / 3;
        return normalized(x, y);
    }

    /** −1000..1000 (sensor) a 0..1 (pantalla/encuadre) recortando. */
    static double[] normalized(int sensorX, int sensorY) {
        double x = (sensorX + 1000.0) / 2000.0;
        double y = (sensorY + 1000.0) / 2000.0;
        return new double[]{clamp01(x), clamp01(y)};
    }

    private static double clamp01(double v) {
        return v < 0 ? 0 : (v > 1 ? 1 : v);
    }

    // -- envío ---------------------------------------------------------------

    interface TouchAfSender {
        void send(AfTracker.Command cmd);

        void close();

        String name();
    }

    /** Sólo log: modo seguro por defecto (no toca la cámara). */
    static final class LogSender implements TouchAfSender {
        @Override
        public void send(AfTracker.Command cmd) {
            // ya se registra en apply(); no se envía nada a la cámara
        }

        @Override
        public void close() {
        }

        @Override
        public String name() {
            return "log";
        }
    }

    /**
     * Escribe el mensaje de 1568 B en el socket local de la cámara.
     *
     * <p>El nombre del socket se pasa por extra porque no está verificado en estático cuál es el
     * que atiende {@code MID_REQ_SET_TOUCH_AF_POSITION_EVT}; ver
     * {@code analysis/eyeaf/rc_touchaf.md}.
     */
    static final class UipcSender implements TouchAfSender {
        private final String path;
        private LocalSocket socket;
        private OutputStream out;

        UipcSender(String path) {
            this.path = path;
        }

        @Override
        public synchronized void send(AfTracker.Command cmd) {
            try {
                if (out == null) {
                    socket = new LocalSocket();
                    socket.connect(new LocalSocketAddress(path, LocalSocketAddress.Namespace.FILESYSTEM));
                    out = socket.getOutputStream();
                    Log.i(TAG, "socket conectado: " + path);
                }
                byte[] msg = cmd.cancel
                        ? WebApiMsg.cancelTouchAf()
                        : WebApiMsg.setTouchAf(cmd.xPercent, cmd.yPercent);
                out.write(msg);
                out.flush();
            } catch (Throwable t) {
                Log.e(TAG, "envío por " + path + " falló", t);
                close();
            }
        }

        @Override
        public synchronized void close() {
            try {
                if (out != null) {
                    out.close();
                }
            } catch (Throwable ignored) {
                // cerrando
            }
            try {
                if (socket != null) {
                    socket.close();
                }
            } catch (Throwable ignored) {
                // cerrando
            }
            out = null;
            socket = null;
        }

        @Override
        public String name() {
            return "uipc:" + path;
        }
    }
}
