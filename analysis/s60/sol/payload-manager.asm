43b00b48 push {r4, r5, r6, lr}
43b00b4a mov r3, r0
43b00b4c mov r4, r0
43b00b4e movs r6, #0
43b00b50 str r6, [r0]
43b00b52 str.w r6, [r0, #0x568]
43b00b56 str.w r6, [r0, #0x56c]
43b00b5a strh.w r6, [r0, #0x570]
43b00b5e str.w r6, [r0, #0x574]
43b00b62 strh.w r6, [r0, #0x578]
43b00b66 strh.w r6, [r0, #0x57a]
43b00b6a strb.w r6, [r4, #0x57c]
43b00b6e strb.w r6, [r4, #0x57d]
43b00b72 strb.w r6, [r4, #0x57e]
43b00b76 strh.w r6, [r0, #0x580]
43b00b7a strh.w r6, [r0, #0x582]
43b00b7e strb.w r6, [r4, #0x584]
43b00b82 str.w r6, [r0, #0xd58]
43b00b86 strh.w r6, [r0, #0xd5c]
43b00b8a strb.w r6, [r4, #0xe94]
43b00b8e strb.w r6, [r4, #0xe95]
43b00b92 str.w r6, [r0, #0xea0]
43b00b96 strb.w r6, [r4, #0xea4]
43b00b9a str.w r6, [r0, #0xea8]
43b00b9e adds r2, r4, r6
43b00ba0 adds r6, #2
43b00ba2 movs r5, #0
43b00ba4 str.w r5, [r3, #0x588]
43b00ba8 adds r3, #4
43b00baa cmp r6, #0x10
43b00bac strh.w r5, [r2, #0x5a8]
43b00bb0 bne #0x43b00b9e
43b00bb2 adds r0, r4, #4
43b00bb4 mov r1, r5
43b00bb6 movw r2, #0x564
43b00bba blx #0x439c5a04
43b00bbe mov r1, r5
43b00bc0 mov r2, r6
43b00bc2 add.w r0, r4, #0x5b8
43b00bc6 blx #0x439c5a04
43b00bca movs r2, #0x94
43b00bcc mov r1, r5
43b00bce add.w r0, r4, #0x5c8
43b00bd2 blx #0x439c5a04
43b00bd6 add.w r0, r4, #0x650
43b00bda movs r2, #0xc
43b00bdc adds r0, #0xc
43b00bde mov r1, r5
43b00be0 blx #0x439c5a04
43b00be4 mov r1, r5
43b00be6 mov r2, r6
43b00be8 add.w r0, r4, #0x668
43b00bec blx #0x439c5a04
43b00bf0 movs r2, #0xc
43b00bf2 mov r1, r5
43b00bf4 add.w r0, r4, #0x678
43b00bf8 blx #0x439c5a04
43b00bfc add.w r0, r4, #0x680
43b00c00 movs r2, #0xc
43b00c02 adds r0, #4
43b00c04 mov r1, r5
43b00c06 blx #0x439c5a04
43b00c0a movs r2, #0x24
43b00c0c mov r1, r5
43b00c0e add.w r0, r4, #0x690
43b00c12 blx #0x439c5a04
43b00c16 add.w r0, r4, #0x6b0
43b00c1a movs r2, #0xc
43b00c1c adds r0, #4
43b00c1e mov r1, r5
43b00c20 blx #0x439c5a04
43b00c24 movs r2, #0x54
43b00c26 mov r1, r5
43b00c28 add.w r0, r4, #0xd60
43b00c2c blx #0x439c5a04
43b00c30 add.w r0, r4, #0xda0
43b00c34 movs r2, #0x50
43b00c36 adds r0, #0x14
43b00c38 mov r1, r5
43b00c3a blx #0x439c5a04
43b00c3e add.w r0, r4, #0xe00
43b00c42 movs r2, #0x50
43b00c44 adds r0, #4
43b00c46 mov r1, r5
43b00c48 blx #0x439c5a04
43b00c4c add.w r0, r4, #0xe40
43b00c50 movs r2, #0x18
43b00c52 adds r0, #0x14
43b00c54 mov r1, r5
43b00c56 blx #0x439c5a04
43b00c5a add.w r0, r4, #0xe60
43b00c5e adds r0, #0xc
43b00c60 mov r1, r5
43b00c62 movs r2, #0x14
43b00c64 blx #0x439c5a04
43b00c68 movs r2, #0x14
43b00c6a mov r1, r5
43b00c6c add.w r0, r4, #0xe80
43b00c70 blx #0x439c5a04
43b00c74 mov r1, r5
43b00c76 mov.w r2, #0x5e0
43b00c7a str.w r5, [r4, #0xe9c]
43b00c7e str.w r5, [r4, #0xe98]
43b00c82 add.w r0, r4, #0x6c0
43b00c86 blx #0x439c5a04
43b00c8a add.w r0, r4, #0xca0
43b00c8e mov r1, r5
43b00c90 movs r2, #0x28
43b00c92 blx #0x439c5a04
43b00c96 movs r2, #0x24
43b00c98 movs r1, #0
43b00c9a mul r0, r2, r5
43b00c9e adds r5, #1
43b00ca0 add.w r0, r0, #0xcc0
43b00ca4 adds r0, #8
43b00ca6 adds r0, r4, r0
43b00ca8 blx #0x439c5a04
43b00cac cmp r5, #4
43b00cae bne #0x43b00c96
43b00cb0 mov r0, r4
43b00cb2 pop {r4, r5, r6, pc}
43b00cb4 ldr.w r0, [r0, #0x568]
43b00cb8 bx lr
43b00cba ldrb.w r0, [r0, #0x57c]
43b00cbe bx lr
43b00cc0 ldr.w r3, [r0, #0x568]
43b00cc4 cmp r3, #1
43b00cc6 ite eq
43b00cc8 ldrbeq.w r0, [r0, #0x584]
43b00ccc movne r0, #0
43b00cce bx lr
43b00cd0 ldr.w r3, [r0, #0x568]
43b00cd4 push {r4, r5, r6, lr}
43b00cd6 cmp r3, #1
43b00cd8 mov r4, r0
43b00cda mov r5, r1
43b00cdc bne #0x43b00cf4
43b00cde ldr r3, [r0]
43b00ce0 add.w r0, r0, #0x6c0
43b00ce4 adds r0, #4
43b00ce6 movw r2, #0x564
43b00cea str.w r3, [r1, #0xb8]
43b00cee adds r1, r4, #4
43b00cf0 blx #0x439c5320
43b00cf4 add.w r0, r4, #8
43b00cf8 mov r1, r5
43b00cfa mov.w r2, #0x560
43b00cfe pop.w {r4, r5, r6, lr}
43b00d02 b.w #0x43b7f878
43b00d06 add.w r3, r0, #8
43b00d0a mov.w r2, #0x560
43b00d0e mov r0, r1
43b00d10 mov r1, r3
43b00d12 b.w #0x43b7f878
43b00d16 adds r0, #8
43b00d18 bx lr
43b00d1a ldr r3, [r1, #4]
43b00d1c push {r4, r5, lr}
43b00d1e cmp r3, #6
43b00d20 bhi #0x43b00d76
43b00d22 tbb [pc, r3]
43b00d26 lsls r4, r0, #0x1c
43b00d28 asrs r7, r1, #0xc
43b00d2a subs r0, r5, r0
43b00d2c movs r6, r3
43b00d2e add.w r4, r0, #0x5c0
43b00d32 b #0x43b00d50
43b00d34 add.w r0, r0, #0x5d0
43b00d38 adds r1, #8
43b00d3a movs r2, #0x8c
43b00d3c pop.w {r4, r5, lr}
43b00d40 b.w #0x43b7f878
43b00d44 ldr r3, [r1, #8]
43b00d46 str.w r3, [r0, #0x664]
43b00d4a pop {r4, r5, pc}
43b00d4c add.w r4, r0, #0x670
43b00d50 adds r1, #8
43b00d52 ldm r1, {r0, r1}
43b00d54 stm.w r4, {r0, r1}
43b00d58 pop {r4, r5, pc}
43b00d5a ldr r3, [r1, #8]
43b00d5c str.w r3, [r0, #0x68c]
43b00d60 pop {r4, r5, pc}
43b00d62 add.w r5, r1, #8
43b00d66 add.w r4, r0, #0x698
43b00d6a ldm r5!, {r0, r1, r2, r3}
43b00d6c stm r4!, {r0, r1, r2, r3}
43b00d6e ldm.w r5, {r0, r1, r2}
43b00d72 stm.w r4, {r0, r1, r2}
43b00d76 pop {r4, r5, pc}
43b00d78 ldr r3, [r1, #4]
43b00d7a cmp r3, #4
43b00d7c beq #0x43b00d84
43b00d7e cmp r3, #7
43b00d80 bne #0x43b00d92
43b00d82 b #0x43b00d8c
43b00d84 ldr r3, [r1, #8]
43b00d86 str.w r3, [r0, #0x680]
43b00d8a bx lr
43b00d8c ldr r3, [r1, #8]
43b00d8e str.w r3, [r0, #0x6bc]
43b00d92 bx lr
43b00d94 add.w r0, r0, #0xd60
43b00d98 movs r2, #0x50
43b00d9a adds r0, #4
43b00d9c b.w #0x43b7f878
43b00da0 add.w r0, r0, #0xda0
43b00da4 movs r2, #0x50
43b00da6 adds r0, #0x14
43b00da8 b.w #0x43b7f878
43b00dac push {r4, r5, lr}
43b00dae mov r5, r1
43b00db0 add.w r4, r0, #0xe40
43b00db4 ldm r5!, {r0, r1, r2, r3}
43b00db6 adds r4, #0x18
43b00db8 stm r4!, {r0, r1, r2, r3}
43b00dba ldr r2, [r5]
43b00dbc str r2, [r4]
43b00dbe pop {r4, r5, pc}
43b00dc0 push {r4, r5, lr}
43b00dc2 mov r5, r1
43b00dc4 add.w r4, r0, #0xe60
43b00dc8 ldm r5!, {r0, r1, r2, r3}
43b00dca adds r4, #0xc
43b00dcc stm r4!, {r0, r1, r2, r3}
43b00dce ldr r2, [r5]
43b00dd0 str r2, [r4]
43b00dd2 pop {r4, r5, pc}
43b00dd4 ldrb.w r3, [r0, #0x57c]
43b00dd8 push {r4, r5, r6, lr}
43b00dda mov r4, r0
43b00ddc cmp r3, #0
43b00dde beq #0x43b00e3e
43b00de0 add.w r6, r0, #0xd60
43b00de4 add.w r5, r4, #0xe40
43b00de8 adds r1, r6, #4
43b00dea bl #0x43b00da0
43b00dee mov r0, r4
43b00df0 add.w r1, r5, #0x18
43b00df4 bl #0x43b00dc0
43b00df8 ldr.w r3, [r4, #0x568]
43b00dfc cmp r3, #1
43b00dfe bne #0x43b00e1e
43b00e00 add.w r1, r4, #0xe00
43b00e04 mov r0, r4
43b00e06 adds r1, #4
43b00e08 bl #0x43b00d94
43b00e0c add.w r0, r4, #0xc40
43b00e10 adds r0, #0xc
43b00e12 mov r1, r6
43b00e14 movs r2, #0x54
43b00e16 pop.w {r4, r5, r6, lr}
43b00e1a b.w #0x43b7f878
43b00e1e cmp r3, #2
43b00e20 bne #0x43b00e3e
43b00e22 adds r5, #0x14
43b00e24 mov r0, r4
43b00e26 add.w r1, r4, #0xe80
43b00e2a add.w r4, r4, #0xcb0
43b00e2e bl #0x43b00dac
43b00e32 ldm r5!, {r0, r1, r2, r3}
43b00e34 stm r4!, {r0, r1, r2, r3}
43b00e36 ldm.w r5, {r0, r1}
43b00e3a stm.w r4, {r0, r1}
43b00e3e pop {r4, r5, r6, pc}
43b00e40 ldr r3, [r1, #0x50]
43b00e42 ldrb.w r3, [r3, #0x4c]
43b00e46 strb.w r3, [r0, #0xea4]
43b00e4a bx lr
43b00e4c ldr r3, [r1, #4]
43b00e4e ldr r3, [r3, #0xc]
43b00e50 cbnz r3, #0x43b00e58
43b00e52 ldr.w r3, [r0, #0xd1c]
43b00e56 str r3, [r2]
43b00e58 bx lr
43b00e5a push {r3, lr}
43b00e5c ldr.w r3, [r0, #0x568]
43b00e60 cmp r3, #1
43b00e62 bne #0x43b00e70
43b00e64 bl #0x43ae8488
43b00e68 ldrb r0, [r0, #2]
43b00e6a eor r0, r0, #1
43b00e6e pop {r3, pc}
43b00e70 movs r0, #1
43b00e72 pop {r3, pc}
43b00e74 push {r3, r4, r5, lr}
43b00e76 mov r4, r0
43b00e78 ldr.w r3, [r0, #0x568]
43b00e7c mov r5, r1
43b00e7e cmp r3, #1
43b00e80 bne #0x43b00e98
43b00e82 bl #0x43b00cb4
43b00e86 ldrh.w r3, [r4, #0x57a]
43b00e8a add.w r5, r5, #0x2d4
43b00e8e adds r2, r3, #1
43b00e90 strh.w r2, [r4, #0x57a]
43b00e94 strh.w r3, [r4, r5, lsl #1]
43b00e98 pop {r3, r4, r5, pc}
43b00e9a push {r3, r4, r5, lr}
43b00e9c mov r4, r0
43b00e9e ldr.w r3, [r0, #0x568]
43b00ea2 mov r5, r1
43b00ea4 cmp r3, #2
43b00ea6 bne #0x43b00ebe
43b00ea8 bl #0x43b00cb4
43b00eac ldrh.w r3, [r4, #0x57a]
43b00eb0 add.w r5, r5, #0x2d4
43b00eb4 adds r2, r3, #1
43b00eb6 strh.w r2, [r4, #0x57a]
43b00eba strh.w r3, [r4, r5, lsl #1]
43b00ebe pop {r3, r4, r5, pc}
43b00ec0 push {r4, lr}
43b00ec2 mov r4, r0
43b00ec4 bl #0x43b00cb4
43b00ec8 ldrh.w r3, [r4, #0x57a]
43b00ecc adds r3, #1
43b00ece strh.w r3, [r4, #0x57a]
43b00ed2 pop {r4, pc}
43b00ed4 movs r0, #1
43b00ed6 bx lr
43b00ed8 ldr.w r2, [r0, #0x568]
43b00edc mov r3, r0
43b00ede cmp r2, #1
43b00ee0 bne #0x43b00f08
43b00ee2 ldr r1, [r1, #8]
43b00ee4 ldrh.w r1, [r1, #0x26c]
43b00ee8 sub.w r1, r1, #0x120
43b00eec uxth r0, r1
43b00eee cmp r0, #0xe
43b00ef0 bhi #0x43b00f02
43b00ef2 sxth r1, r1
43b00ef4 lsls r2, r1
43b00ef6 movw r1, #0x7f9b
43b00efa and.w r1, r2, r1
43b00efe cmp r1, #0
43b00f00 bne #0x43b00f20
43b00f02 mov r0, r3
43b00f04 b.w #0x43806398
43b00f08 cmp r2, #2
43b00f0a bne #0x43b00f20
43b00f0c ldr r3, [r1, #8]
43b00f0e ldrh.w r3, [r3, #0x224]
43b00f12 sub.w r3, r3, #0x124
43b00f16 subs r3, #1
43b00f18 cmp r3, #1
43b00f1a bls #0x43b00f20
43b00f1c b.w #0x4380632c
43b00f20 bx lr
43b00f22 ldr.w r3, [r0, #0x568]
43b00f26 push {r4, lr}
43b00f28 cmp r3, #2
43b00f2a mov r4, r0
43b00f2c bne #0x43b00f60
43b00f2e adds r3, #8
43b00f30 strb.w r3, [r0, #0xca0]
43b00f34 bl #0x43b00cb4
43b00f38 ldrh.w r3, [r4, #0x57a]
43b00f3c add.w r1, r4, #0xca0
43b00f40 adds r2, r3, #1
43b00f42 strh.w r2, [r4, #0x57a]
43b00f46 strh.w r3, [r4, #0xca2]
43b00f4a movs r2, #0x28
43b00f4c strh.w r3, [r4, #0x570]
43b00f50 strb.w r0, [r4, #0xca1]
43b00f54 mov r0, r4
43b00f56 bl #0x43806400
43b00f5a cbnz r0, #0x43b00f60
43b00f5c str.w r0, [r4, #0x56c]
43b00f60 pop {r4, pc}
43b00f62 ldr.w r3, [r0, #0x568]
43b00f66 push {r4, lr}
43b00f68 cmp r3, #1
43b00f6a mov r4, r0
43b00f6c bne #0x43b00fa2
43b00f6e adds r3, #9
43b00f70 strb.w r3, [r0, #0x6c0]
43b00f74 bl #0x43b00cb4
43b00f78 ldrh.w r3, [r4, #0x57a]
43b00f7c add.w r1, r4, #0x6c0
43b00f80 adds r2, r3, #1
43b00f82 strh.w r2, [r4, #0x57a]
43b00f86 strh.w r3, [r4, #0x6c2]
43b00f8a mov.w r2, #0x5e0
43b00f8e strh.w r3, [r4, #0x570]
43b00f92 strb.w r0, [r4, #0x6c1]
43b00f96 mov r0, r4
43b00f98 bl #0x43806400
43b00f9c cbnz r0, #0x43b00fa2
43b00f9e str.w r0, [r4, #0x56c]
43b00fa2 pop {r4, pc}
43b00fa4 ldr.w r3, [r0, #0x568]
43b00fa8 push {r4, lr}
43b00faa cmp r3, #2
43b00fac mov r4, r0
43b00fae bne #0x43b00fe4
43b00fb0 adds r3, #2
43b00fb2 strb.w r3, [r0, #0xe54]
43b00fb6 bl #0x43b00cb4
43b00fba ldrh.w r3, [r4, #0x57a]
43b00fbe add.w r1, r4, #0xe40
43b00fc2 adds r2, r3, #1
43b00fc4 adds r1, #0x14
43b00fc6 strh.w r2, [r4, #0x57a]
43b00fca movs r2, #0x18
43b00fcc strh.w r3, [r4, #0xe56]
43b00fd0 strh.w r3, [r4, #0xd5c]
43b00fd4 strb.w r0, [r4, #0xe55]
43b00fd8 mov r0, r4
43b00fda bl #0x43806400
43b00fde cbnz r0, #0x43b00fe4
43b00fe0 str.w r0, [r4, #0xd58]
43b00fe4 pop {r4, pc}
43b00fe6 ldr.w r3, [r0, #0x568]
43b00fea push {r4, lr}
43b00fec cmp r3, #1
43b00fee mov r4, r0
43b00ff0 bne #0x43b01024
43b00ff2 adds r3, #3
43b00ff4 strb.w r3, [r0, #0xd60]
43b00ff8 bl #0x43b00cb4
43b00ffc ldrh.w r3, [r4, #0x57a]
43b01000 add.w r1, r4, #0xd60
43b01004 adds r2, r3, #1
43b01006 strh.w r2, [r4, #0x57a]
43b0100a strh.w r3, [r4, #0xd62]
43b0100e movs r2, #0x54
43b01010 strh.w r3, [r4, #0xd5c]
43b01014 strb.w r0, [r4, #0xd61]
43b01018 mov r0, r4
43b0101a bl #0x43806400
43b0101e cbnz r0, #0x43b01024
43b01020 str.w r0, [r4, #0xd58]
43b01024 pop {r4, pc}
43b01026 ldr.w r3, [r0, #0x568]
43b0102a push {r4, lr}
43b0102c cmp r3, #1
43b0102e mov r4, r0
43b01030 bne #0x43b0105c
43b01032 strb r3, [r0, #4]
43b01034 bl #0x43b00cb4
43b01038 ldrh.w r3, [r4, #0x57a]
43b0103c adds r1, r4, #4
43b0103e adds r2, r3, #1
43b01040 strh.w r2, [r4, #0x57a]
43b01044 strh r3, [r4, #6]
43b01046 movw r2, #0x564
43b0104a strh.w r3, [r4, #0x578]
43b0104e strb r0, [r4, #5]
43b01050 mov r0, r4
43b01052 bl #0x43806400
43b01056 cbnz r0, #0x43b0105c
43b01058 str.w r0, [r4, #0x574]
43b0105c pop {r4, pc}
