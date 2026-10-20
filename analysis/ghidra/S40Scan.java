import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
/** Inventario de operandos y xrefs existentes; nunca modifica el programa. */
public class S40Scan extends GhidraScript {
    public void run() throws Exception {
        JsonArray rows=new JsonArray();
        var it=currentProgram.getListing().getInstructions(true);
        while(it.hasNext()) {
            var ins=it.next(); String s=ins.toString();
            if(!s.contains("#0x458") && !s.contains("#0x450") && !s.contains("#0x454")
                && !s.contains("#0x24]") && !s.contains("#0x48]")) continue;
            JsonObject row=new JsonObject(); row.addProperty("site",ins.getAddress().toString());
            row.addProperty("instruction",s); var f=getFunctionContaining(ins.getAddress());
            if(f!=null)row.addProperty("function",f.getEntryPoint().toString());
            JsonArray refs=new JsonArray();for(var r:getReferencesFrom(ins.getAddress()))refs.add(r.toString());
            row.add("references",refs);rows.add(row);
        }
        Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
        println("S40 operand candidates: "+rows.size());
    }
}
