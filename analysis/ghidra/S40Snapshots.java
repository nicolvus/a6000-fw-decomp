import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
/** Exporta familia de snapshots existente, sin modificar funciones/tipos. */
public class S40Snapshots extends GhidraScript {
    public void run() throws Exception {
        byte[] blob=Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
        String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if(!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"))throw new Exception("SHA mismatch");
        byte[] loaded=new byte[blob.length];currentProgram.getMemory().getBytes(toAddr(0x43541000L),loaded);
        if(!Arrays.equals(blob,loaded))throw new Exception("Loaded bytes mismatch");
        JsonObject root=new JsonObject();root.addProperty("sha256",sha);JsonArray rows=new JsonArray();
        StringBuilder c=new StringBuilder("/* S40: existing snapshot functions; read-only export. */\n");
        DecompInterface dec=new DecompInterface();dec.openProgram(currentProgram);
        try {
            var funcs=currentProgram.getFunctionManager().getFunctions(toAddr(0x43b00b48L),true);
            while(funcs.hasNext()) {
                var f=funcs.next();if(f.getEntryPoint().getOffset()>=0x43b010a0L)break;
                JsonObject row=new JsonObject();row.addProperty("entry",f.getEntryPoint().toString());
                var result=dec.decompileFunction(f,90,monitor);row.addProperty("completed",result.decompileCompleted());
                if(result.getDecompiledFunction()!=null){String code=result.getDecompiledFunction().getC();row.addProperty("pseudo_code",code);c.append("\n/* "+f.getEntryPoint()+" */\n"+code);}
                JsonArray listing=new JsonArray();var it=currentProgram.getListing().getInstructions(f.getBody(),true);
                while(it.hasNext()){var ins=it.next();listing.add(ins.getAddress()+" "+ins);}row.add("listing",listing);
                JsonArray refs=new JsonArray();for(var r:getReferencesTo(f.getEntryPoint()))refs.add(r.toString());row.add("references",refs);rows.add(row);
            }
        } finally {dec.dispose();}
        root.add("functions",rows);String out=getScriptArgs()[0];Files.writeString(Path.of(out),new GsonBuilder().setPrettyPrinting().create().toJson(root));
        Files.writeString(Path.of(out.replace(".json",".c")),c.toString());println("S40 snapshots: "+rows.size());
    }
}
