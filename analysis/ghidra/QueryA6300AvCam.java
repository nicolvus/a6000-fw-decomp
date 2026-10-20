// Consultas Thumb acotadas al av-cam original de la A6300; solo lectura del firmware.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class QueryA6300AvCam extends GhidraScript {
    private static final long BASE = 0x43541000L;
    private static final String SHA256 =
        "6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16";

    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output and addresses required");
        var block = currentProgram.getMemory().getBlock(toAddr(BASE));
        if (block == null || !block.getStart().equals(toAddr(BASE)))
            throw new IllegalArgumentException("A6300 av-cam load base required");
        byte[] bytes = new byte[Math.toIntExact(block.getSize())];
        currentProgram.getMemory().getBytes(toAddr(BASE), bytes);
        String actual = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        if (!actual.equals(SHA256)) throw new IllegalArgumentException("A6300 av-cam hash mismatch");

        JsonArray rows = new JsonArray();
        var decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram))
                throw new IllegalStateException("Decompiler unavailable");
            for (int i = 1; i < args.length; i++) {
                boolean candidate = args[i].startsWith("candidate:");
                var address = toAddr(Long.decode(candidate ? args[i].substring(10) : args[i]));
                var function = getFunctionContaining(address);
                if (candidate && function != null && !function.getEntryPoint().equals(address))
                    throw new IllegalStateException("Candidate overlaps function: " + address);
                if (candidate && function == null) {
                    if (!block.contains(address) || (address.getOffset() & 1) != 0)
                        throw new IllegalArgumentException("Candidate outside even-address image");
                    currentProgram.getProgramContext().setValue(
                        currentProgram.getRegister("TMode"), address, address, BigInteger.ONE);
                    disassemble(address);
                    function = createFunction(address, "candidate_" + address);
                }
                JsonObject row = new JsonObject();
                row.addProperty("query", address.toString());
                row.addProperty("entry_basis", candidate ? "LLVM-checked caller candidate" : "recorded containing function");
                if (function == null) {
                    row.addProperty("status", "no_recorded_function");
                } else {
                    row.addProperty("entry", function.getEntryPoint().toString());
                    var result = decompiler.decompileFunction(function, 45, monitor);
                    row.addProperty("status", result.decompileCompleted() ? "decompiled" : "failed");
                    row.addProperty("error", result.getErrorMessage());
                    if (result.getDecompiledFunction() != null)
                        row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                }
                rows.add(row);
            }
            JsonObject output = new JsonObject();
            output.addProperty("source_sha256", actual);
            output.addProperty("raw_base", Long.toHexString(BASE));
            output.addProperty("method", "hash-locked raw image; explicit LLVM-checked Thumb candidates; no device execution");
            output.add("functions", rows);
            Files.writeString(Path.of(args[0]), output.toString() + "\n");
        } finally {
            decompiler.dispose();
        }
    }
}
