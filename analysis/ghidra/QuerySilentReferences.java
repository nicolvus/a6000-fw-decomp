// Referencias del análisis guardado; una lista vacía no demuestra código muerto.
import ghidra.app.script.GhidraScript;
import java.nio.file.Files;
import java.nio.file.Path;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class QuerySilentReferences extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        JsonArray targets = new JsonArray();
        for (int i = 1; i < args.length; i++) {
            var address = toAddr(Long.decode(args[i]));
            JsonObject target = new JsonObject();
            target.addProperty("address", address.toString());
            JsonArray refs = new JsonArray();
            for (var ref : getReferencesTo(address)) {
                JsonObject row = new JsonObject();
                row.addProperty("from", ref.getFromAddress().toString());
                row.addProperty("type", ref.getReferenceType().toString());
                var function = getFunctionContaining(ref.getFromAddress());
                if (function != null) row.addProperty("function", function.getEntryPoint().toString());
                refs.add(row);
            }
            target.add("references", refs);
            targets.add(target);
        }
        JsonObject result = new JsonObject();
        result.addProperty("function_count", currentProgram.getFunctionManager().getFunctionCount());
        result.addProperty("coverage", "Ghidra recorded references only; indirect aliases and missing code remain possible");
        result.add("targets", targets);
        Files.writeString(Path.of(args[0]), result.toString() + "\n");
        println("Exported reference queries");
    }
}
