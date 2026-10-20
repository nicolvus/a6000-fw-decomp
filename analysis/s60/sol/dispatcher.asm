438069f0 push.w {r4, r5, r6, r7, r8, lr}
438069f4 mov r4, r0
438069f6 ldr r3, [pc, #0x3d8] ; lit=0x8184e4
438069f8 mov r5, r1
438069fa ldrb r2, [r1]
438069fc add r3, pc
438069fe cmp r2, #0xb
43806a00 bhi.w #0x43806dcc
43806a04 tbh [pc, r2, lsl #1]
43806a08 movs r4, r1
43806a0a movs r7, r4
43806a0c lsls r3, r1, #1
43806a0e lsls r3, r5, #3
43806a10 lsls r0, r2, #4
43806a12 lsls r3, r7, #4
43806a14 lsls r3, r5, #1
43806a16 lsls r2, r2, #2
43806a18 lsls r6, r0, #3
43806a1a lsls r3, r3, #5
43806a1c lsls r7, r7, #5
43806a1e lsls r0, r0, #7
43806a20 ldr r2, [pc, #0x3b0] ; lit=0x6588
43806a22 ldr r6, [r3, r2]
43806a24 ldrb.w r3, [r6, #0x40]
43806a28 tst.w r3, #0x40
43806a2c beq #0x43806a36
43806a2e ldr r0, [pc, #0x3a8] ; lit=0x4a90b6
43806a30 add r0, pc
43806a32 bl #0x43561540
43806a36 mov r0, r4
43806a38 mov r1, r5
43806a3a bl #0x438066d4
43806a3e mov r0, r4
43806a40 bl #0x43b01026
43806a44 ldrb.w r3, [r6, #0x40]
43806a48 tst.w r3, #0x40
43806a4c beq.w #0x43806dcc
43806a50 ldr r0, [pc, #0x388] ; lit=0x4a90a4
43806a52 add r0, pc
43806a54 b #0x43806dc4
43806a56 ldr r2, [pc, #0x37c] ; lit=0x6588
43806a58 ldr r6, [r3, r2]
43806a5a ldrb.w r3, [r6, #0x40]
43806a5e tst.w r3, #0x40
43806a62 beq #0x43806a6c
43806a64 ldr r0, [pc, #0x378] ; lit=0x4a909e
43806a66 add r0, pc
43806a68 bl #0x43561540
43806a6c mov r0, r4
43806a6e mov r1, r5
43806a70 bl #0x438066d4
43806a74 ldr.w r3, [r4, #0x568]
43806a78 adds r1, r5, #4
43806a7a mov r0, r4
43806a7c str.w r3, [r5, #0xb8]
43806a80 bl #0x43b00cd0
43806a84 mov r0, r4
43806a86 ldrh r1, [r5, #2]
43806a88 bl #0x43806668
43806a8c ldrb.w r3, [r6, #0x40]
43806a90 tst.w r3, #0x40
43806a94 beq.w #0x43806dcc
43806a98 ldr r0, [pc, #0x348] ; lit=0x4a9077
43806a9a add r0, pc
43806a9c b #0x43806dc4
43806a9e ldr r2, [pc, #0x334] ; lit=0x6588
43806aa0 ldr r6, [r3, r2]
43806aa2 ldrb.w r3, [r6, #0x40]
43806aa6 tst.w r3, #0x40
43806aaa beq #0x43806ab4
43806aac ldr r0, [pc, #0x338] ; lit=0x4a906e
43806aae add r0, pc
43806ab0 bl #0x43561540
43806ab4 mov r0, r4
43806ab6 mov r1, r5
43806ab8 bl #0x438066d4
43806abc ldrh.w r2, [r4, #0x578]
43806ac0 ldrh r3, [r5, #4]
43806ac2 cmp r2, r3
43806ac4 bne #0x43806acc
43806ac6 movs r3, #0
43806ac8 str.w r3, [r4, #0x574]
43806acc ldrb.w r3, [r6, #0x40]
43806ad0 tst.w r3, #0x40
43806ad4 beq.w #0x43806dcc
43806ad8 ldr r0, [pc, #0x310] ; lit=0x4a9052
43806ada add r0, pc
43806adc b #0x43806dc4
43806ade ldr r2, [pc, #0x2f4] ; lit=0x6588
43806ae0 ldr r6, [r3, r2]
43806ae2 ldrb.w r3, [r6, #0x40]
43806ae6 tst.w r3, #0x40
43806aea beq #0x43806af4
43806aec ldr r0, [pc, #0x300] ; lit=0x4a904c
43806aee add r0, pc
43806af0 bl #0x43561540
43806af4 mov r0, r4
43806af6 mov r1, r5
43806af8 bl #0x438066d4
43806afc ldr.w r3, [r4, #0x568]
43806b00 cmp r3, #1
43806b02 bne #0x43806b0e
43806b04 mov r0, r4
43806b06 ldr r1, [r5, #4]
43806b08 bl #0x43b00e74
43806b0c b #0x43806b1a
43806b0e cmp r3, #2
43806b10 bne #0x43806b1a
43806b12 mov r0, r4
43806b14 ldr r1, [r5, #4]
43806b16 bl #0x43b00e9a
43806b1a ldrb.w r3, [r6, #0x40]
43806b1e tst.w r3, #0x40
43806b22 beq.w #0x43806dcc
43806b26 ldr r0, [pc, #0x2cc] ; lit=0x4a9022
43806b28 add r0, pc
43806b2a b #0x43806dc4
43806b2c ldr r2, [pc, #0x2a4] ; lit=0x6588
43806b2e ldr r6, [r3, r2]
43806b30 ldrb.w r3, [r6, #0x40]
43806b34 tst.w r3, #0x40
43806b38 beq #0x43806b42
43806b3a ldr r0, [pc, #0x2bc] ; lit=0x4a901c
43806b3c add r0, pc
43806b3e bl #0x43561540
43806b42 mov r0, r4
43806b44 mov r1, r5
43806b46 bl #0x438066d4
43806b4a ldr.w r3, [r4, #0x568]
43806b4e cmp r3, #1
43806b50 bne #0x43806b5c
43806b52 mov r0, r4
43806b54 mov r1, r5
43806b56 bl #0x43b00d78
43806b5a b #0x43806b68
43806b5c cmp r3, #2
43806b5e bne #0x43806b68
43806b60 mov r0, r4
43806b62 mov r1, r5
43806b64 bl #0x43b00d1a
43806b68 ldrb.w r3, [r6, #0x49]
43806b6c cbz r3, #0x43806b78
43806b6e ldr r3, [r5, #4]
43806b70 cmp r3, #7
43806b72 beq #0x43806b78
43806b74 cmp r3, #6
43806b76 bne #0x43806b82
43806b78 mov r0, r4
43806b7a ldrh r1, [r5, #2]
43806b7c ldr r2, [r5, #4]
43806b7e bl #0x43b00ec0
43806b82 ldrb.w r3, [r6, #0x40]
43806b86 tst.w r3, #0x40
43806b8a beq.w #0x43806dcc
43806b8e ldr r0, [pc, #0x26c] ; lit=0x4a8fd5
43806b90 add r0, pc
43806b92 b #0x43806dc4
43806b94 ldr r2, [pc, #0x23c] ; lit=0x6588
43806b96 ldr r6, [r3, r2]
43806b98 ldrb.w r3, [r6, #0x40]
43806b9c tst.w r3, #0x40
43806ba0 beq #0x43806baa
43806ba2 ldr r0, [pc, #0x25c] ; lit=0x4a8fcc
43806ba4 add r0, pc
43806ba6 bl #0x43561540
43806baa mov r1, r5
43806bac mov r0, r4
43806bae bl #0x438066d4
43806bb2 ldr r3, [r5, #4]
43806bb4 add.w r2, r3, #0x2d4
43806bb8 ldrh.w r1, [r4, r2, lsl #1]
43806bbc ldrh r2, [r5, #8]
43806bbe cmp r1, r2
43806bc0 bne #0x43806bcc
43806bc2 add.w r3, r3, #0x162
43806bc6 movs r2, #0
43806bc8 str.w r2, [r4, r3, lsl #2]
43806bcc ldrb.w r3, [r6, #0x40]
43806bd0 tst.w r3, #0x40
43806bd4 beq.w #0x43806dcc
43806bd8 ldr r0, [pc, #0x228] ; lit=0x4a8fa6
43806bda add r0, pc
43806bdc b #0x43806dc4
43806bde ldr r2, [pc, #0x1f4] ; lit=0x6588
43806be0 ldr r6, [r3, r2]
43806be2 ldrb.w r3, [r6, #0x40]
43806be6 tst.w r3, #0x40
43806bea beq #0x43806bf4
43806bec ldr r0, [pc, #0x218] ; lit=0x4a8fa0
43806bee add r0, pc
43806bf0 bl #0x43561540
43806bf4 mov r0, r4
43806bf6 mov r1, r5
43806bf8 bl #0x438066d4
43806bfc ldr.w r3, [r4, #0x568]
43806c00 cmp r3, #1
43806c02 bne #0x43806c0c
43806c04 mov r0, r4
43806c06 bl #0x43b00fe6
43806c0a b #0x43806c16
43806c0c cmp r3, #2
43806c0e bne #0x43806c16
43806c10 mov r0, r4
43806c12 bl #0x43b00fa4
43806c16 ldrb.w r3, [r6, #0x40]
43806c1a tst.w r3, #0x40
43806c1e beq.w #0x43806dcc
43806c22 ldr r0, [pc, #0x1e8] ; lit=0x4a8f79
43806c24 add r0, pc
43806c26 b #0x43806dc4
43806c28 ldr r2, [pc, #0x1a8] ; lit=0x6588
43806c2a ldr r6, [r3, r2]
43806c2c ldrb.w r3, [r6, #0x40]
43806c30 tst.w r3, #0x40
43806c34 beq #0x43806c3e
43806c36 ldr r0, [pc, #0x1d8] ; lit=0x4a8f72
43806c38 add r0, pc
43806c3a bl #0x43561540
43806c3e mov r0, r4
43806c40 mov r1, r5
43806c42 bl #0x438066d4
43806c46 ldr.w r3, [r4, #0x568]
43806c4a cmp r3, #1
43806c4c bne #0x43806c58
43806c4e mov r0, r4
43806c50 adds r1, r5, #4
43806c52 bl #0x43b00dac
43806c56 b #0x43806c64
43806c58 cmp r3, #2
43806c5a bne #0x43806c64
43806c5c mov r0, r4
43806c5e adds r1, r5, #4
43806c60 bl #0x43b00d94
43806c64 mov r0, r4
43806c66 ldrh r1, [r5, #2]
43806c68 bl #0x438065fc
43806c6c ldrb.w r3, [r6, #0x40]
43806c70 tst.w r3, #0x40
43806c74 beq.w #0x43806dcc
43806c78 ldr r0, [pc, #0x198] ; lit=0x4a8f3c
43806c7a add r0, pc
43806c7c b #0x43806dc4
43806c7e ldr r2, [pc, #0x154] ; lit=0x6588
43806c80 ldr r6, [r3, r2]
43806c82 ldrb.w r3, [r6, #0x40]
43806c86 tst.w r3, #0x40
43806c8a beq #0x43806c94
43806c8c ldr r0, [pc, #0x188] ; lit=0x4a8f32
43806c8e add r0, pc
43806c90 bl #0x43561540
43806c94 mov r0, r4
43806c96 mov r1, r5
43806c98 bl #0x438066d4
43806c9c ldrh.w r2, [r4, #0xd5c]
43806ca0 ldrh r3, [r5, #4]
43806ca2 cmp r2, r3
43806ca4 bne #0x43806cac
43806ca6 movs r3, #0
43806ca8 str.w r3, [r4, #0xd58]
43806cac ldrb.w r3, [r6, #0x40]
43806cb0 tst.w r3, #0x40
43806cb4 beq.w #0x43806dcc
43806cb8 ldr r0, [pc, #0x160] ; lit=0x4a8f16
43806cba add r0, pc
43806cbc b #0x43806dc4
43806cbe ldr r2, [pc, #0x114] ; lit=0x6588
43806cc0 ldr r6, [r3, r2]
43806cc2 ldrb.w r3, [r6, #0x40]
43806cc6 tst.w r3, #0x40
43806cca beq #0x43806cd4
43806ccc ldr r0, [pc, #0x150] ; lit=0x4a8f10
43806cce add r0, pc
43806cd0 bl #0x43561540
43806cd4 mov r0, r4
43806cd6 mov r1, r5
43806cd8 bl #0x438066d4
43806cdc ldr.w r3, [r4, #0x568]
43806ce0 cmp r3, #1
43806ce2 bne #0x43806cec
43806ce4 mov r0, r4
43806ce6 bl #0x43b00f62
43806cea b #0x43806cf6
43806cec cmp r3, #2
43806cee bne #0x43806cf6
43806cf0 mov r0, r4
43806cf2 bl #0x43b00f22
43806cf6 ldrb.w r3, [r6, #0x40]
43806cfa tst.w r3, #0x40
43806cfe beq #0x43806dcc
43806d00 ldr r0, [pc, #0x120] ; lit=0x4a8eec
43806d02 add r0, pc
43806d04 b #0x43806dc4
43806d06 ldr r2, [pc, #0xcc] ; lit=0x6588
43806d08 ldr r6, [r3, r2]
43806d0a ldrb.w r3, [r6, #0x40]
43806d0e tst.w r3, #0x40
43806d12 beq #0x43806d1c
43806d14 ldr r0, [pc, #0x110] ; lit=0x4a8ee6
43806d16 add r0, pc
43806d18 bl #0x43561540
43806d1c mov r0, r4
43806d1e mov r1, r5
43806d20 bl #0x438066d4
43806d24 ldr.w r3, [r4, #0x568]
43806d28 cmp r3, #1
43806d2a bne #0x43806d3e
43806d2c ldr r3, [r5, #0xc]
43806d2e mov r0, r4
43806d30 add.w r1, r5, #0x14
43806d34 str.w r3, [r4, #0x6bc]
43806d38 bl #0x43b00dac
43806d3c b #0x43806d70
43806d3e cmp r3, #2
43806d40 bne #0x43806d70
43806d42 str.w r3, [r5, #0xbc]
43806d46 mov r0, r4
43806d48 add.w r1, r5, #8
43806d4c add.w r7, r4, #0x698
43806d50 bl #0x43b00cd0
43806d54 add.w lr, r5, #0x570
43806d58 ldm.w lr!, {r0, r1, r2, r3}
43806d5c stm r7!, {r0, r1, r2, r3}
43806d5e ldm.w lr, {r0, r1, r2}
43806d62 stm.w r7, {r0, r1, r2}
43806d66 mov r0, r4
43806d68 add.w r1, r5, #0x590
43806d6c bl #0x43b00d94
43806d70 mov r0, r4
43806d72 ldrh r1, [r5, #2]
43806d74 bl #0x43806590
43806d78 ldrb.w r3, [r6, #0x40]
43806d7c tst.w r3, #0x40
43806d80 beq #0x43806dcc
43806d82 ldr r0, [pc, #0xa8] ; lit=0x4a8e85
43806d84 add r0, pc
43806d86 b #0x43806dc4
43806d88 ldr r2, [pc, #0x48] ; lit=0x6588
43806d8a ldr r6, [r3, r2]
43806d8c ldrb.w r3, [r6, #0x40]
43806d90 tst.w r3, #0x40
43806d94 beq #0x43806d9e
43806d96 ldr r0, [pc, #0x98] ; lit=0x4a8e7c
43806d98 add r0, pc
43806d9a bl #0x43561540
43806d9e mov r0, r4
43806da0 mov r1, r5
43806da2 bl #0x438066d4
43806da6 ldrh.w r2, [r4, #0x570]
43806daa ldrh r3, [r5, #4]
43806dac cmp r2, r3
43806dae bne #0x43806db6
43806db0 movs r3, #0
43806db2 str.w r3, [r4, #0x56c]
43806db6 ldrb.w r3, [r6, #0x40]
43806dba tst.w r3, #0x40
43806dbe beq #0x43806dcc
43806dc0 ldr r0, [pc, #0x70] ; lit=0x4a8e62
43806dc2 add r0, pc
43806dc4 pop.w {r4, r5, r6, r7, r8, lr}
43806dc8 b.w #0x43561540
43806dcc pop.w {r4, r5, r6, r7, r8, pc}
43806dd0 strh r4, [r4, #0x26]
43806dd2 lsls r1, r0, #2
43806dd4 str r0, [r1, #0x58]
43806dd6 movs r0, r0
43806dd8 str r0, [sp, #0x2d8]
43806dda lsls r2, r1, #1
43806ddc str r0, [sp, #0x290]
43806dde lsls r2, r1, #1
43806de0 str r0, [sp, #0x278]
43806de2 lsls r2, r1, #1
43806de4 str r0, [sp, #0x1dc]
43806de6 lsls r2, r1, #1
43806de8 str r0, [sp, #0x1b8]
43806dea lsls r2, r1, #1
43806dec str r0, [sp, #0x148]
43806dee lsls r2, r1, #1
43806df0 str r0, [sp, #0x130]
43806df2 lsls r2, r1, #1
43806df4 str r0, [sp, #0x88]
43806df6 lsls r2, r1, #1
43806df8 str r0, [sp, #0x70]
43806dfa lsls r2, r1, #1
43806dfc ldrh r5, [r2, #0x3e]
43806dfe lsls r2, r1, #1
43806e00 ldrh r4, [r1, #0x3e]
43806e02 lsls r2, r1, #1
43806e04 ldrh r6, [r4, #0x3c]
43806e06 lsls r2, r1, #1
43806e08 ldrh r0, [r4, #0x3c]
43806e0a lsls r2, r1, #1
43806e0c ldrh r1, [r7, #0x3a]
43806e0e lsls r2, r1, #1
43806e10 ldrh r2, [r6, #0x3a]
43806e12 lsls r2, r1, #1
43806e14 ldrh r4, [r7, #0x38]
43806e16 lsls r2, r1, #1
43806e18 ldrh r2, [r6, #0x38]
43806e1a lsls r2, r1, #1
43806e1c ldrh r6, [r2, #0x38]
43806e1e lsls r2, r1, #1
43806e20 ldrh r0, [r2, #0x38]
43806e22 lsls r2, r1, #1
43806e24 ldrh r4, [r5, #0x36]
43806e26 lsls r2, r1, #1
43806e28 ldrh r6, [r4, #0x36]
43806e2a lsls r2, r1, #1
43806e2c ldrh r5, [r0, #0x34]
43806e2e lsls r2, r1, #1
43806e30 ldrh r4, [r7, #0x32]
43806e32 lsls r2, r1, #1
43806e34 ldrh r2, [r4, #0x32]
43806e36 lsls r2, r1, #1
43806e38 push {r0, r1, r4, lr}
43806e3a bl #0x437876dc
43806e3e mov r4, r0
43806e40 ldr r0, [pc, #0x20] ; lit=0x3030f
43806e42 add r1, sp, #4
43806e44 mov.w r2, #-1
43806e48 bl #0x43561260
43806e4c cmp r0, #0
43806e4e bne #0x43806e40
43806e50 mov r0, r4
43806e52 ldr r1, [sp, #4]
43806e54 bl #0x438069f0
43806e58 ldr r1, [sp, #4]
43806e5a ldr r0, [pc, #8] ; lit=0x3030f
43806e5c bl #0x435612ec
43806e60 b #0x43806e40
