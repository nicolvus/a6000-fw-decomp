// S53: vuelca pseudocódigo de todas las funciones a un archivo (ruta en args[0]).
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import java.io.PrintWriter;

public class S53DumpDecomp extends GhidraScript {
    public void run() throws Exception {
        String out = getScriptArgs()[0];
        var di = new DecompInterface();
        di.openProgram(currentProgram);
        int n = 0;
        try (var w = new PrintWriter(out, "UTF-8")) {
            for (var f : currentProgram.getFunctionManager().getFunctions(true)) {
                var r = di.decompileFunction(f, 60, monitor);
                w.println("//==== FUNC " + f.getEntryPoint() + " " + f.getName() + " body=" + f.getBody().getNumAddresses());
                w.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// FAIL " + r.getErrorMessage());
                n++;
            }
        }
        println("S53 dump funcs=" + n);
    }
}
