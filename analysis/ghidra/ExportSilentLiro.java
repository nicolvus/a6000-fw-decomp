// Análisis local de candidatos Thumb; nombres y límites no son símbolos Sony.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class ExportSilentLiro extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("output path required");
        Address base = toAddr(0x43541000L);
        byte[] bytes = new byte[11427236];
        currentProgram.getMemory().getBytes(base, bytes);
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        if (!digest.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"))
            throw new IllegalArgumentException("original LIRO bytes mismatch");
        long[] seeds = {0x438032d4L, 0x43802e4cL, 0x437fee08L, 0x438052d8L,
            0x436d62e4L, 0x436d67ecL, 0x436d74bcL, 0x436d7e08L};
        // Solo metadatos del proyecto dedicado: retirar decodificaciones previas
        // antes de fijar todos los modos; los bytes originales se verifican arriba.
        clearListing(base, base.add(bytes.length - 1));
        for (long seed : seeds) {
            Address address = toAddr(seed);
            currentProgram.getProgramContext().setValue(
                currentProgram.getRegister("TMode"), address, address, BigInteger.ONE);
        }
        for (long seed : seeds) {
            Address address = toAddr(seed);
            disassemble(address);
            if (getFunctionAt(address) == null)
                createFunction(address, "candidate_" + Long.toHexString(seed));
        }
        DecompInterface decompiler = new DecompInterface();
        JsonArray rows = new JsonArray();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("decompiler open failed");
            for (long seed : seeds) {
                Function function = getFunctionAt(toAddr(seed));
                JsonObject row = new JsonObject();
                row.addProperty("address", "0x" + Long.toHexString(seed));
                if (function == null) {
                    row.addProperty("status", "function_not_created");
                } else {
                    DecompileResults result = decompiler.decompileFunction(function, 60, monitor);
                    row.addProperty("status", result.decompileCompleted() ? "decompiled" : "failed");
                    row.addProperty("error", result.getErrorMessage());
                    if (result.getDecompiledFunction() != null)
                        row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                }
                rows.add(row);
            }
        } finally {
            decompiler.dispose();
        }
        JsonObject output = new JsonObject();
        output.addProperty("source_sha256", digest);
        output.addProperty("base", "0x43541000");
        output.addProperty("method", "caller-selected Thumb seeds, no full auto-analysis; inferred function entries");
        output.add("functions", rows);
        Files.writeString(Path.of(args[0]), output.toString() + "\n", StandardCharsets.UTF_8);
        println("Exported " + rows.size() + " candidate functions");
    }
}
