
work/claude/input/a7s-av-cam-view.elf:	file format elf32-littlearm

Disassembly of section .text:

43541000 <_binary_input_a7s_av_cam_bin_start>:
43862e00:      	ldr	r3, [r4, r3]
43862e02:      	ldrh.w	r3, [r3, #0x130]
43862e06:      	strh.w	r3, [r6, #0xb80]
43862e0a:      	pop.w	{r4, r5, r6, r7, r8, pc}
43862e0e:      	nop
43862e10:      	asrs	r6, r5, #0x1e
43862e12:      	lsls	r4, r7, #0x1
43862e14:      	adds	r4, r6, #0x7
43862e16:      	movs	r0, r0
43862e18:      	subs	r1, #0x2c
43862e1a:      	lsls	r2, r6, #0x1
43862e1c:      	subs	r1, #0x1c
43862e1e:      	lsls	r2, r6, #0x1
43862e20:      	subs	r2, #0xd0
43862e22:      	movs	r0, r0
43862e24:      	push.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
43862e28:      	sub	sp, #0x94
43862e2a:      	ldr.w	r10, [pc, #0x87c]       @ 0x438636a8 <_binary_input_a7s_av_cam_bin_start+0x3226a8>
43862e2e:      	mov	r5, r0
43862e30:      	str	r3, [sp, #0x40]
43862e32:      	mov	r6, r1
43862e34:      	ldr.w	r3, [r1, #0x1b8]
43862e38:      	add	r10, pc
43862e3a:      	str	r2, [sp, #0x64]
43862e3c:      	ldr	r4, [sp, #0xb8]
43862e3e:      	ldr.w	r11, [sp, #0xbc]
43862e42:      	cbnz	r3, 0x43862e4a <_binary_input_a7s_av_cam_bin_start+0x321e4a> @ imm = #0x4
43862e44:      	mov	r0, r11
43862e46:      	bl	0x437c66dc <_binary_input_a7s_av_cam_bin_start+0x2856dc> @ imm = #-0x9c76e
43862e4a:      	ldr.w	r3, [pc, #0x860]        @ 0x438636ac <_binary_input_a7s_av_cam_bin_start+0x3226ac>
43862e4e:      	ldr.w	r2, [r10, r3]
43862e52:      	ldrb	r3, [r2]
43862e54:      	str	r2, [sp, #0x54]
43862e56:      	cbnz	r3, 0x43862e64 <_binary_input_a7s_av_cam_bin_start+0x321e64> @ imm = #0xa
43862e58:      	ldrb	r2, [r2, #0x15]
43862e5a:      	cmp	r2, #0x0
43862e5c:      	beq.w	0x438636a0 <_binary_input_a7s_av_cam_bin_start+0x3226a0> @ imm = #0x840
43862e60:      	str	r3, [sp, #0x44]
43862e62:      	b	0x43862e74 <_binary_input_a7s_av_cam_bin_start+0x321e74> @ imm = #0xe
43862e64:      	cbz	r4, 0x43862e72 <_binary_input_a7s_av_cam_bin_start+0x321e72> @ imm = #0xa
43862e66:      	ldr	r0, [sp, #0x40]
43862e68:      	subs	r0, #0x0
43862e6a:      	it	ne
43862e6c:      	movne	r0, #0x1
43862e6e:      	str	r0, [sp, #0x44]
43862e70:      	b	0x43862e74 <_binary_input_a7s_av_cam_bin_start+0x321e74> @ imm = #0x0
43862e72:      	str	r4, [sp, #0x44]
43862e74:      	ldr.w	r1, [r6, #0x1b8]
43862e78:      	mov.w	r0, #0x384
43862e7c:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x82930
43862e80:      	ldr.w	r3, [pc, #0x82c]        @ 0x438636b0 <_binary_input_a7s_av_cam_bin_start+0x3226b0>
43862e84:      	movs	r7, #0x0
43862e86:      	add	r3, pc
43862e88:      	strb	r7, [r3]
43862e8a:      	bl	0x437c3388 <_binary_input_a7s_av_cam_bin_start+0x282388> @ imm = #-0x9fb06
43862e8e:      	str	r0, [r5, #0x8]
43862e90:      	bl	0x437c3394 <_binary_input_a7s_av_cam_bin_start+0x282394> @ imm = #-0x9fb00
43862e94:      	ldr.w	r1, [r6, #0x1b8]
43862e98:      	str	r0, [r5, #0xc]
43862e9a:      	cbz	r1, 0x43862eb4 <_binary_input_a7s_av_cam_bin_start+0x321eb4> @ imm = #0x16
43862e9c:      	cmp.w	r11, #0x0
43862ea0:      	beq	0x43862eb8 <_binary_input_a7s_av_cam_bin_start+0x321eb8> @ imm = #0x14
43862ea2:      	ldr	r3, [r5, #0x8]
43862ea4:      	cmp	r3, #0x11
43862ea6:      	bne	0x43862eba <_binary_input_a7s_av_cam_bin_start+0x321eba> @ imm = #0x10
43862ea8:      	ldr.w	r7, [r11, #0xb78]
43862eac:      	subs	r7, r0, r7
43862eae:      	it	ne
43862eb0:      	movne	r7, #0x1
43862eb2:      	b	0x43862eba <_binary_input_a7s_av_cam_bin_start+0x321eba> @ imm = #0x4
43862eb4:      	movs	r7, #0x1
43862eb6:      	b	0x43862eba <_binary_input_a7s_av_cam_bin_start+0x321eba> @ imm = #0x0
43862eb8:      	mov	r7, r11
43862eba:      	adds	r2, r5, #0x4
43862ebc:      	mov	r3, r11
43862ebe:      	strb	r7, [r5, #0x10]
43862ec0:      	ldr.w	r0, [r6, #0x1c0]
43862ec4:      	bl	0x43862d80 <_binary_input_a7s_av_cam_bin_start+0x321d80> @ imm = #-0x148
43862ec8:      	ldr.w	r1, [r6, #0x1b8]
43862ecc:      	ldr.w	r0, [r6, #0x1c0]
43862ed0:      	bl	0x43862034 <_binary_input_a7s_av_cam_bin_start+0x321034> @ imm = #-0xea0
43862ed4:      	ldr.w	r1, [r6, #0x1b8]
43862ed8:      	mov	r7, r0
43862eda:      	ldr.w	r0, [r6, #0x1c0]
43862ede:      	bl	0x43861fb0 <_binary_input_a7s_av_cam_bin_start+0x320fb0> @ imm = #-0xf32
43862ee2:      	ldr.w	r1, [r6, #0x1b8]
43862ee6:      	mov	r9, r0
43862ee8:      	ldr.w	r0, [r6, #0x1c0]
43862eec:      	bl	0x43861f2c <_binary_input_a7s_av_cam_bin_start+0x320f2c> @ imm = #-0xfc4
43862ef0:      	ldr.w	r1, [r6, #0x1b8]
43862ef4:      	str	r0, [sp, #0x48]
43862ef6:      	ldr.w	r0, [r6, #0x1c0]
43862efa:      	bl	0x43861f84 <_binary_input_a7s_av_cam_bin_start+0x320f84> @ imm = #-0xf7a
43862efe:      	ldr.w	r1, [r6, #0x1b8]
43862f02:      	str	r0, [sp, #0x60]
43862f04:      	ldr.w	r0, [r6, #0x1c0]
43862f08:      	bl	0x43862060 <_binary_input_a7s_av_cam_bin_start+0x321060> @ imm = #-0xeac
43862f0c:      	ldr.w	r3, [r6, #0x1c0]
43862f10:      	mov	r2, r7
43862f12:      	mov	r1, r9
43862f14:      	str.w	r3, [r7, #0x294]
43862f18:      	ldr.w	r3, [r6, #0x76c]
43862f1c:      	str.w	r3, [r7, #0x404]
43862f20:      	str	r0, [sp, #0x5c]
43862f22:      	ldr	r0, [sp, #0x48]
43862f24:      	bl	0x437cb5c0 <_binary_input_a7s_av_cam_bin_start+0x28a5c0> @ imm = #-0x97968
43862f28:      	mov	r0, r7
43862f2a:      	mov	r1, r9
43862f2c:      	bl	0x437d0544 <_binary_input_a7s_av_cam_bin_start+0x28f544> @ imm = #-0x929ec
43862f30:      	mov	r1, r9
43862f32:      	mov	r0, r7
43862f34:      	bl	0x437cf8e4 <_binary_input_a7s_av_cam_bin_start+0x28e8e4> @ imm = #-0x93654
43862f38:      	mov	r0, r6
43862f3a:      	bl	0x437def7c <_binary_input_a7s_av_cam_bin_start+0x29df7c> @ imm = #-0x83fc2
43862f3e:      	mov	r0, r6
43862f40:      	bl	0x43af5a7c <_binary_input_a7s_av_cam_bin_start+0x5b4a7c> @ imm = #0x292b38
43862f44:      	ldr	r2, [sp, #0x44]
43862f46:      	cbnz	r2, 0x43862f54 <_binary_input_a7s_av_cam_bin_start+0x321f54> @ imm = #0xa
43862f48:      	ldr.w	r3, [pc, #0x768]        @ 0x438636b4 <_binary_input_a7s_av_cam_bin_start+0x3226b4>
43862f4c:      	strb	r2, [r5, #0x6]
43862f4e:      	strb	r2, [r5, #0x5]
43862f50:      	add	r3, pc
43862f52:      	b	0x43862f90 <_binary_input_a7s_av_cam_bin_start+0x321f90> @ imm = #0x3a
43862f54:      	ldr	r0, [sp, #0x40]
43862f56:      	ldrb	r3, [r0, #0x1]
43862f58:      	and	r3, r3, #0x1
43862f5c:      	strb	r3, [r5, #0x6]
43862f5e:      	ldr.w	r3, [pc, #0x758]        @ 0x438636b8 <_binary_input_a7s_av_cam_bin_start+0x3226b8>
43862f62:      	ldr.w	r3, [r10, r3]
43862f66:      	ldrb	r3, [r3]
43862f68:      	cbnz	r3, 0x43862f70 <_binary_input_a7s_av_cam_bin_start+0x321f70> @ imm = #0x4
43862f6a:      	ldr	r1, [sp, #0x40]
43862f6c:      	ldrb	r3, [r1, #0x1]
43862f6e:      	lsrs	r3, r3, #0x6
43862f70:      	ldr	r2, [sp, #0x40]
43862f72:      	strb	r3, [r5, #0x5]
43862f74:      	ldr	r0, [sp, #0x40]
43862f76:      	ldrb	r1, [r2, #0x5]
43862f78:      	ldrb	r2, [r2, #0x4]
43862f7a:      	ldr.w	r3, [pc, #0x740]        @ 0x438636bc <_binary_input_a7s_av_cam_bin_start+0x3226bc>
43862f7e:      	lsls	r1, r1, #0x18
43862f80:      	lsls	r2, r2, #0x10
43862f82:      	add	r3, pc
43862f84:      	adds	r1, r1, r2
43862f86:      	ldrb	r2, [r0, #0x2]
43862f88:      	adds	r1, r1, r2
43862f8a:      	ldrb	r2, [r0, #0x3]
43862f8c:      	lsls	r2, r2, #0x8
43862f8e:      	adds	r2, r1, r2
43862f90:      	str	r2, [r3]
43862f92:      	mov.w	r8, #0x0
43862f96:      	ldrb.w	r3, [r7, #0x932]
43862f9a:      	add.w	r1, r5, #0x2c0
43862f9e:      	adds	r2, r5, #0x4
43862fa0:      	mov	r0, r1
43862fa2:      	strb.w	r3, [r5, #0x154]
43862fa6:      	ldr.w	r3, [pc, #0x718]        @ 0x438636c0 <_binary_input_a7s_av_cam_bin_start+0x3226c0>
43862faa:      	ldr.w	r12, [r10, r3]
43862fae:      	ldr.w	r3, [pc, #0x714]        @ 0x438636c4 <_binary_input_a7s_av_cam_bin_start+0x3226c4>
43862fb2:      	str	r1, [sp, #0x4c]
43862fb4:      	mov	r1, r7
43862fb6:      	strb.w	r8, [r12, #0x59c]
43862fba:      	str	r2, [sp, #0x50]
43862fbc:      	stm.w	sp, {r2, r6}
43862fc0:      	ldr.w	r3, [r10, r3]
43862fc4:      	str.w	r12, [sp, #0x38]
43862fc8:      	mov	r2, r3
43862fca:      	str	r3, [sp, #0x3c]
43862fcc:      	mov	r3, r12
43862fce:      	bl	0x437e3500 <_binary_input_a7s_av_cam_bin_start+0x2a2500> @ imm = #-0x7fad2
43862fd2:      	strb.w	r8, [r5, #0x33a]
43862fd6:      	strb.w	r8, [r5, #0x34a]
43862fda:      	bl	0x437436b8 <_binary_input_a7s_av_cam_bin_start+0x2026b8> @ imm = #-0x11f926
43862fde:      	ldr.w	r12, [sp, #0x38]
43862fe2:      	str.w	r12, [sp, #0x58]
43862fe6:      	cbz	r0, 0x43862ff2 <_binary_input_a7s_av_cam_bin_start+0x321ff2> @ imm = #0x8
43862fe8:      	add	r0, sp, #0x68
43862fea:      	strb.w	r8, [sp, #0x83]
43862fee:      	bl	0x438f0580 <_binary_input_a7s_av_cam_bin_start+0x3af580> @ imm = #0x8d58e
43862ff2:      	ldr	r3, [sp, #0x3c]
43862ff4:      	mov	r2, r6
43862ff6:      	mov	r0, r5
43862ff8:      	mov	r1, r11
43862ffa:      	str	r7, [sp]
43862ffc:      	str	r3, [sp, #0x4]
43862ffe:      	ldr	r3, [sp, #0x40]
43863000:      	bl	0x437e3318 <_binary_input_a7s_av_cam_bin_start+0x2a2318> @ imm = #-0x7fcec
43863004:      	ldrb.w	r1, [r5, #0x2c2]
43863008:      	mov	r0, r7
4386300a:      	bl	0x43848f74 <_binary_input_a7s_av_cam_bin_start+0x307f74> @ imm = #-0x1a09a
4386300e:      	movs	r1, #0x0
43863010:      	movs	r2, #0x28
43863012:      	strb.w	r0, [r7, #0x3dc]
43863016:      	add	r0, sp, #0x68
43863018:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x150fe0
4386301c:      	ldr.w	r3, [r7, #0x294]
43863020:      	cmp	r3, #0x9
43863022:      	beq	0x43863042 <_binary_input_a7s_av_cam_bin_start+0x322042> @ imm = #0x1c
43863024:      	ldr	r0, [sp, #0x3c]
43863026:      	ldrb.w	r2, [r0, #0x124]
4386302a:      	cmp	r2, #0x1
4386302c:      	beq	0x43863042 <_binary_input_a7s_av_cam_bin_start+0x322042> @ imm = #0x12
4386302e:      	cmp	r3, #0x12
43863030:      	bne	0x4386303a <_binary_input_a7s_av_cam_bin_start+0x32203a> @ imm = #0x6
43863032:      	ldr.w	r3, [r7, #0x65c]
43863036:      	cmp	r3, #0x5
43863038:      	beq	0x43863042 <_binary_input_a7s_av_cam_bin_start+0x322042> @ imm = #0x6
4386303a:      	ldr	r1, [sp, #0x3c]
4386303c:      	ldrb	r3, [r1, #0x2]
4386303e:      	strb.w	r3, [sp, #0x82]
43863042:      	add	r0, sp, #0x68
43863044:      	bl	0x438f055c <_binary_input_a7s_av_cam_bin_start+0x3af55c> @ imm = #0x8d514
43863048:      	ldr	r1, [sp, #0x3c]
4386304a:      	mov	r0, r7
4386304c:      	bl	0x4386208c <_binary_input_a7s_av_cam_bin_start+0x32108c> @ imm = #-0xfc4
43863050:      	ldr	r1, [sp, #0x4c]
43863052:      	mov	r2, r7
43863054:      	bl	0x43861cc4 <_binary_input_a7s_av_cam_bin_start+0x320cc4> @ imm = #-0x1394
43863058:      	ldr	r2, [sp, #0x3c]
4386305a:      	ldr.w	r3, [pc, #0x66c]        @ 0x438636c8 <_binary_input_a7s_av_cam_bin_start+0x3226c8>
4386305e:      	ldr	r1, [sp, #0x60]
43863060:      	str	r2, [sp]
43863062:      	ldr.w	r3, [r10, r3]
43863066:      	ldr	r2, [sp, #0x58]
43863068:      	ldrh.w	r0, [r6, #0x1b8]
4386306c:      	str	r3, [sp, #0x4]
4386306e:      	ldr	r3, [sp, #0x5c]
43863070:      	str	r1, [sp, #0xc]
43863072:      	mov	r1, r7
43863074:      	str	r2, [sp, #0x10]
43863076:      	str	r3, [sp, #0x8]
43863078:      	mov	r3, r9
4386307a:      	ldr	r2, [sp, #0x48]
4386307c:      	bl	0x437c7000 <_binary_input_a7s_av_cam_bin_start+0x286000> @ imm = #-0x9c080
43863080:      	mov	r0, r6
43863082:      	bl	0x43aee5b8 <_binary_input_a7s_av_cam_bin_start+0x5ad5b8> @ imm = #0x28b532
43863086:      	mov	r1, r0
43863088:      	mov	r0, r9
4386308a:      	bl	0x43b0b994 <_binary_input_a7s_av_cam_bin_start+0x5ca994> @ imm = #0x2a8906
4386308e:      	ldr	r3, [sp, #0x54]
43863090:      	ldrb.w	r8, [r3, #0x15]
43863094:      	cmp.w	r8, #0x0
43863098:      	bne	0x438630c0 <_binary_input_a7s_av_cam_bin_start+0x3220c0> @ imm = #0x24
4386309a:      	ldrh.w	r3, [r6, #0x1b8]
4386309e:      	mov	r1, r9
438630a0:      	mov	r2, r7
438630a2:      	ldr	r0, [sp, #0x58]
438630a4:      	str	r3, [sp]
438630a6:      	ldr	r3, [sp, #0x3c]
438630a8:      	bl	0x438649bc <_binary_input_a7s_av_cam_bin_start+0x3239bc> @ imm = #0x1910
438630ac:      	ldrh.w	r0, [r9, #0x162]
438630b0:      	bl	0x43adbfdc <_binary_input_a7s_av_cam_bin_start+0x59afdc> @ imm = #0x278f28
438630b4:      	mov	r0, r5
438630b6:      	ldr.w	r1, [r6, #0x1b8]
438630ba:      	mov	r2, r8
438630bc:      	bl	0x43861a58 <_binary_input_a7s_av_cam_bin_start+0x320a58> @ imm = #-0x1668
438630c0:      	ldr.w	r3, [pc, #0x608]        @ 0x438636cc <_binary_input_a7s_av_cam_bin_start+0x3226cc>
438630c4:      	mov	r0, r6
438630c6:      	str.w	r11, [sp]
438630ca:      	mov	r1, r7
438630cc:      	ldr	r2, [sp, #0x3c]
438630ce:      	ldr.w	r8, [r10, r3]
438630d2:      	mov	r3, r8
438630d4:      	bl	0x437e3424 <_binary_input_a7s_av_cam_bin_start+0x2a2424> @ imm = #-0x7fcb4
438630d8:      	ldrb.w	r3, [r8]
438630dc:      	cmp	r3, #0x1
438630de:      	str	r0, [r5, #0x14]
438630e0:      	bne	0x4386311a <_binary_input_a7s_av_cam_bin_start+0x32211a> @ imm = #0x36
438630e2:      	ldrh.w	r0, [r9, #0x162]
438630e6:      	ldrh.w	r1, [r9, #0x140]
438630ea:      	strh.w	r0, [r5, #0x2d2]
438630ee:      	mov	r0, r7
438630f0:      	strh.w	r1, [r5, #0x4a2]
438630f4:      	bl	0x437e5080 <_binary_input_a7s_av_cam_bin_start+0x2a4080> @ imm = #-0x7e078
438630f8:      	mov	r1, r8
438630fa:      	mov	r2, r0
438630fc:      	ldr	r0, [sp, #0x4c]
438630fe:      	bl	0x43b0d45e <_binary_input_a7s_av_cam_bin_start+0x5cc45e> @ imm = #0x2aa35c
43863102:      	ldrh.w	r2, [r8, #0x8]
43863106:      	ldrh.w	r3, [r8, #0xa]
4386310a:      	ldrh.w	r0, [r8, #0xc]
4386310e:      	strh.w	r2, [r5, #0x4d6]
43863112:      	strh.w	r3, [r5, #0x4d8]
43863116:      	strh.w	r0, [r5, #0x4da]
4386311a:      	ldr	r1, [sp, #0x44]
4386311c:      	cmp	r1, #0x1
4386311e:      	bne.w	0x438633ac <_binary_input_a7s_av_cam_bin_start+0x3223ac> @ imm = #0x28a
43863122:      	movs	r3, #0x0
43863124:      	strb	r3, [r4]
43863126:      	ldrh.w	r2, [r7, #0x4c4]
4386312a:      	ands	r2, r2, #0x20
4386312e:      	beq	0x43863140 <_binary_input_a7s_av_cam_bin_start+0x322140> @ imm = #0xe
43863130:      	ldr.w	r2, [pc, #0x59c]        @ 0x438636d0 <_binary_input_a7s_av_cam_bin_start+0x3226d0>
43863134:      	add	r2, pc
43863136:      	ldrb	r2, [r2]
43863138:      	cmp	r2, #0x1
4386313a:      	bne	0x43863174 <_binary_input_a7s_av_cam_bin_start+0x322174> @ imm = #0x36
4386313c:      	adds	r3, #0x40
4386313e:      	b	0x43863174 <_binary_input_a7s_av_cam_bin_start+0x322174> @ imm = #0x32
43863140:      	ldr.w	r3, [pc, #0x590]        @ 0x438636d4 <_binary_input_a7s_av_cam_bin_start+0x3226d4>
43863144:      	add	r3, pc
43863146:      	ldr	r3, [r3]
43863148:      	cmp	r3, #0x1
4386314a:      	bne	0x4386315c <_binary_input_a7s_av_cam_bin_start+0x32215c> @ imm = #0xe
4386314c:      	ldr.w	r3, [pc, #0x588]        @ 0x438636d8 <_binary_input_a7s_av_cam_bin_start+0x3226d8>
43863150:      	add	r3, pc
43863152:      	ldrb	r3, [r3]
43863154:      	cmp	r3, #0x1
43863156:      	bne	0x43863178 <_binary_input_a7s_av_cam_bin_start+0x322178> @ imm = #0x1e
43863158:      	adds	r3, #0x3f
4386315a:      	b	0x43863174 <_binary_input_a7s_av_cam_bin_start+0x322174> @ imm = #0x16
4386315c:      	cmp	r3, #0x3
4386315e:      	beq	0x43863162 <_binary_input_a7s_av_cam_bin_start+0x322162> @ imm = #0x0
43863160:      	cbnz	r3, 0x43863178 <_binary_input_a7s_av_cam_bin_start+0x322178> @ imm = #0x14
43863162:      	ldr.w	r3, [pc, #0x578]        @ 0x438636dc <_binary_input_a7s_av_cam_bin_start+0x3226dc>
43863166:      	add	r3, pc
43863168:      	ldrb	r3, [r3]
4386316a:      	cmp	r3, #0x1
4386316c:      	bne	0x43863172 <_binary_input_a7s_av_cam_bin_start+0x322172> @ imm = #0x2
4386316e:      	adds	r3, #0x41
43863170:      	b	0x43863174 <_binary_input_a7s_av_cam_bin_start+0x322174> @ imm = #0x0
43863172:      	movs	r3, #0x2
43863174:      	strb	r3, [r4, #0x1]
43863176:      	b	0x4386317a <_binary_input_a7s_av_cam_bin_start+0x32217a> @ imm = #0x0
43863178:      	strb	r2, [r4, #0x1]
4386317a:      	ldr	r2, [sp, #0x3c]
4386317c:      	ldrb	r3, [r2, #0x2]
4386317e:      	cmp	r3, #0x1
43863180:      	bne	0x43863188 <_binary_input_a7s_av_cam_bin_start+0x322188> @ imm = #0x4
43863182:      	ldrb	r3, [r4, #0x1]
43863184:      	adds	r3, #0x14
43863186:      	strb	r3, [r4, #0x1]
43863188:      	ldr	r3, [r5, #0x14]
4386318a:      	subs	r3, #0x1
4386318c:      	cmp	r3, #0x2
4386318e:      	bhi	0x43863198 <_binary_input_a7s_av_cam_bin_start+0x322198> @ imm = #0x6
43863190:      	ldrb	r3, [r4, #0x1]
43863192:      	orn	r3, r3, #0x7f
43863196:      	strb	r3, [r4, #0x1]
43863198:      	ldrh.w	r0, [r9, #0x166]
4386319c:      	bl	0x4384b23c <_binary_input_a7s_av_cam_bin_start+0x30a23c> @ imm = #-0x17f64
438631a0:      	cmp	r0, #0x1
438631a2:      	bne	0x438631aa <_binary_input_a7s_av_cam_bin_start+0x3221aa> @ imm = #0x4
438631a4:      	movs	r3, #0x0
438631a6:      	strb	r3, [r4, #0x2]
438631a8:      	b	0x438631b6 <_binary_input_a7s_av_cam_bin_start+0x3221b6> @ imm = #0xa
438631aa:      	ldrh.w	r3, [r9, #0x166]
438631ae:      	strb	r3, [r4, #0x2]
438631b0:      	ldrh.w	r3, [r9, #0x166]
438631b4:      	asrs	r3, r3, #0x8
438631b6:      	strb	r3, [r4, #0x3]
438631b8:      	ldrh.w	r3, [r9, #0x162]
438631bc:      	strb	r3, [r4, #0x4]
438631be:      	ldrh.w	r3, [r9, #0x162]
438631c2:      	asrs	r3, r3, #0x8
438631c4:      	strb	r3, [r4, #0x5]
438631c6:      	ldr	r0, [sp, #0x3c]
438631c8:      	ldrb	r3, [r0, #0x2]
438631ca:      	cmp	r3, #0x1
438631cc:      	bne	0x43863210 <_binary_input_a7s_av_cam_bin_start+0x322210> @ imm = #0x40
438631ce:      	add.w	r3, r6, #0x1480
438631d2:      	ldrb	r0, [r3, #0x18]
438631d4:      	bl	0x43aeef7c <_binary_input_a7s_av_cam_bin_start+0x5adf7c> @ imm = #0x28bda4
438631d8:      	cmp	r0, #0x1
438631da:      	bne	0x43863200 <_binary_input_a7s_av_cam_bin_start+0x322200> @ imm = #0x22
438631dc:      	ldr.w	r2, [r7, #0x428]
438631e0:      	cmp	r2, #0x4
438631e2:      	bhi	0x438631ee <_binary_input_a7s_av_cam_bin_start+0x3221ee> @ imm = #0x8
438631e4:      	ldr.w	r3, [pc, #0x4f8]        @ 0x438636e0 <_binary_input_a7s_av_cam_bin_start+0x3226e0>
438631e8:      	add	r3, pc
438631ea:      	ldrb	r3, [r3, r2]
438631ec:      	b	0x438631f0 <_binary_input_a7s_av_cam_bin_start+0x3221f0> @ imm = #0x0
438631ee:      	movs	r3, #0x0
438631f0:      	ldr	r1, [sp, #0x3c]
438631f2:      	ldrb.w	r2, [r1, #0xff]
438631f6:      	cmp	r2, r3
438631f8:      	bls	0x43863210 <_binary_input_a7s_av_cam_bin_start+0x322210> @ imm = #0x14
438631fa:      	subs	r3, r2, r3
438631fc:      	uxtb	r3, r3
438631fe:      	b	0x43863216 <_binary_input_a7s_av_cam_bin_start+0x322216> @ imm = #0x14
43863200:      	ldr	r3, [r5, #0x14]
43863202:      	cbnz	r3, 0x43863210 <_binary_input_a7s_av_cam_bin_start+0x322210> @ imm = #0xa
43863204:      	cmp.w	r11, #0x0
43863208:      	beq	0x43863214 <_binary_input_a7s_av_cam_bin_start+0x322214> @ imm = #0x8
4386320a:      	ldrb.w	r3, [r11, #0x4ba]
4386320e:      	b	0x43863216 <_binary_input_a7s_av_cam_bin_start+0x322216> @ imm = #0x4
43863210:      	movs	r3, #0x0
43863212:      	b	0x43863216 <_binary_input_a7s_av_cam_bin_start+0x322216> @ imm = #0x0
43863214:      	mov	r3, r11
43863216:      	strb	r3, [r4, #0x6]
43863218:      	ldrb.w	r3, [r8]
4386321c:      	cmp	r3, #0x1
4386321e:      	bne	0x4386322a <_binary_input_a7s_av_cam_bin_start+0x32222a> @ imm = #0x8
43863220:      	ldrh.w	r0, [r8, #0x8]
43863224:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5d30
43863228:      	strb	r0, [r4, #0x6]
4386322a:      	movs	r3, #0xa0
4386322c:      	strb	r3, [r4, #0x8]
4386322e:      	ldr.w	r3, [pc, #0x4b4]        @ 0x438636e4 <_binary_input_a7s_av_cam_bin_start+0x3226e4>
43863232:      	movs	r2, #0x0
43863234:      	strb	r2, [r4, #0x9]
43863236:      	add	r3, pc
43863238:      	ldrh	r3, [r3]
4386323a:      	strb	r2, [r4, #0xc]
4386323c:      	strb	r3, [r4, #0xa]
4386323e:      	asrs	r3, r3, #0x8
43863240:      	strb	r3, [r4, #0xb]
43863242:      	ldr.w	r2, [r6, #0x1c0]
43863246:      	ldrb.w	r3, [r7, #0x38d]
4386324a:      	cmp	r2, #0x19
4386324c:      	beq	0x43863264 <_binary_input_a7s_av_cam_bin_start+0x322264> @ imm = #0x14
4386324e:      	ldrh	r1, [r7]
43863250:      	movw	r2, #0x313
43863254:      	cmp	r1, r2
43863256:      	beq	0x43863264 <_binary_input_a7s_av_cam_bin_start+0x322264> @ imm = #0xa
43863258:      	ldr.w	r2, [r6, #0x76c]
4386325c:      	cmp	r2, #0x2
4386325e:      	it	eq
43863260:      	moveq	r3, #0x2
43863262:      	b	0x43863266 <_binary_input_a7s_av_cam_bin_start+0x322266> @ imm = #0x0
43863264:      	movs	r3, #0x2
43863266:      	ldrb.w	r1, [r7, #0x38c]
4386326a:      	lsls	r3, r3, #0x6
4386326c:      	ldrb.w	r2, [r7, #0x38e]
43863270:      	and	r1, r1, #0x1
43863274:      	cmp	r2, #0x4
43863276:      	it	eq
43863278:      	moveq	r2, #0x1
4386327a:      	and	r2, r2, #0x3
4386327e:      	lsls	r1, r1, #0x5
43863280:      	adds	r3, r3, r1
43863282:      	add.w	r3, r3, r2, lsl #3
43863286:      	strb	r3, [r4, #0xd]
43863288:      	movs	r3, #0x0
4386328a:      	strb	r3, [r4, #0xe]
4386328c:      	ldr.w	r3, [pc, #0x458]        @ 0x438636e8 <_binary_input_a7s_av_cam_bin_start+0x3226e8>
43863290:      	ldr.w	r2, [r10, r3]
43863294:      	ldrb	r3, [r2]
43863296:      	cmp	r3, #0x0
43863298:      	bne	0x43863398 <_binary_input_a7s_av_cam_bin_start+0x322398> @ imm = #0xfc
4386329a:      	ldr.w	r2, [r6, #0x76c]
4386329e:      	sub.w	r1, r2, #0x2
438632a2:      	rsbs	r2, r1, #0
438632a4:      	adc.w	r2, r2, r1
438632a8:      	ldrb.w	r1, [r8]
438632ac:      	lsls	r2, r2, #0x5
438632ae:      	cmp	r1, #0x1
438632b0:      	it	eq
438632b2:      	addeq	r2, #0x1
438632b4:      	strb	r2, [r4, #0x12]
438632b6:      	ldr.w	r1, [r5, #0x310]
438632ba:      	sub.w	r2, r1, #0x12
438632be:      	cmp	r2, #0x1
438632c0:      	ldr.w	r2, [r5, #0x320]
438632c4:      	bhi	0x43863322 <_binary_input_a7s_av_cam_bin_start+0x322322> @ imm = #0x5a
438632c6:      	cmp	r2, #0x1
438632c8:      	ldrh.w	r0, [r8, #0xc]
438632cc:      	bne	0x43863306 <_binary_input_a7s_av_cam_bin_start+0x322306> @ imm = #0x36
438632ce:      	ldrh.w	r1, [r5, #0x2d4]
438632d2:      	bl	0x43b0903c <_binary_input_a7s_av_cam_bin_start+0x5c803c> @ imm = #0x2a5d66
438632d6:      	ldrb.w	r3, [r8, #0x10]
438632da:      	subs	r3, r0, r3
438632dc:      	strb	r3, [r4, #0x13]
438632de:      	ldrh.w	r1, [r5, #0x2d4]
438632e2:      	ldrh.w	r0, [r8, #0x8]
438632e6:      	bl	0x43b0903c <_binary_input_a7s_av_cam_bin_start+0x5c803c> @ imm = #0x2a5d52
438632ea:      	ldrb.w	r3, [r8, #0x10]
438632ee:      	subs	r3, r0, r3
438632f0:      	strb	r3, [r4, #0x14]
438632f2:      	ldrh.w	r0, [r8, #0xa]
438632f6:      	ldrh.w	r1, [r5, #0x2d4]
438632fa:      	bl	0x43b0903c <_binary_input_a7s_av_cam_bin_start+0x5c803c> @ imm = #0x2a5d3e
438632fe:      	ldrb.w	r3, [r8, #0x10]
43863302:      	subs	r3, r0, r3
43863304:      	b	0x438633aa <_binary_input_a7s_av_cam_bin_start+0x3223aa> @ imm = #0xa2
43863306:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5c4e
4386330a:      	strb	r0, [r4, #0x13]
4386330c:      	ldrh.w	r0, [r8, #0x8]
43863310:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5c44
43863314:      	strb	r0, [r4, #0x14]
43863316:      	ldrh.w	r0, [r8, #0xa]
4386331a:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5c3a
4386331e:      	strb	r0, [r4, #0x15]
43863320:      	b	0x438633ac <_binary_input_a7s_av_cam_bin_start+0x3223ac> @ imm = #0x88
43863322:      	subs	r1, #0x14
43863324:      	cmp	r1, #0x3
43863326:      	bhi	0x4386336e <_binary_input_a7s_av_cam_bin_start+0x32236e> @ imm = #0x44
43863328:      	cmp	r2, #0x1
4386332a:      	ldrh.w	r0, [r8, #0xa]
4386332e:      	bne	0x43863358 <_binary_input_a7s_av_cam_bin_start+0x322358> @ imm = #0x26
43863330:      	ldrh.w	r1, [r5, #0x2d4]
43863334:      	str	r3, [sp, #0x38]
43863336:      	bl	0x43b0903c <_binary_input_a7s_av_cam_bin_start+0x5c803c> @ imm = #0x2a5d02
4386333a:      	ldrb.w	r2, [r8, #0x10]
4386333e:      	subs	r2, r0, r2
43863340:      	strb	r2, [r4, #0x13]
43863342:      	ldrh.w	r0, [r8, #0x8]
43863346:      	ldrh.w	r1, [r5, #0x2d4]
4386334a:      	bl	0x43b0903c <_binary_input_a7s_av_cam_bin_start+0x5c803c> @ imm = #0x2a5cee
4386334e:      	ldrb.w	r2, [r8, #0x10]
43863352:      	subs	r2, r0, r2
43863354:      	strb	r2, [r4, #0x14]
43863356:      	b	0x4386336a <_binary_input_a7s_av_cam_bin_start+0x32236a> @ imm = #0x10
43863358:      	str	r3, [sp, #0x38]
4386335a:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5bfa
4386335e:      	strb	r0, [r4, #0x13]
43863360:      	ldrh.w	r0, [r8, #0x8]
43863364:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5bf0
43863368:      	strb	r0, [r4, #0x14]
4386336a:      	ldr	r3, [sp, #0x38]
4386336c:      	b	0x438633aa <_binary_input_a7s_av_cam_bin_start+0x3223aa> @ imm = #0x3a
4386336e:      	cmp	r2, #0x1
43863370:      	ldrh.w	r0, [r8, #0x8]
43863374:      	bne	0x4386338a <_binary_input_a7s_av_cam_bin_start+0x32238a> @ imm = #0x12
43863376:      	ldrh.w	r1, [r5, #0x2d4]
4386337a:      	str	r3, [sp, #0x38]
4386337c:      	bl	0x43b0903c <_binary_input_a7s_av_cam_bin_start+0x5c803c> @ imm = #0x2a5cbc
43863380:      	ldrb.w	r2, [r8, #0x10]
43863384:      	subs	r2, r0, r2
43863386:      	strb	r2, [r4, #0x13]
43863388:      	b	0x43863392 <_binary_input_a7s_av_cam_bin_start+0x322392> @ imm = #0x6
4386338a:      	str	r3, [sp, #0x38]
4386338c:      	bl	0x43b08f58 <_binary_input_a7s_av_cam_bin_start+0x5c7f58> @ imm = #0x2a5bc8
43863390:      	strb	r0, [r4, #0x13]
43863392:      	ldr	r3, [sp, #0x38]
43863394:      	strb	r3, [r4, #0x14]
43863396:      	b	0x438633aa <_binary_input_a7s_av_cam_bin_start+0x3223aa> @ imm = #0x10
43863398:      	movs	r3, #0x1
4386339a:      	strb	r3, [r4, #0x12]
4386339c:      	ldrb	r3, [r2]
4386339e:      	strb	r3, [r4, #0x13]
438633a0:      	ldrb	r3, [r2]
438633a2:      	adds	r3, #0x8
438633a4:      	strb	r3, [r4, #0x14]
438633a6:      	ldrb	r3, [r2]
438633a8:      	adds	r3, #0x10
438633aa:      	strb	r3, [r4, #0x15]
438633ac:      	ldrh.w	r0, [r9, #0x166]
438633b0:      	bl	0x4384aed4 <_binary_input_a7s_av_cam_bin_start+0x309ed4> @ imm = #-0x184e0
438633b4:      	ldr	r3, [pc, #0x334]        @ 0x438636ec <_binary_input_a7s_av_cam_bin_start+0x3226ec>
438633b6:      	ldr	r2, [sp, #0x3c]
438633b8:      	add	r3, pc
438633ba:      	ldrb	r1, [r2, #0x2]
438633bc:      	subs	r1, #0x0
438633be:      	it	ne
438633c0:      	movne	r1, #0x1
438633c2:      	str	r0, [r3]
438633c4:      	mov	r0, r7
438633c6:      	ldr	r3, [pc, #0x328]        @ 0x438636f0 <_binary_input_a7s_av_cam_bin_start+0x3226f0>
438633c8:      	ldr.w	r8, [r10, r3]
438633cc:      	ldrh.w	r3, [r9, #0x168]
438633d0:      	ldrh.w	r2, [r8, #0x9a]
438633d4:      	bl	0x4384a138 <_binary_input_a7s_av_cam_bin_start+0x309138> @ imm = #-0x192a0
438633d8:      	str.w	r8, [sp, #0x5c]
438633dc:      	str.w	r0, [r5, #0x184]
438633e0:      	cmp.w	r11, #0x0
438633e4:      	beq	0x438633f0 <_binary_input_a7s_av_cam_bin_start+0x3223f0> @ imm = #0x8
438633e6:      	ldr.w	r3, [r6, #0x1b8]
438633ea:      	cbnz	r3, 0x438633f0 <_binary_input_a7s_av_cam_bin_start+0x3223f0> @ imm = #0x2
438633ec:      	str.w	r0, [r11, #0xb84]
438633f0:      	ldr.w	r1, [r6, #0x1b8]
438633f4:      	ldr.w	r0, [r6, #0x1c0]
438633f8:      	bl	0x43861f58 <_binary_input_a7s_av_cam_bin_start+0x320f58> @ imm = #-0x14a4
438633fc:      	movs	r1, #0x0
438633fe:      	mov.w	r2, #0x154
43863402:      	mov	r8, r0
43863404:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x150bf4
43863408:      	ldrh.w	r3, [r6, #0x1bc]
4386340c:      	add.w	r12, r8, #0x8
43863410:      	ldr	r1, [sp, #0x64]
43863412:      	ldrh.w	r0, [r6, #0x1b8]
43863416:      	strh.w	r3, [r8]
4386341a:      	ldr	r3, [r1]
4386341c:      	strh.w	r0, [r8, #0x2]
43863420:      	mov	lr, r3
43863422:      	ldm.w	lr!, {r0, r1, r2, r3}
43863426:      	stm.w	r12!, {r0, r1, r2, r3}
4386342a:      	ldm.w	lr!, {r0, r1, r2, r3}
4386342e:      	stm.w	r12!, {r0, r1, r2, r3}
43863432:      	ldm.w	lr, {r0, r1, r2}
43863436:      	stm.w	r12, {r0, r1, r2}
4386343a:      	ldr	r0, [sp, #0x54]
4386343c:      	ldrh.w	r2, [r9, #0x166]
43863440:      	ldrb	r3, [r0, #0x15]
43863442:      	strh.w	r2, [r8, #0xf2]
43863446:      	cmp	r3, #0x1
43863448:      	beq	0x43863452 <_binary_input_a7s_av_cam_bin_start+0x322452> @ imm = #0x6
4386344a:      	ldr.w	r3, [r6, #0x76c]
4386344e:      	cmp	r3, #0x2
43863450:      	bne	0x4386345c <_binary_input_a7s_av_cam_bin_start+0x32245c> @ imm = #0x8
43863452:      	mov	r0, r8
43863454:      	mov	r1, r7
43863456:      	bl	0x43861e14 <_binary_input_a7s_av_cam_bin_start+0x320e14> @ imm = #-0x1646
4386345a:      	b	0x4386346e <_binary_input_a7s_av_cam_bin_start+0x32246e> @ imm = #0x10
4386345c:      	ldrh.w	r3, [r8, #0x1c]
43863460:      	movs	r1, #0x0
43863462:      	strh.w	r1, [r8, #0x64]
43863466:      	strh.w	r1, [r8, #0x66]
4386346a:      	str.w	r3, [r8, #0x60]
4386346e:      	ldr	r3, [pc, #0x284]        @ 0x438636f4 <_binary_input_a7s_av_cam_bin_start+0x3226f4>
43863470:      	movs	r2, #0x5a
43863472:      	ldr	r1, [pc, #0x284]        @ 0x438636f8 <_binary_input_a7s_av_cam_bin_start+0x3226f8>
43863474:      	add.w	r0, r8, #0x74
43863478:      	add	r3, pc
4386347a:      	ldr	r3, [r3]
4386347c:      	strb.w	r3, [r8, #0x69]
43863480:      	ldr	r3, [pc, #0x278]        @ 0x438636fc <_binary_input_a7s_av_cam_bin_start+0x3226fc>
43863482:      	add	r1, pc
43863484:      	add	r3, pc
43863486:      	ldrb	r3, [r3]
43863488:      	strb.w	r3, [r8, #0xce]
4386348c:      	ldr	r3, [pc, #0x270]        @ 0x43863700 <_binary_input_a7s_av_cam_bin_start+0x322700>
4386348e:      	add	r3, pc
43863490:      	ldrb	r3, [r3]
43863492:      	strb.w	r3, [r8, #0xcf]
43863496:      	blx	0x439b3918 <_binary_input_a7s_av_cam_bin_start+0x472918> @ imm = #0x150480
4386349a:      	ldr.w	r3, [r6, #0x1c0]
4386349e:      	cmp	r3, #0x14
438634a0:      	bgt	0x438634b8 <_binary_input_a7s_av_cam_bin_start+0x3224b8> @ imm = #0x14
438634a2:      	cmp	r3, #0x13
438634a4:      	bge	0x438634e6 <_binary_input_a7s_av_cam_bin_start+0x3224e6> @ imm = #0x3e
438634a6:      	cmp	r3, #0x7
438634a8:      	beq	0x438634ce <_binary_input_a7s_av_cam_bin_start+0x3224ce> @ imm = #0x22
438634aa:      	bgt	0x438634b2 <_binary_input_a7s_av_cam_bin_start+0x3224b2> @ imm = #0x4
438634ac:      	cmp	r3, #0x1
438634ae:      	bne	0x43863560 <_binary_input_a7s_av_cam_bin_start+0x322560> @ imm = #0xae
438634b0:      	b	0x438634f6 <_binary_input_a7s_av_cam_bin_start+0x3224f6> @ imm = #0x42
438634b2:      	cmp	r3, #0x9
438634b4:      	bgt	0x43863560 <_binary_input_a7s_av_cam_bin_start+0x322560> @ imm = #0xa8
438634b6:      	b	0x438634e6 <_binary_input_a7s_av_cam_bin_start+0x3224e6> @ imm = #0x2c
438634b8:      	cmp	r3, #0x1b
438634ba:      	beq	0x438634e6 <_binary_input_a7s_av_cam_bin_start+0x3224e6> @ imm = #0x28
438634bc:      	bgt	0x438634c4 <_binary_input_a7s_av_cam_bin_start+0x3224c4> @ imm = #0x4
438634be:      	cmp	r3, #0x18
438634c0:      	bne	0x43863560 <_binary_input_a7s_av_cam_bin_start+0x322560> @ imm = #0x9c
438634c2:      	b	0x438634e6 <_binary_input_a7s_av_cam_bin_start+0x3224e6> @ imm = #0x20
438634c4:      	cmp	r3, #0x1f
438634c6:      	beq	0x43863548 <_binary_input_a7s_av_cam_bin_start+0x322548> @ imm = #0x7e
438634c8:      	cmp	r3, #0x20
438634ca:      	bne	0x43863560 <_binary_input_a7s_av_cam_bin_start+0x322560> @ imm = #0x92
438634cc:      	b	0x43863554 <_binary_input_a7s_av_cam_bin_start+0x322554> @ imm = #0x84
438634ce:      	ldr.w	r3, [r6, #0x6b0]
438634d2:      	cmp	r3, #0x1
438634d4:      	ldr	r3, [pc, #0x22c]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
438634d6:      	ldr.w	r3, [r10, r3]
438634da:      	ite	eq
438634dc:      	ldrheq.w	r3, [r3, #0xb4]
438634e0:      	ldrhne.w	r3, [r3, #0xaa]
438634e4:      	b	0x43863562 <_binary_input_a7s_av_cam_bin_start+0x322562> @ imm = #0x7a
438634e6:      	ldr.w	r3, [r6, #0x6b0]
438634ea:      	cmp	r3, #0x1
438634ec:      	ldr	r3, [pc, #0x214]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
438634ee:      	ldr.w	r3, [r10, r3]
438634f2:      	bne	0x4386350e <_binary_input_a7s_av_cam_bin_start+0x32250e> @ imm = #0x18
438634f4:      	b	0x4386354e <_binary_input_a7s_av_cam_bin_start+0x32254e> @ imm = #0x56
438634f6:      	ldr.w	r3, [r6, #0x94]
438634fa:      	cmp	r3, #0x7
438634fc:      	bne	0x43863514 <_binary_input_a7s_av_cam_bin_start+0x322514> @ imm = #0x14
438634fe:      	add.w	r3, r6, #0x4800
43863502:      	ldr	r3, [r3, #0x70]
43863504:      	cmp	r3, #0x4
43863506:      	bne	0x43863514 <_binary_input_a7s_av_cam_bin_start+0x322514> @ imm = #0xa
43863508:      	ldr	r3, [pc, #0x1f8]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
4386350a:      	ldr.w	r3, [r10, r3]
4386350e:      	ldrh.w	r3, [r3, #0xa4]
43863512:      	b	0x43863562 <_binary_input_a7s_av_cam_bin_start+0x322562> @ imm = #0x4c
43863514:      	ldr	r3, [r6, #0x28]
43863516:      	cbnz	r3, 0x43863530 <_binary_input_a7s_av_cam_bin_start+0x322530> @ imm = #0x16
43863518:      	ldr.w	r3, [r6, #0x6b0]
4386351c:      	cmp	r3, #0x1
4386351e:      	ldr	r3, [pc, #0x1e4]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
43863520:      	ldr.w	r3, [r10, r3]
43863524:      	ite	eq
43863526:      	ldrheq.w	r3, [r3, #0xac]
4386352a:      	ldrhne.w	r3, [r3, #0xa0]
4386352e:      	b	0x43863562 <_binary_input_a7s_av_cam_bin_start+0x322562> @ imm = #0x30
43863530:      	cmp	r3, #0x1
43863532:      	bne	0x43863540 <_binary_input_a7s_av_cam_bin_start+0x322540> @ imm = #0xa
43863534:      	ldr	r3, [pc, #0x1cc]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
43863536:      	ldr.w	r3, [r10, r3]
4386353a:      	ldrh.w	r3, [r3, #0xa2]
4386353e:      	b	0x43863562 <_binary_input_a7s_av_cam_bin_start+0x322562> @ imm = #0x20
43863540:      	movs	r2, #0x0
43863542:      	strh.w	r2, [r8, #0x152]
43863546:      	b	0x43863566 <_binary_input_a7s_av_cam_bin_start+0x322566> @ imm = #0x1c
43863548:      	ldr	r3, [pc, #0x1b8]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
4386354a:      	ldr.w	r3, [r10, r3]
4386354e:      	ldrh.w	r3, [r3, #0xa6]
43863552:      	b	0x43863562 <_binary_input_a7s_av_cam_bin_start+0x322562> @ imm = #0xc
43863554:      	ldr	r3, [pc, #0x1ac]        @ 0x43863704 <_binary_input_a7s_av_cam_bin_start+0x322704>
43863556:      	ldr.w	r3, [r10, r3]
4386355a:      	ldrh.w	r3, [r3, #0xa8]
4386355e:      	b	0x43863562 <_binary_input_a7s_av_cam_bin_start+0x322562> @ imm = #0x0
43863560:      	movs	r3, #0x0
43863562:      	strh.w	r3, [r8, #0x152]
43863566:      	ldr	r3, [pc, #0x1a0]        @ 0x43863708 <_binary_input_a7s_av_cam_bin_start+0x322708>
43863568:      	ldr	r0, [sp, #0x58]
4386356a:      	ldr	r1, [sp, #0x60]
4386356c:      	ldr.w	r3, [r10, r3]
43863570:      	ldr	r2, [sp, #0x5c]
43863572:      	str	r3, [sp]
43863574:      	ldr	r3, [pc, #0x194]        @ 0x4386370c <_binary_input_a7s_av_cam_bin_start+0x32270c>
43863576:      	ldr.w	r3, [r10, r3]
4386357a:      	str	r0, [sp, #0x8]
4386357c:      	ldr	r0, [sp, #0x50]
4386357e:      	str	r3, [sp, #0x4]
43863580:      	ldr	r3, [pc, #0x18c]        @ 0x43863710 <_binary_input_a7s_av_cam_bin_start+0x322710>
43863582:      	ldr.w	r3, [r10, r3]
43863586:      	str	r1, [sp, #0x10]
43863588:      	str	r2, [sp, #0x14]
4386358a:      	str	r3, [sp, #0xc]
4386358c:      	ldr	r3, [pc, #0x184]        @ 0x43863714 <_binary_input_a7s_av_cam_bin_start+0x322714>
4386358e:      	ldr	r1, [sp, #0x4c]
43863590:      	ldr	r2, [sp, #0x48]
43863592:      	ldr.w	r3, [r10, r3]
43863596:      	str	r0, [sp, #0x20]
43863598:      	mov	r0, r7
4386359a:      	str	r1, [sp, #0x24]
4386359c:      	mov	r1, r9
4386359e:      	str	r3, [sp, #0x18]
438635a0:      	ldr	r3, [sp, #0x3c]
438635a2:      	str.w	r8, [sp, #0x2c]
438635a6:      	str	r3, [sp, #0x1c]
438635a8:      	add.w	r3, r5, #0x960
438635ac:      	adds	r3, #0x1c
438635ae:      	str	r3, [sp, #0x28]
438635b0:      	movs	r3, #0x0
438635b2:      	str	r3, [sp, #0x30]
438635b4:      	ldr	r3, [pc, #0x160]        @ 0x43863718 <_binary_input_a7s_av_cam_bin_start+0x322718>
438635b6:      	ldr.w	r3, [r10, r3]
438635ba:      	bl	0x437c33a0 <_binary_input_a7s_av_cam_bin_start+0x2823a0> @ imm = #-0xa021e
438635be:      	ldr	r2, [sp, #0x50]
438635c0:      	mov	r0, r7
438635c2:      	ldr	r1, [sp, #0x48]
438635c4:      	bl	0x43861fdc <_binary_input_a7s_av_cam_bin_start+0x320fdc> @ imm = #-0x15ec
438635c8:      	ldrh.w	r1, [r9, #0x164]
438635cc:      	ldrh.w	r3, [r9, #0x162]
438635d0:      	movw	r0, #0x391
438635d4:      	orr.w	r1, r3, r1, lsl #16
438635d8:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x8308c
438635dc:      	ldrh.w	r1, [r9, #0x168]
438635e0:      	ldrh.w	r3, [r9, #0x166]
438635e4:      	movw	r0, #0x391
438635e8:      	orr.w	r1, r3, r1, lsl #16
438635ec:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x830a0
438635f0:      	ldr	r2, [sp, #0x44]
438635f2:      	cmp	r2, #0x1
438635f4:      	bne	0x4386364c <_binary_input_a7s_av_cam_bin_start+0x32264c> @ imm = #0x54
438635f6:      	ldr	r0, [sp, #0x40]
438635f8:      	ldrb	r2, [r4]
438635fa:      	ldrb	r1, [r4, #0x1]
438635fc:      	ldrb	r3, [r0, #0x1]
438635fe:      	lsls	r3, r3, #0x8
43863600:      	orr.w	r3, r3, r2, lsl #16
43863604:      	ldrb	r2, [r0]
43863606:      	movw	r0, #0x391
4386360a:      	orrs	r3, r2
4386360c:      	orr.w	r1, r3, r1, lsl #24
43863610:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x830c4
43863614:      	ldrb	r3, [r4, #0x4]
43863616:      	ldrb	r2, [r4, #0x5]
43863618:      	movw	r0, #0x391
4386361c:      	ldrb	r1, [r4, #0x3]
4386361e:      	lsls	r3, r3, #0x10
43863620:      	orr.w	r3, r3, r2, lsl #24
43863624:      	ldrb	r2, [r4, #0x2]
43863626:      	orrs	r3, r2
43863628:      	orr.w	r1, r3, r1, lsl #8
4386362c:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x830e0
43863630:      	ldrb	r3, [r4, #0xd]
43863632:      	ldrb	r2, [r4, #0xe]
43863634:      	movw	r0, #0x391
43863638:      	ldrb	r1, [r4, #0xc]
4386363a:      	lsls	r3, r3, #0x10
4386363c:      	orr.w	r3, r3, r2, lsl #24
43863640:      	ldrb	r2, [r4, #0x6]
43863642:      	orrs	r3, r2
43863644:      	orr.w	r1, r3, r1, lsl #8
43863648:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x830fc
4386364c:      	movw	r0, #0x391
43863650:      	ldrb.w	r1, [r5, #0x2c2]
43863654:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x83108
43863658:      	ldrb.w	r1, [r5, #0x320]
4386365c:      	ldrb.w	r3, [r5, #0x324]
43863660:      	movw	r0, #0x391
43863664:      	lsls	r1, r1, #0x8
43863666:      	orr.w	r1, r1, r3, lsl #16
4386366a:      	ldrb.w	r3, [r5, #0x31c]
4386366e:      	orrs	r1, r3
43863670:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x83124
43863674:      	ldrh.w	r1, [r5, #0x32c]
43863678:      	ldrh.w	r3, [r5, #0x32a]
4386367c:      	movw	r0, #0x391
43863680:      	orr.w	r1, r3, r1, lsl #16
43863684:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x83138
43863688:      	movw	r0, #0x391
4386368c:      	ldrh.w	r1, [r5, #0x32e]
43863690:      	bl	0x437e0514 <_binary_input_a7s_av_cam_bin_start+0x29f514> @ imm = #-0x83180
43863694:      	movs	r0, #0x10
43863696:      	mov	r1, r5
43863698:      	add.w	r2, r6, #0x1b8
4386369c:      	bl	0x437e1fb0 <_binary_input_a7s_av_cam_bin_start+0x2a0fb0> @ imm = #-0x816f0
438636a0:      	add	sp, #0x94
438636a2:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, r11, pc}
438636a6:      	nop
438636a8:      	asrs	r4, r0, #0x1c
438636aa:      	lsls	r4, r7, #0x1
438636ac:      	subs	r4, r1, r4
438636ae:      	movs	r0, r0
438636b0:      	ldrh	r1, [r3, #0x1e]
438636b2:      	lsls	r4, r6, #0x1
438636b4:      	movs	r7, #0x2c
438636b6:      	lsls	r2, r5, #0x1
438636b8:      	asrs	r0, r4, #0x1e
438636ba:      	movs	r0, r0
438636bc:      	movs	r6, #0xfa
438636be:      	lsls	r2, r5, #0x1
438636c0:      	subs	r7, #0x7c
438636c2:      	movs	r0, r0
438636c4:      	adds	r7, #0x78
438636c6:      	movs	r0, r0
438636c8:      	ldr	r0, [pc, #0x1e0]        @ 0x438638ac <_binary_input_a7s_av_cam_bin_start+0x3228ac>
438636ca:      	movs	r0, r0
438636cc:      	ldrh	r0, [r1, #0x28]
438636ce:      	movs	r0, r0
438636d0:      	ldrh	r1, [r5, #0x8]
438636d2:      	lsls	r4, r6, #0x1
438636d4:      	subs	r4, r0, r5
438636d6:      	lsls	r2, r5, #0x1
438636d8:      	ldrh	r5, [r1, #0x8]
438636da:      	lsls	r4, r6, #0x1
438636dc:      	ldrh	r7, [r6, #0x6]
438636de:      	lsls	r4, r6, #0x1
438636e0:      	cmp	r1, #0x99
438636e2:      	lsls	r5, r0, #0x1
438636e4:      	adds	r4, #0xdc
438636e6:      	lsls	r2, r6, #0x1
438636e8:      	ldr	r0, [r7, #0x5c]
438636ea:      	movs	r0, r0
438636ec:      	movs	r2, #0xc8
438636ee:      	lsls	r2, r5, #0x1
438636f0:      	movs	r7, #0xf0
438636f2:      	movs	r0, r0
438636f4:      	adds	r0, r2, r0
438636f6:      	lsls	r2, r5, #0x1
438636f8:      	adds	r2, #0x9e
438636fa:      	lsls	r2, r6, #0x1
438636fc:      	strh	r7, [r2, #0x2e]
438636fe:      	lsls	r4, r6, #0x1
43863700:      	strh	r7, [r1, #0x2e]
43863702:      	lsls	r4, r6, #0x1
43863704:      	lsls	r0, r4, #0x13
43863706:      	movs	r0, r0
43863708:      	str	r4, [r0, r6]
4386370a:      	movs	r0, r0
4386370c:      	adds	r1, #0x0
4386370e:      	movs	r0, r0
43863710:      	lsrs	r0, r6, #0x2
43863712:      	movs	r0, r0
43863714:      	strb	r0, [r4, #0x5]
43863716:      	movs	r0, r0
43863718:      	ldr	r0, [r6, r7]
4386371a:      	movs	r0, r0
4386371c:      	push.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
43863720:      	mov	r5, r0
43863722:      	ldr.w	r10, [pc, #0x568]       @ 0x43863c8c <_binary_input_a7s_av_cam_bin_start+0x322c8c>
43863726:      	sub	sp, #0x2c
43863728:      	ldr.w	r3, [pc, #0x564]        @ 0x43863c90 <_binary_input_a7s_av_cam_bin_start+0x322c90>
4386372c:      	mov	r6, r1
4386372e:      	add	r10, pc
43863730:      	mov	r8, r2
43863732:      	ldr.w	r3, [r10, r3]
43863736:      	ldr.w	r3, [r3, #0x4fc]
4386373a:      	cmp	r3, #0x1
4386373c:      	bne.w	0x43863848 <_binary_input_a7s_av_cam_bin_start+0x322848> @ imm = #0x108
43863740:      	ldr.w	r3, [pc, #0x550]        @ 0x43863c94 <_binary_input_a7s_av_cam_bin_start+0x322c94>
43863744:      	ldr.w	r3, [r10, r3]
43863748:      	ldrb.w	r3, [r3, #0x23]
4386374c:      	cmp	r3, #0x0
4386374e:      	beq	0x43863848 <_binary_input_a7s_av_cam_bin_start+0x322848> @ imm = #0xf6
43863750:      	ldr.w	r0, [r1, #0x1c0]
43863754:      	ldr.w	r1, [r1, #0x1b8]
43863758:      	bl	0x43862060 <_binary_input_a7s_av_cam_bin_start+0x321060> @ imm = #-0x16fc
4386375c:      	mov	r11, r0
4386375e:      	ldr.w	r0, [r6, #0x1c0]
43863762:      	bl	0x43861eec <_binary_input_a7s_av_cam_bin_start+0x320eec> @ imm = #-0x187a
43863766:      	cmp	r0, #0x0
43863768:      	beq.w	0x43863c74 <_binary_input_a7s_av_cam_bin_start+0x322c74> @ imm = #0x508
4386376c:      	cmp.w	r8, #0x0
43863770:      	beq.w	0x43863c86 <_binary_input_a7s_av_cam_bin_start+0x322c86> @ imm = #0x512
43863774:      	ldrb.w	r3, [r5, #0x143]
43863778:      	cmp	r3, #0x1
4386377a:      	beq.w	0x43863c74 <_binary_input_a7s_av_cam_bin_start+0x322c74> @ imm = #0x4f6
4386377e:      	ldr	r3, [r5, #0x8]
43863780:      	cmp	r3, #0x11
43863782:      	bne	0x43863790 <_binary_input_a7s_av_cam_bin_start+0x322790> @ imm = #0xa
43863784:      	ldr	r2, [r5, #0xc]
43863786:      	ldr.w	r3, [r8, #0xb78]
4386378a:      	cmp	r2, r3
4386378c:      	bne.w	0x43863c74 <_binary_input_a7s_av_cam_bin_start+0x322c74> @ imm = #0x4e4
43863790:      	ldr.w	r1, [r6, #0x1b8]
43863794:      	add.w	r9, r5, #0x960
43863798:      	ldr.w	r0, [r6, #0x1c0]
4386379c:      	add.w	r10, r5, #0x4
438637a0:      	bl	0x43862d54 <_binary_input_a7s_av_cam_bin_start+0x321d54> @ imm = #-0xa50
438637a4:      	ldr.w	r7, [pc, #0x4f0]        @ 0x43863c98 <_binary_input_a7s_av_cam_bin_start+0x322c98>
438637a8:      	add.w	r9, r9, #0x1c
438637ac:      	add	r7, pc
438637ae:      	mov	r1, r9
438637b0:      	mov	r2, r7
438637b2:      	mov	r4, r0
438637b4:      	mov	r0, r10
438637b6:      	bl	0x437eeebc <_binary_input_a7s_av_cam_bin_start+0x2adebc> @ imm = #-0x748fe
438637ba:      	mov	r0, r10
438637bc:      	mov	r1, r9
438637be:      	mov	r2, r7
438637c0:      	bl	0x438654ec <_binary_input_a7s_av_cam_bin_start+0x3244ec> @ imm = #0x1d28
438637c4:      	add.w	r3, r5, #0x1940
438637c8:      	ldr.w	r0, [r6, #0x1c0]
438637cc:      	ldrh	r2, [r3, #0x4]
438637ce:      	ldrh	r3, [r3, #0x6]
438637d0:      	ldr.w	r1, [r6, #0x1b8]
438637d4:      	strh	r2, [r4]
438637d6:      	strh	r3, [r4, #0x2]
438637d8:      	ldrh.w	r2, [r5, #0x160]
438637dc:      	ldrh.w	r3, [r5, #0x15a]
438637e0:      	adds	r3, r2, r3
438637e2:      	ldrh.w	r2, [r5, #0x164]
438637e6:      	adds	r3, r3, r2
438637e8:      	ldrh.w	r2, [r5, #0x166]
438637ec:      	adds	r3, r3, r2
438637ee:      	strh	r3, [r4, #0x4]
438637f0:      	bl	0x43862034 <_binary_input_a7s_av_cam_bin_start+0x321034> @ imm = #-0x17c0
438637f4:      	ldr.w	r3, [r0, #0x500]
438637f8:      	cbnz	r3, 0x43863812 <_binary_input_a7s_av_cam_bin_start+0x322812> @ imm = #0x16
438637fa:      	ldr.w	r3, [r0, #0x508]
438637fe:      	cmp	r3, #0x1
43863800:      	bne	0x43863812 <_binary_input_a7s_av_cam_bin_start+0x322812> @ imm = #0xe
43863802:      	ldrh.w	r0, [r5, #0x136]
43863806:      	ldrh	r7, [r4, #0x4]
43863808:      	lsrs	r0, r0, #0x4
4386380a:      	bl	0x4370c088 <_binary_input_a7s_av_cam_bin_start+0x1cb088> @ imm = #-0x157786
4386380e:      	adds	r0, r7, r0
43863810:      	strh	r0, [r4, #0x4]
43863812:      	movs	r3, #0x1
43863814:      	mov	r0, r5
43863816:      	strb	r3, [r4, #0x6]
43863818:      	mov	r1, r8
4386381a:      	ldr.w	r3, [r6, #0x1b8]
4386381e:      	mov	r2, r11
43863820:      	bl	0x43b0b838 <_binary_input_a7s_av_cam_bin_start+0x5ca838> @ imm = #0x2a8014
43863824:      	ldr.w	r3, [r6, #0x1b8]
43863828:      	str	r3, [r4, #0x8]
4386382a:      	ldr.w	r3, [r6, #0x1c0]
4386382e:      	str	r3, [r4, #0xc]
43863830:      	ldrb.w	r3, [r5, #0xf0]
43863834:      	strb	r3, [r4, #0x10]
43863836:      	add.w	r3, r5, #0x1940
4386383a:      	ldr	r3, [r3]
4386383c:      	str	r3, [r4, #0x14]
4386383e:      	add.w	r3, r5, #0x1900
43863842:      	ldr	r3, [r3, #0x3c]
43863844:      	str	r3, [r4, #0x18]
43863846:      	b	0x43863c74 <_binary_input_a7s_av_cam_bin_start+0x322c74> @ imm = #0x42a
43863848:      	ldr.w	r3, [pc, #0x450]        @ 0x43863c9c <_binary_input_a7s_av_cam_bin_start+0x322c9c>
4386384c:      	ldr.w	r3, [r10, r3]
43863850:      	ldrb	r3, [r3]
43863852:      	cmp	r3, #0x0
43863854:      	beq.w	0x43863c86 <_binary_input_a7s_av_cam_bin_start+0x322c86> @ imm = #0x42e
43863858:      	movs	r3, #0x0
4386385a:      	ldr.w	r1, [r6, #0x1b8]
4386385e:      	strb	r3, [r5, #0x4]
43863860:      	ldr.w	r0, [r6, #0x1c0]
43863864:      	bl	0x43862034 <_binary_input_a7s_av_cam_bin_start+0x321034> @ imm = #-0x1834
43863868:      	ldr.w	r1, [r6, #0x1b8]
4386386c:      	str	r0, [sp, #0x20]
4386386e:      	ldr.w	r0, [r6, #0x1c0]
43863872:      	bl	0x43861f2c <_binary_input_a7s_av_cam_bin_start+0x320f2c> @ imm = #-0x194a
43863876:      	ldr.w	r1, [r6, #0x1b8]
4386387a:      	mov	r4, r0
4386387c:      	ldr.w	r0, [r6, #0x1c0]
43863880:      	bl	0x43862060 <_binary_input_a7s_av_cam_bin_start+0x321060> @ imm = #-0x1824
43863884:      	mov	r7, r0
43863886:      	ldr.w	r0, [r6, #0x1c0]
4386388a:      	bl	0x43861eec <_binary_input_a7s_av_cam_bin_start+0x320eec> @ imm = #-0x19a2
4386388e:      	cmp	r0, #0x0
43863890:      	beq	0x43863980 <_binary_input_a7s_av_cam_bin_start+0x322980> @ imm = #0xec
43863892:      	cmp.w	r8, #0x0
43863896:      	beq.w	0x43863c86 <_binary_input_a7s_av_cam_bin_start+0x322c86> @ imm = #0x3ec
4386389a:      	ldr	r2, [sp, #0x20]
4386389c:      	ldrb.w	r3, [r2, #0x3dc]
438638a0:      	cmp	r3, #0x1
438638a2:      	bne	0x438638b4 <_binary_input_a7s_av_cam_bin_start+0x3228b4> @ imm = #0xe
438638a4:      	ldr.w	r1, [r6, #0x1b8]
438638a8:      	ldr.w	r0, [r6, #0x1c0]
438638ac:      	adds	r1, #0x1
438638ae:      	bl	0x43b0bb32 <_binary_input_a7s_av_cam_bin_start+0x5cab32> @ imm = #0x2a8280
438638b2:      	b	0x43863980 <_binary_input_a7s_av_cam_bin_start+0x322980> @ imm = #0xca
438638b4:      	ldr	r3, [r5, #0x8]
438638b6:      	cmp	r3, #0x11
438638b8:      	bne	0x438638c4 <_binary_input_a7s_av_cam_bin_start+0x3228c4> @ imm = #0x8
438638ba:      	ldr	r2, [r5, #0xc]
438638bc:      	ldr.w	r3, [r8, #0xb78]
438638c0:      	cmp	r2, r3
438638c2:      	bne	0x43863980 <_binary_input_a7s_av_cam_bin_start+0x322980> @ imm = #0xba
438638c4:      	mov.w	r0, #0x38c
438638c8:      	ldr.w	r1, [r6, #0x1b8]
438638cc:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x83380
438638d0:      	ldr.w	r1, [r6, #0x1b8]
438638d4:      	ldr.w	r0, [r6, #0x1c0]
438638d8:      	add.w	r9, r5, #0x960
438638dc:      	bl	0x43861f84 <_binary_input_a7s_av_cam_bin_start+0x320f84> @ imm = #-0x195c
438638e0:      	ldr.w	r1, [r6, #0x1b8]
438638e4:      	add.w	r9, r9, #0x1c
438638e8:      	mov	r11, r0
438638ea:      	ldr.w	r0, [r6, #0x1c0]
438638ee:      	bl	0x43861fb0 <_binary_input_a7s_av_cam_bin_start+0x320fb0> @ imm = #-0x1942
438638f2:      	adds	r3, r5, #0x4
438638f4:      	mov	r1, r9
438638f6:      	mov	r2, r11
438638f8:      	str	r3, [sp, #0x1c]
438638fa:      	str	r0, [sp, #0x24]
438638fc:      	mov	r0, r3
438638fe:      	bl	0x437eeebc <_binary_input_a7s_av_cam_bin_start+0x2adebc> @ imm = #-0x74a46
43863902:      	ldr	r3, [sp, #0x1c]
43863904:      	mov	r1, r9
43863906:      	mov	r2, r11
43863908:      	mov	r0, r3
4386390a:      	bl	0x438654ec <_binary_input_a7s_av_cam_bin_start+0x3244ec> @ imm = #0x1bde
4386390e:      	add.w	r3, r5, #0x1940
43863912:      	mov	r0, r5
43863914:      	mov	r1, r8
43863916:      	ldrh	r2, [r3, #0x4]
43863918:      	ldrh	r3, [r3, #0x6]
4386391a:      	strh.w	r2, [r4, #0x48]
4386391e:      	strh.w	r3, [r4, #0x4a]
43863922:      	ldrh.w	r2, [r5, #0x160]
43863926:      	ldrh.w	r3, [r5, #0x15a]
4386392a:      	adds	r3, r2, r3
4386392c:      	ldrh.w	r2, [r5, #0x164]
43863930:      	adds	r3, r3, r2
43863932:      	ldrh.w	r2, [r5, #0x166]
43863936:      	adds	r3, r3, r2
43863938:      	mov	r2, r7
4386393a:      	strh	r3, [r4, #0x36]
4386393c:      	ldr.w	r3, [r6, #0x1b8]
43863940:      	bl	0x43b0b838 <_binary_input_a7s_av_cam_bin_start+0x5ca838> @ imm = #0x2a7ef4
43863944:      	ldr	r3, [sp, #0x24]
43863946:      	str.w	r11, [sp]
4386394a:      	ldr	r0, [sp, #0x20]
4386394c:      	str	r3, [sp, #0x4]
4386394e:      	ldr	r3, [pc, #0x350]        @ 0x43863ca0 <_binary_input_a7s_av_cam_bin_start+0x322ca0>
43863950:      	ldr.w	r3, [r10, r3]
43863954:      	str	r4, [sp, #0xc]
43863956:      	str	r7, [sp, #0x10]
43863958:      	str	r3, [sp, #0x8]
4386395a:      	ldr	r3, [pc, #0x348]        @ 0x43863ca4 <_binary_input_a7s_av_cam_bin_start+0x322ca4>
4386395c:      	str.w	r8, [sp, #0x14]
43863960:      	ldr.w	r1, [r10, r3]
43863964:      	ldr	r3, [pc, #0x340]        @ 0x43863ca8 <_binary_input_a7s_av_cam_bin_start+0x322ca8>
43863966:      	ldr.w	r2, [r10, r3]
4386396a:      	add.w	r3, r5, #0xb00
4386396e:      	adds	r3, #0x14
43863970:      	bl	0x43854cd8 <_binary_input_a7s_av_cam_bin_start+0x313cd8> @ imm = #-0xec9c
43863974:      	movs	r3, #0x1
43863976:      	mov	r0, r4
43863978:      	strb	r3, [r5, #0x4]
4386397a:      	ldr	r1, [sp, #0x24]
4386397c:      	bl	0x437c8160 <_binary_input_a7s_av_cam_bin_start+0x287160> @ imm = #-0x9b820
43863980:      	mov	r0, r6
43863982:      	bl	0x43aee5b8 <_binary_input_a7s_av_cam_bin_start+0x5ad5b8> @ imm = #0x28ac32
43863986:      	mov	r3, r0
43863988:      	cmp	r0, #0x0
4386398a:      	beq.w	0x43863c74 <_binary_input_a7s_av_cam_bin_start+0x322c74> @ imm = #0x2e6
4386398e:      	ldrb.w	r2, [r6, #0x1b8]
43863992:      	strb.w	r2, [r0, #0x184]
43863996:      	ldrb.w	r2, [r6, #0x1b9]
4386399a:      	strb.w	r2, [r0, #0x185]
4386399e:      	ldrb.w	r2, [r6, #0x1ba]
438639a2:      	strb.w	r2, [r0, #0x186]
438639a6:      	ldrb.w	r2, [r6, #0x1bb]
438639aa:      	strb.w	r2, [r0, #0x187]
438639ae:      	ldrb.w	r2, [r6, #0x1c0]
438639b2:      	strb.w	r2, [r0, #0x188]
438639b6:      	ldrb.w	r2, [r6, #0x1c1]
438639ba:      	strb.w	r2, [r0, #0x189]
438639be:      	ldrb.w	r2, [r6, #0x1c2]
438639c2:      	strb.w	r2, [r0, #0x18a]
438639c6:      	ldrb.w	r2, [r6, #0x1c3]
438639ca:      	strb.w	r2, [r0, #0x18b]
438639ce:      	ldrb	r2, [r5, #0x4]
438639d0:      	strb.w	r2, [r0, #0x18d]
438639d4:      	add.w	r0, r0, #0x18c
438639d8:      	str	r3, [sp, #0x1c]
438639da:      	bl	0x43848e74 <_binary_input_a7s_av_cam_bin_start+0x307e74> @ imm = #-0x1ab6a
438639de:      	ldrb	r2, [r5, #0x4]
438639e0:      	ldr	r3, [sp, #0x1c]
438639e2:      	cmp	r2, #0x0
438639e4:      	beq.w	0x43863c74 <_binary_input_a7s_av_cam_bin_start+0x322c74> @ imm = #0x28c
438639e8:      	ldrb.w	r2, [r5, #0xf0]
438639ec:      	add.w	r0, r5, #0x1900
438639f0:      	strb.w	r2, [r3, #0x18e]
438639f4:      	add.w	r2, r5, #0x1940
438639f8:      	ldrb	r1, [r2]
438639fa:      	strb.w	r1, [r3, #0x18f]
438639fe:      	ldrb	r1, [r2, #0x1]
43863a00:      	strb.w	r1, [r3, #0x190]
43863a04:      	ldrb	r1, [r2, #0x2]
43863a06:      	strb.w	r1, [r3, #0x191]
43863a0a:      	ldrb	r1, [r2, #0x3]
43863a0c:      	strb.w	r1, [r3, #0x192]
43863a10:      	add.w	r1, r0, #0x3c
43863a14:      	ldrb.w	r0, [r0, #0x3c]
43863a18:      	strb.w	r0, [r3, #0x193]
43863a1c:      	ldrb	r0, [r1, #0x1]
43863a1e:      	strb.w	r0, [r3, #0x194]
43863a22:      	ldrb	r0, [r1, #0x2]
43863a24:      	strb.w	r0, [r3, #0x195]
43863a28:      	ldrb	r1, [r1, #0x3]
43863a2a:      	strb.w	r1, [r3, #0x196]
43863a2e:      	ldrb	r1, [r2, #0x6]
43863a30:      	strb.w	r1, [r3, #0x197]
43863a34:      	ldrb	r1, [r2, #0x7]
43863a36:      	strb.w	r1, [r3, #0x198]
43863a3a:      	ldrb	r1, [r2, #0x4]
43863a3c:      	strb.w	r1, [r3, #0x199]
43863a40:      	ldrb	r2, [r2, #0x5]
43863a42:      	strb.w	r2, [r3, #0x19a]
43863a46:      	ldrb.w	r2, [r4, #0x48]
43863a4a:      	strb.w	r2, [r3, #0x19d]
43863a4e:      	ldrb.w	r2, [r4, #0x49]
43863a52:      	strb.w	r2, [r3, #0x19e]
43863a56:      	ldrb.w	r2, [r4, #0x4a]
43863a5a:      	strb.w	r2, [r3, #0x19b]
43863a5e:      	ldrb.w	r2, [r4, #0x4b]
43863a62:      	strb.w	r2, [r3, #0x19c]
43863a66:      	ldrb.w	r2, [r4, #0x36]
43863a6a:      	strb.w	r2, [r3, #0x19f]
43863a6e:      	ldrb.w	r2, [r4, #0x37]
43863a72:      	strb.w	r2, [r3, #0x1a0]
43863a76:      	ldrb.w	r2, [r4, #0x11e]
43863a7a:      	strb.w	r2, [r3, #0x1a1]
43863a7e:      	ldrb.w	r2, [r4, #0x11f]
43863a82:      	strb.w	r2, [r3, #0x1a2]
43863a86:      	ldrb.w	r2, [r4, #0x50]
43863a8a:      	strb.w	r2, [r3, #0x1a3]
43863a8e:      	ldrb.w	r2, [r4, #0x51]
43863a92:      	strb.w	r2, [r3, #0x1a4]
43863a96:      	ldrb.w	r2, [r4, #0x1ce]
43863a9a:      	strb.w	r2, [r3, #0x1a5]
43863a9e:      	ldrb.w	r2, [r4, #0x1cf]
43863aa2:      	strb.w	r2, [r3, #0x1a6]
43863aa6:      	ldrb.w	r2, [r4, #0x1d0]
43863aaa:      	strb.w	r2, [r3, #0x1a7]
43863aae:      	ldrb.w	r2, [r4, #0x1d1]
43863ab2:      	strb.w	r2, [r3, #0x1a8]
43863ab6:      	ldrb.w	r2, [r4, #0x1d2]
43863aba:      	strb.w	r2, [r3, #0x1a9]
43863abe:      	ldrb.w	r2, [r4, #0x1d3]
43863ac2:      	strb.w	r2, [r3, #0x1aa]
43863ac6:      	ldrb.w	r2, [r4, #0x1d6]
43863aca:      	strb.w	r2, [r3, #0x1ab]
43863ace:      	ldrb.w	r2, [r4, #0x1d7]
43863ad2:      	strb.w	r2, [r3, #0x1ac]
43863ad6:      	ldrb.w	r2, [r4, #0x1d8]
43863ada:      	strb.w	r2, [r3, #0x1ad]
43863ade:      	ldrb.w	r2, [r4, #0x1d9]
43863ae2:      	strb.w	r2, [r3, #0x1ae]
43863ae6:      	ldrb.w	r2, [r4, #0x1da]
43863aea:      	strb.w	r2, [r3, #0x1af]
43863aee:      	ldrb.w	r2, [r4, #0x1db]
43863af2:      	strb.w	r2, [r3, #0x1b0]
43863af6:      	ldrb.w	r2, [r4, #0x1dc]
43863afa:      	strb.w	r2, [r3, #0x1b1]
43863afe:      	ldrb.w	r2, [r4, #0x1dd]
43863b02:      	strb.w	r2, [r3, #0x1b2]
43863b06:      	ldrb.w	r2, [r4, #0x1de]
43863b0a:      	strb.w	r2, [r3, #0x24e]
43863b0e:      	ldrb.w	r2, [r4, #0x1df]
43863b12:      	strb.w	r2, [r3, #0x24f]
43863b16:      	ldrb.w	r2, [r4, #0x1e0]
43863b1a:      	strb.w	r2, [r3, #0x1b3]
43863b1e:      	ldrb.w	r2, [r4, #0x1e1]
43863b22:      	strb.w	r2, [r3, #0x1b4]
43863b26:      	ldrb.w	r2, [r4, #0x120]
43863b2a:      	strb.w	r2, [r3, #0x1b5]
43863b2e:      	ldrb.w	r2, [r4, #0x121]
43863b32:      	strb.w	r2, [r3, #0x1b6]
43863b36:      	ldrb.w	r2, [r4, #0x124]
43863b3a:      	strb.w	r2, [r3, #0x1b7]
43863b3e:      	ldrb.w	r2, [r4, #0x125]
43863b42:      	strb.w	r2, [r3, #0x1b8]
43863b46:      	cmp.w	r8, #0x0
43863b4a:      	beq	0x43863b62 <_binary_input_a7s_av_cam_bin_start+0x322b62> @ imm = #0x14
43863b4c:      	ldrb.w	r2, [r8, #0xb7e]
43863b50:      	strb.w	r2, [r3, #0x1b9]
43863b54:      	ldrb.w	r2, [r8, #0xb7f]
43863b58:      	strb.w	r2, [r3, #0x1ba]
43863b5c:      	ldrb.w	r2, [r8, #0xb7c]
43863b60:      	b	0x43863b6e <_binary_input_a7s_av_cam_bin_start+0x322b6e> @ imm = #0xa
43863b62:      	mov.w	r2, #0xffffffff
43863b66:      	strb.w	r2, [r3, #0x1b9]
43863b6a:      	strb.w	r2, [r3, #0x1ba]
43863b6e:      	strb.w	r2, [r3, #0x1bb]
43863b72:      	ldrb	r2, [r7, #0x1]
43863b74:      	strb.w	r2, [r3, #0x1bc]
43863b78:      	ldrb	r2, [r7, #0x4]
43863b7a:      	strb.w	r2, [r3, #0x1bd]
43863b7e:      	ldrb	r2, [r7, #0x5]
43863b80:      	strb.w	r2, [r3, #0x1be]
43863b84:      	ldrb	r2, [r7, #0x6]
43863b86:      	strb.w	r2, [r3, #0x1bf]
43863b8a:      	ldrb	r2, [r7, #0x7]
43863b8c:      	strb.w	r2, [r3, #0x1c0]
43863b90:      	ldrb.w	r2, [r7, #0x32]
43863b94:      	strb.w	r2, [r3, #0x1c1]
43863b98:      	ldrb.w	r2, [r7, #0x33]
43863b9c:      	strb.w	r2, [r3, #0x1c2]
43863ba0:      	ldrb	r2, [r7, #0xc]
43863ba2:      	strb.w	r2, [r3, #0x1c3]
43863ba6:      	ldrb	r2, [r7, #0xd]
43863ba8:      	strb.w	r2, [r3, #0x1c4]
43863bac:      	ldrb.w	r2, [r7, #0x34]
43863bb0:      	strb.w	r2, [r3, #0x1c5]
43863bb4:      	ldrb.w	r2, [r7, #0x35]
43863bb8:      	strb.w	r2, [r3, #0x1c6]
43863bbc:      	ldrb	r2, [r7, #0xe]
43863bbe:      	strb.w	r2, [r3, #0x1c7]
43863bc2:      	ldrb	r2, [r7, #0xf]
43863bc4:      	strb.w	r2, [r3, #0x1c8]
43863bc8:      	ldrb.w	r2, [r7, #0x36]
43863bcc:      	strb.w	r2, [r3, #0x1c9]
43863bd0:      	ldrb.w	r2, [r7, #0x37]
43863bd4:      	strb.w	r2, [r3, #0x1ca]
43863bd8:      	ldrb	r2, [r7, #0x12]
43863bda:      	strb.w	r2, [r3, #0x1cb]
43863bde:      	ldrb	r2, [r7, #0x13]
43863be0:      	strb.w	r2, [r3, #0x1cc]
43863be4:      	ldrb.w	r2, [r4, #0x202]
43863be8:      	strb.w	r2, [r3, #0x1cd]
43863bec:      	ldrb.w	r2, [r4, #0x203]
43863bf0:      	strb.w	r2, [r3, #0x1ce]
43863bf4:      	ldrb.w	r2, [r4, #0x204]
43863bf8:      	strb.w	r2, [r3, #0x1cf]
43863bfc:      	ldrb.w	r2, [r4, #0x205]
43863c00:      	strb.w	r2, [r3, #0x1d0]
43863c04:      	ldrb.w	r2, [r4, #0x206]
43863c08:      	strb.w	r2, [r3, #0x1d1]
43863c0c:      	ldrb.w	r2, [r4, #0x207]
43863c10:      	strb.w	r2, [r3, #0x1d2]
43863c14:      	ldrb.w	r2, [r4, #0x130]
43863c18:      	strb.w	r2, [r3, #0x1d3]
43863c1c:      	ldrb.w	r2, [r4, #0x131]
43863c20:      	strb.w	r2, [r3, #0x1d4]
43863c24:      	ldrb.w	r2, [r4, #0x132]
43863c28:      	strb.w	r2, [r3, #0x1d5]
43863c2c:      	ldrb.w	r2, [r4, #0x133]
43863c30:      	strb.w	r2, [r3, #0x1d6]
43863c34:      	ldrb.w	r2, [r5, #0x15a]
43863c38:      	strb.w	r2, [r3, #0x1d7]
43863c3c:      	ldrb.w	r2, [r5, #0x15b]
43863c40:      	strb.w	r2, [r3, #0x1d8]
43863c44:      	ldrb.w	r2, [r5, #0x160]
43863c48:      	strb.w	r2, [r3, #0x1d9]
43863c4c:      	ldrb.w	r2, [r5, #0x161]
43863c50:      	strb.w	r2, [r3, #0x1da]
43863c54:      	ldrb.w	r2, [r5, #0x164]
43863c58:      	strb.w	r2, [r3, #0x1db]
43863c5c:      	ldrb.w	r2, [r5, #0x165]
43863c60:      	strb.w	r2, [r3, #0x1dc]
43863c64:      	ldrb.w	r2, [r5, #0x166]
43863c68:      	strb.w	r2, [r3, #0x1dd]
43863c6c:      	ldrb.w	r2, [r5, #0x167]
43863c70:      	strb.w	r2, [r3, #0x1de]
43863c74:      	movs	r0, #0x1a
43863c76:      	mov	r1, r5
43863c78:      	add.w	r2, r6, #0x1b8
43863c7c:      	add	sp, #0x2c
43863c7e:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
43863c82:      	b.w	0x437e1fb0 <_binary_input_a7s_av_cam_bin_start+0x2a0fb0> @ imm = #-0x81cd6
43863c86:      	add	sp, #0x2c
43863c88:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, r11, pc}
43863c8c:      	lsrs	r6, r1, #0x18
43863c8e:      	lsls	r4, r7, #0x1
43863c90:      	adds	r5, #0x28
43863c92:      	movs	r0, r0
43863c94:      	lsls	r0, r4, #0x13
43863c96:      	movs	r0, r0
43863c98:      	asrs	r0, r4, #0x15
43863c9a:      	lsls	r2, r5, #0x1
43863c9c:      	subs	r4, r1, r4
43863c9e:      	movs	r0, r0
43863ca0:      	lsrs	r0, r6, #0x2
43863ca2:      	movs	r0, r0
43863ca4:      	subs	r7, #0x7c
43863ca6:      	movs	r0, r0
43863ca8:      	adds	r1, #0x0
43863caa:      	movs	r0, r0
43863cac:      	push.w	{r4, r5, r6, r7, r8, lr}
43863cb0:      	mov	r7, r3
43863cb2:      	ldr	r4, [pc, #0x5c]         @ 0x43863d10 <_binary_input_a7s_av_cam_bin_start+0x322d10>
43863cb4:      	mov	r5, r1
43863cb6:      	ldr	r3, [pc, #0x5c]         @ 0x43863d14 <_binary_input_a7s_av_cam_bin_start+0x322d14>
43863cb8:      	mov	r6, r2
43863cba:      	add	r4, pc
43863cbc:      	ldr	r3, [r4, r3]
43863cbe:      	ldrb	r3, [r3]
43863cc0:      	cmp	r3, #0x0
43863cc2:      	beq	0x43863d0a <_binary_input_a7s_av_cam_bin_start+0x322d0a> @ imm = #0x44
43863cc4:      	ldr	r0, [r2, #0x8]
43863cc6:      	bl	0x43861eec <_binary_input_a7s_av_cam_bin_start+0x320eec> @ imm = #-0x1dde
43863cca:      	cmp	r0, #0x0
43863ccc:      	beq	0x43863d0a <_binary_input_a7s_av_cam_bin_start+0x322d0a> @ imm = #0x3a
43863cce:      	ldr	r1, [r6]
43863cd0:      	cmp	r1, #0x0
43863cd2:      	beq	0x43863d02 <_binary_input_a7s_av_cam_bin_start+0x322d02> @ imm = #0x2c
43863cd4:      	cbnz	r7, 0x43863ce2 <_binary_input_a7s_av_cam_bin_start+0x322ce2> @ imm = #0xa
43863cd6:      	ldr	r0, [pc, #0x40]         @ 0x43863d18 <_binary_input_a7s_av_cam_bin_start+0x322d18>
43863cd8:      	add	r0, pc
43863cda:      	pop.w	{r4, r5, r6, r7, r8, lr}
43863cde:      	b.w	0x438f7114 <_binary_input_a7s_av_cam_bin_start+0x3b6114> @ imm = #0x93432
43863ce2:      	movw	r0, #0x38d
43863ce6:      	bl	0x437e0550 <_binary_input_a7s_av_cam_bin_start+0x29f550> @ imm = #-0x8379a
43863cea:      	ldr	r1, [r6]
43863cec:      	ldr	r0, [r6, #0x8]
43863cee:      	bl	0x43862034 <_binary_input_a7s_av_cam_bin_start+0x321034> @ imm = #-0x1cbe
43863cf2:      	ldr	r3, [pc, #0x28]         @ 0x43863d1c <_binary_input_a7s_av_cam_bin_start+0x322d1c>
43863cf4:      	ldr	r2, [r4, r3]
43863cf6:      	mov	r1, r0
43863cf8:      	mov	r0, r5
43863cfa:      	pop.w	{r4, r5, r6, r7, r8, lr}
43863cfe:      	b.w	0x437c96ec <_binary_input_a7s_av_cam_bin_start+0x2886ec> @ imm = #-0x9a616
43863d02:      	pop.w	{r4, r5, r6, r7, r8, lr}
43863d06:      	b.w	0x43848e64 <_binary_input_a7s_av_cam_bin_start+0x307e64> @ imm = #-0x1aea6
43863d0a:      	pop.w	{r4, r5, r6, r7, r8, pc}
43863d0e:      	nop
43863d10:      	lsrs	r2, r0, #0x2
43863d12:      	lsls	r4, r7, #0x1
43863d14:      	subs	r4, r1, r4
43863d16:      	movs	r0, r0
43863d18:      	movs	r2, #0x29
43863d1a:      	lsls	r5, r0, #0x1
43863d1c:      	adds	r7, #0x78
43863d1e:      	movs	r0, r0
43863d20:      	ldr	r3, [pc, #0x18]         @ 0x43863d3c <_binary_input_a7s_av_cam_bin_start+0x322d3c>
43863d22:      	ldr	r2, [pc, #0x1c]         @ 0x43863d40 <_binary_input_a7s_av_cam_bin_start+0x322d40>
43863d24:      	add	r3, pc
43863d26:      	ldr	r3, [r3, r2]
43863d28:      	ldrb.w	r3, [r3, #0x103]
43863d2c:      	tst.w	r3, #0x1
43863d30:      	itte	eq
43863d32:      	addeq.w	r0, r0, #0x1180
43863d36:      	ldreq	r0, [r0, #0x1c]
43863d38:      	movne	r0, #0x0
43863d3a:      	bx	lr
43863d3c:      	lsrs	r0, r3, #0x20
43863d3e:      	lsls	r4, r7, #0x1
43863d40:      	strb	r4, [r5, #0x6]
43863d42:      	movs	r0, r0
43863d44:      	ldr	r0, [pc, #0x4]          @ 0x43863d4c <_binary_input_a7s_av_cam_bin_start+0x322d4c>
43863d46:      	add	r0, pc
43863d48:      	ldr	r0, [r0]
43863d4a:      	bx	lr
43863d4c:      	adds	r2, r7, r4
43863d4e:      	lsls	r2, r5, #0x1
43863d50:      	ldr	r3, [pc, #0x14]         @ 0x43863d68 <_binary_input_a7s_av_cam_bin_start+0x322d68>
43863d52:      	ldrb.w	r2, [r0, #0x89]
43863d56:      	add	r3, pc
43863d58:      	strb	r2, [r3]
43863d5a:      	ldr	r3, [pc, #0x10]         @ 0x43863d6c <_binary_input_a7s_av_cam_bin_start+0x322d6c>
43863d5c:      	ldrh.w	r1, [r1, #0x5c]
43863d60:      	add	r3, pc
43863d62:      	strh	r1, [r3]
43863d64:      	bx	lr
43863d66:      	nop
43863d68:      	ldrb	r6, [r0, #0x14]
43863d6a:      	lsls	r4, r6, #0x1
43863d6c:      	cmp	r1, #0xb6
43863d6e:      	lsls	r2, r6, #0x1
43863d70:      	ldr	r3, [pc, #0x4]          @ 0x43863d78 <_binary_input_a7s_av_cam_bin_start+0x322d78>
43863d72:      	add	r3, pc
43863d74:      	ldrb	r0, [r3]
43863d76:      	bx	lr
43863d78:      	ldrb	r5, [r5, #0x13]
43863d7a:      	lsls	r4, r6, #0x1
43863d7c:      	ldr	r3, [pc, #0x8]          @ 0x43863d88 <_binary_input_a7s_av_cam_bin_start+0x322d88>
43863d7e:      	movs	r2, #0x1
43863d80:      	add	r3, pc
43863d82:      	strb	r2, [r3]
43863d84:      	bx	lr
43863d86:      	nop
43863d88:      	ldrb	r7, [r3, #0x13]
43863d8a:      	lsls	r4, r6, #0x1
43863d8c:      	push.w	{r0, r1, r4, r5, r6, r7, r8, lr}
43863d90:      	mov	r4, r0
43863d92:      	ldr	r7, [pc, #0x8c]         @ 0x43863e20 <_binary_input_a7s_av_cam_bin_start+0x322e20>
43863d94:      	mov	r8, r1
43863d96:      	ldr	r3, [pc, #0x8c]         @ 0x43863e24 <_binary_input_a7s_av_cam_bin_start+0x322e24>
43863d98:      	add	r7, pc
43863d9a:      	ldr	r3, [r7, r3]
43863d9c:      	ldrb	r2, [r3]
43863d9e:      	cbnz	r2, 0x43863da6 <_binary_input_a7s_av_cam_bin_start+0x322da6> @ imm = #0x4
43863da0:      	ldrb	r3, [r3, #0x15]
43863da2:      	cmp	r3, #0x0
43863da4:      	beq	0x43863e1a <_binary_input_a7s_av_cam_bin_start+0x322e1a> @ imm = #0x72
43863da6:      	ldr	r3, [pc, #0x80]         @ 0x43863e28 <_binary_input_a7s_av_cam_bin_start+0x322e28>
43863da8:      	movs	r6, #0x0
43863daa:      	movs	r2, #0x12
43863dac:      	mov	r1, r6
43863dae:      	add	r3, pc
43863db0:      	strb	r6, [r3]
43863db2:      	ldr	r3, [pc, #0x78]         @ 0x43863e2c <_binary_input_a7s_av_cam_bin_start+0x322e2c>
43863db4:      	ldr	r0, [r7, r3]
43863db6:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x150244
43863dba:      	bl	0x437c3388 <_binary_input_a7s_av_cam_bin_start+0x282388> @ imm = #-0xa0a36
43863dbe:      	mov	r1, r6
43863dc0:      	str	r0, [r4, #0x8]
43863dc2:      	ldr.w	r0, [r8, #0x1c0]
43863dc6:      	bl	0x43862034 <_binary_input_a7s_av_cam_bin_start+0x321034> @ imm = #-0x1d96
43863dca:      	ldr	r3, [pc, #0x64]         @ 0x43863e30 <_binary_input_a7s_av_cam_bin_start+0x322e30>
43863dcc:      	adds	r2, r4, #0x4
43863dce:      	ldr	r3, [r7, r3]
43863dd0:      	strb.w	r6, [r3, #0x59c]
43863dd4:      	add.w	r6, r4, #0x2c0
43863dd8:      	stm.w	sp, {r2, r8}
43863ddc:      	ldr	r2, [pc, #0x54]         @ 0x43863e34 <_binary_input_a7s_av_cam_bin_start+0x322e34>
43863dde:      	ldr	r7, [r7, r2]
43863de0:      	mov	r2, r7
43863de2:      	mov	r5, r0
43863de4:      	mov	r0, r6
43863de6:      	mov	r1, r5
43863de8:      	bl	0x437e3500 <_binary_input_a7s_av_cam_bin_start+0x2a2500> @ imm = #-0x808ec
43863dec:      	mov	r1, r7
43863dee:      	mov	r0, r5
43863df0:      	bl	0x4386208c <_binary_input_a7s_av_cam_bin_start+0x32108c> @ imm = #-0x1d68
43863df4:      	mov	r2, r5
43863df6:      	mov	r1, r6
43863df8:      	mov	r7, r0
43863dfa:      	bl	0x43861cc4 <_binary_input_a7s_av_cam_bin_start+0x320cc4> @ imm = #-0x213a
43863dfe:      	movs	r3, #0x1
43863e00:      	sub.w	r2, r7, #0x12
43863e04:      	cmp	r2, r3
43863e06:      	strb.w	r3, [r4, #0x34a]
43863e0a:      	bhi	0x43863e10 <_binary_input_a7s_av_cam_bin_start+0x322e10> @ imm = #0x2
43863e0c:      	adds	r3, r3, r3
43863e0e:      	b	0x43863e18 <_binary_input_a7s_av_cam_bin_start+0x322e18> @ imm = #0x6
43863e10:      	subs	r7, #0x14
43863e12:      	cmp	r7, #0x1
43863e14:      	it	ls
43863e16:      	movls	r3, #0x3
43863e18:      	str	r3, [r4, #0x14]
43863e1a:      	pop.w	{r2, r3, r4, r5, r6, r7, r8, pc}
43863e1e:      	nop
43863e20:      	lsls	r4, r4, #0x1e
43863e22:      	lsls	r4, r7, #0x1
43863e24:      	subs	r4, r1, r4
43863e26:      	movs	r0, r0
43863e28:      	ldrb	r1, [r6, #0x12]
43863e2a:      	lsls	r4, r6, #0x1
43863e2c:      	ldrh	r0, [r1, #0x28]
43863e2e:      	movs	r0, r0
43863e30:      	subs	r7, #0x7c
43863e32:      	movs	r0, r0
43863e34:      	adds	r7, #0x78
43863e36:      	movs	r0, r0
43863e38:      	ldr	r2, [r0, #0x8]
43863e3a:      	ldr	r3, [pc, #0x24]         @ 0x43863e60 <_binary_input_a7s_av_cam_bin_start+0x322e60>
43863e3c:      	ldr.w	r2, [r2, #0x1f0]
43863e40:      	add	r3, pc
43863e42:      	cbnz	r2, 0x43863e48 <_binary_input_a7s_av_cam_bin_start+0x322e48> @ imm = #0x2
43863e44:      	adds	r2, #0x1
43863e46:      	b	0x43863e4a <_binary_input_a7s_av_cam_bin_start+0x322e4a> @ imm = #0x0
43863e48:      	movs	r2, #0x0
43863e4a:      	strb	r2, [r1, #0xa]
43863e4c:      	ldr	r2, [pc, #0x14]         @ 0x43863e64 <_binary_input_a7s_av_cam_bin_start+0x322e64>
43863e4e:      	ldr	r3, [r3, r2]
43863e50:      	ldrb.w	r3, [r3, #0x102]
43863e54:      	tst.w	r3, #0x40
43863e58:      	beq	0x43863e5e <_binary_input_a7s_av_cam_bin_start+0x322e5e> @ imm = #0x2
43863e5a:      	movs	r3, #0x1
43863e5c:      	strb	r3, [r1, #0xa]
43863e5e:      	bx	lr
43863e60:      	lsls	r4, r7, #0x1b
43863e62:      	lsls	r4, r7, #0x1
43863e64:      	strb	r4, [r5, #0x6]
43863e66:      	movs	r0, r0
43863e68:      	ldr	r3, [pc, #0x20]         @ 0x43863e8c <_binary_input_a7s_av_cam_bin_start+0x322e8c>
43863e6a:      	add	r3, pc
43863e6c:      	cbnz	r0, 0x43863e72 <_binary_input_a7s_av_cam_bin_start+0x322e72> @ imm = #0x2
43863e6e:      	movs	r2, #0x1
43863e70:      	b	0x43863e74 <_binary_input_a7s_av_cam_bin_start+0x322e74> @ imm = #0x0
43863e72:      	movs	r2, #0x0
43863e74:      	strb	r2, [r1]
43863e76:      	ldr	r2, [pc, #0x18]         @ 0x43863e90 <_binary_input_a7s_av_cam_bin_start+0x322e90>
43863e78:      	ldr	r3, [r3, r2]
43863e7a:      	ldrb.w	r3, [r3, #0x102]
43863e7e:      	tst.w	r3, #0x40
43863e82:      	beq	0x43863e88 <_binary_input_a7s_av_cam_bin_start+0x322e88> @ imm = #0x2
43863e84:      	movs	r3, #0x1
43863e86:      	strb	r3, [r1]
43863e88:      	bx	lr
43863e8a:      	nop
43863e8c:      	lsls	r2, r2, #0x1b
43863e8e:      	lsls	r4, r7, #0x1
43863e90:      	strb	r4, [r5, #0x6]
43863e92:      	movs	r0, r0
43863e94:      	push	{r4, r5, r6, lr}
43863e96:      	mov	r4, r0
43863e98:      	ldrb.w	r2, [r1, #0x644]
43863e9c:      	mov	r6, r1
43863e9e:      	ldrb.w	r3, [r0, #0xbdd]
43863ea2:      	ldr	r5, [pc, #0xd0]         @ 0x43863f74 <_binary_input_a7s_av_cam_bin_start+0x322f74>
43863ea4:      	cmp	r2, r3
43863ea6:      	add	r5, pc
43863ea8:      	beq	0x43863eb8 <_binary_input_a7s_av_cam_bin_start+0x322eb8> @ imm = #0xc
43863eaa:      	movs	r3, #0x1
43863eac:      	strb	r3, [r1, #0xb]
43863eae:      	ldrb.w	r3, [r0, #0xbdd]
43863eb2:      	strb.w	r3, [r1, #0x644]
43863eb6:      	b	0x43863ebc <_binary_input_a7s_av_cam_bin_start+0x322ebc> @ imm = #0x2
43863eb8:      	movs	r3, #0x0
43863eba:      	strb	r3, [r1, #0xb]
43863ebc:      	bl	0x437436b8 <_binary_input_a7s_av_cam_bin_start+0x2026b8> @ imm = #-0x120808
43863ec0:      	cmp	r0, #0x0
43863ec2:      	bne	0x43863f6e <_binary_input_a7s_av_cam_bin_start+0x322f6e> @ imm = #0xa8
43863ec4:      	bl	0x4374372c <_binary_input_a7s_av_cam_bin_start+0x20272c> @ imm = #-0x12079c
43863ec8:      	cmp	r0, #0x0
43863eca:      	beq	0x43863f6e <_binary_input_a7s_av_cam_bin_start+0x322f6e> @ imm = #0xa0
43863ecc:      	bl	0x43848e30 <_binary_input_a7s_av_cam_bin_start+0x307e30> @ imm = #-0x1b0a0
43863ed0:      	rsbs.w	r0, r0, #0x1
43863ed4:      	it	lo
43863ed6:      	movlo	r0, #0x0
43863ed8:      	ldrb.w	r3, [r4, #0xbde]
43863edc:      	cbnz	r3, 0x43863ee2 <_binary_input_a7s_av_cam_bin_start+0x322ee2> @ imm = #0x2
43863ede:      	cbnz	r0, 0x43863ee2 <_binary_input_a7s_av_cam_bin_start+0x322ee2> @ imm = #0x0
43863ee0:      	strb	r0, [r6, #0xb]
43863ee2:      	mov	r0, r6
43863ee4:      	bl	0x43aedd8a <_binary_input_a7s_av_cam_bin_start+0x5acd8a> @ imm = #0x289ea2
43863ee8:      	cmp	r0, #0x1
43863eea:      	bne	0x43863f2a <_binary_input_a7s_av_cam_bin_start+0x322f2a> @ imm = #0x3c
43863eec:      	ldrb.w	r3, [r6, #0x553]
43863ef0:      	cmp	r3, #0x1
43863ef2:      	bne	0x43863f2a <_binary_input_a7s_av_cam_bin_start+0x322f2a> @ imm = #0x34
43863ef4:      	ldrb.w	r2, [r6, #0x26a]
43863ef8:      	cbnz	r2, 0x43863f2a <_binary_input_a7s_av_cam_bin_start+0x322f2a> @ imm = #0x2e
43863efa:      	ldrb	r2, [r6, #0x8]
43863efc:      	cmp	r2, #0x11
43863efe:      	beq	0x43863f1e <_binary_input_a7s_av_cam_bin_start+0x322f1e> @ imm = #0x1c
43863f00:      	cmp	r2, #0x9
43863f02:      	beq	0x43863f1e <_binary_input_a7s_av_cam_bin_start+0x322f1e> @ imm = #0x18
43863f04:      	cmp	r2, #0x1
43863f06:      	beq	0x43863f1c <_binary_input_a7s_av_cam_bin_start+0x322f1c> @ imm = #0x12
43863f08:      	cmp	r2, #0xd
43863f0a:      	beq	0x43863f1e <_binary_input_a7s_av_cam_bin_start+0x322f1e> @ imm = #0x10
43863f0c:      	cmp	r2, #0x10
43863f0e:      	beq	0x43863f1e <_binary_input_a7s_av_cam_bin_start+0x322f1e> @ imm = #0xc
43863f10:      	sub.w	r2, r2, #0x2
43863f14:      	rsbs	r3, r2, #0
43863f16:      	adc.w	r3, r3, r2
43863f1a:      	b	0x43863f1e <_binary_input_a7s_av_cam_bin_start+0x322f1e> @ imm = #0x0
43863f1c:      	mov	r3, r2
43863f1e:      	ldr.w	r2, [r6, #0x238]
43863f22:      	cmp	r2, #0x1
43863f24:      	bhi	0x43863f2a <_binary_input_a7s_av_cam_bin_start+0x322f2a> @ imm = #0x2
43863f26:      	cbnz	r3, 0x43863f2a <_binary_input_a7s_av_cam_bin_start+0x322f2a> @ imm = #0x0
43863f28:      	strb	r3, [r6, #0xb]
43863f2a:      	movs	r3, #0x0
43863f2c:      	strb.w	r3, [r6, #0x269]
43863f30:      	ldrb.w	r2, [r4, #0xbb8]
43863f34:      	cbnz	r2, 0x43863f3c <_binary_input_a7s_av_cam_bin_start+0x322f3c> @ imm = #0x4
43863f36:      	ldrb.w	r2, [r4, #0xbd0]
43863f3a:      	cbz	r2, 0x43863f44 <_binary_input_a7s_av_cam_bin_start+0x322f44> @ imm = #0x6
43863f3c:      	strb	r3, [r6, #0xb]
43863f3e:      	movs	r3, #0x1
43863f40:      	strb.w	r3, [r6, #0x269]
43863f44:      	ldr	r3, [pc, #0x30]         @ 0x43863f78 <_binary_input_a7s_av_cam_bin_start+0x322f78>
43863f46:      	ldr	r3, [r5, r3]
43863f48:      	ldrb	r3, [r3]
43863f4a:      	cmp	r3, #0x1
43863f4c:      	it	eq
43863f4e:      	strbeq	r3, [r6, #0xb]
43863f50:      	ldr	r3, [pc, #0x28]         @ 0x43863f7c <_binary_input_a7s_av_cam_bin_start+0x322f7c>
43863f52:      	ldr	r3, [r5, r3]
43863f54:      	ldrb.w	r3, [r3, #0x102]
43863f58:      	tst.w	r3, #0x20
43863f5c:      	beq	0x43863f72 <_binary_input_a7s_av_cam_bin_start+0x322f72> @ imm = #0x12
43863f5e:      	movs	r3, #0x1
43863f60:      	strb	r3, [r6, #0xb]
43863f62:      	ldrb.w	r3, [r6, #0x644]
43863f66:      	adds	r3, #0x1
43863f68:      	strb.w	r3, [r6, #0x644]
43863f6c:      	pop	{r4, r5, r6, pc}
43863f6e:      	movs	r0, #0x0
43863f70:      	b	0x43863ed8 <_binary_input_a7s_av_cam_bin_start+0x322ed8> @ imm = #-0x9c
43863f72:      	pop	{r4, r5, r6, pc}
43863f74:      	lsls	r6, r2, #0x1a
43863f76:      	lsls	r4, r7, #0x1
43863f78:      	subs	r5, #0xc8
43863f7a:      	movs	r0, r0
43863f7c:      	strb	r4, [r5, #0x6]
43863f7e:      	movs	r0, r0
43863f80:      	ldr	r3, [r0, #0x8]
43863f82:      	push	{r4, r5, r6, lr}
43863f84:      	mov	r6, r0
43863f86:      	ldr	r5, [pc, #0x3c]         @ 0x43863fc4 <_binary_input_a7s_av_cam_bin_start+0x322fc4>
43863f88:      	mov	r4, r1
43863f8a:      	ldrb.w	r3, [r3, #0x3d]
43863f8e:      	add	r5, pc
43863f90:      	cbz	r3, 0x43863fa0 <_binary_input_a7s_av_cam_bin_start+0x322fa0> @ imm = #0xc
43863f92:      	ldr.w	r0, [r1, #0x420]
43863f96:      	movs	r1, #0x1
43863f98:      	bl	0x43b0913a <_binary_input_a7s_av_cam_bin_start+0x5c813a> @ imm = #0x2a519e
43863f9c:      	str.w	r0, [r4, #0x420]
43863fa0:      	ldr	r3, [pc, #0x24]         @ 0x43863fc8 <_binary_input_a7s_av_cam_bin_start+0x322fc8>
43863fa2:      	add.w	r0, r4, #0x36c
43863fa6:      	ldr.w	r1, [r6, #0x80]
43863faa:      	movs	r2, #0xb4
43863fac:      	ldr	r5, [r5, r3]
43863fae:      	ldr.w	r3, [r4, #0x420]
43863fb2:      	str.w	r3, [r5, #0xaa4]
43863fb6:      	blx	0x439b3918 <_binary_input_a7s_av_cam_bin_start+0x472918> @ imm = #0x14f960
43863fba:      	ldr.w	r3, [r4, #0x36c]
43863fbe:      	str.w	r3, [r5, #0xab0]
43863fc2:      	pop	{r4, r5, r6, pc}
43863fc4:      	lsls	r6, r5, #0x16
43863fc6:      	lsls	r4, r7, #0x1
43863fc8:      	ldrb	r4, [r6, #0x1d]
43863fca:      	movs	r0, r0
43863fcc:      	ldr	r3, [pc, #0xa4]         @ 0x43864074 <_binary_input_a7s_av_cam_bin_start+0x323074>
43863fce:      	push	{r0, r1, r2, r4, r5, r6, r7, lr}
43863fd0:      	mov	r5, r2
43863fd2:      	ldr	r2, [pc, #0xa4]         @ 0x43864078 <_binary_input_a7s_av_cam_bin_start+0x323078>
43863fd4:      	add	r3, pc
43863fd6:      	mov	r4, r0
43863fd8:      	mov	r6, r1
43863fda:      	ldr	r7, [r3, r2]
43863fdc:      	ldr	r3, [r0, #0x8]
43863fde:      	ldrb.w	r3, [r3, #0x3d]
43863fe2:      	strb.w	r3, [r7, #0xaa8]
43863fe6:      	ldr	r0, [r0, #0x8]
43863fe8:      	add.w	r0, r0, #0x860
43863fec:      	adds	r0, #0x1c
43863fee:      	bl	0x43aed9c8 <_binary_input_a7s_av_cam_bin_start+0x5ac9c8> @ imm = #0x2899d6
43863ff2:      	cmp	r0, #0x0
43863ff4:      	ite	ne
43863ff6:      	movne	r0, #0x1
43863ff8:      	moveq	r0, #0xff
43863ffa:      	strb.w	r0, [r7, #0xaa9]
43863ffe:      	ldr	r3, [r4, #0x20]
43864000:      	ldrb	r3, [r3, #0x1]
43864002:      	strb.w	r3, [r7, #0xaaa]
43864006:      	ldr	r3, [r4, #0x8]
43864008:      	ldrb.w	r3, [r3, #0x3d]
4386400c:      	cmp	r3, #0x0
4386400e:      	beq	0x4386406e <_binary_input_a7s_av_cam_bin_start+0x32306e> @ imm = #0x5c
43864010:      	ldr	r3, [r4, #0x20]
43864012:      	ldrb	r3, [r3, #0x1]
43864014:      	cmp	r3, #0x1
43864016:      	bne	0x4386406e <_binary_input_a7s_av_cam_bin_start+0x32306e> @ imm = #0x54
43864018:      	ldr	r3, [r4, #0x7c]
4386401a:      	mvn	r1, #0x1
4386401e:      	ldr.w	r0, [r3, #0x310]
43864022:      	bl	0x43b0913a <_binary_input_a7s_av_cam_bin_start+0x5c813a> @ imm = #0x2a5114
43864026:      	ldr	r3, [r4, #0x4]
43864028:      	movs	r1, #0xc
4386402a:      	str	r0, [r5, #0x2c]
4386402c:      	str.w	r0, [r7, #0xaac]
43864030:      	ldr	r0, [r3, #0x8]
43864032:      	bl	0x4385ae40 <_binary_input_a7s_av_cam_bin_start+0x319e40> @ imm = #-0x91f6
43864036:      	ldr	r1, [r4, #0x8]
43864038:      	add.w	r3, r5, #0x3c
4386403c:      	mov	r0, r4
4386403e:      	add.w	r1, r1, #0x860
43864042:      	str	r3, [sp]
43864044:      	adds	r1, #0x1c
43864046:      	ldr	r3, [r5, #0x2c]
43864048:      	mov	r2, r6
4386404a:      	bl	0x437ed0b8 <_binary_input_a7s_av_cam_bin_start+0x2ac0b8> @ imm = #-0x76f96
4386404e:      	ldr	r0, [r4, #0x8]
43864050:      	add.w	r1, r5, #0x30
43864054:      	add.w	r0, r0, #0x860
43864058:      	adds	r0, #0x1c
4386405a:      	bl	0x437e80f8 <_binary_input_a7s_av_cam_bin_start+0x2a70f8> @ imm = #-0x7bf66
4386405e:      	ldr	r3, [r4, #0x4]
43864060:      	movs	r1, #0xd
43864062:      	ldr	r0, [r3, #0x8]
43864064:      	add	sp, #0xc
43864066:      	pop.w	{r4, r5, r6, r7, lr}
4386406a:      	b.w	0x4385ae40 <_binary_input_a7s_av_cam_bin_start+0x319e40> @ imm = #-0x922e
4386406e:      	add	sp, #0xc
43864070:      	pop	{r4, r5, r6, r7, pc}
43864072:      	nop
43864074:      	lsls	r0, r5, #0x15
43864076:      	lsls	r4, r7, #0x1
43864078:      	ldrb	r4, [r6, #0x1d]
4386407a:      	movs	r0, r0
4386407c:      	ldr	r3, [r0, #0x4c]
4386407e:      	push.w	{r0, r1, r4, r5, r6, r7, r8, lr}
43864082:      	cmp	r3, #0x2
43864084:      	ldr	r6, [pc, #0xf8]         @ 0x43864180 <_binary_input_a7s_av_cam_bin_start+0x323180>
43864086:      	mov	r5, r0
43864088:      	mov	r4, r2
4386408a:      	add	r6, pc
4386408c:      	bne	0x43864172 <_binary_input_a7s_av_cam_bin_start+0x323172> @ imm = #0xe2
4386408e:      	ldrb.w	r3, [r0, #0x44]
43864092:      	cmp	r3, #0x1
43864094:      	bne	0x43864172 <_binary_input_a7s_av_cam_bin_start+0x323172> @ imm = #0xda
43864096:      	ldrb.w	r3, [r0, #0x64]
4386409a:      	cmp	r3, #0x1
4386409c:      	bne	0x43864172 <_binary_input_a7s_av_cam_bin_start+0x323172> @ imm = #0xd2
4386409e:      	ldr.w	r0, [r0, #0x88]
438640a2:      	ldr.w	r1, [r5, #0x8c]
438640a6:      	ldrb.w	r2, [r5, #0x37]
438640aa:      	bl	0x437d0cf4 <_binary_input_a7s_av_cam_bin_start+0x28fcf4> @ imm = #-0x933ba
438640ae:      	cmp	r0, #0x1
438640b0:      	bne	0x43864172 <_binary_input_a7s_av_cam_bin_start+0x323172> @ imm = #0xbe
438640b2:      	ldrsh.w	r0, [r5, #0x90]
438640b6:      	movs	r1, #0x4
438640b8:      	ldr	r7, [r5, #0x30]
438640ba:      	movs	r3, #0x0
438640bc:      	bic.w	r0, r0, r0, asr #31
438640c0:      	uxth	r0, r0
438640c2:      	sxth	r6, r0
438640c4:      	asr.w	r12, r6, #0x1
438640c8:      	uxth.w	r12, r12
438640cc:      	cbnz	r7, 0x438640d4 <_binary_input_a7s_av_cam_bin_start+0x3230d4> @ imm = #0x4
438640ce:      	strh.w	r0, [r4, r3, lsl #1]
438640d2:      	b	0x4386410e <_binary_input_a7s_av_cam_bin_start+0x32310e> @ imm = #0x38
438640d4:      	cmp	r7, #0x2
438640d6:      	bne	0x438640fa <_binary_input_a7s_av_cam_bin_start+0x3230fa> @ imm = #0x20
438640d8:      	ldr.w	r8, [r5, #0x94]
438640dc:      	adds	r2, r3, #0x5
438640de:      	and	r2, r2, #0x3
438640e2:      	cmp.w	r8, #0x2
438640e6:      	beq	0x438640ee <_binary_input_a7s_av_cam_bin_start+0x3230ee> @ imm = #0x4
438640e8:      	cmp	r2, #0x3
438640ea:      	beq	0x438640ee <_binary_input_a7s_av_cam_bin_start+0x3230ee> @ imm = #0x0
438640ec:      	cbnz	r2, 0x438640f4 <_binary_input_a7s_av_cam_bin_start+0x3230f4> @ imm = #0x4
438640ee:      	strh.w	r0, [r4, r2, lsl #1]
438640f2:      	b	0x4386410e <_binary_input_a7s_av_cam_bin_start+0x32310e> @ imm = #0x18
438640f4:      	strh.w	r12, [r4, r2, lsl #1]
438640f8:      	b	0x4386410e <_binary_input_a7s_av_cam_bin_start+0x32310e> @ imm = #0x12
438640fa:      	add.w	r8, r3, #0x1
438640fe:      	and	r2, r3, #0x3
43864102:      	mul	r8, r6, r8
43864106:      	asr.w	r8, r8, #0x2
4386410a:      	strh.w	r8, [r4, r2, lsl #1]
4386410e:      	subs	r1, #0x1
43864110:      	adds	r3, #0x1
43864112:      	uxtb	r1, r1
43864114:      	uxtb	r3, r3
43864116:      	cmp	r1, #0x0
43864118:      	bne	0x438640cc <_binary_input_a7s_av_cam_bin_start+0x3230cc> @ imm = #-0x50
4386411a:      	b	0x4386417a <_binary_input_a7s_av_cam_bin_start+0x32317a> @ imm = #0x5c
4386411c:      	ldr	r3, [pc, #0x64]         @ 0x43864184 <_binary_input_a7s_av_cam_bin_start+0x323184>
4386411e:      	ldr	r2, [r6, r3]
43864120:      	ldrb.w	r3, [r2, #0x9a]
43864124:      	cbnz	r3, 0x4386412a <_binary_input_a7s_av_cam_bin_start+0x32312a> @ imm = #0x2
43864126:      	movs	r3, #0x0
43864128:      	b	0x43864168 <_binary_input_a7s_av_cam_bin_start+0x323168> @ imm = #0x3c
4386412a:      	ldrsh.w	r1, [r5, #0x90]
4386412e:      	add	r5, sp, #0x8
43864130:      	muls	r3, r1, r3
43864132:      	ldrh.w	r0, [r2, #0x9c]
43864136:      	it	mi
43864138:      	addmi	r3, #0x7f
4386413a:      	ldrh.w	r6, [r2, #0x9e]
4386413e:      	cmp	r0, #0x0
43864140:      	it	eq
43864142:      	moveq	r0, #0x80
43864144:      	asrs	r3, r3, #0x7
43864146:      	strh	r3, [r5, #-2]!
4386414a:      	movw	r3, #0xff80
4386414e:      	sxth	r0, r0
43864150:      	cmp	r6, #0x0
43864152:      	it	eq
43864154:      	moveq	r6, r3
43864156:      	mov	r1, r5
43864158:      	bl	0x43b0bede <_binary_input_a7s_av_cam_bin_start+0x5caede> @ imm = #0x2a7d82
4386415c:      	mov	r1, r5
4386415e:      	sxth	r0, r6
43864160:      	bl	0x43b0beea <_binary_input_a7s_av_cam_bin_start+0x5caeea> @ imm = #0x2a7d86
43864164:      	ldrh.w	r3, [sp, #0x6]
43864168:      	strh	r3, [r4]
4386416a:      	strh	r3, [r4, #0x2]
4386416c:      	strh	r3, [r4, #0x4]
4386416e:      	strh	r3, [r4, #0x6]
43864170:      	b	0x4386417a <_binary_input_a7s_av_cam_bin_start+0x32317a> @ imm = #0x6
43864172:      	ldr	r3, [r5, #0x4c]
43864174:      	cmp	r3, #0x1
43864176:      	bne	0x43864126 <_binary_input_a7s_av_cam_bin_start+0x323126> @ imm = #-0x54
43864178:      	b	0x4386411c <_binary_input_a7s_av_cam_bin_start+0x32311c> @ imm = #-0x60
4386417a:      	pop.w	{r2, r3, r4, r5, r6, r7, r8, pc}
4386417e:      	nop
43864180:      	lsls	r2, r6, #0x12
43864182:      	lsls	r4, r7, #0x1
43864184:      	lsls	r0, r4, #0x13
43864186:      	movs	r0, r0
43864188:      	ldr	r3, [pc, #0x14]         @ 0x438641a0 <_binary_input_a7s_av_cam_bin_start+0x3231a0>
4386418a:      	movs	r2, #0x1
4386418c:      	add	r3, pc
4386418e:      	strb	r2, [r3]
43864190:      	ldr	r3, [pc, #0x10]         @ 0x438641a4 <_binary_input_a7s_av_cam_bin_start+0x3231a4>
43864192:      	ldr	r2, [r0]
43864194:      	add	r3, pc
43864196:      	str	r2, [r3]
43864198:      	ldr	r2, [r0, #0xc]
4386419a:      	str	r2, [r3, #0xc]
4386419c:      	bx	lr
4386419e:      	nop
438641a0:      	ldrb	r5, [r2, #0x3]
438641a2:      	lsls	r4, r6, #0x1
438641a4:      	cmp	r2, #0x20
438641a6:      	lsls	r2, r5, #0x1
438641a8:      	push	{r4, r5, r6, lr}
438641aa:      	mov	r4, r0
438641ac:      	ldr	r5, [pc, #0xe8]         @ 0x43864298 <_binary_input_a7s_av_cam_bin_start+0x323298>
438641ae:      	ldr	r3, [pc, #0xec]         @ 0x4386429c <_binary_input_a7s_av_cam_bin_start+0x32329c>
438641b0:      	add	r5, pc
438641b2:      	ldr	r3, [r5, r3]
438641b4:      	ldrb	r3, [r3]
438641b6:      	cbnz	r3, 0x438641d6 <_binary_input_a7s_av_cam_bin_start+0x3231d6> @ imm = #0x1c
438641b8:      	ldr	r2, [pc, #0xe4]         @ 0x438642a0 <_binary_input_a7s_av_cam_bin_start+0x3232a0>
438641ba:      	movs	r1, #0x1
438641bc:      	str.w	r3, [r0, #0x6cc]
438641c0:      	add	r2, pc
438641c2:      	str.w	r3, [r0, #0x6d0]
438641c6:      	strb	r1, [r2]
438641c8:      	ldr	r2, [pc, #0xd8]         @ 0x438642a4 <_binary_input_a7s_av_cam_bin_start+0x3232a4>
438641ca:      	add	r2, pc
438641cc:      	str	r3, [r2]
438641ce:      	ldr	r2, [pc, #0xd8]         @ 0x438642a8 <_binary_input_a7s_av_cam_bin_start+0x3232a8>
438641d0:      	add	r2, pc
438641d2:      	strb	r3, [r2]
438641d4:      	pop	{r4, r5, r6, pc}
438641d6:      	ldr	r3, [pc, #0xd4]         @ 0x438642ac <_binary_input_a7s_av_cam_bin_start+0x3232ac>
438641d8:      	add	r3, pc
438641da:      	ldrb	r3, [r3]
438641dc:      	subs	r3, #0x1
438641de:      	cmp	r3, #0x3
438641e0:      	bhi	0x43864296 <_binary_input_a7s_av_cam_bin_start+0x323296> @ imm = #0xb2
438641e2:      	tbb	[pc, r3]
438641e6:      	asrs	r2, r0, #0x8
438641e8:      	subs	r4, #0x1d
438641ea:      	ldrb.w	r3, [r0, #0x261]
438641ee:      	cmp	r3, #0x0
438641f0:      	beq	0x43864296 <_binary_input_a7s_av_cam_bin_start+0x323296> @ imm = #0xa2
438641f2:      	bl	0x439e8fa8 <_binary_input_a7s_av_cam_bin_start+0x4a7fa8> @ imm = #0x184db2
438641f6:      	ldr	r3, [pc, #0xb8]         @ 0x438642b0 <_binary_input_a7s_av_cam_bin_start+0x3232b0>
438641f8:      	ldr.w	r2, [r4, #0x22c]
438641fc:      	add	r3, pc
438641fe:      	adds	r2, #0x2
43864200:      	str	r2, [r3]
43864202:      	movs	r2, #0x2
43864204:      	ldr	r3, [pc, #0xac]         @ 0x438642b4 <_binary_input_a7s_av_cam_bin_start+0x3232b4>
43864206:      	add	r3, pc
43864208:      	b	0x4386425a <_binary_input_a7s_av_cam_bin_start+0x32325a> @ imm = #0x4e
4386420a:      	ldr	r3, [pc, #0xac]         @ 0x438642b8 <_binary_input_a7s_av_cam_bin_start+0x3232b8>
4386420c:      	add	r3, pc
4386420e:      	ldr	r2, [r3]
43864210:      	subs	r2, #0x1
43864212:      	str	r2, [r3]
43864214:      	cmp	r2, #0x0
43864216:      	bne	0x43864296 <_binary_input_a7s_av_cam_bin_start+0x323296> @ imm = #0x7c
43864218:      	ldr	r3, [pc, #0xa0]         @ 0x438642bc <_binary_input_a7s_av_cam_bin_start+0x3232bc>
4386421a:      	adds	r2, #0x3
4386421c:      	add	r3, pc
4386421e:      	b	0x4386425a <_binary_input_a7s_av_cam_bin_start+0x32325a> @ imm = #0x38
43864220:      	ldr	r4, [pc, #0x9c]         @ 0x438642c0 <_binary_input_a7s_av_cam_bin_start+0x3232c0>
43864222:      	movs	r3, #0x2a
43864224:      	ldr	r6, [pc, #0x9c]         @ 0x438642c4 <_binary_input_a7s_av_cam_bin_start+0x3232c4>
43864226:      	movs	r1, #0x28
43864228:      	add	r4, pc
4386422a:      	movs	r2, #0x10
4386422c:      	add	r6, pc
4386422e:      	strh	r3, [r4]
43864230:      	mov	r0, r6
43864232:      	movs	r3, #0x14
43864234:      	strh	r1, [r4, #0x2]
43864236:      	strh	r2, [r4, #0x4]
43864238:      	movs	r1, #0x0
4386423a:      	strh	r3, [r4, #0x6]
4386423c:      	movs	r2, #0x10
4386423e:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fdbc
43864242:      	ldr	r3, [pc, #0x84]         @ 0x438642c8 <_binary_input_a7s_av_cam_bin_start+0x3232c8>
43864244:      	mov	r0, r4
43864246:      	mov	r1, r6
43864248:      	ldr	r2, [r5, r3]
4386424a:      	bl	0x439e9300 <_binary_input_a7s_av_cam_bin_start+0x4a8300> @ imm = #0x1850b2
4386424e:      	ldr	r3, [pc, #0x7c]         @ 0x438642cc <_binary_input_a7s_av_cam_bin_start+0x3232cc>
43864250:      	movs	r2, #0x4
43864252:      	add	r3, pc
43864254:      	str	r0, [r3]
43864256:      	ldr	r3, [pc, #0x78]         @ 0x438642d0 <_binary_input_a7s_av_cam_bin_start+0x3232d0>
43864258:      	add	r3, pc
4386425a:      	strb	r2, [r3]
4386425c:      	pop	{r4, r5, r6, pc}
4386425e:      	ldr	r3, [pc, #0x74]         @ 0x438642d4 <_binary_input_a7s_av_cam_bin_start+0x3232d4>
43864260:      	add	r3, pc
43864262:      	ldrb	r3, [r3]
43864264:      	cbz	r3, 0x43864296 <_binary_input_a7s_av_cam_bin_start+0x323296> @ imm = #0x2e
43864266:      	ldr	r3, [pc, #0x70]         @ 0x438642d8 <_binary_input_a7s_av_cam_bin_start+0x3232d8>
43864268:      	add	r3, pc
4386426a:      	ldr	r3, [r3]
4386426c:      	cbnz	r3, 0x43864286 <_binary_input_a7s_av_cam_bin_start+0x323286> @ imm = #0x16
4386426e:      	ldr	r3, [pc, #0x6c]         @ 0x438642dc <_binary_input_a7s_av_cam_bin_start+0x3232dc>
43864270:      	add	r3, pc
43864272:      	ldr	r5, [r3]
43864274:      	ldr	r1, [r3, #0xc]
43864276:      	mov	r0, r5
43864278:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x3063e4
4386427c:      	str.w	r5, [r4, #0x6d0]
43864280:      	str.w	r0, [r4, #0x6cc]
43864284:      	b	0x4386428e <_binary_input_a7s_av_cam_bin_start+0x32328e> @ imm = #0x6
43864286:      	mov.w	r3, #0xffffffff
4386428a:      	str.w	r3, [r0, #0x6cc]
4386428e:      	ldr	r3, [pc, #0x50]         @ 0x438642e0 <_binary_input_a7s_av_cam_bin_start+0x3232e0>
43864290:      	movs	r2, #0x5
43864292:      	add	r3, pc
43864294:      	strb	r2, [r3]
43864296:      	pop	{r4, r5, r6, pc}
43864298:      	lsls	r4, r1, #0xe
4386429a:      	lsls	r4, r7, #0x1
4386429c:      	ldrh	r4, [r2, #0xa]
4386429e:      	movs	r0, r0
438642a0:      	ldrb	r0, [r4, #0x2]
438642a2:      	lsls	r4, r6, #0x1
438642a4:      	cmp	r1, #0xe6
438642a6:      	lsls	r2, r5, #0x1
438642a8:      	ldrb	r1, [r2, #0x2]
438642aa:      	lsls	r4, r6, #0x1
438642ac:      	ldrb	r0, [r1, #0x2]
438642ae:      	lsls	r4, r6, #0x1
438642b0:      	cmp	r1, #0xb4
438642b2:      	lsls	r2, r5, #0x1
438642b4:      	ldrb	r2, [r3, #0x1]
438642b6:      	lsls	r4, r6, #0x1
438642b8:      	cmp	r1, #0xa4
438642ba:      	lsls	r2, r5, #0x1
438642bc:      	ldrb	r4, [r0, #0x1]
438642be:      	lsls	r4, r6, #0x1
438642c0:      	movs	r5, #0x52
438642c2:      	lsls	r2, r6, #0x1
438642c4:      	cmp	r1, #0x88
438642c6:      	lsls	r2, r5, #0x1
438642c8:      	ldrh	r4, [r3, #0x2c]
438642ca:      	movs	r0, r0
438642cc:      	cmp	r1, #0x5a
438642ce:      	lsls	r2, r5, #0x1
438642d0:      	ldrb	r0, [r1]
438642d2:      	lsls	r4, r6, #0x1
438642d4:      	ldrb	r1, [r0]
438642d6:      	lsls	r4, r6, #0x1
438642d8:      	cmp	r1, #0x44
438642da:      	lsls	r2, r5, #0x1
438642dc:      	cmp	r1, #0x44
438642de:      	lsls	r2, r5, #0x1
438642e0:      	strb	r6, [r1, #0x1f]
438642e2:      	lsls	r4, r6, #0x1
438642e4:      	ldr	r3, [pc, #0x4]          @ 0x438642ec <_binary_input_a7s_av_cam_bin_start+0x3232ec>
438642e6:      	add	r3, pc
438642e8:      	strb	r0, [r3]
438642ea:      	bx	lr
438642ec:      	strb	r4, [r7, #0x1d]
438642ee:      	lsls	r4, r6, #0x1
438642f0:      	push	{r4, r5, r6, r7, lr}
438642f2:      	sub	sp, #0x14
438642f4:      	movs	r2, #0xc
438642f6:      	mov	r4, r0
438642f8:      	movs	r1, #0x0
438642fa:      	add	r0, sp, #0x4
438642fc:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fcfc
43864300:      	ldr	r3, [pc, #0xc0]         @ 0x438643c4 <_binary_input_a7s_av_cam_bin_start+0x3233c4>
43864302:      	ldr	r5, [pc, #0xc4]         @ 0x438643c8 <_binary_input_a7s_av_cam_bin_start+0x3233c8>
43864304:      	add	r3, pc
43864306:      	add	r5, pc
43864308:      	ldrh	r2, [r3]
4386430a:      	cbnz	r2, 0x43864318 <_binary_input_a7s_av_cam_bin_start+0x323318> @ imm = #0xa
4386430c:      	ldr	r2, [pc, #0xbc]         @ 0x438643cc <_binary_input_a7s_av_cam_bin_start+0x3233cc>
4386430e:      	ldr	r2, [r5, r2]
43864310:      	ldrh.w	r1, [r2, #0xe6]
43864314:      	cbnz	r1, 0x43864322 <_binary_input_a7s_av_cam_bin_start+0x323322> @ imm = #0xa
43864316:      	b	0x4386433c <_binary_input_a7s_av_cam_bin_start+0x32333c> @ imm = #0x22
43864318:      	ldr	r2, [pc, #0xb4]         @ 0x438643d0 <_binary_input_a7s_av_cam_bin_start+0x3233d0>
4386431a:      	movs	r1, #0x9
4386431c:      	add	r2, pc
4386431e:      	mov	r3, r2
43864320:      	b	0x43864354 <_binary_input_a7s_av_cam_bin_start+0x323354> @ imm = #0x30
43864322:      	ldrh.w	r6, [r2, #0xe8]
43864326:      	ldrh.w	r0, [r2, #0xea]
4386432a:      	add.w	r2, r3, #0x14
4386432e:      	strh	r1, [r3], #2
43864332:      	cmp	r3, r2
43864334:      	strh	r6, [r3, #0x12]
43864336:      	strh	r0, [r3, #0x26]
43864338:      	bne	0x4386432e <_binary_input_a7s_av_cam_bin_start+0x32332e> @ imm = #-0xe
4386433a:      	b	0x43864318 <_binary_input_a7s_av_cam_bin_start+0x323318> @ imm = #-0x26
4386433c:      	ldrh	r6, [r4]
4386433e:      	add.w	r2, r3, #0x14
43864342:      	ldrh	r0, [r4, #0x2]
43864344:      	ldrh	r1, [r4, #0x4]
43864346:      	strh	r6, [r3], #2
4386434a:      	cmp	r3, r2
4386434c:      	strh	r0, [r3, #0x12]
4386434e:      	strh	r1, [r3, #0x26]
43864350:      	bne	0x43864346 <_binary_input_a7s_av_cam_bin_start+0x323346> @ imm = #-0xe
43864352:      	b	0x43864318 <_binary_input_a7s_av_cam_bin_start+0x323318> @ imm = #-0x3e
43864354:      	ldrh	r0, [r3, #0x10]
43864356:      	subs	r1, #0x1
43864358:      	uxtb	r1, r1
4386435a:      	strh	r0, [r3, #0x12]
4386435c:      	ldrh	r0, [r3, #0x24]
4386435e:      	strh	r0, [r3, #0x26]
43864360:      	ldrh	r0, [r3, #0x38]
43864362:      	strh	r0, [r3, #0x3a]
43864364:      	subs	r3, #0x2
43864366:      	cmp	r1, #0x0
43864368:      	bne	0x43864354 <_binary_input_a7s_av_cam_bin_start+0x323354> @ imm = #-0x18
4386436a:      	ldr	r3, [pc, #0x68]         @ 0x438643d4 <_binary_input_a7s_av_cam_bin_start+0x3233d4>
4386436c:      	adds	r2, #0x14
4386436e:      	ldrh	r1, [r4]
43864370:      	add	r3, pc
43864372:      	strh	r1, [r3]
43864374:      	ldrh	r0, [r4, #0x2]
43864376:      	strh	r0, [r3, #0x14]
43864378:      	ldrh	r4, [r4, #0x4]
4386437a:      	strh	r4, [r3, #0x28]
4386437c:      	ldrh	r1, [r3], #2
43864380:      	ldr	r0, [sp, #0x4]
43864382:      	ldr	r7, [sp, #0x8]
43864384:      	cmp	r3, r2
43864386:      	add	r0, r1
43864388:      	ldrh	r1, [r3, #0x12]
4386438a:      	ldr	r6, [sp, #0xc]
4386438c:      	add	r7, r1
4386438e:      	ldrh	r1, [r3, #0x26]
43864390:      	str	r0, [sp, #0x4]
43864392:      	add	r6, r1
43864394:      	str	r7, [sp, #0x8]
43864396:      	str	r6, [sp, #0xc]
43864398:      	bne	0x4386437c <_binary_input_a7s_av_cam_bin_start+0x32337c> @ imm = #-0x20
4386439a:      	ldr	r3, [pc, #0x30]         @ 0x438643cc <_binary_input_a7s_av_cam_bin_start+0x3233cc>
4386439c:      	movs	r1, #0xa
4386439e:      	ldr	r4, [r5, r3]
438643a0:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x30650c
438643a4:      	movs	r1, #0xa
438643a6:      	strh.w	r0, [r4, #0xe6]
438643aa:      	mov	r0, r7
438643ac:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x306518
438643b0:      	movs	r1, #0xa
438643b2:      	strh.w	r0, [r4, #0xe8]
438643b6:      	mov	r0, r6
438643b8:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x306524
438643bc:      	strh.w	r0, [r4, #0xea]
438643c0:      	add	sp, #0x14
438643c2:      	pop	{r4, r5, r6, r7, pc}
438643c4:      	movs	r4, #0x7e
438643c6:      	lsls	r2, r6, #0x1
438643c8:      	lsls	r6, r6, #0x8
438643ca:      	lsls	r4, r7, #0x1
438643cc:      	lsrs	r4, r4, #0x12
438643ce:      	movs	r0, r0
438643d0:      	movs	r4, #0x66
438643d2:      	lsls	r2, r6, #0x1
438643d4:      	movs	r4, #0x12
438643d6:      	lsls	r2, r6, #0x1
438643d8:      	push.w	{r4, r5, r6, r7, r8, r9, r10, lr}
438643dc:      	sub	sp, #0x1f8
438643de:      	ldr.w	r10, [pc, #0x4c]        @ 0x4386442c <_binary_input_a7s_av_cam_bin_start+0x32342c>
438643e2:      	add	r5, sp, #0x154
438643e4:      	mov	r4, r0
438643e6:      	mov	r9, r1
438643e8:      	add	r10, pc
438643ea:      	mov	r1, r5
438643ec:      	mov	r8, r2
438643ee:      	ldrh.w	r6, [r10, #0x84]
438643f2:      	ldrh.w	r7, [r10, #0x86]
438643f6:      	bl	0x43864e9c <_binary_input_a7s_av_cam_bin_start+0x323e9c> @ imm = #0xaa2
438643fa:      	str	r5, [sp]
438643fc:      	mov	r0, r4
438643fe:      	add	r5, sp, #0xb0
43864400:      	add.w	r1, r10, #0x4
43864404:      	mov	r2, r9
43864406:      	movs	r3, #0xb
43864408:      	str	r5, [sp, #0x4]
4386440a:      	bl	0x43864ee4 <_binary_input_a7s_av_cam_bin_start+0x323ee4> @ imm = #0xad6
4386440e:      	mov	r0, r4
43864410:      	mov	r1, r5
43864412:      	add	r2, sp, #0xc
43864414:      	mov	r3, r6
43864416:      	str	r7, [sp]
43864418:      	bl	0x438652c0 <_binary_input_a7s_av_cam_bin_start+0x3242c0> @ imm = #0xea4
4386441c:      	mov	r0, r4
4386441e:      	add	r1, sp, #0xc
43864420:      	mov	r2, r8
43864422:      	bl	0x43865008 <_binary_input_a7s_av_cam_bin_start+0x324008> @ imm = #0xbe2
43864426:      	add	sp, #0x1f8
43864428:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, pc}
4386442c:      	cmp	r0, #0x40
4386442e:      	lsls	r2, r5, #0x1
43864430:      	push.w	{r4, r5, r6, r7, r8, r9, r10, lr}
43864434:      	sub	sp, #0x180
43864436:      	movs	r1, #0x0
43864438:      	movs	r2, #0x52
4386443a:      	add	r0, sp, #0x100
4386443c:      	ldr	r5, [pc, #0x150]        @ 0x43864590 <_binary_input_a7s_av_cam_bin_start+0x323590>
4386443e:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fbbc
43864442:      	movs	r1, #0x0
43864444:      	movs	r2, #0x52
43864446:      	add	r0, sp, #0xac
43864448:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fbb0
4386444c:      	movs	r1, #0x0
4386444e:      	movs	r2, #0x2c
43864450:      	add	r0, sp, #0x154
43864452:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fba8
43864456:      	movs	r1, #0x0
43864458:      	movs	r2, #0x52
4386445a:      	add	r0, sp, #0x58
4386445c:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fb9c
43864460:      	add	r0, sp, #0x4
43864462:      	movs	r1, #0x0
43864464:      	movs	r2, #0x52
43864466:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fb94
4386446a:      	movs	r3, #0x0
4386446c:      	add	r5, pc
4386446e:      	add	r6, sp, #0x154
43864470:      	mov.w	r2, #0xffffffff
43864474:      	str	r2, [r6, r3]
43864476:      	adds	r3, #0x4
43864478:      	cmp	r3, #0x2c
4386447a:      	bne	0x4386446e <_binary_input_a7s_av_cam_bin_start+0x32346e> @ imm = #-0x10
4386447c:      	ldr	r4, [pc, #0x114]        @ 0x43864594 <_binary_input_a7s_av_cam_bin_start+0x323594>
4386447e:      	add	r2, sp, #0x100
43864480:      	add	r4, pc
43864482:      	mov	r1, r4
43864484:      	ldrb	r0, [r1], #36
43864488:      	bl	0x438643d8 <_binary_input_a7s_av_cam_bin_start+0x3233d8> @ imm = #-0xb4
4386448c:      	ldrb	r0, [r4]
4386448e:      	add	r1, sp, #0x100
43864490:      	add	r2, sp, #0xac
43864492:      	bl	0x43865068 <_binary_input_a7s_av_cam_bin_start+0x324068> @ imm = #0xbd2
43864496:      	ldrb	r0, [r4]
43864498:      	add	r2, sp, #0x180
4386449a:      	mov	r1, r6
4386449c:      	add	r6, sp, #0x4
4386449e:      	add.w	r3, r2, r0, lsl #1
438644a2:      	ldrh	r8, [r3, #-214]
438644a6:      	and	r3, r0, #0xfe
438644aa:      	adds	r3, r2, r3
438644ac:      	add	r2, sp, #0x58
438644ae:      	ldrh	r7, [r3, #-214]
438644b2:      	bl	0x438643d8 <_binary_input_a7s_av_cam_bin_start+0x3233d8> @ imm = #-0xde
438644b6:      	mov	r2, r6
438644b8:      	ldrb	r0, [r4]
438644ba:      	add	r1, sp, #0x58
438644bc:      	bl	0x43865068 <_binary_input_a7s_av_cam_bin_start+0x324068> @ imm = #0xba8
438644c0:      	ldrb	r3, [r4]
438644c2:      	subs	r2, r3, #0x1
438644c4:      	asrs	r3, r3, #0x1
438644c6:      	subs	r3, #0x1
438644c8:      	ldrh.w	r9, [r6, r2, lsl #1]
438644cc:      	ldrh.w	r3, [r6, r3, lsl #1]
438644d0:      	cmp	r3, r7
438644d2:      	bls	0x438644e2 <_binary_input_a7s_av_cam_bin_start+0x3234e2> @ imm = #0xc
438644d4:      	subs	r7, r3, r7
438644d6:      	uxth	r7, r7
438644d8:      	mov	r0, r7
438644da:      	bl	0x438650d8 <_binary_input_a7s_av_cam_bin_start+0x3240d8> @ imm = #0xbfa
438644de:      	mov	r4, r0
438644e0:      	b	0x438644e6 <_binary_input_a7s_av_cam_bin_start+0x3234e6> @ imm = #0x2
438644e2:      	movs	r4, #0x0
438644e4:      	mov	r7, r4
438644e6:      	ldr	r3, [pc, #0xb0]         @ 0x43864598 <_binary_input_a7s_av_cam_bin_start+0x323598>
438644e8:      	add.w	r0, sp, #0xfe
438644ec:      	add	r3, pc
438644ee:      	ldrb	r1, [r3]
438644f0:      	ldr	r3, [pc, #0xa8]         @ 0x4386459c <_binary_input_a7s_av_cam_bin_start+0x32359c>
438644f2:      	add	r3, pc
438644f4:      	adds	r2, r3, #0x2
438644f6:      	movs	r3, #0x0
438644f8:      	b	0x43864506 <_binary_input_a7s_av_cam_bin_start+0x323506> @ imm = #0xa
438644fa:      	adds	r3, #0x1
438644fc:      	ldrh	r6, [r0, #2]!
43864500:      	uxtb	r3, r3
43864502:      	strh	r6, [r2, #2]!
43864506:      	cmp	r3, r1
43864508:      	bne	0x438644fa <_binary_input_a7s_av_cam_bin_start+0x3234fa> @ imm = #-0x12
4386450a:      	b	0x43864524 <_binary_input_a7s_av_cam_bin_start+0x323524> @ imm = #0x16
4386450c:      	ldr	r2, [pc, #0x90]         @ 0x438645a0 <_binary_input_a7s_av_cam_bin_start+0x3235a0>
4386450e:      	add	r6, sp, #0x180
43864510:      	add.w	r0, r6, r1, lsl #1
43864514:      	add	r2, pc
43864516:      	add.w	r2, r2, r3, lsl #1
4386451a:      	adds	r3, #0x1
4386451c:      	ldrh	r0, [r0, #-130]
43864520:      	uxtb	r3, r3
43864522:      	strh	r0, [r2, #0x4]
43864524:      	cmp	r3, #0x28
43864526:      	bls	0x4386450c <_binary_input_a7s_av_cam_bin_start+0x32350c> @ imm = #-0x1e
43864528:      	ldr	r3, [pc, #0x78]         @ 0x438645a4 <_binary_input_a7s_av_cam_bin_start+0x3235a4>
4386452a:      	add	r3, pc
4386452c:      	ldrh	r6, [r3, #0x2]
4386452e:      	cbz	r6, 0x43864532 <_binary_input_a7s_av_cam_bin_start+0x323532> @ imm = #0x0
43864530:      	cbnz	r7, 0x4386453e <_binary_input_a7s_av_cam_bin_start+0x32353e> @ imm = #0xa
43864532:      	ldr	r3, [pc, #0x74]         @ 0x438645a8 <_binary_input_a7s_av_cam_bin_start+0x3235a8>
43864534:      	movs	r2, #0x0
43864536:      	add	r3, pc
43864538:      	strh.w	r2, [r3, #0x56]
4386453c:      	b	0x43864568 <_binary_input_a7s_av_cam_bin_start+0x323568> @ imm = #0x28
4386453e:      	mov	r1, r6
43864540:      	mov	r0, r4
43864542:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x3066ae
43864546:      	mov	r1, r6
43864548:      	mov	r10, r0
4386454a:      	mov	r0, r4
4386454c:      	bl	0x4355e0f4 <_binary_input_a7s_av_cam_bin_start+0x1d0f4> @ imm = #-0x30645c
43864550:      	ldr	r3, [pc, #0x58]         @ 0x438645ac <_binary_input_a7s_av_cam_bin_start+0x3235ac>
43864552:      	movw	r2, #0xffff
43864556:      	cmp	r10, r2
43864558:      	it	hs
4386455a:      	movhs	r10, r2
4386455c:      	add	r3, pc
4386455e:      	strh.w	r10, [r3, #0x56]
43864562:      	cmp	r1, r2
43864564:      	it	lo
43864566:      	movlo	r2, r1
43864568:      	strh.w	r2, [r3, #0x58]
4386456c:      	add	r7, r8
4386456e:      	ldr	r3, [pc, #0x40]         @ 0x438645b0 <_binary_input_a7s_av_cam_bin_start+0x3235b0>
43864570:      	ldr	r2, [pc, #0x40]         @ 0x438645b4 <_binary_input_a7s_av_cam_bin_start+0x3235b4>
43864572:      	uxth	r7, r7
43864574:      	add	r3, pc
43864576:      	mov	r6, r7
43864578:      	strh	r7, [r3]
4386457a:      	ldr	r2, [r5, r2]
4386457c:      	strh.w	r9, [r3, #0x5a]
43864580:      	ldr	r3, [pc, #0x34]         @ 0x438645b8 <_binary_input_a7s_av_cam_bin_start+0x3235b8>
43864582:      	strh	r7, [r2]
43864584:      	ldr	r3, [r5, r3]
43864586:      	strh.w	r9, [r3]
4386458a:      	add	sp, #0x180
4386458c:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, pc}
43864590:      	lsls	r0, r2, #0x3
43864592:      	lsls	r4, r7, #0x1
43864594:      	movs	r7, #0xa8
43864596:      	lsls	r2, r5, #0x1
43864598:      	movs	r7, #0x3c
4386459a:      	lsls	r2, r5, #0x1
4386459c:      	movs	r6, #0xd2
4386459e:      	lsls	r2, r5, #0x1
438645a0:      	movs	r6, #0xb0
438645a2:      	lsls	r2, r5, #0x1
438645a4:      	movs	r6, #0xfe
438645a6:      	lsls	r2, r5, #0x1
438645a8:      	movs	r6, #0x8e
438645aa:      	lsls	r2, r5, #0x1
438645ac:      	movs	r6, #0x68
438645ae:      	lsls	r2, r5, #0x1
438645b0:      	movs	r6, #0x50
438645b2:      	lsls	r2, r5, #0x1
438645b4:      	ldr	r4, [r5, #0x4]
438645b6:      	movs	r0, r0
438645b8:      	strh	r4, [r2, #0x3e]
438645ba:      	movs	r0, r0
438645bc:      	sub	sp, #0x10
438645be:      	push	{r4, r5, r6, r7, lr}
438645c0:      	sub	sp, #0x8c
438645c2:      	add	r4, sp, #0xa0
438645c4:      	ldr	r5, [pc, #0x388]        @ 0x43864950 <_binary_input_a7s_av_cam_bin_start+0x323950>
438645c6:      	ldr	r6, [sp, #0x120]
438645c8:      	stm.w	r4, {r0, r1, r2, r3}
438645cc:      	movs	r1, #0x0
438645ce:      	ldr	r4, [pc, #0x384]        @ 0x43864954 <_binary_input_a7s_av_cam_bin_start+0x323954>
438645d0:      	movs	r2, #0x88
438645d2:      	add	r5, pc
438645d4:      	add	r4, pc
438645d6:      	mov	r0, r4
438645d8:      	blx	0x439b3ffc <_binary_input_a7s_av_cam_bin_start+0x472ffc> @ imm = #0x14fa20
438645dc:      	add	r1, sp, #0xa0
438645de:      	movs	r2, #0x80
438645e0:      	adds	r0, r4, #0x4
438645e2:      	blx	0x439b3918 <_binary_input_a7s_av_cam_bin_start+0x472918> @ imm = #0x14f334
438645e6:      	ldr	r3, [pc, #0x370]        @ 0x43864958 <_binary_input_a7s_av_cam_bin_start+0x323958>
438645e8:      	movs	r2, #0x0
438645ea:      	add	r3, pc
438645ec:      	strb	r2, [r3, #0x2]
438645ee:      	movs	r3, #0x29
438645f0:      	strb	r3, [r4]
438645f2:      	ldr	r3, [pc, #0x368]        @ 0x4386495c <_binary_input_a7s_av_cam_bin_start+0x32395c>
438645f4:      	ldr	r1, [r5, r3]
438645f6:      	ldrb	r3, [r1, #0x10]
438645f8:      	cbz	r3, 0x438645fc <_binary_input_a7s_av_cam_bin_start+0x3235fc> @ imm = #0x0
438645fa:      	strb	r3, [r4]
438645fc:      	ldr	r3, [pc, #0x360]        @ 0x43864960 <_binary_input_a7s_av_cam_bin_start+0x323960>
438645fe:      	movw	r2, #0x473
43864602:      	add	r3, pc
43864604:      	strh	r2, [r3, #0x2]
43864606:      	ldrh	r2, [r1, #0xe]
43864608:      	cbz	r2, 0x4386460c <_binary_input_a7s_av_cam_bin_start+0x32360c> @ imm = #0x0
4386460a:      	strh	r2, [r3, #0x2]
4386460c:      	ldr	r2, [pc, #0x354]        @ 0x43864964 <_binary_input_a7s_av_cam_bin_start+0x323964>
4386460e:      	add	r2, pc
43864610:      	ldrb.w	r3, [r2, #0x74]
43864614:      	cmp	r3, #0x0
43864616:      	bne	0x438646e8 <_binary_input_a7s_av_cam_bin_start+0x3236e8> @ imm = #0xce
43864618:      	ldrh.w	r3, [r2, #0x76]
4386461c:      	cmp	r3, #0x42
4386461e:      	beq	0x43864662 <_binary_input_a7s_av_cam_bin_start+0x323662> @ imm = #0x40
43864620:      	bhi	0x43864638 <_binary_input_a7s_av_cam_bin_start+0x323638> @ imm = #0x14
43864622:      	cmp	r3, #0x20
43864624:      	beq	0x43864662 <_binary_input_a7s_av_cam_bin_start+0x323662> @ imm = #0x3a
43864626:      	bhi	0x4386462e <_binary_input_a7s_av_cam_bin_start+0x32362e> @ imm = #0x4
43864628:      	cmp	r3, #0x14
4386462a:      	bne	0x43864692 <_binary_input_a7s_av_cam_bin_start+0x323692> @ imm = #0x64
4386462c:      	b	0x43864680 <_binary_input_a7s_av_cam_bin_start+0x323680> @ imm = #0x50
4386462e:      	cmp	r3, #0x2a
43864630:      	beq	0x4386465a <_binary_input_a7s_av_cam_bin_start+0x32365a> @ imm = #0x26
43864632:      	cmp	r3, #0x2b
43864634:      	bne	0x43864692 <_binary_input_a7s_av_cam_bin_start+0x323692> @ imm = #0x5a
43864636:      	b	0x4386467c <_binary_input_a7s_av_cam_bin_start+0x32367c> @ imm = #0x42
43864638:      	movw	r2, #0x6479
4386463c:      	cmp	r3, r2
4386463e:      	beq	0x43864676 <_binary_input_a7s_av_cam_bin_start+0x323676> @ imm = #0x34
43864640:      	bhi	0x4386464a <_binary_input_a7s_av_cam_bin_start+0x32364a> @ imm = #0x6
43864642:      	subs	r2, #0x96
43864644:      	cmp	r3, r2
43864646:      	bne	0x43864692 <_binary_input_a7s_av_cam_bin_start+0x323692> @ imm = #0x48
43864648:      	b	0x4386465e <_binary_input_a7s_av_cam_bin_start+0x32365e> @ imm = #0x12
4386464a:      	movw	r2, #0x64bf
4386464e:      	cmp	r3, r2
43864650:      	beq	0x43864696 <_binary_input_a7s_av_cam_bin_start+0x323696> @ imm = #0x42
43864652:      	movw	r2, #0x6613
43864656:      	cmp	r3, r2
43864658:      	bne	0x43864692 <_binary_input_a7s_av_cam_bin_start+0x323692> @ imm = #0x36
4386465a:      	movs	r3, #0xa
4386465c:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x3c
4386465e:      	movs	r3, #0x1
43864660:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x38
43864662:      	ldr	r3, [pc, #0x304]        @ 0x43864968 <_binary_input_a7s_av_cam_bin_start+0x323968>
43864664:      	add	r3, pc
43864666:      	ldrb.w	r2, [r3, #0x80]
4386466a:      	movw	r3, #0xffda
4386466e:      	cmp	r2, #0x0
43864670:      	it	ne
43864672:      	movne	r3, #0x0
43864674:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x24
43864676:      	movw	r3, #0xfff1
4386467a:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x1e
4386467c:      	movs	r3, #0x15
4386467e:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x1a
43864680:      	ldrb.w	r3, [r2, #0x80]
43864684:      	cmp	r3, #0x1
43864686:      	beq	0x4386469a <_binary_input_a7s_av_cam_bin_start+0x32369a> @ imm = #0x10
43864688:      	cmp	r3, #0x2
4386468a:      	ite	eq
4386468c:      	moveq	r3, #0x25
4386468e:      	movne	r3, #0x0
43864690:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x8
43864692:      	movs	r3, #0x0
43864694:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x4
43864696:      	movs	r3, #0x4
43864698:      	b	0x4386469c <_binary_input_a7s_av_cam_bin_start+0x32369c> @ imm = #0x0
4386469a:      	movs	r3, #0x18
4386469c:      	ldrb.w	r2, [r1, #0xfe]
438646a0:      	cbz	r2, 0x438646a8 <_binary_input_a7s_av_cam_bin_start+0x3236a8> @ imm = #0x4
438646a2:      	sxtab	r3, r3, r2
438646a6:      	uxth	r3, r3
438646a8:      	cbz	r3, 0x438646ea <_binary_input_a7s_av_cam_bin_start+0x3236ea> @ imm = #0x3e
438646aa:      	mov.w	r7, #0x3e8
438646ae:      	add	r2, sp, #0xbc
438646b0:      	add.w	lr, sp, #0xe8
438646b4:      	mov	r4, r2
438646b6:      	smulbb	r7, r3, r7
438646ba:      	movs	r0, #0x0
438646bc:      	ldr	r12, [r4, #4]!
438646c0:      	add	r12, r7
438646c2:      	cmp.w	r12, #0x0
438646c6:      	it	gt
438646c8:      	movgt	r0, #0x1
438646ca:      	cmp	r4, lr
438646cc:      	bne	0x438646bc <_binary_input_a7s_av_cam_bin_start+0x3236bc> @ imm = #-0x14
438646ce:      	cmp	r0, #0x1
438646d0:      	bne	0x438646e8 <_binary_input_a7s_av_cam_bin_start+0x3236e8> @ imm = #0x14
438646d2:      	ldr	r0, [pc, #0x298]        @ 0x4386496c <_binary_input_a7s_av_cam_bin_start+0x32396c>
438646d4:      	add	r0, pc
438646d6:      	adds	r0, #0x20
438646d8:      	ldr	r4, [r2, #4]!
438646dc:      	cmp	r2, lr
438646de:      	add	r4, r7
438646e0:      	str	r4, [r0, #4]!
438646e4:      	bne	0x438646d8 <_binary_input_a7s_av_cam_bin_start+0x3236d8> @ imm = #-0x10
438646e6:      	b	0x438646ea <_binary_input_a7s_av_cam_bin_start+0x3236ea> @ imm = #0x0
438646e8:      	movs	r3, #0x0
438646ea:      	ldr	r2, [pc, #0x284]        @ 0x43864970 <_binary_input_a7s_av_cam_bin_start+0x323970>
438646ec:      	ldr	r0, [r5, r2]
438646ee:      	ldr	r2, [pc, #0x284]        @ 0x43864974 <_binary_input_a7s_av_cam_bin_start+0x323974>
438646f0:      	add	r2, pc
438646f2:      	strh.w	r3, [r0, #0x9aa]
438646f6:      	ldrh.w	r3, [sp, #0xb4]
438646fa:      	ldrh.w	r4, [r2, #0x76]
438646fe:      	strh.w	r4, [r0, #0x9a8]
43864702:      	cbnz	r3, 0x4386472e <_binary_input_a7s_av_cam_bin_start+0x32372e> @ imm = #0x28
43864704:      	ldr	r3, [sp, #0xe8]
43864706:      	cbnz	r3, 0x4386472e <_binary_input_a7s_av_cam_bin_start+0x32372e> @ imm = #0x24
43864708:      	ldrh.w	r0, [r1, #0xdc]
4386470c:      	mov.w	r4, #0x3e8
43864710:      	muls	r4, r0, r4
43864712:      	adds	r0, r2, #0x2
43864714:      	adds	r2, #0x20
43864716:      	strh	r3, [r0, #2]!
4386471a:      	add.w	r3, r3, #0x580
4386471e:      	adds	r3, #0xc
43864720:      	movw	r7, #0x3d04
43864724:      	str	r4, [r2, #4]!
43864728:      	uxth	r3, r3
4386472a:      	cmp	r3, r7
4386472c:      	bne	0x43864716 <_binary_input_a7s_av_cam_bin_start+0x323716> @ imm = #-0x1a
4386472e:      	ldr	r3, [pc, #0x248]        @ 0x43864978 <_binary_input_a7s_av_cam_bin_start+0x323978>
43864730:      	ldr	r4, [r5, r3]
43864732:      	ldrh.w	r3, [r4, #0xae]
43864736:      	cbz	r3, 0x43864762 <_binary_input_a7s_av_cam_bin_start+0x323762> @ imm = #0x28
43864738:      	mov.w	r7, #0x3e8
4386473c:      	muls	r7, r3, r7
4386473e:      	ldr	r3, [pc, #0x23c]        @ 0x4386497c <_binary_input_a7s_av_cam_bin_start+0x32397c>
43864740:      	add	r3, pc
43864742:      	adds	r0, r3, #0x2
43864744:      	add.w	r2, r3, #0x20
43864748:      	movs	r3, #0x0
4386474a:      	strh	r3, [r0, #2]!
4386474e:      	add.w	r3, r3, #0x580
43864752:      	adds	r3, #0xc
43864754:      	movw	lr, #0x3d04
43864758:      	str	r7, [r2, #4]!
4386475c:      	uxth	r3, r3
4386475e:      	cmp	r3, lr
43864760:      	bne	0x4386474a <_binary_input_a7s_av_cam_bin_start+0x32374a> @ imm = #-0x1a
43864762:      	ldrb.w	r3, [r6, #0x5c]
43864766:      	cmp	r3, #0x1
43864768:      	bne	0x4386479a <_binary_input_a7s_av_cam_bin_start+0x32379a> @ imm = #0x2e
4386476a:      	ldrh.w	r3, [r6, #0xb2a]
4386476e:      	cbz	r3, 0x4386479a <_binary_input_a7s_av_cam_bin_start+0x32379a> @ imm = #0x28
43864770:      	mov.w	r7, #0x3e8
43864774:      	muls	r7, r3, r7
43864776:      	ldr	r3, [pc, #0x208]        @ 0x43864980 <_binary_input_a7s_av_cam_bin_start+0x323980>
43864778:      	add	r3, pc
4386477a:      	adds	r0, r3, #0x2
4386477c:      	add.w	r2, r3, #0x20
43864780:      	movs	r3, #0x0
43864782:      	strh	r3, [r0, #2]!
43864786:      	add.w	r3, r3, #0x580
4386478a:      	adds	r3, #0xc
4386478c:      	movw	lr, #0x3d04
43864790:      	str	r7, [r2, #4]!
43864794:      	uxth	r3, r3
43864796:      	cmp	r3, lr
43864798:      	bne	0x43864782 <_binary_input_a7s_av_cam_bin_start+0x323782> @ imm = #-0x1a
4386479a:      	ldr	r7, [pc, #0x1e8]        @ 0x43864984 <_binary_input_a7s_av_cam_bin_start+0x323984>
4386479c:      	ldr	r3, [pc, #0x1e8]        @ 0x43864988 <_binary_input_a7s_av_cam_bin_start+0x323988>
4386479e:      	add	r7, pc
438647a0:      	ldr	r3, [r5, r3]
438647a2:      	ldrb.w	r2, [r7, #0x71]
438647a6:      	strb	r2, [r3]
438647a8:      	ldr	r3, [pc, #0x1e0]        @ 0x4386498c <_binary_input_a7s_av_cam_bin_start+0x32398c>
438647aa:      	ldrb.w	r2, [r7, #0x72]
438647ae:      	ldr	r3, [r5, r3]
438647b0:      	strb	r2, [r3]
438647b2:      	ldr	r3, [pc, #0x1dc]        @ 0x43864990 <_binary_input_a7s_av_cam_bin_start+0x323990>
438647b4:      	ldrb.w	r2, [r7, #0x73]
438647b8:      	ldr	r3, [r5, r3]
438647ba:      	strb	r2, [r3]
438647bc:      	ldr	r3, [pc, #0x1d4]        @ 0x43864994 <_binary_input_a7s_av_cam_bin_start+0x323994>
438647be:      	ldrb.w	r2, [r7, #0x74]
438647c2:      	ldr	r3, [r5, r3]
438647c4:      	strb	r2, [r3]
438647c6:      	ldrb.w	r2, [r7, #0x7c]
438647ca:      	ldr	r3, [r7, #0x7c]
438647cc:      	cmp	r2, #0x0
438647ce:      	bne	0x4386489a <_binary_input_a7s_av_cam_bin_start+0x32389a> @ imm = #0xc8
438647d0:      	ldrb.w	r2, [r6, #0x5c]
438647d4:      	cmp	r2, #0x1
438647d6:      	bne	0x43864820 <_binary_input_a7s_av_cam_bin_start+0x323820> @ imm = #0x46
438647d8:      	ldrb.w	r2, [r6, #0xb02]
438647dc:      	cmp	r2, #0x1
438647de:      	bne	0x43864820 <_binary_input_a7s_av_cam_bin_start+0x323820> @ imm = #0x3e
438647e0:      	add.w	r0, r6, #0xb00
438647e4:      	adds	r0, #0x16
438647e6:      	bl	0x438642f0 <_binary_input_a7s_av_cam_bin_start+0x3232f0> @ imm = #-0x4fa
438647ea:      	ldr	r3, [pc, #0x1ac]        @ 0x43864998 <_binary_input_a7s_av_cam_bin_start+0x323998>
438647ec:      	ldrh.w	r2, [r4, #0xe6]
438647f0:      	ldr	r3, [r5, r3]
438647f2:      	strh.w	r2, [r3, #0xc8]
438647f6:      	ldrh.w	r2, [r6, #0xb16]
438647fa:      	strh.w	r2, [r7, #0x64]
438647fe:      	ldrh.w	r2, [r4, #0xe8]
43864802:      	strh.w	r2, [r3, #0xca]
43864806:      	ldrh.w	r2, [r6, #0xb18]
4386480a:      	strh.w	r2, [r7, #0x66]
4386480e:      	ldrh.w	r2, [r4, #0xea]
43864812:      	strh.w	r2, [r3, #0xcc]
43864816:      	ldrh.w	r3, [r6, #0xb1a]
4386481a:      	strh.w	r3, [r7, #0x68]
4386481e:      	b	0x4386489a <_binary_input_a7s_av_cam_bin_start+0x32389a> @ imm = #0x78
43864820:      	ldrh.w	r5, [r1, #0x168]
43864824:      	ldrh.w	r2, [r4, #0xe6]
43864828:      	cmp	r5, #0x0
4386482a:      	it	eq
4386482c:      	moveq	r5, #0x32
4386482e:      	cbnz	r2, 0x43864838 <_binary_input_a7s_av_cam_bin_start+0x323838> @ imm = #0x6
43864830:      	sub.w	r2, r5, #0xa
43864834:      	strh.w	r2, [r4, #0xec]
43864838:      	ldr	r0, [pc, #0x160]        @ 0x4386499c <_binary_input_a7s_av_cam_bin_start+0x32399c>
4386483a:      	add	r0, pc
4386483c:      	ldrh.w	r2, [r0, #0x64]
43864840:      	cbz	r2, 0x4386487e <_binary_input_a7s_av_cam_bin_start+0x32387e> @ imm = #0x3a
43864842:      	ldr	r2, [r0, #0x78]
43864844:      	cbnz	r2, 0x4386487e <_binary_input_a7s_av_cam_bin_start+0x32387e> @ imm = #0x36
43864846:      	ands	r7, r3, #0xff00ff00
4386484a:      	bne	0x4386487e <_binary_input_a7s_av_cam_bin_start+0x32387e> @ imm = #0x30
4386484c:      	adds	r0, #0x64
4386484e:      	bl	0x438642f0 <_binary_input_a7s_av_cam_bin_start+0x3232f0> @ imm = #-0x562
43864852:      	ldrh.w	r3, [r4, #0xec]
43864856:      	adds	r3, #0x1
43864858:      	uxth	r3, r3
4386485a:      	strh.w	r3, [r4, #0xec]
4386485e:      	cmp	r3, r5
43864860:      	blo	0x4386487e <_binary_input_a7s_av_cam_bin_start+0x32387e> @ imm = #0x1a
43864862:      	ldrh.w	r2, [r4, #0xe6]
43864866:      	ldrh.w	r3, [r4, #0xe8]
4386486a:      	strh.w	r7, [r4, #0xec]
4386486e:      	strh.w	r2, [r4, #0xf0]
43864872:      	ldrh.w	r2, [r4, #0xea]
43864876:      	strh.w	r3, [r4, #0xf2]
4386487a:      	strh.w	r2, [r4, #0xf4]
4386487e:      	ldr	r3, [pc, #0x120]        @ 0x438649a0 <_binary_input_a7s_av_cam_bin_start+0x3239a0>
43864880:      	ldrh.w	r2, [r4, #0xf0]
43864884:      	add	r3, pc
43864886:      	strh.w	r2, [r3, #0x64]
4386488a:      	ldrh.w	r2, [r4, #0xf2]
4386488e:      	strh.w	r2, [r3, #0x66]
43864892:      	ldrh.w	r2, [r4, #0xf4]
43864896:      	strh.w	r2, [r3, #0x68]
4386489a:      	ldr	r5, [pc, #0x108]        @ 0x438649a4 <_binary_input_a7s_av_cam_bin_start+0x3239a4>
4386489c:      	movs	r2, #0x70
4386489e:      	mov	r0, sp
438648a0:      	str	r6, [sp, #0x70]
438648a2:      	add	r5, pc
438648a4:      	add.w	r1, r5, #0x14
438648a8:      	blx	0x439b3918 <_binary_input_a7s_av_cam_bin_start+0x472918> @ imm = #0x14f06c
438648ac:      	adds	r3, r5, #0x4
438648ae:      	ldm	r3, {r0, r1, r2, r3}
438648b0:      	bl	0x43865100 <_binary_input_a7s_av_cam_bin_start+0x324100> @ imm = #0x84c
438648b4:      	bl	0x43865240 <_binary_input_a7s_av_cam_bin_start+0x324240> @ imm = #0x988
438648b8:      	strh.w	r0, [sp, #0x78]
438648bc:      	ubfx	r0, r0, #0x10, #0x10
438648c0:      	strh.w	r0, [sp, #0x7a]
438648c4:      	ldr	r3, [sp, #0x78]
438648c6:      	strh.w	r3, [r5, #0x84]
438648ca:      	str	r3, [sp, #0x84]
438648cc:      	bl	0x43865240 <_binary_input_a7s_av_cam_bin_start+0x324240> @ imm = #0x970
438648d0:      	strh.w	r0, [sp, #0x78]
438648d4:      	ubfx	r0, r0, #0x10, #0x10
438648d8:      	strh.w	r0, [sp, #0x7a]
438648dc:      	ldr	r3, [sp, #0x78]
438648de:      	str	r3, [sp, #0x80]
438648e0:      	lsrs	r3, r3, #0x10
438648e2:      	strh.w	r3, [r5, #0x86]
438648e6:      	bl	0x43864430 <_binary_input_a7s_av_cam_bin_start+0x323430> @ imm = #-0x4ba
438648ea:      	mov	r3, r4
438648ec:      	ldrb	r2, [r3, #176]!
438648f0:      	cmp	r2, #0x1
438648f2:      	bne	0x4386490c <_binary_input_a7s_av_cam_bin_start+0x32390c> @ imm = #0x16
438648f4:      	mov	r1, r3
438648f6:      	subs	r2, #0x1
438648f8:      	ldr	r3, [pc, #0xac]         @ 0x438649a8 <_binary_input_a7s_av_cam_bin_start+0x3239a8>
438648fa:      	ldrb	r5, [r1, #1]!
438648fe:      	add	r3, pc
43864900:      	adds	r0, r3, r2
43864902:      	adds	r2, #0x2
43864904:      	cmp	r2, #0x52
43864906:      	strh	r5, [r0, #0x4]
43864908:      	bne	0x438648f8 <_binary_input_a7s_av_cam_bin_start+0x3238f8> @ imm = #-0x14
4386490a:      	b	0x43864934 <_binary_input_a7s_av_cam_bin_start+0x323934> @ imm = #0x26
4386490c:      	mov	r1, r3
4386490e:      	movs	r2, #0x0
43864910:      	ldr	r3, [pc, #0x98]         @ 0x438649ac <_binary_input_a7s_av_cam_bin_start+0x3239ac>
43864912:      	add	r3, pc
43864914:      	adds	r0, r3, r2
43864916:      	adds	r2, #0x2
43864918:      	cmp	r2, #0x52
4386491a:      	ldrh	r0, [r0, #0x4]
4386491c:      	strb	r0, [r1, #1]!
43864920:      	bne	0x43864910 <_binary_input_a7s_av_cam_bin_start+0x323910> @ imm = #-0x14
43864922:      	ldrh.w	r2, [r3, #0x56]
43864926:      	ldrh.w	r3, [r3, #0x58]
4386492a:      	strh.w	r2, [r4, #0xda]
4386492e:      	strh.w	r3, [r4, #0xdc]
43864932:      	b	0x43864944 <_binary_input_a7s_av_cam_bin_start+0x323944> @ imm = #0xe
43864934:      	ldrh.w	r2, [r4, #0xda]
43864938:      	ldrh.w	r4, [r4, #0xdc]
4386493c:      	strh.w	r2, [r3, #0x56]
43864940:      	strh.w	r4, [r3, #0x58]
43864944:      	add	sp, #0x8c
43864946:      	pop.w	{r4, r5, r6, r7, lr}
4386494a:      	add	sp, #0x10
4386494c:      	bx	lr
4386494e:      	nop
43864950:      	<unknown>
43864954:      	movs	r6, #0x54
43864956:      	lsls	r2, r5, #0x1
43864958:      	movs	r5, #0xda
4386495a:      	lsls	r2, r5, #0x1
4386495c:      	orrs	r4, r5
4386495e:      	movs	r0, r0
43864960:      	movs	r6, #0x26
43864962:      	lsls	r2, r5, #0x1
43864964:      	movs	r6, #0x1a
43864966:      	lsls	r2, r5, #0x1
43864968:      	movs	r5, #0xc4
4386496a:      	lsls	r2, r5, #0x1
4386496c:      	movs	r5, #0x54
4386496e:      	lsls	r2, r5, #0x1
43864970:      	ldrb	r4, [r6, #0x1d]
43864972:      	movs	r0, r0
43864974:      	movs	r5, #0x38
43864976:      	lsls	r2, r5, #0x1
43864978:      	lsrs	r4, r4, #0x12
4386497a:      	movs	r0, r0
4386497c:      	movs	r4, #0xe8
4386497e:      	lsls	r2, r5, #0x1
43864980:      	movs	r4, #0xb0
43864982:      	lsls	r2, r5, #0x1
43864984:      	movs	r4, #0x8a
43864986:      	lsls	r2, r5, #0x1
43864988:      	strb	r4, [r0, #0x1b]
4386498a:      	movs	r0, r0
4386498c:      	ldrh	r4, [r2, #0x2a]
4386498e:      	movs	r0, r0
43864990:      	lsrs	r0, r4, #0x1d
43864992:      	movs	r0, r0
43864994:      	ldrb	r0, [r4, #0x15]
43864996:      	movs	r0, r0
43864998:      	ldr	r4, [r2, #0x60]
4386499a:      	movs	r0, r0
4386499c:      	movs	r3, #0xee
4386499e:      	lsls	r2, r5, #0x1
438649a0:      	movs	r3, #0xa4
438649a2:      	lsls	r2, r5, #0x1
438649a4:      	movs	r3, #0x86
438649a6:      	lsls	r2, r5, #0x1
438649a8:      	movs	r2, #0xc6
438649aa:      	lsls	r2, r5, #0x1
438649ac:      	movs	r2, #0xb2
438649ae:      	lsls	r2, r5, #0x1
438649b0:      	ldr	r3, [pc, #0x4]          @ 0x438649b8 <_binary_input_a7s_av_cam_bin_start+0x3239b8>
438649b2:      	add	r3, pc
438649b4:      	ldrb	r0, [r3]
438649b6:      	bx	lr
438649b8:      	strb	r0, [r6, #0x2]
438649ba:      	lsls	r4, r6, #0x1
438649bc:      	push.w	{r4, r5, r6, r7, r8, lr}
438649c0:      	mov	r7, r2
438649c2:      	ldrh.w	r2, [r2, #0x4c4]
438649c6:      	mov	r5, r0
438649c8:      	ldr	r4, [pc, #0x1e4]        @ 0x43864bb0 <_binary_input_a7s_av_cam_bin_start+0x323bb0>
438649ca:      	mov	r6, r1
438649cc:      	tst.w	r2, #0x60
438649d0:      	add	r4, pc
438649d2:      	bne	0x438649da <_binary_input_a7s_av_cam_bin_start+0x3239da> @ imm = #0x4
438649d4:      	ands	r1, r2, #0x80
438649d8:      	beq	0x438649f0 <_binary_input_a7s_av_cam_bin_start+0x3239f0> @ imm = #0x14
438649da:      	tst.w	r2, #0x20
438649de:      	beq	0x438649e8 <_binary_input_a7s_av_cam_bin_start+0x3239e8> @ imm = #0x6
438649e0:      	ldr	r2, [pc, #0x1d0]        @ 0x43864bb4 <_binary_input_a7s_av_cam_bin_start+0x323bb4>
438649e2:      	movs	r1, #0x5
438649e4:      	add	r2, pc
438649e6:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x5e
438649e8:      	ldr	r2, [pc, #0x1cc]        @ 0x43864bb8 <_binary_input_a7s_av_cam_bin_start+0x323bb8>
438649ea:      	movs	r1, #0x1
438649ec:      	add	r2, pc
438649ee:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x56
438649f0:      	ldr.w	r2, [r7, #0x404]
438649f4:      	cmp	r2, #0x2
438649f6:      	bne	0x438649fe <_binary_input_a7s_av_cam_bin_start+0x3239fe> @ imm = #0x4
438649f8:      	ldr	r2, [pc, #0x1c0]        @ 0x43864bbc <_binary_input_a7s_av_cam_bin_start+0x323bbc>
438649fa:      	add	r2, pc
438649fc:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x48
438649fe:      	ldr.w	r1, [r7, #0x424]
43864a02:      	cmp	r1, #0x1
43864a04:      	bne	0x43864a42 <_binary_input_a7s_av_cam_bin_start+0x323a42> @ imm = #0x3a
43864a06:      	ldrb	r2, [r3, #0x2]
43864a08:      	cbnz	r2, 0x43864a24 <_binary_input_a7s_av_cam_bin_start+0x323a24> @ imm = #0x18
43864a0a:      	ldr	r2, [pc, #0x1b4]        @ 0x43864bc0 <_binary_input_a7s_av_cam_bin_start+0x323bc0>
43864a0c:      	ldrh.w	r0, [r6, #0x166]
43864a10:      	ldr	r2, [r4, r2]
43864a12:      	ldrh	r2, [r2]
43864a14:      	cmp	r0, r2
43864a16:      	bls	0x43864a1e <_binary_input_a7s_av_cam_bin_start+0x323a1e> @ imm = #0x4
43864a18:      	ldr	r2, [pc, #0x1a8]        @ 0x43864bc4 <_binary_input_a7s_av_cam_bin_start+0x323bc4>
43864a1a:      	add	r2, pc
43864a1c:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x28
43864a1e:      	ldr	r2, [pc, #0x1a8]        @ 0x43864bc8 <_binary_input_a7s_av_cam_bin_start+0x323bc8>
43864a20:      	add	r2, pc
43864a22:      	b	0x43864a46 <_binary_input_a7s_av_cam_bin_start+0x323a46> @ imm = #0x20
43864a24:      	cmp	r2, #0x1
43864a26:      	bne	0x43864a3c <_binary_input_a7s_av_cam_bin_start+0x323a3c> @ imm = #0x12
43864a28:      	ldrb.w	r1, [r7, #0x38c]
43864a2c:      	cmp	r1, #0x1
43864a2e:      	bne	0x43864a36 <_binary_input_a7s_av_cam_bin_start+0x323a36> @ imm = #0x4
43864a30:      	ldr	r2, [pc, #0x198]        @ 0x43864bcc <_binary_input_a7s_av_cam_bin_start+0x323bcc>
43864a32:      	add	r2, pc
43864a34:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x10
43864a36:      	ldr	r2, [pc, #0x198]        @ 0x43864bd0 <_binary_input_a7s_av_cam_bin_start+0x323bd0>
43864a38:      	add	r2, pc
43864a3a:      	b	0x43864a46 <_binary_input_a7s_av_cam_bin_start+0x323a46> @ imm = #0x8
43864a3c:      	ldr	r2, [pc, #0x194]        @ 0x43864bd4 <_binary_input_a7s_av_cam_bin_start+0x323bd4>
43864a3e:      	add	r2, pc
43864a40:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x4
43864a42:      	ldr	r2, [pc, #0x194]        @ 0x43864bd8 <_binary_input_a7s_av_cam_bin_start+0x323bd8>
43864a44:      	add	r2, pc
43864a46:      	movs	r1, #0x3
43864a48:      	str	r1, [r2, #0x5c]
43864a4a:      	ldr	r2, [pc, #0x190]        @ 0x43864bdc <_binary_input_a7s_av_cam_bin_start+0x323bdc>
43864a4c:      	ldr	r1, [r4, r2]
43864a4e:      	mov	r8, r1
43864a50:      	ldrb.w	r2, [r1, #0x7e]
43864a54:      	cmp	r2, #0x0
43864a56:      	beq	0x43864abe <_binary_input_a7s_av_cam_bin_start+0x323abe> @ imm = #0x64
43864a58:      	cmp	r2, #0x1
43864a5a:      	bne	0x43864a64 <_binary_input_a7s_av_cam_bin_start+0x323a64> @ imm = #0x6
43864a5c:      	ldr	r2, [pc, #0x180]        @ 0x43864be0 <_binary_input_a7s_av_cam_bin_start+0x323be0>
43864a5e:      	movs	r1, #0x0
43864a60:      	add	r2, pc
43864a62:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x56
43864a64:      	cmp	r2, #0x2
43864a66:      	bne	0x43864a6e <_binary_input_a7s_av_cam_bin_start+0x323a6e> @ imm = #0x4
43864a68:      	ldr	r2, [pc, #0x178]        @ 0x43864be4 <_binary_input_a7s_av_cam_bin_start+0x323be4>
43864a6a:      	add	r2, pc
43864a6c:      	b	0x43864aba <_binary_input_a7s_av_cam_bin_start+0x323aba> @ imm = #0x4a
43864a6e:      	cmp	r2, #0x3
43864a70:      	bne	0x43864a7a <_binary_input_a7s_av_cam_bin_start+0x323a7a> @ imm = #0x6
43864a72:      	ldr	r2, [pc, #0x174]        @ 0x43864be8 <_binary_input_a7s_av_cam_bin_start+0x323be8>
43864a74:      	movs	r1, #0x2
43864a76:      	add	r2, pc
43864a78:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x40
43864a7a:      	cmp	r2, #0x4
43864a7c:      	bne	0x43864a86 <_binary_input_a7s_av_cam_bin_start+0x323a86> @ imm = #0x6
43864a7e:      	ldr	r2, [pc, #0x16c]        @ 0x43864bec <_binary_input_a7s_av_cam_bin_start+0x323bec>
43864a80:      	movs	r1, #0x3
43864a82:      	add	r2, pc
43864a84:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x34
43864a86:      	cmp	r2, #0x5
43864a88:      	bne	0x43864a92 <_binary_input_a7s_av_cam_bin_start+0x323a92> @ imm = #0x6
43864a8a:      	ldr	r2, [pc, #0x164]        @ 0x43864bf0 <_binary_input_a7s_av_cam_bin_start+0x323bf0>
43864a8c:      	movs	r1, #0x4
43864a8e:      	add	r2, pc
43864a90:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x28
43864a92:      	cmp	r2, #0x6
43864a94:      	bne	0x43864a9e <_binary_input_a7s_av_cam_bin_start+0x323a9e> @ imm = #0x6
43864a96:      	ldr	r2, [pc, #0x15c]        @ 0x43864bf4 <_binary_input_a7s_av_cam_bin_start+0x323bf4>
43864a98:      	movs	r1, #0x5
43864a9a:      	add	r2, pc
43864a9c:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x1c
43864a9e:      	cmp	r2, #0x7
43864aa0:      	bne	0x43864aaa <_binary_input_a7s_av_cam_bin_start+0x323aaa> @ imm = #0x6
43864aa2:      	ldr	r2, [pc, #0x154]        @ 0x43864bf8 <_binary_input_a7s_av_cam_bin_start+0x323bf8>
43864aa4:      	movs	r1, #0x6
43864aa6:      	add	r2, pc
43864aa8:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x10
43864aaa:      	cmp	r2, #0x8
43864aac:      	bne	0x43864ab6 <_binary_input_a7s_av_cam_bin_start+0x323ab6> @ imm = #0x6
43864aae:      	ldr	r2, [pc, #0x14c]        @ 0x43864bfc <_binary_input_a7s_av_cam_bin_start+0x323bfc>
43864ab0:      	movs	r1, #0x7
43864ab2:      	add	r2, pc
43864ab4:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x4
43864ab6:      	ldr	r2, [pc, #0x148]        @ 0x43864c00 <_binary_input_a7s_av_cam_bin_start+0x323c00>
43864ab8:      	add	r2, pc
43864aba:      	movs	r1, #0x1
43864abc:      	str	r1, [r2, #0x5c]
43864abe:      	ldrb	r0, [r3, #0x2]
43864ac0:      	cmp	r0, #0x1
43864ac2:      	bne	0x43864aca <_binary_input_a7s_av_cam_bin_start+0x323aca> @ imm = #0x4
43864ac4:      	ldrb.w	r3, [r7, #0x38c]
43864ac8:      	cbz	r3, 0x43864acc <_binary_input_a7s_av_cam_bin_start+0x323acc> @ imm = #0x0
43864aca:      	movs	r0, #0x0
43864acc:      	bl	0x438642e4 <_binary_input_a7s_av_cam_bin_start+0x3232e4> @ imm = #-0x7ec
43864ad0:      	ldr.w	r3, [r7, #0x404]
43864ad4:      	cmp	r3, #0x2
43864ad6:      	bne	0x43864ae0 <_binary_input_a7s_av_cam_bin_start+0x323ae0> @ imm = #0x6
43864ad8:      	ldr	r3, [pc, #0x128]        @ 0x43864c04 <_binary_input_a7s_av_cam_bin_start+0x323c04>
43864ada:      	movs	r2, #0x0
43864adc:      	add	r3, pc
43864ade:      	b	0x43864b00 <_binary_input_a7s_av_cam_bin_start+0x323b00> @ imm = #0x1e
43864ae0:      	ldr.w	r2, [r7, #0x424]
43864ae4:      	cmp	r2, #0x1
43864ae6:      	bne	0x43864aee <_binary_input_a7s_av_cam_bin_start+0x323aee> @ imm = #0x4
43864ae8:      	ldr	r3, [pc, #0x11c]        @ 0x43864c08 <_binary_input_a7s_av_cam_bin_start+0x323c08>
43864aea:      	add	r3, pc
43864aec:      	b	0x43864b00 <_binary_input_a7s_av_cam_bin_start+0x323b00> @ imm = #0x10
43864aee:      	ldr	r3, [pc, #0x11c]        @ 0x43864c0c <_binary_input_a7s_av_cam_bin_start+0x323c0c>
43864af0:      	movs	r2, #0x0
43864af2:      	add	r3, pc
43864af4:      	strb.w	r2, [r3, #0x60]
43864af8:      	ldrb.w	r2, [r8, #0x10f]
43864afc:      	cmp	r2, #0x1
43864afe:      	bne	0x43864b04 <_binary_input_a7s_av_cam_bin_start+0x323b04> @ imm = #0x2
43864b00:      	strb.w	r2, [r3, #0x60]
43864b04:      	ldrb.w	r2, [r8, #0xf9]
43864b08:      	cmp	r2, #0x1
43864b0a:      	bne	0x43864b22 <_binary_input_a7s_av_cam_bin_start+0x323b22> @ imm = #0x14
43864b0c:      	ldr	r3, [pc, #0x100]        @ 0x43864c10 <_binary_input_a7s_av_cam_bin_start+0x323c10>
43864b0e:      	add	r3, pc
43864b10:      	ldr	r1, [r3, #0x5c]
43864b12:      	cmp	r1, #0x3
43864b14:      	bne	0x43864b22 <_binary_input_a7s_av_cam_bin_start+0x323b22> @ imm = #0xa
43864b16:      	ldrh.w	r0, [r6, #0x166]
43864b1a:      	ldrh.w	r1, [r8, #0xfc]
43864b1e:      	cmp	r0, r1
43864b20:      	bhs	0x43864b28 <_binary_input_a7s_av_cam_bin_start+0x323b28> @ imm = #0x4
43864b22:      	ldr	r3, [pc, #0xf0]         @ 0x43864c14 <_binary_input_a7s_av_cam_bin_start+0x323c14>
43864b24:      	movs	r2, #0x0
43864b26:      	add	r3, pc
43864b28:      	strb.w	r2, [r3, #0x61]
43864b2c:      	ldrb.w	r0, [r5, #0x36]
43864b30:      	cmp	r0, #0x1
43864b32:      	bne	0x43864b76 <_binary_input_a7s_av_cam_bin_start+0x323b76> @ imm = #0x40
43864b34:      	ldr	r3, [pc, #0xe0]         @ 0x43864c18 <_binary_input_a7s_av_cam_bin_start+0x323c18>
43864b36:      	movs	r1, #0x0
43864b38:      	add	r3, pc
43864b3a:      	strb.w	r1, [r3, #0x61]
43864b3e:      	strb.w	r1, [r3, #0x60]
43864b42:      	ldrb.w	r2, [r5, #0x37]
43864b46:      	cbnz	r2, 0x43864b4c <_binary_input_a7s_av_cam_bin_start+0x323b4c> @ imm = #0x2
43864b48:      	str	r0, [r3, #0x5c]
43864b4a:      	b	0x43864b76 <_binary_input_a7s_av_cam_bin_start+0x323b76> @ imm = #0x28
43864b4c:      	cmp	r2, #0x1
43864b4e:      	bne	0x43864b54 <_binary_input_a7s_av_cam_bin_start+0x323b54> @ imm = #0x2
43864b50:      	adds	r2, #0x2
43864b52:      	b	0x43864b74 <_binary_input_a7s_av_cam_bin_start+0x323b74> @ imm = #0x1e
43864b54:      	cmp	r2, #0x2
43864b56:      	beq	0x43864b74 <_binary_input_a7s_av_cam_bin_start+0x323b74> @ imm = #0x1a
43864b58:      	cmp	r2, #0x3
43864b5a:      	bne	0x43864b60 <_binary_input_a7s_av_cam_bin_start+0x323b60> @ imm = #0x2
43864b5c:      	str	r1, [r3, #0x5c]
43864b5e:      	b	0x43864b76 <_binary_input_a7s_av_cam_bin_start+0x323b76> @ imm = #0x14
43864b60:      	cmp	r2, #0x4
43864b62:      	beq	0x43864b74 <_binary_input_a7s_av_cam_bin_start+0x323b74> @ imm = #0xe
43864b64:      	cmp	r2, #0x5
43864b66:      	beq	0x43864b74 <_binary_input_a7s_av_cam_bin_start+0x323b74> @ imm = #0xa
43864b68:      	cmp	r2, #0x6
43864b6a:      	beq	0x43864b74 <_binary_input_a7s_av_cam_bin_start+0x323b74> @ imm = #0x6
43864b6c:      	cmp	r2, #0x7
43864b6e:      	ite	ne
43864b70:      	movne	r2, #0x1
43864b72:      	moveq	r2, #0x7
43864b74:      	str	r2, [r3, #0x5c]
43864b76:      	ldr	r3, [pc, #0xa4]         @ 0x43864c1c <_binary_input_a7s_av_cam_bin_start+0x323c1c>
43864b78:      	ldr	r1, [pc, #0xa4]         @ 0x43864c20 <_binary_input_a7s_av_cam_bin_start+0x323c20>
43864b7a:      	add	r3, pc
43864b7c:      	ldr	r1, [r4, r1]
43864b7e:      	ldrb.w	r2, [r3, #0x5c]
43864b82:      	strb.w	r2, [r1, #0x9ac]
43864b86:      	ldr	r1, [pc, #0x9c]         @ 0x43864c24 <_binary_input_a7s_av_cam_bin_start+0x323c24>
43864b88:      	ldr	r1, [r4, r1]
43864b8a:      	strb	r2, [r1]
43864b8c:      	ldr	r2, [pc, #0x98]         @ 0x43864c28 <_binary_input_a7s_av_cam_bin_start+0x323c28>
43864b8e:      	ldr.w	r1, [r7, #0x424]
43864b92:      	ldr	r2, [r4, r2]
43864b94:      	strb	r1, [r2]
43864b96:      	ldr	r2, [pc, #0x94]         @ 0x43864c2c <_binary_input_a7s_av_cam_bin_start+0x323c2c>
43864b98:      	ldrb.w	r1, [r3, #0x60]
43864b9c:      	ldrb.w	r3, [r3, #0x61]
43864ba0:      	ldr	r2, [r4, r2]
43864ba2:      	strb	r1, [r2]
43864ba4:      	ldr	r2, [pc, #0x88]         @ 0x43864c30 <_binary_input_a7s_av_cam_bin_start+0x323c30>
43864ba6:      	ldr	r2, [r4, r2]
43864ba8:      	strb	r3, [r2]
43864baa:      	pop.w	{r4, r5, r6, r7, r8, pc}
43864bae:      	nop
43864bb0:      	<unknown>
43864bb4:      	movs	r1, #0xe0
43864bb6:      	lsls	r2, r5, #0x1
43864bb8:      	movs	r1, #0xd8
43864bba:      	lsls	r2, r5, #0x1
43864bbc:      	movs	r1, #0xca
43864bbe:      	lsls	r2, r5, #0x1
43864bc0:      	strh	r0, [r5, #0x18]
43864bc2:      	movs	r0, r0
43864bc4:      	movs	r1, #0xaa
43864bc6:      	lsls	r2, r5, #0x1
43864bc8:      	movs	r1, #0xa4
43864bca:      	lsls	r2, r5, #0x1
43864bcc:      	movs	r1, #0x92
43864bce:      	lsls	r2, r5, #0x1
43864bd0:      	movs	r1, #0x8c
43864bd2:      	lsls	r2, r5, #0x1
43864bd4:      	movs	r1, #0x86
43864bd6:      	lsls	r2, r5, #0x1
43864bd8:      	movs	r1, #0x80
43864bda:      	lsls	r2, r5, #0x1
43864bdc:      	orrs	r4, r5
43864bde:      	movs	r0, r0
43864be0:      	movs	r1, #0x64
43864be2:      	lsls	r2, r5, #0x1
43864be4:      	movs	r1, #0x5a
43864be6:      	lsls	r2, r5, #0x1
43864be8:      	movs	r1, #0x4e
43864bea:      	lsls	r2, r5, #0x1
43864bec:      	movs	r1, #0x42
43864bee:      	lsls	r2, r5, #0x1
43864bf0:      	movs	r1, #0x36
43864bf2:      	lsls	r2, r5, #0x1
43864bf4:      	movs	r1, #0x2a
43864bf6:      	lsls	r2, r5, #0x1
43864bf8:      	movs	r1, #0x1e
43864bfa:      	lsls	r2, r5, #0x1
43864bfc:      	movs	r1, #0x12
43864bfe:      	lsls	r2, r5, #0x1
43864c00:      	movs	r1, #0xc
43864c02:      	lsls	r2, r5, #0x1
43864c04:      	movs	r0, #0xe8
43864c06:      	lsls	r2, r5, #0x1
43864c08:      	movs	r0, #0xda
43864c0a:      	lsls	r2, r5, #0x1
43864c0c:      	movs	r0, #0xd2
43864c0e:      	lsls	r2, r5, #0x1
43864c10:      	movs	r0, #0xb6
43864c12:      	lsls	r2, r5, #0x1
43864c14:      	movs	r0, #0x9e
43864c16:      	lsls	r2, r5, #0x1
43864c18:      	movs	r0, #0x8c
43864c1a:      	lsls	r2, r5, #0x1
43864c1c:      	movs	r0, #0x4a
43864c1e:      	lsls	r2, r5, #0x1
43864c20:      	ldrb	r4, [r6, #0x1d]
43864c22:      	movs	r0, r0
43864c24:      	str	r0, [r3, #0x64]
43864c26:      	movs	r0, r0
43864c28:      	adds	r2, #0x70
43864c2a:      	movs	r0, r0
43864c2c:      	str	r0, [r2, #0x10]
43864c2e:      	movs	r0, r0
43864c30:      	subs	r2, #0x50
43864c32:      	movs	r0, r0
43864c34:      	ldr	r3, [pc, #0x34]         @ 0x43864c6c <_binary_input_a7s_av_cam_bin_start+0x323c6c>
43864c36:      	mov	r1, r0
43864c38:      	push	{r4, lr}
43864c3a:      	add	r3, pc
43864c3c:      	ldrh	r2, [r3]
43864c3e:      	ldrb	r3, [r3, #0x2]
43864c40:      	strh	r2, [r0]
43864c42:      	movs	r2, #0x0
43864c44:      	strb	r3, [r1, #2]!
43864c48:      	ldr	r3, [pc, #0x24]         @ 0x43864c70 <_binary_input_a7s_av_cam_bin_start+0x323c70>
43864c4a:      	add	r3, pc
43864c4c:      	adds	r4, r3, r2
43864c4e:      	adds	r2, #0x2
43864c50:      	cmp	r2, #0x52
43864c52:      	ldrh	r4, [r4, #0x4]
43864c54:      	strh	r4, [r1, #2]!
43864c58:      	bne	0x43864c48 <_binary_input_a7s_av_cam_bin_start+0x323c48> @ imm = #-0x14
43864c5a:      	ldrh.w	r2, [r3, #0x56]
43864c5e:      	ldrh.w	r3, [r3, #0x58]
43864c62:      	strh.w	r2, [r0, #0x56]
43864c66:      	strh.w	r3, [r0, #0x58]
43864c6a:      	pop	{r4, pc}
43864c6c:      	subs	r2, r1, #0x6
43864c6e:      	lsls	r2, r5, #0x1
43864c70:      	subs	r2, r7, #0x5
43864c72:      	lsls	r2, r5, #0x1
43864c74:      	ldr	r3, [pc, #0x4]          @ 0x43864c7c <_binary_input_a7s_av_cam_bin_start+0x323c7c>
43864c76:      	add	r3, pc
43864c78:      	ldr	r0, [r3, #0x5c]
43864c7a:      	bx	lr
43864c7c:      	subs	r6, r1, #0x5
43864c7e:      	lsls	r2, r5, #0x1
43864c80:      	ldr	r3, [pc, #0x8]          @ 0x43864c8c <_binary_input_a7s_av_cam_bin_start+0x323c8c>
43864c82:      	add	r3, pc
43864c84:      	ldrh.w	r0, [r3, #0x5a]
43864c88:      	bx	lr
43864c8a:      	nop
43864c8c:      	subs	r2, r0, #0x5
43864c8e:      	lsls	r2, r5, #0x1
43864c90:      	ldr	r3, [pc, #0x8]          @ 0x43864c9c <_binary_input_a7s_av_cam_bin_start+0x323c9c>
43864c92:      	add	r3, pc
43864c94:      	ldrb.w	r0, [r3, #0x60]
43864c98:      	bx	lr
43864c9a:      	nop
43864c9c:      	subs	r2, r6, #0x4
43864c9e:      	lsls	r2, r5, #0x1
43864ca0:      	ldr	r3, [pc, #0x8]          @ 0x43864cac <_binary_input_a7s_av_cam_bin_start+0x323cac>
43864ca2:      	add	r3, pc
43864ca4:      	ldrb.w	r0, [r3, #0x61]
43864ca8:      	bx	lr
43864caa:      	nop
43864cac:      	subs	r2, r4, #0x4
43864cae:      	lsls	r2, r5, #0x1
43864cb0:      	ldr	r3, [pc, #0x1c8]        @ 0x43864e7c <_binary_input_a7s_av_cam_bin_start+0x323e7c>
43864cb2:      	push	{r4, r5, r6, lr}
43864cb4:      	add	r3, pc
43864cb6:      	cmp	r0, #0x0
43864cb8:      	beq.w	0x43864e78 <_binary_input_a7s_av_cam_bin_start+0x323e78> @ imm = #0x1bc
43864cbc:      	ldr	r2, [pc, #0x1c0]        @ 0x43864e80 <_binary_input_a7s_av_cam_bin_start+0x323e80>
43864cbe:      	add	r2, pc
43864cc0:      	adds	r5, r2, #0x2
43864cc2:      	ldrb	r1, [r2]
43864cc4:      	strb.w	r1, [r0, #0x6b]
43864cc8:      	ldrb	r1, [r2, #0x2]
43864cca:      	strb.w	r1, [r0, #0x6c]
43864cce:      	ldrb	r1, [r2, #0x3]
43864cd0:      	adds	r2, #0x20
43864cd2:      	strb.w	r1, [r0, #0x6d]
43864cd6:      	movs	r1, #0x0
43864cd8:      	add.w	r4, r1, #0x34
43864cdc:      	ldrb	r6, [r5, #2]!
43864ce0:      	add.w	r4, r0, r4, lsl #1
43864ce4:      	strb	r6, [r4, #0x6]
43864ce6:      	ldrb	r6, [r5, #0x1]
43864ce8:      	strb	r6, [r4, #0x7]
43864cea:      	add.w	r4, r1, #0x20
43864cee:      	ldrb	r6, [r2, #4]!
43864cf2:      	adds	r1, #0x1
43864cf4:      	add.w	r4, r0, r4, lsl #2
43864cf8:      	cmp	r1, #0xb
43864cfa:      	strb	r6, [r4, #0x4]
43864cfc:      	ldrb	r6, [r2, #0x1]
43864cfe:      	strb	r6, [r4, #0x5]
43864d00:      	ldrb	r6, [r2, #0x2]
43864d02:      	strb	r6, [r4, #0x6]
43864d04:      	ldrb	r6, [r2, #0x3]
43864d06:      	strb	r6, [r4, #0x7]
43864d08:      	bne	0x43864cd8 <_binary_input_a7s_av_cam_bin_start+0x323cd8> @ imm = #-0x34
43864d0a:      	ldr	r2, [pc, #0x178]        @ 0x43864e84 <_binary_input_a7s_av_cam_bin_start+0x323e84>
43864d0c:      	mov	r4, r0
43864d0e:      	add	r2, pc
43864d10:      	ldrb.w	r1, [r2, #0x64]
43864d14:      	strb.w	r1, [r0, #0xb0]
43864d18:      	ldrb.w	r1, [r2, #0x65]
43864d1c:      	strb.w	r1, [r0, #0xb1]
43864d20:      	ldrb.w	r1, [r2, #0x66]
43864d24:      	strb.w	r1, [r0, #0xb2]
43864d28:      	ldrb.w	r1, [r2, #0x67]
43864d2c:      	strb.w	r1, [r0, #0xb3]
43864d30:      	ldrb.w	r1, [r2, #0x68]
43864d34:      	strb.w	r1, [r0, #0xb4]
43864d38:      	ldrb.w	r1, [r2, #0x69]
43864d3c:      	strb.w	r1, [r0, #0xb5]
43864d40:      	ldrb.w	r1, [r2, #0x6c]
43864d44:      	strb.w	r1, [r0, #0xb6]
43864d48:      	ldrb.w	r1, [r2, #0x6d]
43864d4c:      	strb.w	r1, [r0, #0xb7]
43864d50:      	ldrb.w	r1, [r2, #0x6e]
43864d54:      	strb.w	r1, [r0, #0xb8]
43864d58:      	ldrb.w	r1, [r2, #0x6f]
43864d5c:      	strb.w	r1, [r0, #0xb9]
43864d60:      	ldrb.w	r1, [r2, #0x70]
43864d64:      	strb.w	r1, [r0, #0xba]
43864d68:      	ldrb.w	r1, [r2, #0x71]
43864d6c:      	strb.w	r1, [r0, #0xf2]
43864d70:      	ldrb.w	r1, [r2, #0x72]
43864d74:      	strb.w	r1, [r0, #0xf3]
43864d78:      	ldrb.w	r2, [r2, #0x73]
43864d7c:      	strb.w	r2, [r0, #0xf4]
43864d80:      	ldr	r2, [pc, #0x104]        @ 0x43864e88 <_binary_input_a7s_av_cam_bin_start+0x323e88>
43864d82:      	add	r2, pc
43864d84:      	ldrb	r1, [r2]
43864d86:      	strb.w	r1, [r0, #0xbb]
43864d8a:      	ldrb	r1, [r2, #0x1]
43864d8c:      	strb.w	r1, [r0, #0xbc]
43864d90:      	movs	r1, #0x0
43864d92:      	ldrb	r2, [r2, #0x2]
43864d94:      	strb.w	r2, [r0, #0xbf]
43864d98:      	ldr	r2, [pc, #0xf0]         @ 0x43864e8c <_binary_input_a7s_av_cam_bin_start+0x323e8c>
43864d9a:      	add	r2, pc
43864d9c:      	adds	r5, r2, r1
43864d9e:      	adds	r1, #0x2
43864da0:      	ldrh	r5, [r5, #0x4]
43864da2:      	strb.w	r5, [r4, #0xc0]
43864da6:      	adds	r4, #0x1
43864da8:      	cmp	r1, #0x52
43864daa:      	bne	0x43864d98 <_binary_input_a7s_av_cam_bin_start+0x323d98> @ imm = #-0x16
43864dac:      	ldrb.w	r1, [r2, #0x56]
43864db0:      	strb.w	r1, [r0, #0xe9]
43864db4:      	ldrb.w	r1, [r2, #0x57]
43864db8:      	strb.w	r1, [r0, #0xea]
43864dbc:      	ldrb.w	r1, [r2, #0x58]
43864dc0:      	strb.w	r1, [r0, #0xeb]
43864dc4:      	ldrb.w	r1, [r2, #0x59]
43864dc8:      	strb.w	r1, [r0, #0xec]
43864dcc:      	ldrb.w	r1, [r2, #0x5a]
43864dd0:      	strb.w	r1, [r0, #0xed]
43864dd4:      	ldrb.w	r1, [r2, #0x5b]
43864dd8:      	strb.w	r1, [r0, #0xee]
43864ddc:      	ldr	r2, [r2, #0x5c]
43864dde:      	cbz	r2, 0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0x1a
43864de0:      	cmp	r2, #0x1
43864de2:      	beq	0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0x16
43864de4:      	cmp	r2, #0x2
43864de6:      	beq	0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0x12
43864de8:      	cmp	r2, #0x3
43864dea:      	beq	0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0xe
43864dec:      	cmp	r2, #0x4
43864dee:      	beq	0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0xa
43864df0:      	cmp	r2, #0x5
43864df2:      	beq	0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0x6
43864df4:      	cmp	r2, #0x6
43864df6:      	beq	0x43864dfc <_binary_input_a7s_av_cam_bin_start+0x323dfc> @ imm = #0x2
43864df8:      	cmp	r2, #0x7
43864dfa:      	bne	0x43864e00 <_binary_input_a7s_av_cam_bin_start+0x323e00> @ imm = #0x2
43864dfc:      	adds	r2, #0x1
43864dfe:      	b	0x43864e02 <_binary_input_a7s_av_cam_bin_start+0x323e02> @ imm = #0x0
43864e00:      	movs	r2, #0xff
43864e02:      	strb.w	r2, [r0, #0xef]
43864e06:      	ldr	r2, [pc, #0x88]         @ 0x43864e90 <_binary_input_a7s_av_cam_bin_start+0x323e90>
43864e08:      	add	r2, pc
43864e0a:      	ldrb.w	r1, [r2, #0x60]
43864e0e:      	strb.w	r1, [r0, #0xf0]
43864e12:      	ldrb.w	r2, [r2, #0x61]
43864e16:      	strb.w	r2, [r0, #0xf1]
43864e1a:      	ldr	r2, [pc, #0x78]         @ 0x43864e94 <_binary_input_a7s_av_cam_bin_start+0x323e94>
43864e1c:      	ldr	r2, [r3, r2]
43864e1e:      	ldrb.w	r1, [r2, #0x100]
43864e22:      	strb.w	r1, [r0, #0x263]
43864e26:      	ldrb.w	r1, [r2, #0x101]
43864e2a:      	strb.w	r1, [r0, #0x264]
43864e2e:      	ldrb	r1, [r2, #0x12]
43864e30:      	strb.w	r1, [r0, #0x265]
43864e34:      	ldrb.w	r1, [r2, #0x197]
43864e38:      	strb.w	r1, [r0, #0x266]
43864e3c:      	ldr	r1, [pc, #0x58]         @ 0x43864e98 <_binary_input_a7s_av_cam_bin_start+0x323e98>
43864e3e:      	ldr	r3, [r3, r1]
43864e40:      	ldrb.w	r3, [r3, #0xde]
43864e44:      	strb.w	r3, [r0, #0x267]
43864e48:      	ldrb.w	r3, [r2, #0xc8]
43864e4c:      	strb.w	r3, [r0, #0x268]
43864e50:      	ldrb.w	r3, [r2, #0xc9]
43864e54:      	strb.w	r3, [r0, #0x269]
43864e58:      	ldrb.w	r3, [r2, #0xca]
43864e5c:      	strb.w	r3, [r0, #0x26a]
43864e60:      	ldrb.w	r3, [r2, #0xcb]
43864e64:      	strb.w	r3, [r0, #0x26b]
43864e68:      	ldrb.w	r3, [r2, #0xcc]
43864e6c:      	strb.w	r3, [r0, #0x26c]
43864e70:      	ldrb.w	r3, [r2, #0xcd]
43864e74:      	strb.w	r3, [r0, #0x26d]
43864e78:      	pop	{r4, r5, r6, pc}
43864e7a:      	nop
43864e7c:      	strb.w	r0, [r8, #0x7b]
43864e80:      	subs	r2, r5, #0x5
43864e82:      	lsls	r2, r5, #0x1
43864e84:      	subs	r2, r3, #0x4
43864e86:      	lsls	r2, r5, #0x1
43864e88:      	subs	r2, r0, #0x1
43864e8a:      	lsls	r2, r5, #0x1
43864e8c:      	subs	r2, r5, #0x0
43864e8e:      	lsls	r2, r5, #0x1
43864e90:      	adds	r4, r7, #0x6
43864e92:      	lsls	r2, r5, #0x1
43864e94:      	ldr	r4, [r2, #0x60]
43864e96:      	movs	r0, r0
43864e98:      	lsrs	r4, r4, #0x12
43864e9a:      	movs	r0, r0
43864e9c:      	ldr	r3, [pc, #0x3c]         @ 0x43864edc <_binary_input_a7s_av_cam_bin_start+0x323edc>
43864e9e:      	ldr	r2, [pc, #0x40]         @ 0x43864ee0 <_binary_input_a7s_av_cam_bin_start+0x323ee0>
43864ea0:      	add	r3, pc
43864ea2:      	push	{r4, r5, r6, r7, lr}
43864ea4:      	ldr	r3, [r3, r2]
43864ea6:      	mov	r2, r1
43864ea8:      	ldrh	r6, [r3, #0xa]
43864eaa:      	ldrh	r5, [r3, #0x4]
43864eac:      	ldrh	r3, [r3, #0x6]
43864eae:      	lsrs	r4, r6, #0x1
43864eb0:      	subs	r5, r5, r3
43864eb2:      	movs	r3, #0x0
43864eb4:      	subs	r7, r5, r4
43864eb6:      	b	0x43864ed6 <_binary_input_a7s_av_cam_bin_start+0x323ed6> @ imm = #0x1c
43864eb8:      	cbnz	r3, 0x43864ec8 <_binary_input_a7s_av_cam_bin_start+0x323ec8> @ imm = #0xc
43864eba:      	cmp	r5, r4
43864ebc:      	ite	ls
43864ebe:      	movls	r12, r3
43864ec0:      	movhi	r12, r7
43864ec2:      	str.w	r12, [r1]
43864ec6:      	b	0x43864ed2 <_binary_input_a7s_av_cam_bin_start+0x323ed2> @ imm = #0x8
43864ec8:      	ldr	r12, [r2, #-4]
43864ecc:      	add	r12, r6
43864ece:      	str.w	r12, [r2]
43864ed2:      	adds	r3, #0x1
43864ed4:      	adds	r2, #0x4
43864ed6:      	cmp	r3, r0
43864ed8:      	blt	0x43864eb8 <_binary_input_a7s_av_cam_bin_start+0x323eb8> @ imm = #-0x24
43864eda:      	pop	{r4, r5, r6, r7, pc}
43864edc:      	<unknown>
43864ee0:      	orrs	r4, r5
43864ee2:      	movs	r0, r0
43864ee4:      	push.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
43864ee8:      	sub	sp, #0x24
43864eea:      	ldr	r5, [pc, #0x114]        @ 0x43865000 <_binary_input_a7s_av_cam_bin_start+0x324000>
43864eec:      	movs	r6, #0x0
43864eee:      	str	r3, [sp, #0x1c]
43864ef0:      	ldr	r3, [pc, #0x110]        @ 0x43865004 <_binary_input_a7s_av_cam_bin_start+0x324004>
43864ef2:      	add	r5, pc
43864ef4:      	str	r1, [sp, #0x8]
43864ef6:      	str	r0, [sp, #0x18]
43864ef8:      	ldr	r3, [r5, r3]
43864efa:      	ldr.w	r8, [sp, #0x48]
43864efe:      	ldr.w	r9, [sp, #0x4c]
43864f02:      	ldrh	r1, [r3, #0x4]
43864f04:      	mov	r4, r8
43864f06:      	ldrh	r3, [r3, #0x8]
43864f08:      	mov	r8, r2
43864f0a:      	str	r6, [sp, #0x4]
43864f0c:      	str	r1, [sp, #0x14]
43864f0e:      	str	r3, [sp, #0x10]
43864f10:      	b	0x43864ff2 <_binary_input_a7s_av_cam_bin_start+0x323ff2> @ imm = #0xde
43864f12:      	ldr	r2, [r4], #4
43864f16:      	movs	r5, #0x0
43864f18:      	ldr	r3, [sp, #0x14]
43864f1a:      	subs	r7, r3, r2
43864f1c:      	str	r2, [sp, #0xc]
43864f1e:      	eor.w	r0, r7, r7, asr #31
43864f22:      	sub.w	r0, r0, r7, asr #31
43864f26:      	ldr	r1, [sp, #0x1c]
43864f28:      	subs	r3, r1, #0x2
43864f2a:      	cmp	r5, r3
43864f2c:      	bge	0x43864f3e <_binary_input_a7s_av_cam_bin_start+0x323f3e> @ imm = #0xe
43864f2e:      	ldr	r1, [sp, #0x8]
43864f30:      	adds	r3, r5, #0x1
43864f32:      	ldrh.w	r2, [r1, r3, lsl #1]
43864f36:      	cmp	r2, r0
43864f38:      	bhs	0x43864f3e <_binary_input_a7s_av_cam_bin_start+0x323f3e> @ imm = #0x2
43864f3a:      	uxth	r5, r3
43864f3c:      	b	0x43864f26 <_binary_input_a7s_av_cam_bin_start+0x323f26> @ imm = #-0x1a
43864f3e:      	ldr	r2, [sp, #0x8]
43864f40:      	add.w	r12, r5, #0x1
43864f44:      	ldr.w	r11, [r8, r12, lsl #2]
43864f48:      	ldrh.w	r3, [r2, r5, lsl #1]
43864f4c:      	ldrh.w	r1, [r2, r12, lsl #1]
43864f50:      	ldr.w	r5, [r8, r5, lsl #2]
43864f54:      	cmp	r1, r3
43864f56:      	bls	0x43864f5c <_binary_input_a7s_av_cam_bin_start+0x323f5c> @ imm = #0x2
43864f58:      	subs	r1, r1, r3
43864f5a:      	b	0x43864f60 <_binary_input_a7s_av_cam_bin_start+0x323f60> @ imm = #0x2
43864f5c:      	bhs	0x43864fa4 <_binary_input_a7s_av_cam_bin_start+0x323fa4> @ imm = #0x44
43864f5e:      	subs	r1, r3, r1
43864f60:      	subs	r0, r0, r3
43864f62:      	movw	r10, #0x2710
43864f66:      	uxth	r1, r1
43864f68:      	mul	r0, r10, r0
43864f6c:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x3070d8
43864f70:      	cmp	r11, r5
43864f72:      	bls	0x43864f8c <_binary_input_a7s_av_cam_bin_start+0x323f8c> @ imm = #0x16
43864f74:      	rsb	r11, r5, r11
43864f78:      	mov	r1, r10
43864f7a:      	mul	r0, r11, r0
43864f7e:      	add.w	r0, r0, #0x1380
43864f82:      	adds	r0, #0x8
43864f84:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x3070f0
43864f88:      	adds	r5, r5, r0
43864f8a:      	b	0x43864fa4 <_binary_input_a7s_av_cam_bin_start+0x323fa4> @ imm = #0x16
43864f8c:      	bhs	0x43864fa4 <_binary_input_a7s_av_cam_bin_start+0x323fa4> @ imm = #0x14
43864f8e:      	rsb	r11, r11, r5
43864f92:      	mov	r1, r10
43864f94:      	mul	r0, r11, r0
43864f98:      	add.w	r0, r0, #0x1380
43864f9c:      	adds	r0, #0x8
43864f9e:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x30710a
43864fa2:      	subs	r5, r5, r0
43864fa4:      	cbz	r5, 0x43864fce <_binary_input_a7s_av_cam_bin_start+0x323fce> @ imm = #0x26
43864fa6:      	cmp	r7, #0x0
43864fa8:      	ble	0x43864fb6 <_binary_input_a7s_av_cam_bin_start+0x323fb6> @ imm = #0xa
43864faa:      	ldr	r3, [sp, #0x10]
43864fac:      	mul	r0, r3, r7
43864fb0:      	add.w	r0, r0, r5, lsr #1
43864fb4:      	b	0x43864fc2 <_binary_input_a7s_av_cam_bin_start+0x323fc2> @ imm = #0xa
43864fb6:      	beq	0x43864fcc <_binary_input_a7s_av_cam_bin_start+0x323fcc> @ imm = #0x12
43864fb8:      	ldr	r1, [sp, #0x10]
43864fba:      	mul	r0, r1, r7
43864fbe:      	sub.w	r0, r0, r5, lsr #1
43864fc2:      	mov	r1, r5
43864fc4:      	bl	0x4355e110 <_binary_input_a7s_av_cam_bin_start+0x1d110> @ imm = #-0x306eb8
43864fc8:      	mov	r6, r0
43864fca:      	b	0x43864fce <_binary_input_a7s_av_cam_bin_start+0x323fce> @ imm = #0x0
43864fcc:      	mov	r6, r7
43864fce:      	ldr	r2, [sp, #0xc]
43864fd0:      	adds	r3, r6, r2
43864fd2:      	str	r3, [r9], #4
43864fd6:      	ldr.w	r3, [r8]
43864fda:      	cmp.w	r3, #0xffffffff
43864fde:      	bne	0x43864fea <_binary_input_a7s_av_cam_bin_start+0x323fea> @ imm = #0x8
43864fe0:      	ldr	r3, [r4, #-4]
43864fe4:      	movs	r6, #0x0
43864fe6:      	str	r3, [r9, #-4]
43864fea:      	ldr	r1, [sp, #0x4]
43864fec:      	adds	r3, r1, #0x1
43864fee:      	uxtb	r3, r3
43864ff0:      	str	r3, [sp, #0x4]
43864ff2:      	ldr	r2, [sp, #0x4]
43864ff4:      	ldr	r3, [sp, #0x18]
43864ff6:      	cmp	r2, r3
43864ff8:      	blo	0x43864f12 <_binary_input_a7s_av_cam_bin_start+0x323f12> @ imm = #-0xea
43864ffa:      	add	sp, #0x24
43864ffc:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, r11, pc}
43865000:      	movw	r0, #0xa87b
43865004:      	orrs	r4, r5
43865006:      	movs	r0, r0
43865008:      	ldr	r3, [pc, #0x54]         @ 0x43865060 <_binary_input_a7s_av_cam_bin_start+0x324060>
4386500a:      	push.w	{r4, r5, r6, r7, r8, r9, r10, lr}
4386500e:      	mov	r9, r2
43865010:      	ldr	r2, [pc, #0x50]         @ 0x43865064 <_binary_input_a7s_av_cam_bin_start+0x324064>
43865012:      	add	r3, pc
43865014:      	mov	r4, r0
43865016:      	mov	r5, r1
43865018:      	movs	r1, #0xa
4386501a:      	movs	r6, #0x0
4386501c:      	ldr	r3, [r3, r2]
4386501e:      	mov	r8, r6
43865020:      	ldrh	r2, [r3, #0x2]
43865022:      	ldrh	r0, [r3]
43865024:      	muls	r0, r2, r0
43865026:      	bl	0x4355e110 <_binary_input_a7s_av_cam_bin_start+0x1d110> @ imm = #-0x306f1a
4386502a:      	uxth	r7, r0
4386502c:      	asr.w	r10, r7, #0x1
43865030:      	b	0x43865056 <_binary_input_a7s_av_cam_bin_start+0x324056> @ imm = #0x22
43865032:      	subs	r3, r4, #0x1
43865034:      	cmp	r6, r3
43865036:      	bge	0x43865040 <_binary_input_a7s_av_cam_bin_start+0x324040> @ imm = #0x6
43865038:      	ldr	r2, [r5, #0x4]
4386503a:      	ldr	r3, [r5]
4386503c:      	rsb	r8, r3, r2
43865040:      	cbz	r7, 0x43865052 <_binary_input_a7s_av_cam_bin_start+0x324052> @ imm = #0xe
43865042:      	movs	r0, #0x64
43865044:      	mov	r1, r7
43865046:      	mla	r0, r0, r8, r10
4386504a:      	bl	0x4355de98 <_binary_input_a7s_av_cam_bin_start+0x1ce98> @ imm = #-0x3071b6
4386504e:      	strh.w	r0, [r9, r6, lsl #1]
43865052:      	adds	r6, #0x1
43865054:      	adds	r5, #0x4
43865056:      	cmp	r6, r4
43865058:      	blt	0x43865032 <_binary_input_a7s_av_cam_bin_start+0x324032> @ imm = #-0x2a
4386505a:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, pc}
4386505e:      	nop
