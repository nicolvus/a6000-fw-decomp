import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;
import com.google.gson.*;

public class S37Export extends GhidraScript {
    public void run() throws Exception {
        JsonObject root = new JsonObject();
        root.addProperty("program", currentProgram.getName());
        root.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        root.addProperty("image_base", currentProgram.getImageBase().toString());
        JsonArray rows = new JsonArray();
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        StringBuilder c = new StringBuilder("/* S37: static analysis only. */\n");
        try {
            var it = currentProgram.getFunctionManager().getFunctions(true);
            while (it.hasNext()) {
                Function f = it.next();
                JsonObject row = new JsonObject();
                row.addProperty("name", f.getName(true));
                row.addProperty("entry", f.getEntryPoint().toString());
                row.addProperty("external", f.isExternal());
                row.addProperty("thunk", f.isThunk());
                var result = dec.decompileFunction(f, 60, monitor);
                row.addProperty("completed", result.decompileCompleted());
                row.addProperty("error", result.getErrorMessage());
                if (result.getDecompiledFunction() != null) {
                    String code = result.getDecompiledFunction().getC();
                    row.addProperty("pseudo_code", code);
                    c.append("\n/* ").append(f.getEntryPoint()).append(" */\n").append(code);
                }
                JsonArray listing = new JsonArray();
                var instructions = currentProgram.getListing().getInstructions(f.getBody(), true);
                while (instructions.hasNext()) {
                    var ins = instructions.next();
                    listing.add(ins.getAddress() + " " + ins);
                }
                row.add("listing", listing);
                JsonArray refs = new JsonArray();
                for (var ref : getReferencesTo(f.getEntryPoint())) refs.add(ref.getFromAddress().toString());
                row.add("references", refs);
                rows.add(row);
            }
        } finally { dec.dispose(); }
        root.add("functions", rows);
        Files.writeString(Path.of(getScriptArgs()[0]), new GsonBuilder().setPrettyPrinting().create().toJson(root));
        Files.writeString(Path.of(getScriptArgs()[0].replace(".json", ".c")), c.toString());
        println("S37 exported " + rows.size() + " functions");
    }
}
