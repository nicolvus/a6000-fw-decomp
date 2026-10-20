import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
public class Summary extends GhidraScript {
  public void run() throws Exception {
    int n=0; for (Function f: currentProgram.getFunctionManager().getFunctions(true)) n++;
    println("SUMMARY lang="+currentProgram.getLanguageID()+" funcs="+n+" blocks="+currentProgram.getMemory().getBlocks().length+" strings="+currentProgram.getListing().getDefinedData(true).iterator().hasNext());
  }
}
