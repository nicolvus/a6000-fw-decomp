import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Inventario de constantes y cadenas del programa cargado, solo lectura. */
public class S41Scan extends GhidraScript {
 public void run() throws Exception {
  byte[] b=Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
  String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));
  if(!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"))throw new Exception("SHA mismatch");
  byte[] loaded=new byte[b.length];currentProgram.getMemory().getBytes(toAddr(0x43541000L),loaded);if(!Arrays.equals(b,loaded))throw new Exception("Memory mismatch");
  JsonObject root=new JsonObject();root.addProperty("sha256",sha);JsonArray hits=new JsonArray();
  for(int i=0;i<b.length-4;i++) {
   long v=(b[i]&255L)|((b[i+1]&255L)<<8)|((b[i+2]&255L)<<16)|((b[i+3]&255L)<<24);
   if(v==0x30001L||v==0x3030fL||v==0x43806e39L||(v&0xffff0000L)==0x30230000L) {
    JsonObject h=new JsonObject();long a=0x43541000L+i;h.addProperty("address",Long.toHexString(a));h.addProperty("value",Long.toHexString(v));JsonArray refs=new JsonArray();
    for(var r:getReferencesTo(toAddr(a))) {JsonObject q=new JsonObject();q.addProperty("ref",r.toString());var f=getFunctionContaining(r.getFromAddress());if(f!=null)q.addProperty("function",f.getEntryPoint().toString());refs.add(q);}h.add("references",refs);hits.add(h);
   }
  }
  root.add("constants",hits);JsonArray commands=new JsonArray();var instructions=currentProgram.getListing().getInstructions(true);
  while(instructions.hasNext()){var ins=instructions.next();String s=ins.toString();
   if(s.matches(".*#0x(4000|4036|3023)(,.*)?$")||(ins.getAddress().getOffset()>=0x43816000L&&ins.getAddress().getOffset()<0x4381a200L&&s.endsWith("#0x23"))){JsonObject h=new JsonObject();h.addProperty("instruction",ins.getAddress()+" "+s);var f=getFunctionContaining(ins.getAddress());if(f!=null)h.addProperty("function",f.getEntryPoint().toString());commands.add(h);}}
  root.add("command_instructions",commands);JsonArray strings=new JsonArray();
  for(int start=0;start<b.length;) {int end=start;while(end<b.length&&b[end]>=32&&b[end]<127)end++;
   if(end-start>=4) {String s=new String(b,start,end-start,java.nio.charset.StandardCharsets.US_ASCII);
    if(s.toLowerCase().matches(".*(setmode|setexposure|integration|readout|vmax|hmax|imx210|messagequeue|osal.*(receive|send)|receive.*message).*")) {JsonObject h=new JsonObject();h.addProperty("address",Long.toHexString(0x43541000L+start));h.addProperty("text",s);strings.add(h);}}
   start=end+1;
  }root.add("strings",strings);Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(root));println("S41 scan complete");
 }
}
