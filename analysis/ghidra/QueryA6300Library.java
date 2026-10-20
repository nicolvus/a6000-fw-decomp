// Consultas ELF acotadas a entradas verificadas en .ARM.exidx; sin autoanálisis global.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.ParameterImpl;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.TreeSet;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class QueryA6300Library extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output and ELF virtual entries required");
        byte[] source = Files.readAllBytes(Path.of(currentProgram.getExecutablePath()));
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(source));
        if (!digest.equals("c70b635bcbd386b4b34b6a5c37ef941a1463253aebb43d83fada7fe4e9fe9073"))
            throw new IllegalArgumentException("verified A6300 libObj required");
        if (!digest.equals(currentProgram.getExecutableSHA256()))
            throw new IllegalStateException("loaded ELF identity mismatch");
        // PT_LOAD mínimo = 0 en este original. Ghidra puede reubicar el ELF DYN.
        long bias = currentProgram.getImageBase().getOffset();
        var bytes = ByteBuffer.wrap(source).order(ByteOrder.LITTLE_ENDIAN);
        var unwindEntries = new TreeSet<Long>();
        for (int offset = 0xf3b894; offset < 0xf3b894 + 0x70170; offset += 8) {
            int relative = (bytes.getInt(offset) << 1) >> 1;
            unwindEntries.add((offset + (long)relative) & 0xffffffffL);
        }
        DecompInterface decompiler = new DecompInterface();
        DecompileOptions options = new DecompileOptions();
        options.setRespectReadOnly(true);
        decompiler.setOptions(options);
        JsonArray rows = new JsonArray();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("decompiler unavailable");
            for (int i = 1; i < args.length; i++) {
                boolean splitCandidate = args[i].startsWith("candidate:");
                long elfEntry = Long.decode(splitCandidate ? args[i].substring(10) : args[i]);
                if (!splitCandidate && !unwindEntries.contains(elfEntry))
                    throw new IllegalArgumentException("not an .ARM.exidx entry: " + args[i]);
                var address = toAddr(elfEntry + bias);
                var function = getFunctionAt(address);
                if (function == null) {
                    if (getFunctionContaining(address) != null)
                        throw new IllegalStateException("overlapping inferred function at " + address);
                    if (getInstructionAt(address) == null) {
                        currentProgram.getProgramContext().setValue(
                            currentProgram.getRegister("TMode"), address, address, BigInteger.ONE);
                        disassemble(address);
                    }
                    function = createFunction(address, "elf_" + Long.toHexString(elfEntry));
                }
                JsonObject row = new JsonObject();
                row.addProperty("elf_entry", Long.toHexString(elfEntry));
                row.addProperty("ghidra_entry", address.toString());
                row.addProperty("entry_basis", splitCandidate
                    ? "caller-selected split candidate; independently verify instructions"
                    : "recorded .ARM.exidx entry; adjacent functions may share unwind record");
                row.addProperty("unwind_predecessor", Long.toHexString(unwindEntries.floor(elfEntry)));
                if (function == null) row.addProperty("status", "function_not_created");
                else {
                    // 9418c2 llama al traductor de estado; el epílogo conserva R0.
                    if (elfEntry == 0x941860L) {
                        function.setReturnType(UnsignedIntegerDataType.dataType, SourceType.ANALYSIS);
                        var names = new String[]{"sender", "data", "length", "prefix", "prefixLength"};
                        var parameters = new ParameterImpl[names.length];
                        for (int n = 0; n < names.length; n++)
                            parameters[n] = new ParameterImpl(names[n], UnsignedIntegerDataType.dataType, currentProgram);
                        function.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                            true, SourceType.ANALYSIS, parameters);
                        row.addProperty("return_type_basis", "LLVM 9418c2..9418cc preserves mapper result in R0");
                        row.addProperty("parameter_basis", "adbf58 caller and 941860 body: R0 sender, R1 data, R2 length, R3 prefix, stack prefixLength");
                    }
                    var result = decompiler.decompileFunction(function, 45, monitor);
                    row.addProperty("status", result.decompileCompleted() ? "decompiled" : "failed");
                    row.addProperty("error", result.getErrorMessage());
                    if (result.getDecompiledFunction() != null)
                        row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                }
                rows.add(row);
            }
        } finally { decompiler.dispose(); }
        JsonObject output = new JsonObject();
        output.addProperty("source_sha256", digest);
        output.addProperty("image_bias", Long.toHexString(bias));
        output.addProperty("method", "ELF loader relocations; caller-selected Thumb entries corroborated by .ARM.exidx; no broad analysis");
        output.addProperty("limitation", "Unwind entries can cover merged adjacent functions; verify each entry and use, not total coverage");
        output.add("functions", rows);
        Files.writeString(Path.of(args[0]), output + "\n");
        println("Exported ELF queries: " + rows.size());
    }
}
