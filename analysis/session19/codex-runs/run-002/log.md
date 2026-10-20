# S19-02 run log

Read-only commands used:

- `llvm-objdump -d --triple=thumbv7-linux-gnueabi` on the five candidate libraries, `libObj.so`, and `libMWF.so`.
- `readelf -rW/-Ws` to correlate PLT slots and `R_ARM_JUMP_SLOT` relocations.
- raw little-endian words at `libObj.so:0xcc6694` to recover the three Thumb vtable slots.

No Ghidra project, original firmware binary, camera, network resource, package, Git repository, or external process was changed or used.

Conclusion: the wrapper/UObjPin-to-MWF path is statically verified; the LifeCycle-to-Connect execution edge remains unverified.
