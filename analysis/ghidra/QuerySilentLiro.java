// Consultas incrementales: conserva las funciones y anotaciones del proyecto.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class QuerySilentLiro extends GhidraScript {
    private record FirmwareProfile(String model, int size, String sha256, long constantEnd) {}

    private FirmwareProfile profileFor(long size) {
        // Solo se aceptan los dos originales verificados para esta comparación.
        if (size == 11427236) return new FirmwareProfile("ILCE-6000 3.21", 11427236,
            "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9", 0x43bc0000L);
        if (size == 13382836) return new FirmwareProfile("ILCE-6300 2.01", 13382836,
            "6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16", 0x43d00000L);
        throw new IllegalArgumentException("unsupported LIRO image size: " + size);
    }

    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output and Thumb addresses required");
        var memory = currentProgram.getMemory();
        FirmwareProfile profile = profileFor(memory.getSize());
        byte[] original = new byte[profile.size()];
        currentProgram.getMemory().getBytes(toAddr(0x43541000L), original);
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original));
        if (!digest.equals(profile.sha256()))
            throw new IllegalArgumentException("original LIRO bytes mismatch");
        // Hipótesis de análisis: código/pools previos al límite del perfil constantes.
        // Permite plegar literales PIC; los datos posteriores siguen escribibles.
        var codeBlock = memory.getBlock(toAddr(0x43541000L));
        var boundary = toAddr(profile.constantEnd());
        if (codeBlock.contains(boundary)) memory.split(codeBlock, boundary);
        codeBlock.setWrite(false);
        JsonArray rows = new JsonArray();
        DecompInterface decompiler = new DecompInterface();
        DecompileOptions options = new DecompileOptions();
        options.setRespectReadOnly(true);
        decompiler.setOptions(options);
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("decompiler open failed");
            for (int i = 1; i < args.length; i++) {
                boolean existingOnly = args[i].startsWith("@");
                boolean exact = args[i].startsWith("!"); // "!addr": forzar entrada exacta (sesión readOnly)
                Address address = toAddr(Long.decode(existingOnly || exact ? args[i].substring(1) : args[i]));
                Function function = getFunctionContaining(address);
                if (exact && function != null && !function.getEntryPoint().equals(address)) {
                    removeFunction(function);
                    function = null;
                }
                if (function == null && !existingOnly) {
                    // Solo fijar modo si no hay instrucción; nunca borrar el proyecto.
                    if (getInstructionAt(address) == null) {
                        currentProgram.getProgramContext().setValue(
                            currentProgram.getRegister("TMode"), address, address, BigInteger.ONE);
                        disassemble(address);
                    }
                    function = createFunction(address, "candidate_" + address);
                }
                JsonObject row = new JsonObject();
                row.addProperty("query", address.toString());
                if (function == null) {
                    row.addProperty("status", "function_not_created");
                } else {
                    row.addProperty("entry", function.getEntryPoint().toString());
                    DecompileResults result = decompiler.decompileFunction(function, 60, monitor);
                    row.addProperty("status", result.decompileCompleted() ? "decompiled" : "failed");
                    row.addProperty("error", result.getErrorMessage());
                    if (result.getDecompiledFunction() != null)
                        row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                    JsonArray callers = new JsonArray();
                    for (var ref : getReferencesTo(function.getEntryPoint())) callers.add(ref.getFromAddress().toString());
                    row.add("references", callers);
                }
                rows.add(row);
            }
        } finally { decompiler.dispose(); }
        JsonObject output = new JsonObject();
        output.addProperty("firmware_profile", profile.model());
        output.addProperty("source_size", profile.size());
        output.addProperty("source_sha256", digest);
        output.addProperty("method", "incremental caller-selected Thumb candidates; function boundaries inferred");
        output.addProperty("constant_memory_assumption", "43541000.." +
            Long.toHexString(profile.constantEnd()) + " marked read-only in analysis; bytes unchanged");
        output.add("functions", rows);
        Files.writeString(Path.of(args[0]), output.toString() + "\n");
        println("Exported " + rows.size() + " queries");
    }
}
