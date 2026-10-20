import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
/** Lee tablas ya cargadas; no crea tipos ni referencias en el proyecto. */
public class S40Tables extends GhidraScript {
    public void run() throws Exception {
        byte[] blob=Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
        String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if(!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"))throw new Exception("SHA mismatch");
        byte[] loaded=new byte[blob.length];currentProgram.getMemory().getBytes(toAddr(0x43541000L),loaded);
        if(!Arrays.equals(blob,loaded))throw new Exception("Loaded bytes mismatch");
        var mem=currentProgram.getMemory();JsonObject root=new JsonObject();root.addProperty("sha256",sha);
        long base=((mem.getInt(toAddr(0x43805324L))&0xffffffffL)+0x438052f6L)&0xffffffffL;
        root.addProperty("dispatch_base",Long.toHexString(base));root.addProperty("stride",12);root.addProperty("count",220);
        JsonArray rows=new JsonArray();StringBuilder c=new StringBuilder("/* S40: literal table dump, not executable firmware. */\n");
        for(int i=0;i<220;i++) {
            long a=base+i*12;byte[] b=new byte[12];mem.getBytes(toAddr(a),b);JsonObject r=new JsonObject();
            r.addProperty("index",i);r.addProperty("address",Long.toHexString(a));r.addProperty("raw",HexFormat.of().formatHex(b));
            r.addProperty("command",mem.getShort(toAddr(a))&0xffff);r.addProperty("handler",Long.toHexString(mem.getInt(toAddr(a+4))&0xffffffffL));
            r.addProperty("flag",mem.getByte(toAddr(a+8))&255);rows.add(r);
            c.append("/* "+Long.toHexString(a)+" "+HexFormat.of().formatHex(b)+" */\n");
        }
        root.add("dispatch",rows);
        long selector=((mem.getInt(toAddr(0x43794a74L))&0xffffffffL)+0x43794a64L)&0xffffffffL;
        byte[] b=new byte[4];mem.getBytes(toAddr(selector),b);root.addProperty("selector_base",Long.toHexString(selector));root.addProperty("selector_raw",HexFormat.of().formatHex(b));
        c.append("/* selector "+Long.toHexString(selector)+": "+HexFormat.of().formatHex(b)+" */\n");
        String out=getScriptArgs()[0];Files.writeString(Path.of(out),new GsonBuilder().setPrettyPrinting().create().toJson(root));
        Files.writeString(Path.of(out.replace(".json",".c")),c.toString());println("S40 tables exported; SHA/memory verified");
    }
}
