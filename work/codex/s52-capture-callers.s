
work/claude/input/a7s-av-cam-view.elf:	file format elf32-littlearm

Disassembly of section .text:

43541000 <_binary_input_a7s_av_cam_bin_start>:
43828180:      	<unknown>
43828184:      	b	0x43828188 <_binary_input_a7s_av_cam_bin_start+0x2e7188> @ imm = #0x0
43828186:      	movs	r3, #0x1
43828188:      	add.w	r5, r5, r5, lsl #1
4382818c:      	ldr	r2, [pc, #0x6c]         @ 0x438281fc <_binary_input_a7s_av_cam_bin_start+0x2e71fc>
4382818e:      	adds	r3, r5, r3
43828190:      	add.w	r7, r7, r3, lsl #1
43828194:      	ldr	r2, [r4, r2]
43828196:      	uxth	r7, r7
43828198:      	ldr.w	r0, [r2, r7, lsl #2]
4382819c:      	b	0x438281dc <_binary_input_a7s_av_cam_bin_start+0x2e71dc> @ imm = #0x3c
4382819e:      	ldrb.w	r5, [r3, #0xa8]
438281a2:      	ldr	r3, [r0, #0x34]
438281a4:      	cmp	r5, #0x1
438281a6:      	it	hs
438281a8:      	movhs	r5, #0x1
438281aa:      	cmp	r3, #0x3
438281ac:      	bhi	0x438281be <_binary_input_a7s_av_cam_bin_start+0x2e71be> @ imm = #0xe
438281ae:      	tbb	[pc, r3]
438281b2:      	lsls	r6, r1, #0x10
438281b4:      	lsrs	r2, r0, #0x10
438281b6:      	movs	r3, #0x3
438281b8:      	b	0x438281d0 <_binary_input_a7s_av_cam_bin_start+0x2e71d0> @ imm = #0x14
438281ba:      	movs	r3, #0x4
438281bc:      	b	0x438281d0 <_binary_input_a7s_av_cam_bin_start+0x2e71d0> @ imm = #0x10
438281be:      	ldr	r0, [pc, #0x40]         @ 0x43828200 <_binary_input_a7s_av_cam_bin_start+0x2e7200>
438281c0:      	ldr	r1, [pc, #0x40]         @ 0x43828204 <_binary_input_a7s_av_cam_bin_start+0x2e7204>
438281c2:      	add	r0, pc
438281c4:      	add	r1, pc
438281c6:      	bl	0x438f7114 <_binary_input_a7s_av_cam_bin_start+0x3b6114> @ imm = #0xcef4a
438281ca:      	movs	r3, #0x0
438281cc:      	b	0x438281d0 <_binary_input_a7s_av_cam_bin_start+0x2e71d0> @ imm = #0x0
438281ce:      	movs	r3, #0x1
438281d0:      	ldr	r2, [pc, #0x34]         @ 0x43828208 <_binary_input_a7s_av_cam_bin_start+0x2e7208>
438281d2:      	add.w	r5, r5, r3, lsl #1
438281d6:      	ldr	r2, [r4, r2]
438281d8:      	ldr.w	r0, [r2, r5, lsl #2]
438281dc:      	add	r1, sp, #0x4
438281de:      	bl	0x4355f670 <_binary_input_a7s_av_cam_bin_start+0x1e670> @ imm = #-0x2c8b72
438281e2:      	ldr	r0, [sp, #0x4]
438281e4:      	lsls	r0, r0, #0xa
438281e6:      	pop	{r1, r2, r3, r4, r5, r6, r7, pc}
438281e8:      	stm	r4!, {r1, r3}
438281ea:      	lsls	r7, r7, #0x1
438281ec:      	str	r3, [sp, #0x3c4]
438281ee:      	lsls	r0, r1, #0x1
438281f0:      	str	r7, [sp, #0x3f0]
438281f2:      	lsls	r0, r1, #0x1
438281f4:      	str	r3, [sp, #0x3a8]
438281f6:      	lsls	r0, r1, #0x1
438281f8:      	str	r7, [sp, #0x368]
438281fa:      	lsls	r0, r1, #0x1
438281fc:      	strh	r0, [r5, r7]
438281fe:      	movs	r0, r0
43828200:      	str	r7, [sp, #0x70]
43828202:      	lsls	r0, r1, #0x1
43828204:      	str	r6, [sp, #0x228]
43828206:      	lsls	r0, r1, #0x1
43828208:      	ldr	r7, [pc, #0x330]        @ 0x4382853c <_binary_input_a7s_av_cam_bin_start+0x2e753c>
4382820a:      	movs	r0, r0
4382820c:      	ldr	r3, [pc, #0x14]         @ 0x43828224 <_binary_input_a7s_av_cam_bin_start+0x2e7224>
4382820e:      	push	{r0, r1, r2, lr}
43828210:      	add	r3, pc
43828212:      	ldr	r2, [pc, #0x14]         @ 0x43828228 <_binary_input_a7s_av_cam_bin_start+0x2e7228>
43828214:      	add	r1, sp, #0x4
43828216:      	ldr	r3, [r3, r2]
43828218:      	ldr	r0, [r3]
4382821a:      	bl	0x4355f670 <_binary_input_a7s_av_cam_bin_start+0x1e670> @ imm = #-0x2c8bae
4382821e:      	ldr	r0, [sp, #0x4]
43828220:      	lsls	r0, r0, #0xa
43828222:      	pop	{r1, r2, r3, pc}
43828224:      	stm	r3!, {r2, r3, r5}
43828226:      	lsls	r7, r7, #0x1
43828228:      	ldrh	r0, [r2, #0x30]
4382822a:      	movs	r0, r0
4382822c:      	ldr	r3, [pc, #0x114]        @ 0x43828344 <_binary_input_a7s_av_cam_bin_start+0x2e7344>
4382822e:      	ldr	r2, [pc, #0x118]        @ 0x43828348 <_binary_input_a7s_av_cam_bin_start+0x2e7348>
43828230:      	add	r3, pc
43828232:      	push	{r4, r5, lr}
43828234:      	mov	r4, r0
43828236:      	ldr	r3, [r3, r2]
43828238:      	sub	sp, #0x54
4382823a:      	ldr	r3, [r3, #0x24]
4382823c:      	cmp	r3, #0x1
4382823e:      	bne	0x438282a6 <_binary_input_a7s_av_cam_bin_start+0x2e72a6> @ imm = #0x64
43828240:      	add	r3, sp, #0x34
43828242:      	ldrb.w	r1, [r4, #0x4d4]
43828246:      	ldrb.w	r2, [r4, #0x4d5]
4382824a:      	ldr.w	r0, [r0, #0x4d0]
4382824e:      	bl	0x437b8948 <_binary_input_a7s_av_cam_bin_start+0x277948> @ imm = #-0x6f90a
43828252:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0x135a6e
43828256:      	add.w	r2, r4, #0x548
4382825a:      	add	r1, sp, #0x34
4382825c:      	bl	0x436f2848 <_binary_input_a7s_av_cam_bin_start+0x1b1848> @ imm = #-0x135a18
43828260:      	add.w	r2, r4, #0x4a00
43828264:      	add.w	r3, r4, #0x5c0
43828268:      	adds	r3, #0xc
4382826a:      	str	r3, [sp, #0x48]
4382826c:      	ldr.w	r3, [r2, #0xe0]
43828270:      	cbz	r3, 0x43828278 <_binary_input_a7s_av_cam_bin_start+0x2e7278> @ imm = #0x4
43828272:      	add.w	r1, r3, #0x20
43828276:      	b	0x4382827a <_binary_input_a7s_av_cam_bin_start+0x2e727a> @ imm = #0x0
43828278:      	mov	r1, r3
4382827a:      	ldr.w	r2, [r2, #0xe8]
4382827e:      	cbz	r2, 0x43828286 <_binary_input_a7s_av_cam_bin_start+0x2e7286> @ imm = #0x4
43828280:      	ldr	r3, [r2, #0x20]
43828282:      	adds	r2, #0x40
43828284:      	b	0x43828288 <_binary_input_a7s_av_cam_bin_start+0x2e7288> @ imm = #0x0
43828286:      	mov	r3, r2
43828288:      	add.w	r0, r4, #0x1180
4382828c:      	str	r2, [sp]
4382828e:      	str	r1, [sp, #0x4]
43828290:      	adds	r0, #0x28
43828292:      	add.w	r1, r4, #0x20
43828296:      	add	r2, sp, #0x48
43828298:      	bl	0x43862e24 <_binary_input_a7s_av_cam_bin_start+0x321e24> @ imm = #0x3ab88
4382829c:      	mov	r0, r4
4382829e:      	movs	r1, #0x0
438282a0:      	bl	0x43829138 <_binary_input_a7s_av_cam_bin_start+0x2e8138> @ imm = #0xe94
438282a4:      	b	0x438282c6 <_binary_input_a7s_av_cam_bin_start+0x2e72c6> @ imm = #0x1e
438282a6:      	add.w	r3, r0, #0x4a00
438282aa:      	ldr.w	r3, [r3, #0xe0]
438282ae:      	cbz	r3, 0x438282b2 <_binary_input_a7s_av_cam_bin_start+0x2e72b2> @ imm = #0x0
438282b0:      	adds	r3, #0x20
438282b2:      	add.w	r0, r4, #0x1180
438282b6:      	str	r3, [sp]
438282b8:      	adds	r0, #0x28
438282ba:      	add.w	r1, r4, #0x20
438282be:      	add	r2, sp, #0x48
438282c0:      	add	r3, sp, #0x34
438282c2:      	bl	0x437c67bc <_binary_input_a7s_av_cam_bin_start+0x2857bc> @ imm = #-0x61b0a
438282c6:      	add.w	r0, r4, #0x1180
438282ca:      	add.w	r5, r4, #0x20
438282ce:      	adds	r0, #0x28
438282d0:      	bl	0x43aed49a <_binary_input_a7s_av_cam_bin_start+0x5ac49a> @ imm = #0x2c51c6
438282d4:      	subs	r0, #0x0
438282d6:      	it	ne
438282d8:      	movne	r0, #0x1
438282da:      	strb.w	r0, [r4, #0x742]
438282de:      	mov	r0, r4
438282e0:      	bl	0x43826c90 <_binary_input_a7s_av_cam_bin_start+0x2e5c90> @ imm = #-0x1654
438282e4:      	mov	r0, r5
438282e6:      	bl	0x43af5d24 <_binary_input_a7s_av_cam_bin_start+0x5b4d24> @ imm = #0x2cda3a
438282ea:      	add.w	r3, r4, #0x4a00
438282ee:      	ldr.w	r2, [r3, #0xe0]
438282f2:      	cbz	r2, 0x438282fa <_binary_input_a7s_av_cam_bin_start+0x2e72fa> @ imm = #0x4
438282f4:      	add.w	r2, r2, #0x1440
438282f8:      	adds	r2, #0x14
438282fa:      	add.w	r0, r4, #0x2c00
438282fe:      	mov	r1, r5
43828300:      	adds	r0, #0x4c
43828302:      	bl	0x437c22ac <_binary_input_a7s_av_cam_bin_start+0x2812ac> @ imm = #-0x6605a
43828306:      	bl	0x4380ae44 <_binary_input_a7s_av_cam_bin_start+0x2c9e44> @ imm = #-0x1d4c6
4382830a:      	ldr.w	r0, [r4, #0x6cc]
4382830e:      	add	r1, sp, #0xc
43828310:      	bl	0x43aebe50 <_binary_input_a7s_av_cam_bin_start+0x5aae50> @ imm = #0x2c3b3c
43828314:      	cbz	r0, 0x43828326 <_binary_input_a7s_av_cam_bin_start+0x2e7326> @ imm = #0xe
43828316:      	ldr	r0, [pc, #0x34]         @ 0x4382834c <_binary_input_a7s_av_cam_bin_start+0x2e734c>
43828318:      	movw	r2, #0x13d
4382831c:      	ldr	r1, [pc, #0x30]         @ 0x43828350 <_binary_input_a7s_av_cam_bin_start+0x2e7350>
4382831e:      	add	r0, pc
