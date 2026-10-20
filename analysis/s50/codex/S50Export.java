import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Exporta funciones existentes sin modificar listado, referencias ni programa. */
public class S50Export extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        byte[] blob = Files.readAllBytes(Path.of("analysis/rea-independent/input/av-cam.bin"));
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(blob));
        if (!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")) {
            throw new Exception("Firmware SHA mismatch");
        }
        byte[] loaded = new byte[blob.length];
        currentProgram.getMemory().getBytes(toAddr(0x43541000L), loaded);
        if (!Arrays.equals(blob, loaded)) throw new Exception("Loaded bytes mismatch");
        JsonObject root = new JsonObject();
        root.addProperty("sha256", sha);
        JsonArray rows = new JsonArray();
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        try {
            for (int i = 1; i < args.length; i++) {
                long addr = Long.decode(args[i]);
                var a = toAddr(addr);
                var f = getFunctionContaining(a);
                JsonObject row = new JsonObject();
                row.addProperty("query", Long.toHexString(addr));
                byte[] bytes = new byte[64];
                currentProgram.getMemory().getBytes(a, bytes);
                row.addProperty("raw64", HexFormat.of().formatHex(bytes));
                JsonArray refs = new JsonArray();
                for (var r : getReferencesTo(a)) refs.add(r.toString());
                row.add("references", refs);
                JsonArray listing = new JsonArray();
                if (f != null) {
                    row.addProperty("entry", f.getEntryPoint().toString());
                    var result = dec.decompileFunction(f, 90, monitor);
                    row.addProperty("completed", result.decompileCompleted());
                    if (result.getDecompiledFunction() != null) {
                        row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                    }
                    var it = currentProgram.getListing().getInstructions(f.getBody(), true);
                    while (it.hasNext()) {
                        var ins = it.next();
                        listing.add(ins.getAddress() + " " + ins);
                    }
                } else row.addProperty("status", "no_existing_function");
                row.add("listing", listing);
                rows.add(row);
            }
        } finally { dec.dispose(); }
        root.add("functions", rows);
        Files.writeString(Path.of(args[0]), new GsonBuilder().setPrettyPrinting().create().toJson(root));
    }
}
