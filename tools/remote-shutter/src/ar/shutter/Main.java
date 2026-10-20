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
                    OutputStream o = s.getOutputStream();
                    o.write(("HTTP/1.0 200 OK\r\n\r\n" + last + "\n").getBytes());
                    o.close();
                } catch (Throwable t) { Log.e(TAG, "req", t); }
                s.close();
            }
        } catch (Throwable t) { Log.e(TAG, "serve", t); }
    }
}
