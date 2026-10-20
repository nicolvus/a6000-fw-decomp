import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Exporta funciones existentes y xrefs, sin transacciones ni mutaciones. */
public class S39Export extends GhidraScript {
    public void run() throws Exception {
        byte[] blob=Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
        String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if(!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")) throw new Exception("SHA mismatch");
        byte[] loaded=new byte[blob.length];currentProgram.getMemory().getBytes(toAddr(0x43541000L),loaded);
        if(!Arrays.equals(blob,loaded)) throw new Exception("project bytes mismatch");
        JsonObject root=new JsonObject();root.addProperty("sha256",sha);
        TreeSet<Long> targets=new TreeSet<>();JsonArray strings=new JsonArray();
        for(int start=0;start<blob.length;) {
            int end=start;while(end<blob.length && blob[end]>=32 && blob[end]<127)end++;
            if(end-start>=4) {
                String s=new String(blob,start,end-start,java.nio.charset.StandardCharsets.US_ASCII);
                if(s.toLowerCase().matches(".*(yuv|422|420|bayer|planar|packed|8.?bit|10.?bit|12.?bit|raw|enumconverter|sapl_).*")) {
                    JsonObject h=new JsonObject();h.addProperty("address",Long.toHexString(0x43541000L+start));h.addProperty("text",s);
                    JsonArray refs=new JsonArray();for(var r:getReferencesTo(toAddr(0x43541000L+start))) {refs.add(r.toString());}
                    h.add("references",refs);strings.add(h);
                }
            }
            start=end+1;
        }
        root.add("strings",strings);
        JsonArray data=new JsonArray();
        for(int i=1;i<getScriptArgs().length;i++) {
            String arg=getScriptArgs()[i];long a=Long.decode(arg.replace("@",""));
            if(!arg.startsWith("@")){targets.add(a);continue;}
            JsonObject h=new JsonObject();h.addProperty("address",Long.toHexString(a));JsonArray refs=new JsonArray();
            for(var r:getReferencesTo(toAddr(a))) {refs.add(r.toString());var f=getFunctionContaining(r.getFromAddress());if(f!=null)targets.add(f.getEntryPoint().getOffset());}
            h.add("references",refs);data.add(h);
        }
        root.add("data_queries",data);
        JsonArray pic=new JsonArray();Map<String,long[]> regs=new HashMap<>();Set<Long> requestedTargets=new HashSet<>();
        for(int n=1;n<getScriptArgs().length;n++) if(getScriptArgs()[n].startsWith("@"))requestedTargets.add(Long.decode(getScriptArgs()[n].substring(1)));
        var all=currentProgram.getListing().getInstructions(true);
        while(all.hasNext()) {
            var ins=all.next();String op=ins.getMnemonicString();String reg=ins.getNumOperands()>0?ins.getDefaultOperandRepresentation(0):"";
            if(op.startsWith("add") && ins.toString().endsWith(",pc") && regs.containsKey(reg)) {
                long[] source=regs.get(reg);long target=(source[0]+ins.getAddress().getOffset()+4)&0xffffffffL;
                boolean requested=requestedTargets.contains(target);
                if(ins.getAddress().getOffset()-source[1]<128 && (requested || target>=0x43e77c00L && target<0x43e77d00L || target==0x43ef71a4L || target==0x43ef71a0L || target>=0x43e99208L && target<0x43e99218L)) {
                    JsonObject h=new JsonObject();h.addProperty("site",ins.getAddress().toString());h.addProperty("target",Long.toHexString(target));h.addProperty("literal",Long.toHexString(source[2]));
                    var f=getFunctionContaining(ins.getAddress());if(f!=null){h.addProperty("function",f.getEntryPoint().toString());targets.add(f.getEntryPoint().getOffset());}pic.add(h);
                }
            }
            for(Object obj:ins.getResultObjects()) regs.remove(obj.toString());
            if(op.startsWith("ldr") && ins.getNumOperands()==2) {
                var address=ins.getAddress(1);
                if(address!=null && address.getOffset()>=0x43541000L && address.getOffset()+4<=0x43541000L+blob.length) regs.put(reg,new long[]{currentProgram.getMemory().getInt(address)&0xffffffffL,ins.getAddress().getOffset(),address.getOffset()});
            }
        }
        root.add("pic_references",pic);
        JsonArray rows=new JsonArray();StringBuilder c=new StringBuilder("/* S39: existing functions; no project modifications. */\n");
        DecompInterface dec=new DecompInterface();dec.openProgram(currentProgram);
        try {for(long a:targets) {
            var f=getFunctionContaining(toAddr(a));JsonObject row=new JsonObject();row.addProperty("query",Long.toHexString(a));
            if(f==null){row.addProperty("status","listing_only_no_function");JsonArray listing=new JsonArray();var it=currentProgram.getListing().getInstructions(toAddr(a),true);while(it.hasNext()){var ins=it.next();if(ins.getAddress().getOffset()>=a+0x800)break;listing.add(ins.getAddress()+" "+ins);}row.add("listing",listing);rows.add(row);continue;}
            row.addProperty("entry",f.getEntryPoint().toString());var result=dec.decompileFunction(f,90,monitor);row.addProperty("completed",result.decompileCompleted());
            if(result.getDecompiledFunction()!=null){String code=result.getDecompiledFunction().getC();row.addProperty("pseudo_code",code);c.append("\n/* "+f.getEntryPoint()+" */\n"+code);}
            JsonArray listing=new JsonArray();var it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){var ins=it.next();listing.add(ins.getAddress()+" "+ins);}row.add("listing",listing);
            JsonArray refs=new JsonArray();for(var r:getReferencesTo(f.getEntryPoint()))refs.add(r.toString());row.add("references",refs);rows.add(row);
        }} finally {dec.dispose();}
        root.add("functions",rows);String out=getScriptArgs()[0];Files.writeString(Path.of(out),new GsonBuilder().setPrettyPrinting().create().toJson(root));Files.writeString(Path.of(out.replace(".json",".c")),c.toString());println("S39 exported "+rows.size()+" queries; SHA and loaded bytes verified");
    }
}
