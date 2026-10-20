import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

/** Busca referencias PIC candidatas; no crea instrucciones ni guarda el proyecto. */
public class S47References extends GhidraScript {
 public void run() throws Exception {
  Set<Long> wanted=new HashSet<>();
  for(int n=1;n<getScriptArgs().length;n++)wanted.add(Long.decode(getScriptArgs()[n]));
  JsonArray rows=new JsonArray();Map<String,long[]> regs=new HashMap<>();
  var it=currentProgram.getListing().getInstructions(true);
  while(it.hasNext()) {
   var ins=it.next();String op=ins.getMnemonicString();
   String reg=ins.getNumOperands()>0?ins.getDefaultOperandRepresentation(0):"";
   if(op.startsWith("add") && ins.toString().endsWith(",pc") && regs.containsKey(reg)) {
    long[] src=regs.get(reg);long target=(src[0]+ins.getAddress().getOffset()+4)&0xffffffffL;
    boolean inWindow=wanted.contains(0x43ed4000L) && target>=0x43ed4000L && target<0x43ed4800L;
    if((wanted.contains(target) || inWindow) && ins.getAddress().getOffset()-src[1]<128) {
     JsonObject row=new JsonObject();row.addProperty("site",ins.getAddress().toString());
     row.addProperty("target",Long.toHexString(target));row.addProperty("literal",Long.toHexString(src[2]));
     var f=getFunctionContaining(ins.getAddress());if(f!=null)row.addProperty("function",f.getEntryPoint().toString());
     JsonArray ls=new JsonArray();var near=currentProgram.getListing().getInstructions(ins.getAddress().subtract(32),true);
     while(near.hasNext()){var v=near.next();if(v.getAddress().getOffset()>ins.getAddress().getOffset()+64)break;ls.add(v.getAddress()+" "+v);}
     row.add("near_listing",ls);rows.add(row);
    }
   }
   if(wanted.contains(0xceL) && ins.toString().matches(".*#0xce(,|]|$).*")) {
    JsonObject row=new JsonObject();row.addProperty("site",ins.getAddress().toString());
    row.addProperty("immediate",ins.toString());var f=getFunctionContaining(ins.getAddress());
    if(f!=null)row.addProperty("function",f.getEntryPoint().toString());rows.add(row);
   }
   for(Object obj:ins.getResultObjects())regs.remove(obj.toString());
   if(op.startsWith("ldr") && ins.getNumOperands()==2) {
    var a=ins.getAddress(1);
    if(a!=null && currentProgram.getMemory().contains(a) && currentProgram.getMemory().contains(a.add(3)))
     regs.put(reg,new long[]{currentProgram.getMemory().getInt(a)&0xffffffffL,ins.getAddress().getOffset(),a.getOffset()});
   }
  }
  Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
  println("S47 PIC candidates: "+rows.size());
 }
}
