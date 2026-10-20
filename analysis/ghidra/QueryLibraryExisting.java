// Exporta funciones existentes o candidatos Thumb, sin cambiar el contexto de instrucciones existentes.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.listing.Function;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class QueryLibraryExisting extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        JsonArray rows = new JsonArray();
        try {
            for (int index = 1; index < args.length; index++) {
                var address = toAddr(Long.decode(args[index]) & ~1L);
                JsonObject row = new JsonObject();
                row.addProperty("query", address.toString());
                try {
                    Function function = getFunctionContaining(address);
                    if (function == null) {
                        var mode = currentProgram.getLanguage().getRegister("TMode");
                        if (getInstructionAt(address) == null && mode != null) {
                            currentProgram.getProgramContext().setValue(mode, address, address, BigInteger.ONE);
                        }
                        disassemble(address);
                        function = createFunction(address, null);
                    }
                    if (function == null) {
                        row.addProperty("status", "no_function");
                    } else {
                        row.addProperty("entry", function.getEntryPoint().toString());
                        var result = decompiler.decompileFunction(function, 90, monitor);
                        row.addProperty("status", result.decompileCompleted() ? "ok" : "failed");
                        if (result.decompileCompleted()) {
                            row.addProperty("pseudo_code", result.getDecompiledFunction().getC());
                        }
                    }
                } catch (Exception error) {
                    row.addProperty("status", "error");
                    row.addProperty("error", error.toString());
                }
                rows.add(row);
            }
            Files.writeString(Path.of(args[0]), rows.toString());
        } finally {
            decompiler.dispose();
        }
    }
}
