package ar.shutter;

import android.app.Activity;
import android.hardware.Camera;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.FileOutputStream;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.net.ServerSocket;
import java.net.Socket;

/** Abre CameraEx por reflexión y dispara con GET /shoot por el puerto 8080; /ss fija la velocidad, /nr la RR larga, /last da el último JPEG. */
public class Main extends Activity implements SurfaceHolder.Callback {
    private static final String TAG = "RemoteShutter";
    private Object cameraEx;
    private Camera camera;
    private final Handler ui = new Handler();
    private volatile String last = "none";
    private int count;
    private volatile byte[] lastJpeg;
    private volatile long lastMs = -1;
    private volatile int openRetries;
    private volatile int lastShotR5;
    private final StringBuilder shotLog = new StringBuilder();  // CSV: n,t_inicio_ms,ms_hasta_jpeg,bytes
    private static final String VERSION = "v8b";
    private TextView info;
    private String keyLog = "-";

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        SurfaceView v = new SurfaceView(this);
        v.getHolder().addCallback(this);
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        info = new TextView(this);
        info.setTextSize(22);
        Button btn = new Button(this);
        btn.setText("SHUTTER");
        btn.setTextSize(28);
        btn.setOnClickListener(new View.OnClickListener() { public void onClick(View x) { shoot(); } });
        l.addView(btn);
        l.addView(info);
        l.addView(v, new LinearLayout.LayoutParams(1, 1));
        setContentView(l);
        btn.requestFocus();
        refresh();
        new Thread(new Runnable() { public void run() { serve(); } }).start();
    }

    public void surfaceCreated(SurfaceHolder h) { last = "ready"; }
    public void surfaceChanged(SurfaceHolder h, int f, int w, int hh) {}
    public void surfaceDestroyed(SurfaceHolder h) { release(); }
    private void refresh() {
        info.setText("OK = disparar | MENU, atras o izquierda = salir\nestado: " + last + "\ntecla: " + keyLog);
        ui.postDelayed(new Runnable() { public void run() { refresh(); } }, 500);
    }

    @Override public boolean onKeyDown(int k, KeyEvent e) {
        keyLog = String.valueOf(k);
        if (k == KeyEvent.KEYCODE_BACK || k == KeyEvent.KEYCODE_MENU || k == KeyEvent.KEYCODE_DPAD_LEFT) { finish(); return true; }
        return super.onKeyDown(k, e);
    }

    // Mata el proceso al salir: libera el puerto 8080 y deja la cámara limpia para la siguiente apertura.
    @Override protected void onDestroy() { super.onDestroy(); android.os.Process.killProcess(android.os.Process.myPid()); }

    @Override protected void onPause() { super.onPause(); release(); }

    // Sin preview: el overlay falla en esta cámara, pero takePicture funciona sin él.
    private void open() throws Exception {
        Class<?> c = Class.forName("com.sony.scalar.hardware.CameraEx");
        Method open = null;
        for (Method m : c.getMethods()) if (m.getName().equals("open")) open = m;
        cameraEx = open.invoke(null, 0, null);
        camera = (Camera) c.getMethod("getNormalCamera").invoke(cameraEx);
    }

    private void release() {
        silentRevert("release");
        try {
            if (cameraEx != null) cameraEx.getClass().getMethod("release").invoke(cameraEx);
        } catch (Throwable t) { Log.e(TAG, "release", t); }
        camera = null; cameraEx = null;
    }

    private void shoot() {
        ui.post(new Runnable() { public void run() {
            try {
                release();
                // Reabrir justo tras liberar puede fallar ("Fail to connect to cameraex service"): se reintenta y se cuenta.
                int tries = 0;
                while (true) {
                    try { open(); break; }
                    catch (Throwable t) { if (++tries > 6) throw t; release(); Thread.sleep(400); }
                }
                openRetries = tries;
                String sil = "normal";
                lastShotR5 = 0;
                if (silentOn) {
                    int r5 = silentR5();
                    if (r5 < 0) sil = "normal(velocidad-lenta)";
                    else { sil = silentApply(r5); if (sil.startsWith("silent r5=")) lastShotR5 = r5; else throw new Exception(sil); }
                }
                silentLog = sil;
                last = "shooting";
                final long t0 = android.os.SystemClock.elapsedRealtime();
                camera.takePicture(null, null, new Camera.PictureCallback() {
                    public void onPictureTaken(byte[] data, Camera cam) {
                        silentRevert("cb");   // primero revertir: el estado «done» ya no ve el parche
                        final long ms = android.os.SystemClock.elapsedRealtime() - t0;
                        int id = ++count;
                        try {
                            lastJpeg = data;
                            OutputStream o = new FileOutputStream("/mnt/sdcard/RS" + id + ".JPG");
                            o.write(data); o.close();
                        } catch (Throwable t) { Log.e(TAG, "save", t); }
                        lastMs = ms;
                        synchronized (shotLog) { shotLog.append(id + "," + t0 + "," + ms + "," + (data == null ? 0 : data.length) + "," + openRetries + "," + lastShotR5 + "\n"); }
                        last = "done " + (data == null ? 0 : data.length) + " ms=" + ms + " n=" + id;
                        release();
                    }
                });
            } catch (Throwable t) { last = "shoot-error " + cause(t); Log.e(TAG, "shoot", t); release(); }
        }});
    }

    /** GET /params : getters sin argumentos de ParametersModifier (modo, ISO, EV...) y Camera.Parameters.flatten(). */
    private synchronized String params() {
        StringBuilder sb = new StringBuilder();
        try {
            Object pm = modifier();
            for (Method m : pm.getClass().getMethods()) {
                String n = m.getName();
                if (m.getParameterTypes().length != 0 || !(n.startsWith("get") || n.startsWith("is")) || n.equals("getClass")) continue;
                try { sb.append(n + "=" + render(m.invoke(pm)) + "\n"); } catch (Throwable t) { sb.append(n + "=err " + cause(t) + "\n"); }
            }
            sb.append("flatten=" + camera.getParameters().flatten() + "\n");
        } catch (Throwable t) { sb.append("params-error " + cause(t)); }
        return sb.toString();
    }

    private static String render(Object o) {
        if (o instanceof java.util.List) return o.toString();
        if (o instanceof android.util.Pair) return ((android.util.Pair<?, ?>) o).first + "/" + ((android.util.Pair<?, ?>) o).second;
        return String.valueOf(o);
    }

    /** GET /iso?v=N : fija ISO con setISOSensitivity (0 = auto); sin v devuelve el valor actual. */
    private synchronized String iso(int v) {
        try {
            Camera.Parameters prm = camera == null ? null : camera.getParameters();
            if (prm == null) { open(); prm = camera.getParameters(); }
            Object pm = cameraEx.getClass().getMethod("createParametersModifier", Camera.Parameters.class).invoke(cameraEx, prm);
            if (v >= 0) { pm.getClass().getMethod("setISOSensitivity", int.class).invoke(pm, v); camera.setParameters(prm); }
            Object pm2 = modifier();
            return "iso " + pm2.getClass().getMethod("getISOSensitivity").invoke(pm2);
        } catch (Throwable t) { Log.e(TAG, "iso", t); return "iso-error " + cause(t); }
    }

    /** GET /fmt?v=jpeg|raw|rawjpeg : formato de almacenamiento (setPictureStorageFormat); sin v devuelve el actual. */
    private synchronized String fmt(String v) {
        try {
            Camera.Parameters prm = camera == null ? null : camera.getParameters();
            if (prm == null) { open(); prm = camera.getParameters(); }
            Object pm = cameraEx.getClass().getMethod("createParametersModifier", Camera.Parameters.class).invoke(cameraEx, prm);
            if (v != null) { pm.getClass().getMethod("setPictureStorageFormat", String.class).invoke(pm, v); camera.setParameters(prm); }
            Object pm2 = modifier();
            return "fmt " + pm2.getClass().getMethod("getPictureStorageFormat").invoke(pm2);
        } catch (Throwable t) { Log.e(TAG, "fmt", t); return "fmt-error " + cause(t); }
    }

    /** GET /reopen?n=&gap= : n ciclos abrir/liberar CameraEx sin disparar; cuenta fallos (aísla el error de apertura de takePicture). */
    private String reopen(int n, int gap) {
        StringBuilder sb = new StringBuilder();
        int fails = 0;
        for (int i = 0; i < n; i++) {
            long t0 = android.os.SystemClock.elapsedRealtime();
            try { release(); open(); sb.append("ok:" + (android.os.SystemClock.elapsedRealtime() - t0) + " "); }
            catch (Throwable t) { fails++; sb.append("FAIL(" + cause(t) + "):" + (android.os.SystemClock.elapsedRealtime() - t0) + " "); }
            try { release(); Thread.sleep(gap); } catch (Throwable t) { /* sigue */ }
        }
        return "reopen n=" + n + " gap=" + gap + " fails=" + fails + " " + sb;
    }


    // ---- Modo silencioso (E25-11): ShutMode 0 + r5 calculado desde la velocidad, parche RAM de BIONZ con reversión ----
    private static final long SM_A = 0x836D6FB6L, R5_A = 0x836D7000L;       // ldrb.w sb,[r1,#9] / asrs r0,r5,#8; uxtb.w lr,r5
    private static final byte[] SM_O = {(byte) 0x91, (byte) 0xf8, 0x09, (byte) 0x90}, SM_N = {0x4f, (byte) 0xf0, 0x00, 0x09};
    private static final byte[] R5_O = {0x28, 0x12, 0x5f, (byte) 0xfa, (byte) 0x85, (byte) 0xfe};
    private static final double LINE_US = 15.2;     // tiempo de línea medido (T044/T046)
    private static final int R5_FULL = 4219;        // exposición nula (T046): E = (4219 - r5)·15,2 µs; r5 mínimo seguro:
    private static final int R5_MIN = 10;
    private volatile boolean silentOn;
    private volatile boolean patched;
    private volatile int lastR5;
    private volatile String silentLog = "-";
    private long patchedAt;

    // RandomAccessFile no llega por encima de 2 GiB (lseek de 32 bits: «Value too large»): se usa `dd` de /system/bin, que sí direcciona /dev/mem.
    private static byte[] memRead(long addr, int n) throws Exception {
        Process p = Runtime.getRuntime().exec(new String[] {"dd", "if=/dev/mem", "bs=2", "skip=" + (addr / 2), "count=" + (n / 2)});
        java.io.InputStream in = p.getInputStream();
        byte[] b = new byte[n];
        int off = 0, r;
        while (off < n && (r = in.read(b, off, n - off)) > 0) off += r;
        p.waitFor();
        if (off < n) throw new java.io.IOException("lectura corta " + off + "/" + n);
        return b;
    }

    private static void memWrite(long addr, byte[] b) throws Exception {
        Process p = Runtime.getRuntime().exec(new String[] {"dd", "of=/dev/mem", "bs=2", "seek=" + (addr / 2), "count=" + (b.length / 2)});
        OutputStream o = p.getOutputStream();
        o.write(b); o.close();
        if (p.waitFor() != 0) throw new java.io.IOException("dd de escritura falló");
    }

    private static byte[] r5Bytes(int v) { return new byte[] {(byte) (v >> 8), 0x20, 0x4f, (byte) 0xf0, (byte) v, 0x0e}; }

    /** r5 para la velocidad actual, o -1 si queda fuera del rango (exposición más larga que el cuadro completo). */
    private int silentR5() throws Exception {
        long lines = Math.round(speed() * 1e6 / LINE_US);
        int r5 = (int) (R5_FULL - lines);
        return r5 >= R5_MIN ? r5 : -1;
    }

    /** Aplica ShutMode 0 + r5 tras comprobar el código original; deja patched=true solo si todo se verificó. */
    private synchronized String silentApply(int r5) {
        try {
            if (!java.util.Arrays.equals(memRead(SM_A, 4), SM_O) || !java.util.Arrays.equals(memRead(R5_A, 6), R5_O)) return "silent-abort codigo-inesperado";
            memWrite(SM_A, SM_N);
            memWrite(R5_A, r5Bytes(r5));
            if (!java.util.Arrays.equals(memRead(SM_A, 4), SM_N) || !java.util.Arrays.equals(memRead(R5_A, 6), r5Bytes(r5))) {
                silentRevert("verify");
                return "silent-abort verificacion";
            }
            patched = true; lastR5 = r5; patchedAt = android.os.SystemClock.elapsedRealtime();
            // vigilante: si el disparo no termina, se revierte solo
            new Thread(new Runnable() { public void run() {
                try { Thread.sleep(45000); } catch (InterruptedException e) { return; }
                if (patched && android.os.SystemClock.elapsedRealtime() - patchedAt >= 44000) silentRevert("watchdog");
            }}).start();
            return "silent r5=" + r5;
        } catch (Throwable t) { silentRevert("error"); return "silent-error " + cause(t); }
    }

    private synchronized void silentRevert(String why) {
        if (!patched && !"verify".equals(why) && !"error".equals(why)) return;
        try {
            memWrite(R5_A, R5_O);
            memWrite(SM_A, SM_O);
            boolean ok = java.util.Arrays.equals(memRead(SM_A, 4), SM_O) && java.util.Arrays.equals(memRead(R5_A, 6), R5_O);
            silentLog = "revert(" + why + ")=" + (ok ? "OK" : "FALLO");
            if (!ok) Log.e(TAG, "revert FALLO " + why);
        } catch (Throwable t) { silentLog = "revert(" + why + ")=error " + cause(t); Log.e(TAG, "revert", t); }
        patched = false;
    }

    /** GET /silent?v=0|1 activa o no el modo; sin v informa; /silent?v=check lee los dos sitios (solo lectura). */
    private String silentCmd(String req) {
        int a = req.indexOf("v=");
        String v = a < 0 ? "" : req.substring(a + 2).split("[ &]")[0];
        if ("1".equals(v)) silentOn = true;
        else if ("0".equals(v)) { silentOn = false; silentRevert("off"); }
        String chk;
        try { chk = "sm=" + hex(memRead(SM_A, 4)) + " r5=" + hex(memRead(R5_A, 6)); } catch (Throwable t) { chk = "lectura-error " + cause(t); }
        return "silent on=" + silentOn + " patched=" + patched + " lastR5=" + lastR5 + " " + chk + " " + silentLog;
    }

    /** GET /burst?n=&gap= : n disparos seguidos (gap ms entre ellos); cada uno espera su JPEG. Mide el rearme. Resultado en /log. */
    private volatile boolean bursting;
    private void burst(final int n, final int gap) {
        if (bursting) return;
        bursting = true;
        new Thread(new Runnable() { public void run() {
            try {
                for (int i = 0; i < n; i++) {
                    long w = android.os.SystemClock.elapsedRealtime();
                    last = "queued";
                    shoot();
                    while (!(last.startsWith("done") || last.startsWith("shoot-error")) && android.os.SystemClock.elapsedRealtime() - w < 30000) Thread.sleep(20);
                    if (last.startsWith("shoot-error")) break;
                    Thread.sleep(gap);
                }
            } catch (Throwable t) { Log.e(TAG, "burst", t); } finally { bursting = false; }
        }}).start();
    }

    /** GET /seq?w=&h=&f=&n= : CameraSequence.startPreviewSequence + getPreviewSequenceFrames (frames de Live View, sin obturador). */
    private void seq(final int w, final int h, final int f, final int n, final boolean spv, final boolean trig) {
        ui.post(new Runnable() { public void run() {
            final StringBuilder sb = new StringBuilder("seq");
            try {
                release();
                open();
                final Class<?> cs = Class.forName("com.sony.scalar.hardware.CameraSequence");
                final Class<?> op = Class.forName("com.sony.scalar.hardware.CameraSequence$Options");
                final Object seq = cs.getMethod("open", cameraEx.getClass()).invoke(null, cameraEx);
                sb.append(" open-ok");
                if (trig) {
                    final Class<?> cb = Class.forName("com.sony.scalar.hardware.CameraSequence$ShutterSequenceCallback");
                    Object proxy = java.lang.reflect.Proxy.newProxyInstance(cb.getClassLoader(), new Class<?>[] { cb },
                        new java.lang.reflect.InvocationHandler() {
                            public Object invoke(Object pr, Method m, Object[] a) {
                                try {
                                    sb.append(" CB:" + m.getName());
                                    Method gf = cs.getMethod("getPreviewSequenceFrames", int.class);
                                    for (int k = 0; k <= 2; k++) {
                                        Object[] fr = (Object[]) gf.invoke(seq, k);
                                        sb.append(" frames(" + k + ")=" + (fr == null ? "null" : String.valueOf(fr.length)));
                                    }
                                    Object rd = a[0];
                                    if (rd != null) {
                                        Object ri = rd.getClass().getMethod("getRawDataInfo").invoke(rd);
                                        sb.append(" raw=" + ri.getClass().getField("validSizeX").get(ri) + "x" + ri.getClass().getField("validSizeY").get(ri));
                                    }
                                } catch (Throwable t) { sb.append(" cb-error " + cause(t)); }
                                return null;
                            }
                        });
                    Object o2 = op.newInstance();
                    Method s2 = op.getMethod("setOption", String.class, int.class);
                    s2.invoke(o2, (String) op.getField("RECORD_COUNT").get(null), 1);
                    s2.invoke(o2, (String) op.getField("EXPOSURE_COUNT").get(null), 1);
                    try {
                        cs.getMethod("setShutterSequenceCallback", cb, op).invoke(seq, proxy, o2);
                        sb.append(" cb2-set");
                    } catch (Throwable t) {
                        sb.append(" cb2-error " + cause(t));
                        try { cs.getMethod("stopPreviewSequence").invoke(seq); sb.append(" stopped"); } catch (Throwable t2) { sb.append(" stop-error " + cause(t2)); }
                        cs.getMethod("setShutterSequenceCallback", cb, op).invoke(seq, proxy, o2);
                        sb.append(" cb2-set-after-stop");
                    }
                }
                if (spv) {
                    try { camera.startPreview(); sb.append(" preview-ok"); }
                    catch (Throwable t) { sb.append(" preview-error " + cause(t)); }
                }
                final Object o = op.newInstance();
                Method seti = op.getMethod("setOption", String.class, int.class);
                seti.invoke(o, (String) op.getField("PREVIEW_FRAME_WIDTH").get(null), w);
                seti.invoke(o, (String) op.getField("PREVIEW_FRAME_HEIGHT").get(null), h);
                seti.invoke(o, (String) op.getField("PREVIEW_FRAME_FORMAT").get(null), f);
                seti.invoke(o, (String) op.getField("PREVIEW_FRAME_MAX_NUM").get(null), n);
                cs.getMethod("startPreviewSequence", op).invoke(seq, o);
                sb.append(" start-ok");
                last = sb.toString();
                if (trig) {
                    camera.takePicture(null, null, new Camera.PictureCallback() {
                        public void onPictureTaken(byte[] data, Camera cam) { sb.append(" jpeg=" + (data == null ? 0 : data.length)); }
                    });
                }
                ui.postDelayed(new Runnable() { public void run() {
                    try {
                        Method gf = cs.getMethod("getPreviewSequenceFrames", int.class);
                        for (int k = 0; k <= 2; k++) {
                            Object[] fr = (Object[]) gf.invoke(seq, k);
                            sb.append(" frames(" + k + ")=" + (fr == null ? "null" : String.valueOf(fr.length)));
                            if (fr != null && fr.length > 0) sb.append(" f0=" + fr[0]);
                        }
                        Object inf = cs.getMethod("getPreviewSequenceFrameInfo").invoke(seq);
                        byte[] dd = inf == null ? null : (byte[]) inf.getClass().getField("detailData").get(inf);
                        sb.append(" info=" + (dd == null ? "null" : dd.length + " " + hex(dd)));
                        cs.getMethod("stopPreviewSequence").invoke(seq);
                        cs.getMethod("release").invoke(seq);
                    } catch (Throwable t) { sb.append(" frames-error " + cause(t)); }
                    last = sb.toString(); release();
                }}, 4000);
            } catch (Throwable t) { sb.append(" error " + cause(t)); last = sb.toString(); Log.e(TAG, "seq", t); release(); }
        }});
    }

    private Object modifier() throws Exception {
        if (cameraEx == null) open();
        return cameraEx.getClass().getMethod("createParametersModifier", Camera.Parameters.class).invoke(cameraEx, camera.getParameters());
    }

    private double speed() throws Exception {
        Object pm = modifier();
        android.util.Pair<?, ?> p = (android.util.Pair<?, ?>) pm.getClass().getMethod("getShutterSpeed").invoke(pm);
        return ((Integer) p.first).doubleValue() / (Integer) p.second;
    }

    /** GET /ss?n=&d= : lleva la velocidad a n/d con CameraEx.adjustShutterSpeed (no hay setter directo); el sentido del paso se descubre. */
    private synchronized String ss(int n, int d) {
        try {
            Method adj = null;
            if (cameraEx == null) open();
            for (Method m : cameraEx.getClass().getMethods()) if (m.getName().equals("adjustShutterSpeed")) adj = m;
            double target = (double) n / d, v = speed(), err = Math.abs(Math.log(v / target));
            int dir = v > target ? 1 : -1;
            for (int i = 0; i < 80 && err > 0.05; i++) {
                adj.invoke(cameraEx, dir);
                Thread.sleep(120);
                double v2 = speed(), e2 = Math.abs(Math.log(v2 / target));
                if (e2 > err) dir = -dir;
                v = v2; err = e2;
            }
            return (err > 0.05 ? "ss-fail " : "ss-ok ") + v;
        } catch (Throwable t) { Log.e(TAG, "ss", t); return "ss-error " + cause(t); }
    }

    /** GET /nr?v=0|1 : reducción de ruido de exposición larga. */
    private synchronized String nr(boolean on) {
        try {
            Camera.Parameters prm = (cameraEx == null ? null : camera.getParameters());
            if (prm == null) { open(); prm = camera.getParameters(); }
            Object pm = cameraEx.getClass().getMethod("createParametersModifier", Camera.Parameters.class).invoke(cameraEx, prm);
            pm.getClass().getMethod("setLongExposureNR", boolean.class).invoke(pm, on);
            camera.setParameters(prm);
            Object pm2 = modifier();
            return "nr " + pm2.getClass().getMethod("getLongExposureNR").invoke(pm2);
        } catch (Throwable t) { Log.e(TAG, "nr", t); return "nr-error " + cause(t); }
    }

    private static String hex(byte[] d) {
        StringBuilder h = new StringBuilder();
        for (int i = 0; i < d.length && i < 48; i++) h.append(String.format("%02x", d[i]));
        return h.toString();
    }

    private static String cause(Throwable t) {
        while (t.getCause() != null) t = t.getCause();
        return t.toString();
    }

    private static int q(String req, String k, int d) {
        int i = req.indexOf(k + "=");
        if (i < 0) return d;
        int e = i + k.length() + 1, j = e;
        while (j < req.length() && Character.isDigit(req.charAt(j))) j++;
        return j > e ? Integer.parseInt(req.substring(e, j)) : d;
    }

    private void serve() {
        try {
            ServerSocket ss = new ServerSocket(8080);
            while (true) {
                Socket s = ss.accept();
                try {
                    byte[] buf = new byte[512];
                    int n = s.getInputStream().read(buf);
                    String req = n > 0 ? new String(buf, 0, n) : "";
                    if (req.startsWith("GET /last")) {
                        byte[] j = lastJpeg;
                        OutputStream o = s.getOutputStream();
                        o.write(("HTTP/1.0 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: " + (j == null ? 0 : j.length) + "\r\n\r\n").getBytes());
                        if (j != null) o.write(j);
                        o.close(); s.close(); continue;
                    }
                    if (req.startsWith("GET /jpg")) {
                        java.io.File f = new java.io.File("/mnt/sdcard/RS" + q(req, "i", 0) + ".JPG");
                        byte[] j = new byte[(int) f.length()];
                        java.io.FileInputStream in = new java.io.FileInputStream(f);
                        int off = 0, r;
                        while (off < j.length && (r = in.read(j, off, j.length - off)) > 0) off += r;
                        in.close();
                        OutputStream o = s.getOutputStream();
                        o.write(("HTTP/1.0 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: " + j.length + "\r\n\r\n").getBytes());
                        o.write(j); o.close(); s.close(); continue;
                    }
                    if (req.startsWith("GET /log")) {
                        String l;
                        synchronized (shotLog) { l = shotLog.toString(); if (q(req, "clear", 0) == 1) shotLog.setLength(0); }
                        OutputStream o = s.getOutputStream();
                        o.write(("HTTP/1.0 200 OK\r\n\r\n" + l).getBytes());
                        o.close(); s.close(); continue;
                    }
                    if (req.startsWith("GET /info")) {
                        String sp = "?";
                        try { sp = String.valueOf(speed()); } catch (Throwable t) { sp = "err " + cause(t); }
                        OutputStream o = s.getOutputStream();
                        o.write(("HTTP/1.0 200 OK\r\n\r\n" + VERSION + " speed=" + sp + " count=" + count + " lastMs=" + lastMs + " bursting=" + bursting + " t=" + android.os.SystemClock.elapsedRealtime() + "\n").getBytes());
                        o.close(); s.close(); continue;
                    }
                    if (req.startsWith("GET /silent")) last = silentCmd(req);
                    else if (req.startsWith("GET /params")) last = params();
                    else if (req.startsWith("GET /iso")) last = iso(q(req, "v", -1));
                    else if (req.startsWith("GET /fmt")) { int a = req.indexOf("v="); last = fmt(a < 0 ? null : req.substring(a + 2).split("[ &]")[0]); }
                    else if (req.startsWith("GET /reopen")) last = reopen(q(req, "n", 10), q(req, "gap", 0));
                    else if (req.startsWith("GET /burst")) burst(q(req, "n", 5), q(req, "gap", 0));
                    else if (req.startsWith("GET /ss")) last = ss(q(req, "n", 1), q(req, "d", 60));
                    else if (req.startsWith("GET /nr")) last = nr(q(req, "v", 0) == 1);
                    else if (req.startsWith("GET /shoot")) shoot();
                    else if (req.startsWith("GET /seq")) seq(q(req, "w", 1280), q(req, "h", 720), q(req, "f", 17), q(req, "n", 1), q(req, "p", 0) == 1, q(req, "t", 0) == 1);
                    OutputStream o = s.getOutputStream();
                    o.write(("HTTP/1.0 200 OK\r\n\r\n" + last + "\n").getBytes());
                    o.close();
                } catch (Throwable t) { Log.e(TAG, "req", t); }
                s.close();
            }
        } catch (Throwable t) { Log.e(TAG, "serve", t); }
    }
}
