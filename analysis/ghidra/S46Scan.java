import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;

/** Inventario de desplazamientos partidos; cada candidato exige identidad aparte. */
public class S46Scan extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();
  var it=currentProgram.getListing().getInstructions(toAddr(0x43780000L),true);
  while(it.hasNext()) {
   var ins=it.next(); long a=ins.getAddress().getOffset(); if(a>=0x43b10000L)break;
   String s=ins.toString();
   if(s.matches(".*#0x(1e6c|1e00|1f00|1f01|1f0|e6c|e00|f00|1454|6b0|1a4|94|95)(]|,|$).*")) {
    JsonObject row=new JsonObject();row.addProperty("instruction",ins.getAddress()+" "+s);
    var f=getFunctionContaining(ins.getAddress());if(f!=null)row.addProperty("function",f.getEntryPoint().toString());rows.add(row);
   }
  }
  Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
