import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;

/** Candidatos por desplazamiento; su identidad requiere seguimiento separado. */
public class S45Scan extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();
  var it=currentProgram.getListing().getInstructions(true);
  while(it.hasNext()) {
   var ins=it.next(); String s=ins.toString();
   var next=ins.getNext();
   boolean v74=s.startsWith("ldr") && s.contains("#0x74]") && next!=null &&
       (next.toString().startsWith("blx") || next.toString().startsWith("bx"));
   if(v74 || s.contains("#0x1e6c") || s.contains("#0x3a0") || s.contains("437b5b14") ||
      (s.contains("#0x74]") && ins.getAddress().getOffset()>=0x436d0000L && ins.getAddress().getOffset()<0x436e0000L) ||
      (s.startsWith("str") && s.contains("#0x50]") &&
       ins.getAddress().getOffset()>=0x43780000L && ins.getAddress().getOffset()<0x43860000L)) {
    JsonObject r=new JsonObject();r.addProperty("instruction",ins.getAddress()+" "+s);
    var f=getFunctionContaining(ins.getAddress());if(f!=null)r.addProperty("function",f.getEntryPoint().toString());rows.add(r);
   }
  }
  Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
