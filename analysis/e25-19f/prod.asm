0x43af54d8: push {r4, r5, r6, lr}
0x43af54da: sub sp, #0x68
0x43af54dc: mov r4, r0
0x43af54de: mov r6, r1
0x43af54e0: mov r5, r2
0x43af54e2: movs r0, #5
0x43af54e4: bl #0x43ae7482
0x43af54e8: movs r3, #0
0x43af54ea: mov r0, r4
0x43af54ec: str r3, [sp]
0x43af54ee: mov r1, r6
0x43af54f0: mov r2, r5
0x43af54f2: add r3, sp, #0xc
0x43af54f4: bl #0x437d1e6c
0x43af54f8: movs r0, #6
0x43af54fa: bl #0x43ae7482
0x43af54fe: movs r0, #1
0x43af5500: add sp, #0x68
0x43af5502: pop {r4, r5, r6, pc}
0x43af5504: push.w {r0, r1, r4, r5, r6, r7, r8, lr}
0x43af5508: mov r5, r0
0x43af550a: mov r8, r1
0x43af550c: mov r7, r2
0x43af550e: mov r6, r3
0x43af5510: movs r0, #7
0x43af5512: bl #0x43ae7482
0x43af5516: mov r0, r5
0x43af5518: mov r1, r8
0x43af551a: mov r2, r7
0x43af551c: mov r3, r6
0x43af551e: movs r4, #1
0x43af5520: str r4, [sp]
0x43af5522: bl #0x437d1e6c
0x43af5526: movs r0, #8
0x43af5528: bl #0x43ae7482
0x43af552c: mov r0, r4
0x43af552e: pop.w {r2, r3, r4, r5, r6, r7, r8, pc}
0x43af5532: vmov.f32 s9, #1.000000e+00
0x43af5536: vldr s15, [r0]
0x43af553a: vstr s15, [r1]
0x43af553e: vsub.f32 s9, s9, s15
0x43af5542: vmov.f64 d5, #1.000000e+00
0x43af5546: vstr s9, [r1, #4]
0x43af554a: vcvt.f64.f32 d6, s9
0x43af554e: vsub.f64 d5, d5, d6
0x43af5552: vmov.f64 d6, #5.000000e-01
0x43af5556: vmul.f64 d7, d5, d6
0x43af555a: vcvt.f32.f64 s14, d7
0x43af555e: vstr s14, [r1, #8]
0x43af5562: vadd.f32 s14, s14, s9
0x43af5566: vstr s14, [r1, #0xc]
0x43af556a: bx lr
0x43af556c: ldr r3, [r0]
0x43af556e: str r3, [r1]
0x43af5570: ldr r3, [r0, #4]
0x43af5572: str r3, [r1, #4]
0x43af5574: ldr r3, [r0, #8]
0x43af5576: str r3, [r1, #8]
0x43af5578: ldr r3, [r0, #0xc]
0x43af557a: str r3, [r1, #0xc]
0x43af557c: ldr r3, [r0, #0x10]
0x43af557e: str r3, [r1, #0x10]
0x43af5580: bx lr
0x43af5582: push.w {r4, r5, r6, r7, r8, lr}
0x43af5586: sub sp, #0x88
0x43af5588: mov r6, r1
0x43af558a: add r1, sp, #0x20
0x43af558c: mov r4, r3
0x43af558e: mov r7, r2
0x43af5590: bl #0x43af556c
0x43af5594: add r0, sp, #0x20
0x43af5596: add r1, sp, #0x44
0x43af5598: add r5, sp, #0x7c
0x43af559a: bl #0x43af5532
0x43af559e: add r2, sp, #0x60
0x43af55a0: add r0, sp, #0x20
0x43af55a2: add r1, sp, #0x44
0x43af55a4: bl #0x437d2a7c
0x43af55a8: add r0, sp, #0x20
0x43af55aa: add r1, sp, #0xc
0x43af55ac: add.w r8, sp, #0x6c
0x43af55b0: bl #0x437d2ac8
0x43af55b4: mov r3, r7
0x43af55b6: add r0, sp, #0x20
0x43af55b8: add r1, sp, #0x60
0x43af55ba: add r2, sp, #0xc
0x43af55bc: str r5, [sp]
0x43af55be: bl #0x437d2b60
0x43af55c2: mov r0, r5
0x43af55c4: add r1, sp, #0x60
0x43af55c6: add r2, sp, #0x54
0x43af55c8: bl #0x437d2ba0
0x43af55cc: add r0, sp, #0xc
0x43af55ce: add r1, sp, #0x54
0x43af55d0: mov r2, r7
0x43af55d2: add r3, sp, #0x74
0x43af55d4: str.w r8, [sp]
0x43af55d8: bl #0x437d2c00
0x43af55dc: add r3, sp, #0x34
0x43af55de: mov r0, r5
0x43af55e0: str r3, [sp]
0x43af55e2: add r1, sp, #0x74
0x43af55e4: add r3, sp, #0x84
0x43af55e6: mov r2, r8
0x43af55e8: str r3, [sp, #4]
0x43af55ea: add r3, sp, #0x44
0x43af55ec: bl #0x437d2c88
0x43af55f0: ldr r3, [r6]
0x43af55f2: lsls r3, r3, #0xc
0x43af55f4: vmov s14, r3
0x43af55f8: ldr r3, [r6, #4]
0x43af55fa: vcvt.f32.s32 s15, s14
0x43af55fe: vldr s14, [sp, #0x78]
0x43af5602: lsls r3, r3, #0xc
0x43af5604: vmul.f32 s14, s15, s14
0x43af5608: vcvt.s32.f32 s14, s14
0x43af560c: vstr s14, [r4]
0x43af5610: vldr s14, [sp, #0x40]
0x43af5614: vmul.f32 s15, s14, s15
0x43af5618: vmov s14, r3
0x43af561c: vcvt.s32.f32 s15, s15
0x43af5620: vstr s15, [r4, #4]
0x43af5624: vcvt.f32.s32 s15, s14
0x43af5628: vldr s14, [sp, #0x70]
0x43af562c: vmul.f32 s14, s15, s14
0x43af5630: vcvt.s32.f32 s14, s14
0x43af5634: vstr s14, [r4, #8]
0x43af5638: vldr s14, [sp, #0x84]
0x43af563c: vmul.f32 s15, s14, s15
0x43af5640: vcvt.s32.f32 s15, s15
0x43af5644: vstr s15, [r4, #0xc]
0x43af5648: add sp, #0x88
0x43af564a: pop.w {r4, r5, r6, r7, r8, pc}
0x43af564e: ldm r1, {r1, r3}
0x43af5650: lsls r0, r0, #0xc
0x43af5652: push {r4, lr}
0x43af5654: adds r4, r1, r3
0x43af5656: cmp r4, r0
0x43af5658: it gt
0x43af565a: rsb r1, r3, r0
0x43af565e: stm.w r2, {r1, r3}
0x43af5662: pop {r4, pc}
0x43af5664: push {r4, lr}
0x43af5666: mov r4, r0
0x43af5668: bl #0x437d6198
0x43af566c: ldrb r2, [r0]
0x43af566e: tst.w r2, #0x30
0x43af5672: ubfx r3, r2, #4, #2
0x43af5676: bne #0x43af5680
0x43af5678: movs r0, #0x18
0x43af567a: bl #0x437d6280
0x43af567e: ldrb r3, [r0]
0x43af5680: subs r3, #1
0x43af5682: cmp r3, #5
0x43af5684: bhi #0x43af5694
0x43af5686: tbb [pc, r3]
0x43af568a: lsrs r3, r0, #0x1c
0x43af568c: lsrs r7, r0, #4
0x43af568e: lsrs r3, r1, #0x14
0x43af5690: movs r0, #1
0x43af5692: pop {r4, pc}
0x43af5694: ldr r0, [r4]
0x43af5696: pop {r4, pc}
0x43af5698: movs r0, #2
0x43af569a: pop {r4, pc}
0x43af569c: movs r0, #3
0x43af569e: pop {r4, pc}
0x43af56a0: movs r0, #4
0x43af56a2: pop {r4, pc}
0x43af56a4: movs r0, #6
0x43af56a6: pop {r4, pc}
0x43af56a8: movs r0, #0
0x43af56aa: pop {r4, pc}
0x43af56ac: push {r0, r1, r2, r4, r5, lr}
0x43af56ae: add r4, sp, #8
0x43af56b0: mov r5, r2
0x43af56b2: stmdb r4, {r0, r1}
0x43af56b6: mov r4, r3
0x43af56b8: ldr r3, [r2]
0x43af56ba: ldr r2, [sp]
0x43af56bc: asrs r1, r3, #0x1f
0x43af56be: lsls r0, r3, #0xc
0x43af56c0: lsls r1, r1, #0xc
0x43af56c2: orr.w r1, r1, r3, lsr #20
0x43af56c6: asrs r3, r2, #0x1f
0x43af56c8: bl #0x43b11c14
0x43af56cc: ldr r1, [r5, #4]
0x43af56ce: ldr r2, [sp, #4]
0x43af56d0: asrs r3, r1, #0x1f
0x43af56d2: lsls r3, r3, #0xc
0x43af56d4: str r0, [r4]
0x43af56d6: lsls r0, r1, #0xc
0x43af56d8: orr.w r1, r3, r1, lsr #20
0x43af56dc: asrs r3, r2, #0x1f
0x43af56de: bl #0x43b11c14
0x43af56e2: str r0, [r4, #4]
0x43af56e4: pop {r1, r2, r3, r4, r5, pc}
0x43af56e6: push {r0, r1, r2, r4, r5, lr}
0x43af56e8: add r4, sp, #8
0x43af56ea: mov r5, r3
0x43af56ec: ldr r3, [r2]
0x43af56ee: stmdb r4, {r0, r1}
0x43af56f2: ldr r0, [sp]
0x43af56f4: smull r0, r1, r0, r3
0x43af56f8: ldr r3, [r2, #4]
0x43af56fa: ldr r2, [sp, #4]
0x43af56fc: smull r2, r3, r2, r3
