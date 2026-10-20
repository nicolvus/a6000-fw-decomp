43841070:      	push.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
43841074:      	sub	sp, #0xa4
43841076:      	ldr.w	r8, [pc, #0x85c]        @ 0x438418d4 
4384107a:      	mov	r6, r0
4384107c:      	str	r3, [sp, #0x40]
4384107e:      	mov	r7, r1
43841080:      	ldr.w	r3, [r1, #0x1b8]
43841084:      	add	r8, pc
43841086:      	str	r2, [sp, #0x60]
43841088:      	ldr	r4, [sp, #0xc8]
4384108a:      	ldr.w	r11, [sp, #0xcc]
4384108e:      	cbnz	r3, 0x43841096  @ imm = #0x4
43841090:      	mov	r0, r11
43841092:      	bl	0x437b3a24  @ imm = #-0x8d672
43841096:      	ldr.w	r3, [pc, #0x840]        @ 0x438418d8 
4384109a:      	ldr.w	r2, [r8, r3]
4384109e:      	ldrb	r3, [r2]
438410a0:      	str	r2, [sp, #0x48]
438410a2:      	cbnz	r3, 0x438410b0  @ imm = #0xa
438410a4:      	ldrb	r2, [r2, #0x15]
438410a6:      	cmp	r2, #0x0
438410a8:      	beq.w	0x43841a92  @ imm = #0x9e6
438410ac:      	str	r3, [sp, #0x44]
438410ae:      	b	0x438410c0  @ imm = #0xe
438410b0:      	cbz	r4, 0x438410be  @ imm = #0xa
438410b2:      	ldr	r0, [sp, #0x40]
438410b4:      	subs	r0, #0x0
438410b6:      	it	ne
438410b8:      	movne	r0, #0x1
438410ba:      	str	r0, [sp, #0x44]
438410bc:      	b	0x438410c0  @ imm = #0x0
438410be:      	str	r4, [sp, #0x44]
438410c0:      	ldr.w	r1, [r7, #0x1b8]
438410c4:      	mov.w	r0, #0x384
438410c8:      	bl	0x43857f40  @ imm = #0x16e74
438410cc:      	ldr.w	r3, [pc, #0x80c]        @ 0x438418dc 
438410d0:      	movs	r5, #0x0
438410d2:      	add	r3, pc
438410d4:      	strb	r5, [r3]
438410d6:      	bl	0x437b0604  @ imm = #-0x90ad6
438410da:      	str	r0, [r6, #0x8]
438410dc:      	bl	0x437b0610  @ imm = #-0x90ad0
438410e0:      	ldr.w	r1, [r7, #0x1b8]
438410e4:      	str	r0, [r6, #0xc]
438410e6:      	cbz	r1, 0x43841100  @ imm = #0x16
438410e8:      	cmp.w	r11, #0x0
438410ec:      	beq	0x43841104  @ imm = #0x14
438410ee:      	ldr	r3, [r6, #0x8]
438410f0:      	cmp	r3, #0x11
438410f2:      	bne	0x43841106  @ imm = #0x10
438410f4:      	ldr.w	r5, [r11, #0xb6c]
438410f8:      	subs	r5, r0, r5
438410fa:      	it	ne
438410fc:      	movne	r5, #0x1
438410fe:      	b	0x43841106  @ imm = #0x4
43841100:      	movs	r5, #0x1
43841102:      	b	0x43841106  @ imm = #0x0
43841104:      	mov	r5, r11
43841106:      	adds	r2, r6, #0x4
43841108:      	mov	r3, r11
4384110a:      	ldr.w	r0, [r7, #0x1c0]
4384110e:      	strb	r5, [r6, #0x10]
43841110:      	bl	0x438408b8  @ imm = #-0x85c
43841114:      	ldr.w	r1, [r7, #0x1b8]
43841118:      	ldr.w	r0, [r7, #0x1c0]
4384111c:      	bl	0x4383fc48  @ imm = #-0x14d8
43841120:      	ldr.w	r1, [r7, #0x1b8]
43841124:      	mov	r9, r0
43841126:      	ldr.w	r0, [r7, #0x1c0]
4384112a:      	bl	0x4383fbc4  @ imm = #-0x156a
4384112e:      	ldr.w	r1, [r7, #0x1b8]
43841132:      	mov	r10, r0
43841134:      	ldr.w	r0, [r7, #0x1c0]
43841138:      	bl	0x4383fb40  @ imm = #-0x15fc
4384113c:      	ldr.w	r1, [r7, #0x1b8]
43841140:      	str	r0, [sp, #0x4c]
43841142:      	ldr.w	r0, [r7, #0x1c0]
43841146:      	bl	0x4383fb98  @ imm = #-0x15b2
4384114a:      	ldr.w	r1, [r7, #0x1b8]
4384114e:      	str	r0, [sp, #0x64]
43841150:      	ldr.w	r0, [r7, #0x1c0]
43841154:      	bl	0x4383fc74  @ imm = #-0x14e4
43841158:      	ldr.w	r3, [r7, #0x1c0]
4384115c:      	mov	r1, r10
4384115e:      	mov	r2, r9
43841160:      	str.w	r3, [r9, #0x294]
43841164:      	str	r0, [sp, #0x54]
43841166:      	ldr	r0, [sp, #0x4c]
43841168:      	bl	0x43844df8  @ imm = #0x3c8c
4384116c:      	mov	r0, r7
4384116e:      	bl	0x43859a78  @ imm = #0x18906
43841172:      	mov	r0, r7
43841174:      	bl	0x43af51c8  @ imm = #0x2b4050
43841178:      	ldr	r1, [sp, #0x44]
4384117a:      	cbnz	r1, 0x4384118a  @ imm = #0xc
4384117c:      	ldr.w	r3, [pc, #0x760]        @ 0x438418e0 
43841180:      	strb	r1, [r6, #0x6]
43841182:      	add	r3, pc
43841184:      	strb	r1, [r6, #0x5]
43841186:      	str	r1, [r3]
43841188:      	b	0x438411c8  @ imm = #0x3c
4384118a:      	ldr	r2, [sp, #0x40]
4384118c:      	ldrb	r3, [r2, #0x1]
4384118e:      	and	r3, r3, #0x1
43841192:      	strb	r3, [r6, #0x6]
43841194:      	ldr.w	r3, [pc, #0x74c]        @ 0x438418e4 
43841198:      	ldr.w	r3, [r8, r3]
4384119c:      	ldrb	r3, [r3]
4384119e:      	cbnz	r3, 0x438411a6  @ imm = #0x4
438411a0:      	ldr	r0, [sp, #0x40]
438411a2:      	ldrb	r3, [r0, #0x1]
438411a4:      	lsrs	r3, r3, #0x6
438411a6:      	ldr	r2, [sp, #0x40]
438411a8:      	strb	r3, [r6, #0x5]
438411aa:      	ldr	r0, [sp, #0x40]
438411ac:      	ldrb	r1, [r2, #0x5]
438411ae:      	ldrb	r2, [r2, #0x4]
438411b0:      	ldr.w	r3, [pc, #0x734]        @ 0x438418e8 
438411b4:      	lsls	r1, r1, #0x18
438411b6:      	lsls	r2, r2, #0x10
438411b8:      	add	r3, pc
438411ba:      	adds	r1, r1, r2
438411bc:      	ldrb	r2, [r0, #0x2]
438411be:      	adds	r1, r1, r2
438411c0:      	ldrb	r2, [r0, #0x3]
438411c2:      	lsls	r2, r2, #0x8
438411c4:      	adds	r2, r1, r2
438411c6:      	str	r2, [r3]
438411c8:      	ldr.w	r3, [pc, #0x720]        @ 0x438418ec 
438411cc:      	movs	r5, #0x0
438411ce:      	add.w	r1, r6, #0x2bc
438411d2:      	adds	r2, r6, #0x4
438411d4:      	mov	r0, r1
438411d6:      	ldr.w	r12, [r8, r3]
438411da:      	ldr.w	r3, [pc, #0x714]        @ 0x438418f0 
438411de:      	str	r1, [sp, #0x50]
438411e0:      	mov	r1, r9
438411e2:      	strb.w	r5, [r12, #0x590]
438411e6:      	str	r2, [sp, #0x58]
438411e8:      	stm.w	sp, {r2, r7}
438411ec:      	ldr.w	r3, [r8, r3]
438411f0:      	str.w	r12, [sp, #0x38]
438411f4:      	mov	r2, r3
438411f6:      	str	r3, [sp, #0x3c]
438411f8:      	mov	r3, r12
438411fa:      	bl	0x4385ca3c  @ imm = #0x1b83e
438411fe:      	strb.w	r5, [r6, #0x336]
43841202:      	strb.w	r5, [r6, #0x346]
43841206:      	bl	0x437284b4  @ imm = #-0x118d56
4384120a:      	ldr.w	r12, [sp, #0x38]
4384120e:      	str.w	r12, [sp, #0x5c]
43841212:      	cbz	r0, 0x4384121e  @ imm = #0x8
43841214:      	add	r0, sp, #0x74
43841216:      	strb.w	r5, [sp, #0x8f]
4384121a:      	bl	0x438fb1c4  @ imm = #0xb9fa6
4384121e:      	ldr	r3, [sp, #0x3c]
43841220:      	mov	r2, r7
43841222:      	mov	r0, r6
43841224:      	mov	r1, r11
43841226:      	str.w	r9, [sp]
4384122a:      	str	r3, [sp, #0x4]
4384122c:      	ldr	r3, [sp, #0x40]
4384122e:      	bl	0x4385c868  @ imm = #0x1b636
43841232:      	ldrb.w	r1, [r6, #0x2be]
43841236:      	mov	r0, r9
43841238:      	bl	0x4382dcfc  @ imm = #-0x13540
4384123c:      	movs	r1, #0x0
4384123e:      	movs	r2, #0x28
43841240:      	strb.w	r0, [r9, #0x3dc]
43841244:      	add	r0, sp, #0x74
43841246:      	blx	0x439c5a04  @ imm = #0x1847bc
4384124a:      	ldr.w	r3, [r9, #0x294]
4384124e:      	cmp	r3, #0x9
43841250:      	beq	0x43841270  @ imm = #0x1c
43841252:      	ldr	r0, [sp, #0x3c]
43841254:      	ldrb.w	r2, [r0, #0x124]
43841258:      	cmp	r2, #0x1
4384125a:      	beq	0x43841270  @ imm = #0x12
4384125c:      	cmp	r3, #0x12
4384125e:      	bne	0x43841268  @ imm = #0x6
43841260:      	ldr.w	r3, [r9, #0x650]
43841264:      	cmp	r3, #0x5
43841266:      	beq	0x43841270  @ imm = #0x6
43841268:      	ldr	r1, [sp, #0x3c]
4384126a:      	ldrb	r3, [r1, #0x2]
4384126c:      	strb.w	r3, [sp, #0x8e]
43841270:      	add	r0, sp, #0x74
43841272:      	bl	0x438fb1a0  @ imm = #0xb9f2a
43841276:      	ldr	r1, [sp, #0x3c]
43841278:      	mov	r0, r9
4384127a:      	bl	0x4383fca0  @ imm = #-0x15de
4384127e:      	ldr	r1, [sp, #0x50]
43841280:      	mov	r2, r9
43841282:      	bl	0x4383f8f8  @ imm = #-0x198e
43841286:      	ldr	r2, [sp, #0x3c]
43841288:      	ldr.w	r3, [pc, #0x668]        @ 0x438418f4 
4384128c:      	ldrh.w	r0, [r7, #0x1b8]
43841290:      	str	r2, [sp]
43841292:      	ldr.w	r3, [r8, r3]
43841296:      	ldr	r1, [sp, #0x64]
43841298:      	ldr	r2, [sp, #0x5c]
4384129a:      	str	r3, [sp, #0x4]
4384129c:      	ldr	r3, [sp, #0x54]
4384129e:      	str	r1, [sp, #0xc]
438412a0:      	mov	r1, r9
438412a2:      	str	r2, [sp, #0x10]
438412a4:      	str	r3, [sp, #0x8]
438412a6:      	mov	r3, r10
438412a8:      	ldr	r2, [sp, #0x4c]
438412aa:      	bl	0x437b4340  @ imm = #-0x8cf6e
438412ae:      	mov	r0, r7
438412b0:      	bl	0x43b09cd4  @ imm = #0x2c8a20
438412b4:      	mov	r1, r0
438412b6:      	mov	r0, r10
438412b8:      	bl	0x43b08d80  @ imm = #0x2c7ac4
438412bc:      	ldr	r3, [sp, #0x48]
438412be:      	ldrb	r5, [r3, #0x15]
438412c0:      	cbnz	r5, 0x438412e8  @ imm = #0x24
438412c2:      	ldrh.w	r3, [r7, #0x1b8]
438412c6:      	mov	r1, r10
438412c8:      	mov	r2, r9
438412ca:      	ldr	r0, [sp, #0x5c]
438412cc:      	str	r3, [sp]
438412ce:      	ldr	r3, [sp, #0x3c]
438412d0:      	bl	0x43842158  @ imm = #0xe84
438412d4:      	ldrh.w	r0, [r10, #0x15e]
438412d8:      	bl	0x43adcd2a  @ imm = #0x29ba4e
438412dc:      	mov	r0, r6
438412de:      	ldr.w	r1, [r7, #0x1b8]
438412e2:      	mov	r2, r5
438412e4:      	bl	0x4383f5e4  @ imm = #-0x1d04
438412e8:      	ldr.w	r3, [pc, #0x60c]        @ 0x438418f8 
438412ec:      	mov	r0, r7
438412ee:      	str.w	r11, [sp]
438412f2:      	mov	r1, r9
438412f4:      	ldr	r2, [sp, #0x3c]
438412f6:      	ldr.w	r5, [r8, r3]
438412fa:      	mov	r3, r5
438412fc:      	bl	0x4385c974  @ imm = #0x1b674
43841300:      	ldrb	r3, [r5]
43841302:      	cmp	r3, #0x1
43841304:      	str	r0, [r6, #0x14]
43841306:      	bne	0x4384133a  @ imm = #0x30
43841308:      	ldrh.w	r0, [r10, #0x15e]
4384130c:      	ldrh.w	r1, [r10, #0x13c]
43841310:      	strh.w	r0, [r6, #0x2ce]
43841314:      	mov	r0, r9
43841316:      	strh.w	r1, [r6, #0x49a]
4384131a:      	bl	0x4385e598  @ imm = #0x1d27a
4384131e:      	mov	r1, r5
43841320:      	mov	r2, r0
43841322:      	ldr	r0, [sp, #0x50]
43841324:      	bl	0x43b0a3d4  @ imm = #0x2c90ac
43841328:      	ldrh	r2, [r5, #0x8]
4384132a:      	ldrh	r3, [r5, #0xa]
4384132c:      	ldrh	r0, [r5, #0xc]
4384132e:      	strh.w	r2, [r6, #0x4c6]
43841332:      	strh.w	r3, [r6, #0x4c8]
43841336:      	strh.w	r0, [r6, #0x4ca]
4384133a:      	ldr	r1, [sp, #0x44]
4384133c:      	cmp	r1, #0x1
4384133e:      	bne.w	0x43841576  @ imm = #0x234
43841342:      	movs	r3, #0x0
43841344:      	strb	r3, [r4]
43841346:      	ldrh.w	r2, [r9, #0x4bc]
4384134a:      	ands	r2, r2, #0x20
4384134e:      	beq	0x43841360  @ imm = #0xe
43841350:      	ldr.w	r2, [pc, #0x5a8]        @ 0x438418fc 
43841354:      	add	r2, pc
43841356:      	ldrb	r2, [r2]
43841358:      	cmp	r2, #0x1
4384135a:      	bne	0x43841392  @ imm = #0x34
4384135c:      	adds	r3, #0x40
4384135e:      	b	0x43841392  @ imm = #0x30
43841360:      	ldr.w	r3, [pc, #0x59c]        @ 0x43841900 
43841364:      	add	r3, pc
43841366:      	ldr	r3, [r3]
43841368:      	cmp	r3, #0x1
4384136a:      	bne	0x4384137c  @ imm = #0xe
4384136c:      	ldr.w	r3, [pc, #0x594]        @ 0x43841904 
43841370:      	add	r3, pc
43841372:      	ldrb	r3, [r3]
43841374:      	cmp	r3, #0x1
43841376:      	bne	0x43841396  @ imm = #0x1c
43841378:      	adds	r3, #0x3f
4384137a:      	b	0x43841392  @ imm = #0x14
4384137c:      	cmp	r3, #0x3
4384137e:      	bne	0x43841396  @ imm = #0x14
43841380:      	ldr.w	r3, [pc, #0x584]        @ 0x43841908 
43841384:      	add	r3, pc
43841386:      	ldrb	r3, [r3]
43841388:      	cmp	r3, #0x1
4384138a:      	bne	0x43841390  @ imm = #0x2
4384138c:      	adds	r3, #0x41
4384138e:      	b	0x43841392  @ imm = #0x0
43841390:      	movs	r3, #0x2
43841392:      	strb	r3, [r4, #0x1]
43841394:      	b	0x43841398  @ imm = #0x0
43841396:      	strb	r2, [r4, #0x1]
43841398:      	ldr	r2, [sp, #0x3c]
4384139a:      	ldrb	r3, [r2, #0x2]
4384139c:      	cmp	r3, #0x1
4384139e:      	bne	0x438413a6  @ imm = #0x4
438413a0:      	ldrb	r3, [r4, #0x1]
438413a2:      	adds	r3, #0x14
438413a4:      	strb	r3, [r4, #0x1]
438413a6:      	ldr	r3, [r6, #0x14]
438413a8:      	subs	r3, #0x1
438413aa:      	cmp	r3, #0x2
438413ac:      	bhi	0x438413b6  @ imm = #0x6
438413ae:      	ldrb	r3, [r4, #0x1]
438413b0:      	orn	r3, r3, #0x7f
438413b4:      	strb	r3, [r4, #0x1]
438413b6:      	ldrh.w	r0, [r10, #0x162]
438413ba:      	bl	0x4382fe08  @ imm = #-0x115b6
438413be:      	cmp	r0, #0x1
438413c0:      	bne	0x438413c8  @ imm = #0x4
438413c2:      	movs	r3, #0x0
438413c4:      	strb	r3, [r4, #0x2]
438413c6:      	b	0x438413d4  @ imm = #0xa
438413c8:      	ldrh.w	r3, [r10, #0x162]
438413cc:      	strb	r3, [r4, #0x2]
438413ce:      	ldrh.w	r3, [r10, #0x162]
438413d2:      	asrs	r3, r3, #0x8
438413d4:      	strb	r3, [r4, #0x3]
438413d6:      	ldrh.w	r3, [r10, #0x15e]
438413da:      	strb	r3, [r4, #0x4]
438413dc:      	ldrh.w	r3, [r10, #0x15e]
438413e0:      	asrs	r3, r3, #0x8
438413e2:      	strb	r3, [r4, #0x5]
438413e4:      	ldr	r0, [sp, #0x3c]
438413e6:      	ldrb	r3, [r0, #0x2]
438413e8:      	cmp	r3, #0x1
438413ea:      	bne	0x4384142e  @ imm = #0x40
438413ec:      	add.w	r3, r7, #0x1480
438413f0:      	ldrb	r0, [r3, #0x4]
438413f2:      	bl	0x43b0a4ee  @ imm = #0x2c90f8
438413f6:      	cmp	r0, #0x1
438413f8:      	bne	0x4384141e  @ imm = #0x22
438413fa:      	ldr.w	r2, [r9, #0x420]
438413fe:      	cmp	r2, #0x4
43841400:      	bhi	0x4384140c  @ imm = #0x8
43841402:      	ldr.w	r3, [pc, #0x508]        @ 0x4384190c 
43841406:      	add	r3, pc
43841408:      	ldrb	r3, [r3, r2]
4384140a:      	b	0x4384140e  @ imm = #0x0
4384140c:      	movs	r3, #0x0
4384140e:      	ldr	r1, [sp, #0x3c]
43841410:      	ldrb.w	r2, [r1, #0xfe]
43841414:      	cmp	r2, r3
43841416:      	bls	0x4384142e  @ imm = #0x14
43841418:      	subs	r3, r2, r3
4384141a:      	uxtb	r3, r3
4384141c:      	b	0x43841434  @ imm = #0x14
4384141e:      	ldr	r3, [r6, #0x14]
43841420:      	cbnz	r3, 0x4384142e  @ imm = #0xa
43841422:      	cmp.w	r11, #0x0
43841426:      	beq	0x43841432  @ imm = #0x8
43841428:      	ldrb.w	r3, [r11, #0x4ba]
4384142c:      	b	0x43841434  @ imm = #0x4
4384142e:      	movs	r3, #0x0
43841430:      	b	0x43841434  @ imm = #0x0
43841432:      	mov	r3, r11
43841434:      	strb	r3, [r4, #0x6]
43841436:      	ldrb	r3, [r5]
43841438:      	cmp	r3, #0x1
4384143a:      	bne	0x43841444  @ imm = #0x6
4384143c:      	ldrh	r0, [r5, #0x8]
4384143e:      	bl	0x43b075ec  @ imm = #0x2c61aa
43841442:      	strb	r0, [r4, #0x6]
43841444:      	ldr.w	r2, [pc, #0x4c8]        @ 0x43841910 
43841448:      	movs	r3, #0xa0
4384144a:      	strb	r3, [r4, #0x8]
4384144c:      	subs	r3, #0xa0
4384144e:      	add	r2, pc
43841450:      	strb	r3, [r4, #0x9]
43841452:      	ldrh	r2, [r2]
43841454:      	strb	r3, [r4, #0xc]
43841456:      	strb	r2, [r4, #0xa]
43841458:      	asrs	r2, r2, #0x8
4384145a:      	strb	r2, [r4, #0xb]
4384145c:      	ldr.w	r1, [r7, #0x1c0]
43841460:      	ldrb.w	r2, [r9, #0x38d]
43841464:      	ldrb.w	r0, [r9, #0x38e]
43841468:      	cmp	r1, #0x19
4384146a:      	it	eq
4384146c:      	moveq	r2, #0x2
4384146e:      	ldrb.w	r1, [r9, #0x38c]
43841472:      	and	r0, r0, #0x3
43841476:      	strb	r3, [r4, #0xe]
43841478:      	and	r1, r1, #0x1
4384147c:      	ldr.w	r3, [pc, #0x494]        @ 0x43841914 
43841480:      	lsls	r2, r2, #0x6
43841482:      	lsls	r1, r1, #0x5
43841484:      	add.w	r1, r1, r0, lsl #3
43841488:      	adds	r1, r1, r2
4384148a:      	strb	r1, [r4, #0xd]
4384148c:      	ldr.w	r3, [r8, r3]
43841490:      	ldrb	r2, [r3]
43841492:      	cmp	r2, #0x0
43841494:      	bne	0x43841562  @ imm = #0xca
43841496:      	ldrb	r3, [r5]
43841498:      	cmp	r3, #0x1
4384149a:      	ite	ne
4384149c:      	strbne	r2, [r4, #0x12]
4384149e:      	strbeq	r3, [r4, #0x12]
438414a0:      	ldr.w	r2, [r6, #0x30c]
438414a4:      	sub.w	r3, r2, #0x12
438414a8:      	cmp	r3, #0x1
438414aa:      	ldr.w	r3, [r6, #0x31c]
438414ae:      	bhi	0x438414fe  @ imm = #0x4c
438414b0:      	cmp	r3, #0x1
438414b2:      	bne	0x438414e4  @ imm = #0x2e
438414b4:      	ldrh.w	r1, [r6, #0x2d0]
438414b8:      	ldrh	r0, [r5, #0xc]
438414ba:      	bl	0x43b076d0  @ imm = #0x2c6212
438414be:      	ldrb	r3, [r5, #0x10]
438414c0:      	subs	r3, r0, r3
438414c2:      	strb	r3, [r4, #0x13]
438414c4:      	ldrh.w	r1, [r6, #0x2d0]
438414c8:      	ldrh	r0, [r5, #0x8]
438414ca:      	bl	0x43b076d0  @ imm = #0x2c6202
438414ce:      	ldrb	r3, [r5, #0x10]
438414d0:      	subs	r3, r0, r3
438414d2:      	strb	r3, [r4, #0x14]
438414d4:      	ldrh	r0, [r5, #0xa]
438414d6:      	ldrh.w	r1, [r6, #0x2d0]
438414da:      	bl	0x43b076d0  @ imm = #0x2c61f2
438414de:      	ldrb	r3, [r5, #0x10]
438414e0:      	subs	r3, r0, r3
438414e2:      	b	0x43841574  @ imm = #0x8e
438414e4:      	ldrh	r0, [r5, #0xc]
438414e6:      	bl	0x43b075ec  @ imm = #0x2c6102
438414ea:      	strb	r0, [r4, #0x13]
438414ec:      	ldrh	r0, [r5, #0x8]
438414ee:      	bl	0x43b075ec  @ imm = #0x2c60fa
438414f2:      	strb	r0, [r4, #0x14]
438414f4:      	ldrh	r0, [r5, #0xa]
438414f6:      	bl	0x43b075ec  @ imm = #0x2c60f2
438414fa:      	strb	r0, [r4, #0x15]
438414fc:      	b	0x43841576  @ imm = #0x76
438414fe:      	subs	r2, #0x14
43841500:      	cmp	r2, #0x1
43841502:      	bhi	0x4384153e  @ imm = #0x38
43841504:      	cmp	r3, #0x1
43841506:      	bne	0x4384152a  @ imm = #0x20
43841508:      	ldrh.w	r1, [r6, #0x2d0]
4384150c:      	ldrh	r0, [r5, #0xa]
4384150e:      	bl	0x43b076d0  @ imm = #0x2c61be
43841512:      	ldrb	r3, [r5, #0x10]
43841514:      	subs	r3, r0, r3
43841516:      	strb	r3, [r4, #0x13]
43841518:      	ldrh	r0, [r5, #0x8]
4384151a:      	ldrh.w	r1, [r6, #0x2d0]
4384151e:      	bl	0x43b076d0  @ imm = #0x2c61ae
43841522:      	ldrb	r3, [r5, #0x10]
43841524:      	subs	r3, r0, r3
43841526:      	strb	r3, [r4, #0x14]
43841528:      	b	0x4384153a  @ imm = #0xe
4384152a:      	ldrh	r0, [r5, #0xa]
4384152c:      	bl	0x43b075ec  @ imm = #0x2c60bc
43841530:      	strb	r0, [r4, #0x13]
43841532:      	ldrh	r0, [r5, #0x8]
43841534:      	bl	0x43b075ec  @ imm = #0x2c60b4
43841538:      	strb	r0, [r4, #0x14]
4384153a:      	movs	r3, #0x0
4384153c:      	b	0x43841574  @ imm = #0x34
4384153e:      	cmp	r3, #0x1
43841540:      	bne	0x43841554  @ imm = #0x10
43841542:      	ldrh	r0, [r5, #0x8]
43841544:      	ldrh.w	r1, [r6, #0x2d0]
43841548:      	bl	0x43b076d0  @ imm = #0x2c6184
4384154c:      	ldrb	r3, [r5, #0x10]
4384154e:      	subs	r3, r0, r3
43841550:      	strb	r3, [r4, #0x13]
43841552:      	b	0x4384155c  @ imm = #0x6
43841554:      	ldrh	r0, [r5, #0x8]
43841556:      	bl	0x43b075ec  @ imm = #0x2c6092
4384155a:      	strb	r0, [r4, #0x13]
4384155c:      	movs	r3, #0x0
4384155e:      	strb	r3, [r4, #0x14]
43841560:      	b	0x43841574  @ imm = #0x10
43841562:      	movs	r2, #0x1
43841564:      	strb	r2, [r4, #0x12]
43841566:      	ldrb	r2, [r3]
43841568:      	strb	r2, [r4, #0x13]
4384156a:      	ldrb	r2, [r3]
4384156c:      	adds	r2, #0x8
4384156e:      	strb	r2, [r4, #0x14]
43841570:      	ldrb	r3, [r3]
43841572:      	adds	r3, #0x10
43841574:      	strb	r3, [r4, #0x15]
43841576:      	ldrh.w	r0, [r10, #0x162]
4384157a:      	bl	0x4382fac8  @ imm = #-0x11ab6
4384157e:      	ldr	r3, [pc, #0x398]        @ 0x43841918 
43841580:      	ldr	r2, [sp, #0x3c]
43841582:      	add	r3, pc
43841584:      	ldrb	r1, [r2, #0x2]
43841586:      	subs	r1, #0x0
43841588:      	it	ne
4384158a:      	movne	r1, #0x1
4384158c:      	str	r0, [r3]
4384158e:      	mov	r0, r9
43841590:      	ldr	r3, [pc, #0x388]        @ 0x4384191c 
43841592:      	ldr.w	r5, [r8, r3]
43841596:      	ldrh.w	r3, [r10, #0x164]
4384159a:      	ldrh.w	r2, [r5, #0x9a]
4384159e:      	bl	0x4382f914  @ imm = #-0x11c8e
438415a2:      	ldrh.w	r3, [r5, #0xa4]
438415a6:      	str	r5, [sp, #0x6c]
438415a8:      	strh.w	r3, [r6, #0x186]
438415ac:      	str.w	r0, [r6, #0x180]
438415b0:      	cmp.w	r11, #0x0
438415b4:      	beq	0x438415c0  @ imm = #0x8
438415b6:      	ldr.w	r3, [r7, #0x1b8]
438415ba:      	cbnz	r3, 0x438415c0  @ imm = #0x2
438415bc:      	str.w	r0, [r11, #0xb78]
438415c0:      	cbnz	r0, 0x438415c6  @ imm = #0x2
438415c2:      	strh.w	r0, [r6, #0x186]
438415c6:      	ldr.w	r1, [r7, #0x1b8]
438415ca:      	ldr.w	r0, [r7, #0x1c0]
438415ce:      	bl	0x4383fb6c  @ imm = #-0x1a66
438415d2:      	movs	r1, #0x0
438415d4:      	mov.w	r2, #0x158
438415d8:      	mov	r5, r0
438415da:      	blx	0x439c5a04  @ imm = #0x184428
438415de:      	ldr	r2, [sp, #0x60]
438415e0:      	add.w	r12, r5, #0x8
438415e4:      	ldrh.w	r0, [r7, #0x1bc]
438415e8:      	ldrh.w	r1, [r7, #0x1b8]
438415ec:      	ldr	r3, [r2]
438415ee:      	strh	r0, [r5]
438415f0:      	mov	lr, r3
438415f2:      	strh	r1, [r5, #0x2]
438415f4:      	ldm.w	lr!, {r0, r1, r2, r3}
438415f8:      	stm.w	r12!, {r0, r1, r2, r3}
438415fc:      	ldm.w	lr!, {r0, r1, r2, r3}
