43792f40 ldrb.w r3, [r8, #1]
43792f44 cbnz r3, #0x43792f54
43792f46 bl #0x4378f9b4
43792f4a ldr r3, [r0, #4]
43792f4c ldr r3, [r3]
43792f4e adds r3, #5
43792f50 str.w r3, [sl, #0x204]
43792f54 mov r0, sb
43792f56 bl #0x43b00cba
43792f5a cbz r0, #0x43792f84
43792f5c mov r0, sb
43792f5e ldr.w r7, [pc, #0x6dc] ; lit=0x70629a
43792f62 bl #0x43b00dd4
43792f66 ldr.w r2, [pc, #0x6d8] ; lit=0x7085d6
43792f6a add r7, pc
43792f6c mov r0, sb
43792f6e add r2, pc
43792f70 mov r1, r7
43792f72 add.w r3, r2, #0x5a0
43792f76 adds r3, #4
