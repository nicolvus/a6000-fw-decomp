import ghidra.app.script.GhidraScript;
import ghidra.program.model.scalar.Scalar;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

public class S35Scan extends GhidraScript {
    public void run() throws Exception {
        byte[] blob = Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if (!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")) throw new Exception("SHA mismatch");
        JsonObject out = new JsonObject(); out.addProperty("source_sha256",sha);
        JsonArray hits = new JsonArray();
        var it = currentProgram.getListing().getInstructions(true);
        while(it.hasNext()) {
            var ins = it.next();
            boolean match = false;
            for(int n=0;n<ins.getNumOperands();n++) for(Object obj:ins.getOpObjects(n)) {
                if(obj instanceof Scalar) {
                    long v=((Scalar)obj).getUnsignedValue();
                    if(v==0x200000L || v==0x3380000L) match=true;
                }
            }
            if(match) {
                JsonObject row=new JsonObject();row.addProperty("site",ins.getAddress().toString());row.addProperty("instruction",ins.toString());
                var f=getFunctionContaining(ins.getAddress());if(f!=null)row.addProperty("function",f.getEntryPoint().toString());hits.add(row);
            }
        }
        out.add("immediate_hits",hits);
        JsonArray raw = new JsonArray();
        for(int i=0;i+3<blob.length;i++) {
            long v=(blob[i]&255L)|((blob[i+1]&255L)<<8)|((blob[i+2]&255L)<<16)|((blob[i+3]&255L)<<24);
            if(v!=0x200000L && v!=0x3380000L)continue;
            JsonObject row=new JsonObject();row.addProperty("address",Long.toHexString(0x43541000L+i));row.addProperty("value",Long.toHexString(v));
            JsonArray refs=new JsonArray();for(var r:getReferencesTo(toAddr(0x43541000L+i)))refs.add(r.toString());row.add("xrefs",refs);raw.add(row);
        }
        out.add("raw_hits_unaligned",raw);
        Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(out)+"\n");
        println("S35 scan complete; no project mutation");
    }
}
