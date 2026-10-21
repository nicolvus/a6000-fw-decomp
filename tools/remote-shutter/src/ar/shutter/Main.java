package ar.shutter;

import android.app.Activity;
import android.hardware.Camera;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.FileOutputStream;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.net.ServerSocket;
import java.net.Socket;

/** Abre CameraEx por reflexión y dispara con GET /shoot por el puerto 8080. */
public class Main extends Activity implements SurfaceHolder.Callback {
    private static final String TAG = "RemoteShutter";
    private Object cameraEx;
    private Camera camera;
    private final Handler ui = new Handler();
    private volatile String last = "none";
    private int count;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        SurfaceView v = new SurfaceView(this);
        v.getHolder().addCallback(this);
        setContentView(v);
        new Thread(new Runnable() { public void run() { serve(); } }).start();
    }

    public void surfaceCreated(SurfaceHolder h) { last = "ready"; }
    public void surfaceChanged(SurfaceHolder h, int f, int w, int hh) {}
    public void surfaceDestroyed(SurfaceHolder h) { release(); }
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
        try {
            if (cameraEx != null) cameraEx.getClass().getMethod("release").invoke(cameraEx);
        } catch (Throwable t) { Log.e(TAG, "release", t); }
        camera = null; cameraEx = null;
    }

    private void shoot() {
        ui.post(new Runnable() { public void run() {
            try {
                release();
                open();
                last = "shooting";
                camera.takePicture(null, null, new Camera.PictureCallback() {
                    public void onPictureTaken(byte[] data, Camera cam) {
                        try {
                            OutputStream o = new FileOutputStream("/mnt/sdcard/RS" + (++count) + ".JPG");
                            o.write(data); o.close();
                        } catch (Throwable t) { Log.e(TAG, "save", t); }
                        last = "done " + (data == null ? 0 : data.length);
                        release();
                    }
                });
            } catch (Throwable t) { last = "shoot-error " + t; Log.e(TAG, "shoot", t); release(); }
        }});
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
                    if (req.startsWith("GET /shoot")) shoot();
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
