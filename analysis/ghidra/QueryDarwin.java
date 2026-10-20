// Consultas incrementales de Darwin; direcciones de ROM inferidas desde vectores.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class QueryDarwin extends GhidraScript {
    public void run() throws Exception {
        var base = toAddr(0x4200);
        var block = currentProgram.getMemory().getBlock(base);
        if (block == null || !block.getStart().equals(base))
            throw new IllegalArgumentException("Verified Darwin ROM base 4200 required");
        byte[] bytes = new byte[Math.toIntExact(block.getSize())];
        currentProgram.getMemory().getBytes(base, bytes);
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        if (!sha.equals("5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4") &&
            !sha.equals("6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac"))
            throw new IllegalArgumentException("Unknown Darwin image");
        JsonArray rows = new JsonArray();
        var decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("Decompiler unavailable");
            String[] args = getScriptArgs();
            for (int i = 1; i < args.length; i++) {
                boolean candidate = args[i].startsWith("candidate:");
                var address = toAddr(Long.decode(candidate ? args[i].substring(10) : args[i]));
                var function = getFunctionContaining(address);
                if (candidate && function != null && !function.getEntryPoint().equals(address))
                    throw new IllegalStateException("Candidate overlaps a recorded function: " + address);
                if (candidate && function == null) {
                    if (!block.contains(address) || (address.getOffset() & 1) != 0)
                        throw new IllegalArgumentException("Candidate must be an even ROM address");
                    disassemble(address);
                    function = createFunction(address, "candidate_" + address);
                }
                JsonObject row = new JsonObject();
                row.addProperty("query", address.toString());
                row.addProperty("entry_basis", candidate ? "caller-selected candidate; verify instructions" : "recorded containing function");
                if (function == null) row.addProperty("status", "no_recorded_function");
                else {
                    row.addProperty("entry", function.getEntryPoint().toString());
                    var result = decompiler.decompileFunction(function, 45, monitor);
                    row.addProperty("status", result.decompileCompleted() ? "decompiled" : "failed");
                    row.addProperty("error", result.getErrorMessage());
                    if (result.getDecompiledFunction() != null)
                        row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                    JsonArray refs = new JsonArray();
                    for (var ref : getReferencesTo(function.getEntryPoint())) refs.add(ref.getFromAddress().toString());
                    row.add("references", refs);
                }
                rows.add(row);
            }
            JsonObject output = new JsonObject();
            output.addProperty("source_sha256", sha);
            output.addProperty("rom_base", "4200");
            output.addProperty("language", currentProgram.getLanguageID().toString());
            output.addProperty("method", "recorded boundaries or explicit candidates; ROM at 4200 verified using reset, exception handlers and absolute callback table; no device execution");
            output.add("functions", rows);
            Files.writeString(Path.of(args[0]), output.toString() + "\n");
        } finally { decompiler.dispose(); }
    }
}
