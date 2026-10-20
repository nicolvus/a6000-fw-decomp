import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Consulta funciones existentes; nunca crea código ni guarda el programa. */
public class S41Export extends GhidraScript {
    public void run() throws Exception {
        byte[] blob = Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if (!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")) throw new Exception("SHA mismatch");
        byte[] loaded = new byte[blob.length];
        currentProgram.getMemory().getBytes(toAddr(0x43541000L), loaded);
        if (!Arrays.equals(blob, loaded)) throw new Exception("Loaded bytes mismatch");
        JsonObject root = new JsonObject(); root.addProperty("sha256", sha);
        JsonArray rows = new JsonArray(); StringBuilder c = new StringBuilder("/* S41: read-only exports. */\n");
        DecompInterface dec = new DecompInterface(); dec.openProgram(currentProgram);
        try { for (int n=1; n<getScriptArgs().length; n++) {
            boolean pseudo=getScriptArgs()[n].startsWith("~");
            long a=Long.decode(getScriptArgs()[n].replace("~","")); var f=getFunctionContaining(toAddr(a));
            JsonObject row=new JsonObject(); row.addProperty("query",Long.toHexString(a));
            byte[] bytes=new byte[64];currentProgram.getMemory().getBytes(toAddr(a),bytes);row.addProperty("raw64",HexFormat.of().formatHex(bytes));
            JsonArray refs=new JsonArray(); for(var r:getReferencesTo(toAddr(a))) refs.add(r.toString()); row.add("references",refs);
            if(f!=null) {
                row.addProperty("entry",f.getEntryPoint().toString()); var result=dec.decompileFunction(f,60,monitor);
                row.addProperty("completed",result.decompileCompleted());
                if(result.getDecompiledFunction()!=null) {String code=result.getDecompiledFunction().getC();row.addProperty("pseudo_code",code);c.append("\n/* "+f.getEntryPoint()+" */\n"+code);}
            } else row.addProperty("status","listing_only_no_function");
            JsonArray listing=new JsonArray();var it=f==null?currentProgram.getListing().getInstructions(toAddr(a),true):currentProgram.getListing().getInstructions(f.getBody(),true);
            while(it.hasNext()){var ins=it.next();if(f==null && ins.getAddress().getOffset()>=a+0x180)break;listing.add(ins.getAddress()+" "+ins);}row.add("listing",listing); rows.add(row);
            if(pseudo) {
                JsonArray temporary=new JsonArray();
                var dis=ghidra.program.disassemble.Disassembler.getDisassembler(currentProgram,false,false,false,monitor,null);long cursor=a;
                var mode=new ghidra.program.model.lang.RegisterValue(currentProgram.getRegister("TMode"),java.math.BigInteger.ONE).getBaseRegisterValue();
                for(int k=0;k<80 && cursor<a+0x180;k++) {
                    try {byte[] code=new byte[16];currentProgram.getMemory().getBytes(toAddr(cursor),code);
                        var block=dis.pseudoDisassembleBlock(new ghidra.program.model.mem.ByteMemBufferImpl(toAddr(cursor),code,false),mode,1);
                        var ins=block.getInstructionAt(toAddr(cursor));if(ins==null)throw new Exception("No Thumb instruction");temporary.add(ins.getAddress()+" "+ins);cursor+=ins.getLength();
                        if(ins.getFlowType().isTerminal())break;
                    }catch(Exception e){row.addProperty("pseudo_disassembly_error",e.toString());break;}
                }
                row.add("temporary_thumb_listing",temporary);
            }
        }} finally {dec.dispose();}
        root.add("functions",rows);String out=getScriptArgs()[0];Files.writeString(Path.of(out),new GsonBuilder().setPrettyPrinting().create().toJson(root));Files.writeString(Path.of(out.replace(".json",".c")),c.toString());
        println("S41 exported "+rows.size()+" queries; SHA and memory verified");
    }
}
