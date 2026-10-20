import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;

/** Referencias existentes hacia un intervalo de datos, sin mutaciones. */
public class S42DataRefs extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();for(int n=1;n<getScriptArgs().length;n+=2){long a=Long.decode(getScriptArgs()[n]),end=Long.decode(getScriptArgs()[n+1]);
   for(;a<end;a++)for(var r:getReferencesTo(toAddr(a))){JsonObject h=new JsonObject();h.addProperty("reference",r.toString());var f=getFunctionContaining(r.getFromAddress());if(f!=null)h.addProperty("function",f.getEntryPoint().toString());rows.add(h);}
  }Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
