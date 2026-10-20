import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;

/** Inventario de offsets: candidatos, nunca identidad de objeto demostrada. */
public class S43Fields extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();
  var it=currentProgram.getListing().getInstructions(true);
  while(it.hasNext()) {
   var ins=it.next(); String s=ins.toString();
   if(s.contains("#0x3a0]") || (s.startsWith("str") &&
      (s.contains("#0x94]") || s.contains("#0x95]")))) {
    JsonObject row=new JsonObject(); row.addProperty("instruction",ins.getAddress()+" "+s);
    var f=getFunctionContaining(ins.getAddress());
    if(f!=null)row.addProperty("function",f.getEntryPoint().toString());
    rows.add(row);
   }
  }
  Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
