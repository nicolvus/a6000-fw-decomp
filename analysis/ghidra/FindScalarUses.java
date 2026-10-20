// Busca instrucciones cuyo operando escalar (inmediato) coincide con un valor dado.
// Uso: -postScript FindScalarUses.java salida.json 0xVALOR [0xVALOR2 ...]
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import java.nio.file.Files;
import java.nio.file.Path;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class FindScalarUses extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        long[] targets = new long[args.length - 1];
        for (int i = 1; i < args.length; i++) targets[i - 1] = Long.decode(args[i]);
        JsonArray out = new JsonArray();
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        int count = 0;
        while (it.hasNext() && count < 20000) {
            Instruction ins = it.next();
            int n = ins.getNumOperands();
            for (int op = 0; op < n; op++) {
                for (Object o : ins.getOpObjects(op)) {
                    if (o instanceof Scalar) {
                        long v = ((Scalar) o).getValue();
                        for (long t : targets) {
                            if (v == t) {
                                JsonObject row = new JsonObject();
                                row.addProperty("target", "0x" + Long.toHexString(t));
                                row.addProperty("at", ins.getAddress().toString());
                                row.addProperty("mnemonic", ins.getMnemonicString());
                                var fn = getFunctionContaining(ins.getAddress());
                                row.addProperty("function", fn != null ? fn.getEntryPoint().toString() : null);
                                out.add(row);
                                count++;
                            }
                        }
                    }
                }
            }
        }
        JsonObject result = new JsonObject();
        result.addProperty("note", "escaneo lineal de instrucciones ya desensambladas en el proyecto; no reanaliza, no crea funciones nuevas");
        result.add("hits", out);
        Files.writeString(Path.of(args[0]), result.toString() + "\n");
        println("FindScalarUses: " + out.size() + " hits");
    }
}
