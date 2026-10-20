43862e24:      	push.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
43862e28:      	sub	sp, #0x94
43862e2a:      	ldr.w	r10, [pc, #0x87c]       @ 0x438636a8 
43862e2e:      	mov	r5, r0
43862e30:      	str	r3, [sp, #0x40]
43862e32:      	mov	r6, r1
43862e34:      	ldr.w	r3, [r1, #0x1b8]
43862e38:      	add	r10, pc
43862e3a:      	str	r2, [sp, #0x64]
43862e3c:      	ldr	r4, [sp, #0xb8]
43862e3e:      	ldr.w	r11, [sp, #0xbc]
43862e42:      	cbnz	r3, 0x43862e4a  @ imm = #0x4
43862e44:      	mov	r0, r11
43862e46:      	bl	0x437c66dc  @ imm = #-0x9c76e
43862e4a:      	ldr.w	r3, [pc, #0x860]        @ 0x438636ac 
43862e4e:      	ldr.w	r2, [r10, r3]
43862e52:      	ldrb	r3, [r2]
43862e54:      	str	r2, [sp, #0x54]
43862e56:      	cbnz	r3, 0x43862e64  @ imm = #0xa
43862e58:      	ldrb	r2, [r2, #0x15]
43862e5a:      	cmp	r2, #0x0
43862e5c:      	beq.w	0x438636a0  @ imm = #0x840
43862e60:      	str	r3, [sp, #0x44]
43862e62:      	b	0x43862e74  @ imm = #0xe
43862e64:      	cbz	r4, 0x43862e72  @ imm = #0xa
43862e66:      	ldr	r0, [sp, #0x40]
43862e68:      	subs	r0, #0x0
43862e6a:      	it	ne
43862e6c:      	movne	r0, #0x1
43862e6e:      	str	r0, [sp, #0x44]
43862e70:      	b	0x43862e74  @ imm = #0x0
43862e72:      	str	r4, [sp, #0x44]
43862e74:      	ldr.w	r1, [r6, #0x1b8]
43862e78:      	mov.w	r0, #0x384
43862e7c:      	bl	0x437e0550  @ imm = #-0x82930
43862e80:      	ldr.w	r3, [pc, #0x82c]        @ 0x438636b0 
43862e84:      	movs	r7, #0x0
43862e86:      	add	r3, pc
43862e88:      	strb	r7, [r3]
43862e8a:      	bl	0x437c3388  @ imm = #-0x9fb06
43862e8e:      	str	r0, [r5, #0x8]
43862e90:      	bl	0x437c3394  @ imm = #-0x9fb00
43862e94:      	ldr.w	r1, [r6, #0x1b8]
43862e98:      	str	r0, [r5, #0xc]
43862e9a:      	cbz	r1, 0x43862eb4  @ imm = #0x16
43862e9c:      	cmp.w	r11, #0x0
43862ea0:      	beq	0x43862eb8  @ imm = #0x14
43862ea2:      	ldr	r3, [r5, #0x8]
43862ea4:      	cmp	r3, #0x11
43862ea6:      	bne	0x43862eba  @ imm = #0x10
43862ea8:      	ldr.w	r7, [r11, #0xb78]
43862eac:      	subs	r7, r0, r7
43862eae:      	it	ne
43862eb0:      	movne	r7, #0x1
43862eb2:      	b	0x43862eba  @ imm = #0x4
43862eb4:      	movs	r7, #0x1
43862eb6:      	b	0x43862eba  @ imm = #0x0
43862eb8:      	mov	r7, r11
43862eba:      	adds	r2, r5, #0x4
43862ebc:      	mov	r3, r11
43862ebe:      	strb	r7, [r5, #0x10]
43862ec0:      	ldr.w	r0, [r6, #0x1c0]
43862ec4:      	bl	0x43862d80  @ imm = #-0x148
43862ec8:      	ldr.w	r1, [r6, #0x1b8]
43862ecc:      	ldr.w	r0, [r6, #0x1c0]
43862ed0:      	bl	0x43862034  @ imm = #-0xea0
43862ed4:      	ldr.w	r1, [r6, #0x1b8]
43862ed8:      	mov	r7, r0
43862eda:      	ldr.w	r0, [r6, #0x1c0]
43862ede:      	bl	0x43861fb0  @ imm = #-0xf32
43862ee2:      	ldr.w	r1, [r6, #0x1b8]
43862ee6:      	mov	r9, r0
43862ee8:      	ldr.w	r0, [r6, #0x1c0]
43862eec:      	bl	0x43861f2c  @ imm = #-0xfc4
43862ef0:      	ldr.w	r1, [r6, #0x1b8]
43862ef4:      	str	r0, [sp, #0x48]
43862ef6:      	ldr.w	r0, [r6, #0x1c0]
43862efa:      	bl	0x43861f84  @ imm = #-0xf7a
43862efe:      	ldr.w	r1, [r6, #0x1b8]
43862f02:      	str	r0, [sp, #0x60]
43862f04:      	ldr.w	r0, [r6, #0x1c0]
43862f08:      	bl	0x43862060  @ imm = #-0xeac
43862f0c:      	ldr.w	r3, [r6, #0x1c0]
43862f10:      	mov	r2, r7
43862f12:      	mov	r1, r9
43862f14:      	str.w	r3, [r7, #0x294]
43862f18:      	ldr.w	r3, [r6, #0x76c]
43862f1c:      	str.w	r3, [r7, #0x404]
43862f20:      	str	r0, [sp, #0x5c]
43862f22:      	ldr	r0, [sp, #0x48]
43862f24:      	bl	0x437cb5c0  @ imm = #-0x97968
43862f28:      	mov	r0, r7
43862f2a:      	mov	r1, r9
43862f2c:      	bl	0x437d0544  @ imm = #-0x929ec
43862f30:      	mov	r1, r9
43862f32:      	mov	r0, r7
43862f34:      	bl	0x437cf8e4  @ imm = #-0x93654
43862f38:      	mov	r0, r6
43862f3a:      	bl	0x437def7c  @ imm = #-0x83fc2
43862f3e:      	mov	r0, r6
43862f40:      	bl	0x43af5a7c  @ imm = #0x292b38
43862f44:      	ldr	r2, [sp, #0x44]
43862f46:      	cbnz	r2, 0x43862f54  @ imm = #0xa
43862f48:      	ldr.w	r3, [pc, #0x768]        @ 0x438636b4 
43862f4c:      	strb	r2, [r5, #0x6]
43862f4e:      	strb	r2, [r5, #0x5]
43862f50:      	add	r3, pc
43862f52:      	b	0x43862f90  @ imm = #0x3a
43862f54:      	ldr	r0, [sp, #0x40]
43862f56:      	ldrb	r3, [r0, #0x1]
43862f58:      	and	r3, r3, #0x1
43862f5c:      	strb	r3, [r5, #0x6]
43862f5e:      	ldr.w	r3, [pc, #0x758]        @ 0x438636b8 
43862f62:      	ldr.w	r3, [r10, r3]
43862f66:      	ldrb	r3, [r3]
43862f68:      	cbnz	r3, 0x43862f70  @ imm = #0x4
43862f6a:      	ldr	r1, [sp, #0x40]
43862f6c:      	ldrb	r3, [r1, #0x1]
43862f6e:      	lsrs	r3, r3, #0x6
43862f70:      	ldr	r2, [sp, #0x40]
43862f72:      	strb	r3, [r5, #0x5]
43862f74:      	ldr	r0, [sp, #0x40]
43862f76:      	ldrb	r1, [r2, #0x5]
43862f78:      	ldrb	r2, [r2, #0x4]
43862f7a:      	ldr.w	r3, [pc, #0x740]        @ 0x438636bc 
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
43862fa6:      	ldr.w	r3, [pc, #0x718]        @ 0x438636c0 
43862faa:      	ldr.w	r12, [r10, r3]
43862fae:      	ldr.w	r3, [pc, #0x714]        @ 0x438636c4 
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
43862fce:      	bl	0x437e3500  @ imm = #-0x7fad2
43862fd2:      	strb.w	r8, [r5, #0x33a]
43862fd6:      	strb.w	r8, [r5, #0x34a]
43862fda:      	bl	0x437436b8  @ imm = #-0x11f926
43862fde:      	ldr.w	r12, [sp, #0x38]
43862fe2:      	str.w	r12, [sp, #0x58]
43862fe6:      	cbz	r0, 0x43862ff2  @ imm = #0x8
43862fe8:      	add	r0, sp, #0x68
43862fea:      	strb.w	r8, [sp, #0x83]
43862fee:      	bl	0x438f0580  @ imm = #0x8d58e
43862ff2:      	ldr	r3, [sp, #0x3c]
43862ff4:      	mov	r2, r6
43862ff6:      	mov	r0, r5
43862ff8:      	mov	r1, r11
43862ffa:      	str	r7, [sp]
43862ffc:      	str	r3, [sp, #0x4]
43862ffe:      	ldr	r3, [sp, #0x40]
43863000:      	bl	0x437e3318  @ imm = #-0x7fcec
43863004:      	ldrb.w	r1, [r5, #0x2c2]
43863008:      	mov	r0, r7
4386300a:      	bl	0x43848f74  @ imm = #-0x1a09a
4386300e:      	movs	r1, #0x0
43863010:      	movs	r2, #0x28
43863012:      	strb.w	r0, [r7, #0x3dc]
43863016:      	add	r0, sp, #0x68
43863018:      	blx	0x439b3ffc  @ imm = #0x150fe0
4386301c:      	ldr.w	r3, [r7, #0x294]
43863020:      	cmp	r3, #0x9
43863022:      	beq	0x43863042  @ imm = #0x1c
43863024:      	ldr	r0, [sp, #0x3c]
43863026:      	ldrb.w	r2, [r0, #0x124]
4386302a:      	cmp	r2, #0x1
4386302c:      	beq	0x43863042  @ imm = #0x12
4386302e:      	cmp	r3, #0x12
43863030:      	bne	0x4386303a  @ imm = #0x6
43863032:      	ldr.w	r3, [r7, #0x65c]
43863036:      	cmp	r3, #0x5
43863038:      	beq	0x43863042  @ imm = #0x6
4386303a:      	ldr	r1, [sp, #0x3c]
4386303c:      	ldrb	r3, [r1, #0x2]
4386303e:      	strb.w	r3, [sp, #0x82]
43863042:      	add	r0, sp, #0x68
43863044:      	bl	0x438f055c  @ imm = #0x8d514
43863048:      	ldr	r1, [sp, #0x3c]
4386304a:      	mov	r0, r7
4386304c:      	bl	0x4386208c  @ imm = #-0xfc4
43863050:      	ldr	r1, [sp, #0x4c]
43863052:      	mov	r2, r7
43863054:      	bl	0x43861cc4  @ imm = #-0x1394
43863058:      	ldr	r2, [sp, #0x3c]
4386305a:      	ldr.w	r3, [pc, #0x66c]        @ 0x438636c8 
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
4386307c:      	bl	0x437c7000  @ imm = #-0x9c080
43863080:      	mov	r0, r6
43863082:      	bl	0x43aee5b8  @ imm = #0x28b532
43863086:      	mov	r1, r0
43863088:      	mov	r0, r9
4386308a:      	bl	0x43b0b994  @ imm = #0x2a8906
4386308e:      	ldr	r3, [sp, #0x54]
43863090:      	ldrb.w	r8, [r3, #0x15]
43863094:      	cmp.w	r8, #0x0
43863098:      	bne	0x438630c0  @ imm = #0x24
4386309a:      	ldrh.w	r3, [r6, #0x1b8]
4386309e:      	mov	r1, r9
438630a0:      	mov	r2, r7
438630a2:      	ldr	r0, [sp, #0x58]
438630a4:      	str	r3, [sp]
438630a6:      	ldr	r3, [sp, #0x3c]
438630a8:      	bl	0x438649bc  @ imm = #0x1910
438630ac:      	ldrh.w	r0, [r9, #0x162]
438630b0:      	bl	0x43adbfdc  @ imm = #0x278f28
438630b4:      	mov	r0, r5
438630b6:      	ldr.w	r1, [r6, #0x1b8]
438630ba:      	mov	r2, r8
438630bc:      	bl	0x43861a58  @ imm = #-0x1668
438630c0:      	ldr.w	r3, [pc, #0x608]        @ 0x438636cc 
438630c4:      	mov	r0, r6
438630c6:      	str.w	r11, [sp]
438630ca:      	mov	r1, r7
438630cc:      	ldr	r2, [sp, #0x3c]
438630ce:      	ldr.w	r8, [r10, r3]
438630d2:      	mov	r3, r8
438630d4:      	bl	0x437e3424  @ imm = #-0x7fcb4
438630d8:      	ldrb.w	r3, [r8]
438630dc:      	cmp	r3, #0x1
438630de:      	str	r0, [r5, #0x14]
438630e0:      	bne	0x4386311a  @ imm = #0x36
438630e2:      	ldrh.w	r0, [r9, #0x162]
438630e6:      	ldrh.w	r1, [r9, #0x140]
438630ea:      	strh.w	r0, [r5, #0x2d2]
438630ee:      	mov	r0, r7
438630f0:      	strh.w	r1, [r5, #0x4a2]
438630f4:      	bl	0x437e5080  @ imm = #-0x7e078
438630f8:      	mov	r1, r8
438630fa:      	mov	r2, r0
438630fc:      	ldr	r0, [sp, #0x4c]
438630fe:      	bl	0x43b0d45e  @ imm = #0x2aa35c
43863102:      	ldrh.w	r2, [r8, #0x8]
43863106:      	ldrh.w	r3, [r8, #0xa]
4386310a:      	ldrh.w	r0, [r8, #0xc]
4386310e:      	strh.w	r2, [r5, #0x4d6]
43863112:      	strh.w	r3, [r5, #0x4d8]
43863116:      	strh.w	r0, [r5, #0x4da]
4386311a:      	ldr	r1, [sp, #0x44]
4386311c:      	cmp	r1, #0x1
4386311e:      	bne.w	0x438633ac  @ imm = #0x28a
43863122:      	movs	r3, #0x0
43863124:      	strb	r3, [r4]
43863126:      	ldrh.w	r2, [r7, #0x4c4]
4386312a:      	ands	r2, r2, #0x20
4386312e:      	beq	0x43863140  @ imm = #0xe
43863130:      	ldr.w	r2, [pc, #0x59c]        @ 0x438636d0 
43863134:      	add	r2, pc
43863136:      	ldrb	r2, [r2]
43863138:      	cmp	r2, #0x1
4386313a:      	bne	0x43863174  @ imm = #0x36
4386313c:      	adds	r3, #0x40
4386313e:      	b	0x43863174  @ imm = #0x32
43863140:      	ldr.w	r3, [pc, #0x590]        @ 0x438636d4 
43863144:      	add	r3, pc
43863146:      	ldr	r3, [r3]
43863148:      	cmp	r3, #0x1
4386314a:      	bne	0x4386315c  @ imm = #0xe
4386314c:      	ldr.w	r3, [pc, #0x588]        @ 0x438636d8 
43863150:      	add	r3, pc
43863152:      	ldrb	r3, [r3]
43863154:      	cmp	r3, #0x1
43863156:      	bne	0x43863178  @ imm = #0x1e
43863158:      	adds	r3, #0x3f
4386315a:      	b	0x43863174  @ imm = #0x16
4386315c:      	cmp	r3, #0x3
4386315e:      	beq	0x43863162  @ imm = #0x0
43863160:      	cbnz	r3, 0x43863178  @ imm = #0x14
43863162:      	ldr.w	r3, [pc, #0x578]        @ 0x438636dc 
43863166:      	add	r3, pc
43863168:      	ldrb	r3, [r3]
4386316a:      	cmp	r3, #0x1
4386316c:      	bne	0x43863172  @ imm = #0x2
4386316e:      	adds	r3, #0x41
43863170:      	b	0x43863174  @ imm = #0x0
43863172:      	movs	r3, #0x2
43863174:      	strb	r3, [r4, #0x1]
43863176:      	b	0x4386317a  @ imm = #0x0
43863178:      	strb	r2, [r4, #0x1]
4386317a:      	ldr	r2, [sp, #0x3c]
4386317c:      	ldrb	r3, [r2, #0x2]
4386317e:      	cmp	r3, #0x1
43863180:      	bne	0x43863188  @ imm = #0x4
43863182:      	ldrb	r3, [r4, #0x1]
43863184:      	adds	r3, #0x14
43863186:      	strb	r3, [r4, #0x1]
43863188:      	ldr	r3, [r5, #0x14]
4386318a:      	subs	r3, #0x1
4386318c:      	cmp	r3, #0x2
4386318e:      	bhi	0x43863198  @ imm = #0x6
43863190:      	ldrb	r3, [r4, #0x1]
43863192:      	orn	r3, r3, #0x7f
43863196:      	strb	r3, [r4, #0x1]
43863198:      	ldrh.w	r0, [r9, #0x166]
4386319c:      	bl	0x4384b23c  @ imm = #-0x17f64
438631a0:      	cmp	r0, #0x1
438631a2:      	bne	0x438631aa  @ imm = #0x4
438631a4:      	movs	r3, #0x0
438631a6:      	strb	r3, [r4, #0x2]
438631a8:      	b	0x438631b6  @ imm = #0xa
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
438631cc:      	bne	0x43863210  @ imm = #0x40
438631ce:      	add.w	r3, r6, #0x1480
438631d2:      	ldrb	r0, [r3, #0x18]
438631d4:      	bl	0x43aeef7c  @ imm = #0x28bda4
438631d8:      	cmp	r0, #0x1
438631da:      	bne	0x43863200  @ imm = #0x22
438631dc:      	ldr.w	r2, [r7, #0x428]
438631e0:      	cmp	r2, #0x4
438631e2:      	bhi	0x438631ee  @ imm = #0x8
438631e4:      	ldr.w	r3, [pc, #0x4f8]        @ 0x438636e0 
438631e8:      	add	r3, pc
438631ea:      	ldrb	r3, [r3, r2]
438631ec:      	b	0x438631f0  @ imm = #0x0
438631ee:      	movs	r3, #0x0
438631f0:      	ldr	r1, [sp, #0x3c]
438631f2:      	ldrb.w	r2, [r1, #0xff]
438631f6:      	cmp	r2, r3
438631f8:      	bls	0x43863210  @ imm = #0x14
438631fa:      	subs	r3, r2, r3
438631fc:      	uxtb	r3, r3
438631fe:      	b	0x43863216  @ imm = #0x14
43863200:      	ldr	r3, [r5, #0x14]
43863202:      	cbnz	r3, 0x43863210  @ imm = #0xa
43863204:      	cmp.w	r11, #0x0
43863208:      	beq	0x43863214  @ imm = #0x8
4386320a:      	ldrb.w	r3, [r11, #0x4ba]
4386320e:      	b	0x43863216  @ imm = #0x4
43863210:      	movs	r3, #0x0
43863212:      	b	0x43863216  @ imm = #0x0
43863214:      	mov	r3, r11
43863216:      	strb	r3, [r4, #0x6]
43863218:      	ldrb.w	r3, [r8]
4386321c:      	cmp	r3, #0x1
4386321e:      	bne	0x4386322a  @ imm = #0x8
43863220:      	ldrh.w	r0, [r8, #0x8]
43863224:      	bl	0x43b08f58  @ imm = #0x2a5d30
43863228:      	strb	r0, [r4, #0x6]
4386322a:      	movs	r3, #0xa0
4386322c:      	strb	r3, [r4, #0x8]
4386322e:      	ldr.w	r3, [pc, #0x4b4]        @ 0x438636e4 
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
4386324c:      	beq	0x43863264  @ imm = #0x14
4386324e:      	ldrh	r1, [r7]
43863250:      	movw	r2, #0x313
43863254:      	cmp	r1, r2
43863256:      	beq	0x43863264  @ imm = #0xa
43863258:      	ldr.w	r2, [r6, #0x76c]
4386325c:      	cmp	r2, #0x2
4386325e:      	it	eq
43863260:      	moveq	r3, #0x2
43863262:      	b	0x43863266  @ imm = #0x0
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
4386328c:      	ldr.w	r3, [pc, #0x458]        @ 0x438636e8 
43863290:      	ldr.w	r2, [r10, r3]
43863294:      	ldrb	r3, [r2]
43863296:      	cmp	r3, #0x0
43863298:      	bne	0x43863398  @ imm = #0xfc
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
438632c4:      	bhi	0x43863322  @ imm = #0x5a
438632c6:      	cmp	r2, #0x1
438632c8:      	ldrh.w	r0, [r8, #0xc]
438632cc:      	bne	0x43863306  @ imm = #0x36
438632ce:      	ldrh.w	r1, [r5, #0x2d4]
438632d2:      	bl	0x43b0903c  @ imm = #0x2a5d66
438632d6:      	ldrb.w	r3, [r8, #0x10]
438632da:      	subs	r3, r0, r3
438632dc:      	strb	r3, [r4, #0x13]
438632de:      	ldrh.w	r1, [r5, #0x2d4]
438632e2:      	ldrh.w	r0, [r8, #0x8]
438632e6:      	bl	0x43b0903c  @ imm = #0x2a5d52
438632ea:      	ldrb.w	r3, [r8, #0x10]
438632ee:      	subs	r3, r0, r3
438632f0:      	strb	r3, [r4, #0x14]
438632f2:      	ldrh.w	r0, [r8, #0xa]
438632f6:      	ldrh.w	r1, [r5, #0x2d4]
438632fa:      	bl	0x43b0903c  @ imm = #0x2a5d3e
438632fe:      	ldrb.w	r3, [r8, #0x10]
43863302:      	subs	r3, r0, r3
43863304:      	b	0x438633aa  @ imm = #0xa2
43863306:      	bl	0x43b08f58  @ imm = #0x2a5c4e
4386330a:      	strb	r0, [r4, #0x13]
4386330c:      	ldrh.w	r0, [r8, #0x8]
43863310:      	bl	0x43b08f58  @ imm = #0x2a5c44
43863314:      	strb	r0, [r4, #0x14]
43863316:      	ldrh.w	r0, [r8, #0xa]
4386331a:      	bl	0x43b08f58  @ imm = #0x2a5c3a
4386331e:      	strb	r0, [r4, #0x15]
43863320:      	b	0x438633ac  @ imm = #0x88
43863322:      	subs	r1, #0x14
43863324:      	cmp	r1, #0x3
43863326:      	bhi	0x4386336e  @ imm = #0x44
43863328:      	cmp	r2, #0x1
4386332a:      	ldrh.w	r0, [r8, #0xa]
4386332e:      	bne	0x43863358  @ imm = #0x26
43863330:      	ldrh.w	r1, [r5, #0x2d4]
43863334:      	str	r3, [sp, #0x38]
43863336:      	bl	0x43b0903c  @ imm = #0x2a5d02
4386333a:      	ldrb.w	r2, [r8, #0x10]
4386333e:      	subs	r2, r0, r2
43863340:      	strb	r2, [r4, #0x13]
43863342:      	ldrh.w	r0, [r8, #0x8]
43863346:      	ldrh.w	r1, [r5, #0x2d4]
4386334a:      	bl	0x43b0903c  @ imm = #0x2a5cee
4386334e:      	ldrb.w	r2, [r8, #0x10]
43863352:      	subs	r2, r0, r2
43863354:      	strb	r2, [r4, #0x14]
43863356:      	b	0x4386336a  @ imm = #0x10
43863358:      	str	r3, [sp, #0x38]
4386335a:      	bl	0x43b08f58  @ imm = #0x2a5bfa
4386335e:      	strb	r0, [r4, #0x13]
43863360:      	ldrh.w	r0, [r8, #0x8]
43863364:      	bl	0x43b08f58  @ imm = #0x2a5bf0
43863368:      	strb	r0, [r4, #0x14]
4386336a:      	ldr	r3, [sp, #0x38]
4386336c:      	b	0x438633aa  @ imm = #0x3a
4386336e:      	cmp	r2, #0x1
43863370:      	ldrh.w	r0, [r8, #0x8]
43863374:      	bne	0x4386338a  @ imm = #0x12
43863376:      	ldrh.w	r1, [r5, #0x2d4]
4386337a:      	str	r3, [sp, #0x38]
4386337c:      	bl	0x43b0903c  @ imm = #0x2a5cbc
43863380:      	ldrb.w	r2, [r8, #0x10]
43863384:      	subs	r2, r0, r2
43863386:      	strb	r2, [r4, #0x13]
43863388:      	b	0x43863392  @ imm = #0x6
4386338a:      	str	r3, [sp, #0x38]
4386338c:      	bl	0x43b08f58  @ imm = #0x2a5bc8
43863390:      	strb	r0, [r4, #0x13]
43863392:      	ldr	r3, [sp, #0x38]
43863394:      	strb	r3, [r4, #0x14]
43863396:      	b	0x438633aa  @ imm = #0x10
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
438633b0:      	bl	0x4384aed4  @ imm = #-0x184e0
438633b4:      	ldr	r3, [pc, #0x334]        @ 0x438636ec 
438633b6:      	ldr	r2, [sp, #0x3c]
438633b8:      	add	r3, pc
438633ba:      	ldrb	r1, [r2, #0x2]
438633bc:      	subs	r1, #0x0
438633be:      	it	ne
438633c0:      	movne	r1, #0x1
438633c2:      	str	r0, [r3]
438633c4:      	mov	r0, r7
438633c6:      	ldr	r3, [pc, #0x328]        @ 0x438636f0 
438633c8:      	ldr.w	r8, [r10, r3]
438633cc:      	ldrh.w	r3, [r9, #0x168]
438633d0:      	ldrh.w	r2, [r8, #0x9a]
438633d4:      	bl	0x4384a138  @ imm = #-0x192a0
438633d8:      	str.w	r8, [sp, #0x5c]
438633dc:      	str.w	r0, [r5, #0x184]
438633e0:      	cmp.w	r11, #0x0
438633e4:      	beq	0x438633f0  @ imm = #0x8
438633e6:      	ldr.w	r3, [r6, #0x1b8]
438633ea:      	cbnz	r3, 0x438633f0  @ imm = #0x2
438633ec:      	str.w	r0, [r11, #0xb84]
438633f0:      	ldr.w	r1, [r6, #0x1b8]
438633f4:      	ldr.w	r0, [r6, #0x1c0]
438633f8:      	bl	0x43861f58  @ imm = #-0x14a4
438633fc:      	movs	r1, #0x0
438633fe:      	mov.w	r2, #0x154
