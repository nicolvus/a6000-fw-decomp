import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

/** Exporta aristas existentes para comprobar orden sin ejecutar firmware. */
public class S47Flow extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();
  for(int n=1;n<getScriptArgs().length;n++) {
   var f=getFunctionContaining(toAddr(Long.decode(getScriptArgs()[n])));
   if(f==null)throw new Exception("No existing function");
   JsonObject row=new JsonObject();row.addProperty("entry",f.getEntryPoint().toString());
   JsonArray nodes=new JsonArray();var it=currentProgram.getListing().getInstructions(f.getBody(),true);
   while(it.hasNext()) {
    var ins=it.next();JsonObject node=new JsonObject();node.addProperty("address",ins.getAddress().toString());
    node.addProperty("instruction",ins.toString());node.addProperty("bytes",HexFormat.of().formatHex(ins.getBytes()));
    JsonArray edges=new JsonArray();
    if(!ins.getFlowType().isCall())for(var a:ins.getFlows())edges.add(a.toString());
    if(ins.getFallThrough()!=null)edges.add(ins.getFallThrough().toString());
    node.add("successors",edges);nodes.add(node);
   }
   row.add("nodes",nodes);rows.add(row);
  }
  Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
