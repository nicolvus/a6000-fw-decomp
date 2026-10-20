import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Consulta existente, sin crear funciones ni cambiar memoria/contexto. */
public class S38Export extends GhidraScript {
    public void run() throws Exception {
        byte[] blob=Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
        String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if(!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")) throw new Exception("SHA mismatch");
        byte[] loaded=new byte[blob.length];currentProgram.getMemory().getBytes(toAddr(0x43541000L),loaded);
        if(!Arrays.equals(blob,loaded)) throw new Exception("project bytes mismatch");
        JsonObject root=new JsonObject();root.addProperty("sha256",sha);root.addProperty("base","0x43541000");
        TreeSet<Long> targets=new TreeSet<>();JsonArray hits=new JsonArray();
        for(int i=0;i+3<blob.length;i++) {
            long v=(blob[i]&255L)|((blob[i+1]&255L)<<8)|((blob[i+2]&255L)<<16)|((blob[i+3]&255L)<<24);
            if(v!=0x61003cL && v!=0xbf0274L && v!=0x56015cL)continue;
            JsonObject h=new JsonObject();h.addProperty("value",Long.toHexString(v));h.addProperty("literal",Long.toHexString(0x43541000L+i));JsonArray refs=new JsonArray();
            for(var r:getReferencesTo(toAddr(0x43541000L+i))) {refs.add(r.toString());var f=getFunctionContaining(r.getFromAddress());if(f!=null)targets.add(f.getEntryPoint().getOffset());}
            h.add("references",refs);hits.add(h);
        }
        root.add("literal_hits",hits);
        JsonArray immediates=new JsonArray();var instructions=currentProgram.getListing().getInstructions(true);
        while(instructions.hasNext()) {var ins=instructions.next();for(int n=0;n<ins.getNumOperands();n++) for(Object o:ins.getOpObjects(n)) if(o instanceof Scalar && ((Scalar)o).getUnsignedValue()==0x61003cL) {immediates.add(ins.getAddress()+" "+ins);var f=getFunctionContaining(ins.getAddress());if(f!=null)targets.add(f.getEntryPoint().getOffset());}}
        root.add("immediates",immediates);
        for(int i=1;i<getScriptArgs().length;i++)targets.add(Long.decode(getScriptArgs()[i]));
        JsonArray rows=new JsonArray();StringBuilder c=new StringBuilder("/* S38: existing functions, no memory changes. */\n");DecompInterface dec=new DecompInterface();dec.openProgram(currentProgram);
        try {for(long a:targets) {var f=getFunctionContaining(toAddr(a));JsonObject row=new JsonObject();row.addProperty("query",Long.toHexString(a));if(f==null){row.addProperty("status","missing");rows.add(row);continue;}
            row.addProperty("entry",f.getEntryPoint().toString());var result=dec.decompileFunction(f,90,monitor);row.addProperty("completed",result.decompileCompleted());row.addProperty("error",result.getErrorMessage());
            if(result.getDecompiledFunction()!=null){String code=result.getDecompiledFunction().getC();row.addProperty("pseudo_code",code);c.append("\n/* "+f.getEntryPoint()+" */\n"+code);}
            JsonArray listing=new JsonArray();var it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){var ins=it.next();listing.add(ins.getAddress()+" "+ins);}row.add("listing",listing);
            JsonArray refs=new JsonArray();for(var r:getReferencesTo(f.getEntryPoint()))refs.add(r.toString());row.add("references",refs);rows.add(row);
        }} finally {dec.dispose();}
        root.add("functions",rows);String out=getScriptArgs()[0];Files.writeString(Path.of(out),new GsonBuilder().setPrettyPrinting().create().toJson(root));Files.writeString(Path.of(out.replace(".json",".c")),c.toString());println("S38 exported "+rows.size()+" functions");
    }
}
