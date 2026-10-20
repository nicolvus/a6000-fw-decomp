// Decompila funciones Thumb/ARM en direcciones dadas (VA del programa importado); crea la función si falta. Uso: -postScript DecompAt.java salida.json 0xADDR...
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.lang.Register;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class DecompAt extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        JsonArray out = new JsonArray();
        Register tmode = currentProgram.getLanguage().getRegister("TMode");
        for (int i = 1; i < a.length; i++) {
            long v = Long.decode(a[i].replace("t", ""));
            boolean thumb = (v & 1) != 0 || a[i].endsWith("t");
            Address ad = toAddr(v & ~1L);
            if (tmode != null && thumb) currentProgram.getProgramContext().setValue(tmode, ad, ad, BigInteger.ONE);
            Function f = getFunctionAt(ad);
            if (f == null) { disassemble(ad); f = createFunction(ad, null); }
            JsonObject o = new JsonObject();
            o.addProperty("entry", ad.toString());
            if (f == null) { o.addProperty("status", "no function"); }
            else {
                var r = di.decompileFunction(f, 120, monitor);
                o.addProperty("status", r.decompileCompleted() ? "ok" : "fail");
                if (r.decompileCompleted()) o.addProperty("pseudo_code", r.getDecompiledFunction().getC());
            }
            out.add(o);
        }
        Files.writeString(Path.of(a[0]), out.toString());
    }
}
