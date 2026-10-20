// Retira funciones provisionales creadas sin prueba de una entrada ABI.
// Conserva instrucciones, bytes y exports históricos para auditar el descarte.
import ghidra.app.script.GhidraScript;

public class RemoveInteriorQueries extends GhidraScript {
    public void run() throws Exception {
        long[] addresses = {0x437b4ed2L, 0x436d6520L, 0x4378f4d0L};
        int removed = 0;
        for (long value : addresses) {
            var function = getFunctionAt(toAddr(value));
            if (function != null && function.getName().startsWith("candidate_")) {
                removeFunction(function);
                removed++;
            }
        }
        println("Removed " + removed + " unproven interior-query function definitions");
    }
}
