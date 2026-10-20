import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;

/** Inventaría alias por puntero y sus xrefs existentes, sin crear análisis. */
public class S44Pointers extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();var mem=currentProgram.getMemory();
  for(long a=0x43541000L;a<0x44050000L;a+=4){
   if(!mem.contains(toAddr(a+3)))continue;
   long v=mem.getInt(toAddr(a))&0xffffffffL;
   if(v<0x4401c600L||v>=0x4401ca40L)continue;
   JsonObject row=new JsonObject();row.addProperty("slot",Long.toHexString(a));row.addProperty("target",Long.toHexString(v));
   JsonArray refs=new JsonArray();for(var r:getReferencesTo(toAddr(a))){JsonObject x=new JsonObject();x.addProperty("xref",r.toString());var f=getFunctionContaining(r.getFromAddress());if(f!=null)x.addProperty("function",f.getEntryPoint().toString());refs.add(x);}row.add("references",refs);rows.add(row);
  }Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
