import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

/** Busca referencias PIC candidatas; el flujo de punteros se valida aparte. */
public class S42Refs extends GhidraScript {
 public void run() throws Exception {
  Set<Long> targets=new HashSet<>();for(int i=1;i<getScriptArgs().length;i++)targets.add(Long.decode(getScriptArgs()[i]));
  JsonArray hits=new JsonArray();Map<String,long[]> regs=new HashMap<>();var it=currentProgram.getListing().getInstructions(true);
  while(it.hasNext()) {var ins=it.next();String op=ins.getMnemonicString(),reg=ins.getNumOperands()>0?ins.getDefaultOperandRepresentation(0):"";
   if(op.startsWith("add")&&ins.toString().endsWith(",pc")&&regs.containsKey(reg)){long[] src=regs.get(reg);long target=(src[0]+ins.getAddress().getOffset()+4)&0xffffffffL;
    if(ins.getAddress().getOffset()-src[1]<128&&(targets.contains(target)||target>=0x43ffdc00L&&target<0x43fff000L)){JsonObject h=new JsonObject();h.addProperty("site",ins.getAddress().toString());h.addProperty("target",Long.toHexString(target));var f=getFunctionContaining(ins.getAddress());if(f!=null)h.addProperty("function",f.getEntryPoint().toString());hits.add(h);}
   }
   for(Object o:ins.getResultObjects())regs.remove(o.toString());
   if(op.startsWith("ldr")&&ins.getNumOperands()==2){var a=ins.getAddress(1);if(a!=null&&currentProgram.getMemory().contains(a))regs.put(reg,new long[]{currentProgram.getMemory().getInt(a)&0xffffffffL,ins.getAddress().getOffset()});}
  }Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(hits));
 }
}
