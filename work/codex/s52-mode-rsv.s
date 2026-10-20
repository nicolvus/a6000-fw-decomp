
work/claude/input/a7s-av-cam-view.elf:	file format elf32-littlearm

Disassembly of section .text:

43541000 <_binary_input_a7s_av_cam_bin_start>:
437b8800:      	ldr	r3, [pc, #0x1c]         @ 0x437b8820 <_binary_input_a7s_av_cam_bin_start+0x277820>
437b8802:      	movs	r2, #0x0
437b8804:      	add	r3, pc
437b8806:      	str	r2, [r3]
437b8808:      	movs	r2, #0x0
437b880a:      	ldr	r3, [pc, #0x18]         @ 0x437b8824 <_binary_input_a7s_av_cam_bin_start+0x277824>
437b880c:      	add	r3, pc
437b880e:      	strb	r2, [r3]
437b8810:      	pop.w	{r2, r3, r4, r5, r6, r7, r8, pc}
437b8814:      	cmp	r1, #0xfc
437b8816:      	lsls	r7, r5, #0x1
437b8818:      	cmp	r1, #0xf4
437b881a:      	lsls	r7, r5, #0x1
437b881c:      	cmp	r1, #0xee
437b881e:      	lsls	r7, r5, #0x1
437b8820:      	cmp	r1, #0xd0
437b8822:      	lsls	r7, r5, #0x1
437b8824:      	pop	{r1, r2, r4, r5}
437b8826:      	lsls	r6, r7, #0x1
437b8828:      	push	{r4, r5, r6, lr}
437b882a:      	mov	r4, r0
437b882c:      	mov	r5, r1
437b882e:      	bl	0x437b9018 <_binary_input_a7s_av_cam_bin_start+0x278018> @ imm = #0x7e6
437b8832:      	ldr	r3, [pc, #0x28]         @ 0x437b885c <_binary_input_a7s_av_cam_bin_start+0x27785c>
437b8834:      	add	r3, pc
437b8836:      	cmp	r0, #0x2
437b8838:      	str	r0, [r3]
437b883a:      	beq	0x437b884c <_binary_input_a7s_av_cam_bin_start+0x27784c> @ imm = #0xe
437b883c:      	movs	r0, #0x2
437b883e:      	bl	0x437b900c <_binary_input_a7s_av_cam_bin_start+0x27800c> @ imm = #0x7ca
437b8842:      	mov	r0, r5
437b8844:      	mov.w	r1, #0x1020
437b8848:      	bl	0x43aec378 <_binary_input_a7s_av_cam_bin_start+0x5ab378> @ imm = #0x333b2c
437b884c:      	mov	r0, r4
437b884e:      	bl	0x43ad726a <_binary_input_a7s_av_cam_bin_start+0x59626a> @ imm = #0x31ea18
437b8852:      	pop.w	{r4, r5, r6, lr}
437b8856:      	b.w	0x43aec1ca <_binary_input_a7s_av_cam_bin_start+0x5ab1ca> @ imm = #0x333970
437b885a:      	nop
437b885c:      	cmp	r1, #0xa8
437b885e:      	lsls	r7, r5, #0x1
437b8860:      	push	{r4, lr}
437b8862:      	bl	0x43ad726e <_binary_input_a7s_av_cam_bin_start+0x59626e> @ imm = #0x31ea08
437b8866:      	mov	r4, r0
437b8868:      	ldr	r0, [pc, #0x10]         @ 0x437b887c <_binary_input_a7s_av_cam_bin_start+0x27787c>
437b886a:      	add	r0, pc
437b886c:      	ldr	r0, [r0]
437b886e:      	bl	0x437b900c <_binary_input_a7s_av_cam_bin_start+0x27800c> @ imm = #0x79a
437b8872:      	mov	r0, r4
437b8874:      	pop.w	{r4, lr}
437b8878:      	b.w	0x43aec1ca <_binary_input_a7s_av_cam_bin_start+0x5ab1ca> @ imm = #0x33394e
437b887c:      	cmp	r1, #0x72
437b887e:      	lsls	r7, r5, #0x1
437b8880:      	ldr	r3, [pc, #0x8]          @ 0x437b888c <_binary_input_a7s_av_cam_bin_start+0x27788c>
437b8882:      	ldr	r2, [pc, #0xc]          @ 0x437b8890 <_binary_input_a7s_av_cam_bin_start+0x277890>
437b8884:      	add	r3, pc
437b8886:      	ldr	r3, [r3, r2]
437b8888:      	ldr	r0, [r3]
437b888a:      	bx	lr
437b888c:      	pop	{r3, r4, r5, r7}
437b888e:      	lsls	r6, r0, #0x2
437b8890:      	asrs	r4, r1, #0x16
437b8892:      	movs	r0, r0
437b8894:      	ldr	r0, [pc, #0x4]          @ 0x437b889c <_binary_input_a7s_av_cam_bin_start+0x27789c>
437b8896:      	add	r0, pc
437b8898:      	bx	lr
437b889a:      	nop
437b889c:      	cmp	r1, #0x5a
437b889e:      	lsls	r7, r5, #0x1
437b88a0:      	ldr	r3, [pc, #0x4]          @ 0x437b88a8 <_binary_input_a7s_av_cam_bin_start+0x2778a8>
437b88a2:      	add	r3, pc
437b88a4:      	ldrb	r0, [r3]
437b88a6:      	bx	lr
437b88a8:      	cbnz	r4, 0x437b8914 <_binary_input_a7s_av_cam_bin_start+0x277914> @ imm = #0x68
437b88aa:      	lsls	r6, r7, #0x1
437b88ac:      	ldr	r3, [pc, #0x34]         @ 0x437b88e4 <_binary_input_a7s_av_cam_bin_start+0x2778e4>
437b88ae:      	push	{r4, lr}
437b88b0:      	add	r3, pc
437b88b2:      	mov	r4, r0
437b88b4:      	strb	r0, [r3]
437b88b6:      	bl	0x437b88a0 <_binary_input_a7s_av_cam_bin_start+0x2778a0> @ imm = #-0x1a
437b88ba:      	ldr	r3, [pc, #0x2c]         @ 0x437b88e8 <_binary_input_a7s_av_cam_bin_start+0x2778e8>
437b88bc:      	add	r3, pc
437b88be:      	strb	r0, [r3, #0x4]
437b88c0:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc60dc
437b88c4:      	bl	0x43ad96ce <_binary_input_a7s_av_cam_bin_start+0x5986ce> @ imm = #0x320e06
437b88c8:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc60e4
437b88cc:      	mov	r1, r4
437b88ce:      	bl	0x43ad9744 <_binary_input_a7s_av_cam_bin_start+0x598744> @ imm = #0x320e72
437b88d2:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc60ee
437b88d6:      	ldr	r1, [pc, #0x14]         @ 0x437b88ec <_binary_input_a7s_av_cam_bin_start+0x2778ec>
437b88d8:      	add	r1, pc
437b88da:      	pop.w	{r4, lr}
437b88de:      	b.w	0x436f2820 <_binary_input_a7s_av_cam_bin_start+0x1b1820> @ imm = #-0xc60c2
437b88e2:      	nop
437b88e4:      	cbnz	r6, 0x437b894c <_binary_input_a7s_av_cam_bin_start+0x27794c> @ imm = #0x64
437b88e6:      	lsls	r6, r7, #0x1
437b88e8:      	lsrs	r4, r5, #0x19
437b88ea:      	lsls	r4, r0, #0x2
437b88ec:      	cmp	r1, #0x18
437b88ee:      	lsls	r7, r5, #0x1
437b88f0:      	ldr	r3, [pc, #0x4]          @ 0x437b88f8 <_binary_input_a7s_av_cam_bin_start+0x2778f8>
437b88f2:      	add	r3, pc
437b88f4:      	str	r0, [r3]
437b88f6:      	bx	lr
437b88f8:      	lsrs	r6, r6, #0x18
437b88fa:      	lsls	r4, r0, #0x2
437b88fc:      	ldr	r3, [pc, #0x20]         @ 0x437b8920 <_binary_input_a7s_av_cam_bin_start+0x277920>
437b88fe:      	push	{r4, r5, lr}
437b8900:      	add	r3, pc
437b8902:      	ldr	r5, [pc, #0x20]         @ 0x437b8924 <_binary_input_a7s_av_cam_bin_start+0x277924>
437b8904:      	ldrb.w	r4, [r3, #0x3c]
437b8908:      	add	r5, pc
437b890a:      	ldrb.w	r3, [r3, #0x3d]
437b890e:      	eors	r0, r4
437b8910:      	strb	r0, [r2, #0x14]
437b8912:      	eor.w	r3, r1, r3
437b8916:      	strb	r0, [r5, #0x6]
437b8918:      	strb	r3, [r5, #0x5]
437b891a:      	strb	r3, [r2, #0x15]
437b891c:      	pop	{r4, r5, pc}
437b891e:      	nop
437b8920:      	cmp	r0, #0xf0
437b8922:      	lsls	r7, r5, #0x1
437b8924:      	lsrs	r0, r4, #0x18
437b8926:      	lsls	r4, r0, #0x2
437b8928:      	ldr	r3, [pc, #0x18]         @ 0x437b8944 <_binary_input_a7s_av_cam_bin_start+0x277944>
437b892a:      	push	{r4, lr}
437b892c:      	add	r3, pc
437b892e:      	ldrb.w	r4, [r3, #0x3c]
437b8932:      	eors	r0, r4
437b8934:      	strb	r0, [r2, #0x14]
437b8936:      	ldrb.w	r3, [r3, #0x3d]
437b893a:      	eor.w	r3, r1, r3
437b893e:      	strb	r3, [r2, #0x15]
437b8940:      	pop	{r4, pc}
437b8942:      	nop
437b8944:      	cmp	r0, #0xc4
437b8946:      	lsls	r7, r5, #0x1
437b8948:      	push	{r4, r5, r6, lr}
437b894a:      	mov	r4, r3
437b894c:      	ldr	r3, [pc, #0x20]         @ 0x437b8970 <_binary_input_a7s_av_cam_bin_start+0x277970>
437b894e:      	add	r3, pc
437b8950:      	ldrb.w	r5, [r3, #0x3c]
437b8954:      	ldrb.w	r6, [r3, #0x3d]
437b8958:      	str	r0, [r4]
437b895a:      	eor.w	r5, r1, r5
437b895e:      	eor.w	r6, r2, r6
437b8962:      	bl	0x437b88a0 <_binary_input_a7s_av_cam_bin_start+0x2778a0> @ imm = #-0xc6
437b8966:      	strb	r5, [r4, #0x6]
437b8968:      	strb	r6, [r4, #0x5]
437b896a:      	strb	r0, [r4, #0x4]
437b896c:      	pop	{r4, r5, r6, pc}
437b896e:      	nop
437b8970:      	cmp	r0, #0xa2
437b8972:      	lsls	r7, r5, #0x1
437b8974:      	ldr	r3, [pc, #0x20]         @ 0x437b8998 <_binary_input_a7s_av_cam_bin_start+0x277998>
437b8976:      	push	{r4, lr}
437b8978:      	add	r3, pc
437b897a:      	ldr	r2, [r3]
437b897c:      	cmp	r2, r0
437b897e:      	bge	0x437b8996 <_binary_input_a7s_av_cam_bin_start+0x277996> @ imm = #0x14
437b8980:      	cmp	r0, #0x1
437b8982:      	str	r0, [r3]
437b8984:      	bne	0x437b8996 <_binary_input_a7s_av_cam_bin_start+0x277996> @ imm = #0xe
437b8986:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc61a2
437b898a:      	ldr	r1, [pc, #0x10]         @ 0x437b899c <_binary_input_a7s_av_cam_bin_start+0x27799c>
437b898c:      	add	r1, pc
437b898e:      	pop.w	{r4, lr}
437b8992:      	b.w	0x436f2910 <_binary_input_a7s_av_cam_bin_start+0x1b1910> @ imm = #-0xc6086
437b8996:      	pop	{r4, pc}
437b8998:      	cmp	r0, #0xe8
437b899a:      	lsls	r7, r5, #0x1
437b899c:      	lsrs	r4, r3, #0x16
437b899e:      	lsls	r4, r0, #0x2
437b89a0:      	ldr	r3, [pc, #0x8]          @ 0x437b89ac <_binary_input_a7s_av_cam_bin_start+0x2779ac>
437b89a2:      	movs	r2, #0x0
437b89a4:      	add	r3, pc
437b89a6:      	str	r2, [r3]
437b89a8:      	bx	lr
437b89aa:      	nop
437b89ac:      	cmp	r0, #0xbc
437b89ae:      	lsls	r7, r5, #0x1
437b89b0:      	ldr	r0, [pc, #0x4]          @ 0x437b89b8 <_binary_input_a7s_av_cam_bin_start+0x2779b8>
437b89b2:      	add	r0, pc
437b89b4:      	ldr	r0, [r0]
437b89b6:      	bx	lr
437b89b8:      	cmp	r0, #0xae
437b89ba:      	lsls	r7, r5, #0x1
437b89bc:      	push	{r4, lr}
437b89be:      	ldr	r4, [pc, #0x28]         @ 0x437b89e8 <_binary_input_a7s_av_cam_bin_start+0x2779e8>
437b89c0:      	add	r4, pc
437b89c2:      	ldr	r4, [r4]
437b89c4:      	cmp	r4, #0x1
437b89c6:      	beq	0x437b89d4 <_binary_input_a7s_av_cam_bin_start+0x2779d4> @ imm = #0xa
437b89c8:      	cmp	r4, #0x2
437b89ca:      	beq	0x437b89e6 <_binary_input_a7s_av_cam_bin_start+0x2779e6> @ imm = #0x18
437b89cc:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc61e8
437b89d0:      	movs	r1, #0x0
437b89d2:      	b	0x437b89de <_binary_input_a7s_av_cam_bin_start+0x2779de> @ imm = #0x8
437b89d4:      	bl	0x437b8b04 <_binary_input_a7s_av_cam_bin_start+0x277b04> @ imm = #0x12c
437b89d8:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc61f4
437b89dc:      	mov	r1, r4
437b89de:      	pop.w	{r4, lr}
437b89e2:      	b.w	0x43ad9792 <_binary_input_a7s_av_cam_bin_start+0x598792> @ imm = #0x320dac
437b89e6:      	pop	{r4, pc}
437b89e8:      	cmp	r0, #0xa0
437b89ea:      	lsls	r7, r5, #0x1
437b89ec:      	ldr	r3, [pc, #0x4]          @ 0x437b89f4 <_binary_input_a7s_av_cam_bin_start+0x2779f4>
437b89ee:      	add	r3, pc
437b89f0:      	ldrb	r0, [r3]
437b89f2:      	bx	lr
437b89f4:      	rev16	r1, r3
437b89f6:      	lsls	r6, r7, #0x1
437b89f8:      	ldr	r3, [pc, #0x8c]         @ 0x437b8a88 <_binary_input_a7s_av_cam_bin_start+0x277a88>
437b89fa:      	push	{r4, r5, lr}
437b89fc:      	add	r3, pc
437b89fe:      	ldr	r5, [pc, #0x8c]         @ 0x437b8a8c <_binary_input_a7s_av_cam_bin_start+0x277a8c>
437b8a00:      	sub	sp, #0x74
437b8a02:      	ldrb	r3, [r3]
437b8a04:      	add	r5, pc
437b8a06:      	cmp	r3, #0x0
437b8a08:      	bne	0x437b8a82 <_binary_input_a7s_av_cam_bin_start+0x277a82> @ imm = #0x76
437b8a0a:      	ldr	r4, [pc, #0x84]         @ 0x437b8a90 <_binary_input_a7s_av_cam_bin_start+0x277a90>
437b8a0c:      	add	r4, pc
437b8a0e:      	ldr	r3, [r4]
437b8a10:      	cbnz	r3, 0x437b8a38 <_binary_input_a7s_av_cam_bin_start+0x277a38> @ imm = #0x24
437b8a12:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc622e
437b8a16:      	mov	r1, sp
437b8a18:      	bl	0x436f2820 <_binary_input_a7s_av_cam_bin_start+0x1b1820> @ imm = #-0xc61fc
437b8a1c:      	ldrb.w	r1, [sp, #0x1]
437b8a20:      	ldr	r3, [pc, #0x70]         @ 0x437b8a94 <_binary_input_a7s_av_cam_bin_start+0x277a94>
437b8a22:      	str	r1, [r4]
437b8a24:      	ldr	r3, [r5, r3]
437b8a26:      	ldrb.w	r3, [r3, #0x26]
437b8a2a:      	tst.w	r3, #0x10
437b8a2e:      	beq	0x437b8a38 <_binary_input_a7s_av_cam_bin_start+0x277a38> @ imm = #0x6
437b8a30:      	ldr	r0, [pc, #0x64]         @ 0x437b8a98 <_binary_input_a7s_av_cam_bin_start+0x277a98>
437b8a32:      	add	r0, pc
437b8a34:      	bl	0x438f7114 <_binary_input_a7s_av_cam_bin_start+0x3b6114> @ imm = #0x13e6dc
437b8a38:      	ldr	r4, [pc, #0x60]         @ 0x437b8a9c <_binary_input_a7s_av_cam_bin_start+0x277a9c>
437b8a3a:      	ldr	r3, [pc, #0x64]         @ 0x437b8aa0 <_binary_input_a7s_av_cam_bin_start+0x277aa0>
437b8a3c:      	add	r4, pc
437b8a3e:      	add	r3, pc
437b8a40:      	ldr	r3, [r3]
437b8a42:      	ldr	r2, [r4]
437b8a44:      	cmp	r2, r3
437b8a46:      	bhs	0x437b8a76 <_binary_input_a7s_av_cam_bin_start+0x277a76> @ imm = #0x2c
437b8a48:      	adds	r2, #0x1
437b8a4a:      	str	r2, [r4]
437b8a4c:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc6268
437b8a50:      	ldrb	r1, [r4]
437b8a52:      	bl	0x43ad9774 <_binary_input_a7s_av_cam_bin_start+0x598774> @ imm = #0x320d1e
437b8a56:      	movs	r0, #0x2
437b8a58:      	bl	0x437b8974 <_binary_input_a7s_av_cam_bin_start+0x277974> @ imm = #-0xe8
437b8a5c:      	ldr	r3, [pc, #0x34]         @ 0x437b8a94 <_binary_input_a7s_av_cam_bin_start+0x277a94>
437b8a5e:      	ldr	r3, [r5, r3]
437b8a60:      	ldrb.w	r3, [r3, #0x26]
437b8a64:      	tst.w	r3, #0x10
437b8a68:      	beq	0x437b8a82 <_binary_input_a7s_av_cam_bin_start+0x277a82> @ imm = #0x16
437b8a6a:      	ldr	r0, [pc, #0x38]         @ 0x437b8aa4 <_binary_input_a7s_av_cam_bin_start+0x277aa4>
437b8a6c:      	ldr	r1, [r4]
437b8a6e:      	add	r0, pc
437b8a70:      	bl	0x438f7114 <_binary_input_a7s_av_cam_bin_start+0x3b6114> @ imm = #0x13e6a0
437b8a74:      	b	0x437b8a82 <_binary_input_a7s_av_cam_bin_start+0x277a82> @ imm = #0xa
437b8a76:      	ldr	r3, [pc, #0x30]         @ 0x437b8aa8 <_binary_input_a7s_av_cam_bin_start+0x277aa8>
437b8a78:      	movs	r2, #0x1
437b8a7a:      	add	r3, pc
437b8a7c:      	strb	r2, [r3]
437b8a7e:      	movs	r3, #0x0
437b8a80:      	str	r3, [r4]
437b8a82:      	add	sp, #0x74
437b8a84:      	pop	{r4, r5, pc}
437b8a86:      	nop
437b8a88:      	rev16	r3, r1
437b8a8a:      	lsls	r6, r7, #0x1
437b8a8c:      	cbnz	r0, 0x437b8ade <_binary_input_a7s_av_cam_bin_start+0x277ade> @ imm = #0x4e
437b8a8e:      	lsls	r6, r0, #0x2
437b8a90:      	cmp	r0, #0x58
437b8a92:      	lsls	r7, r5, #0x1
437b8a94:      	ldrb	r4, [r0, #0x3]
437b8a96:      	movs	r0, r0
437b8a98:      	lsrs	r5, r4, #0xa
437b8a9a:      	lsls	r7, r1, #0x1
437b8a9c:      	cmp	r0, #0x2c
437b8a9e:      	lsls	r7, r5, #0x1
437b8aa0:      	cmp	r0, #0x26
437b8aa2:      	lsls	r7, r5, #0x1
437b8aa4:      	lsrs	r4, r7, #0x9
437b8aa6:      	lsls	r7, r1, #0x1
437b8aa8:      	cbnz	r5, 0x437b8ade <_binary_input_a7s_av_cam_bin_start+0x277ade> @ imm = #0x32
437b8aaa:      	lsls	r6, r7, #0x1
437b8aac:      	push	{r3, lr}
437b8aae:      	bl	0x436f27e8 <_binary_input_a7s_av_cam_bin_start+0x1b17e8> @ imm = #-0xc62ca
437b8ab2:      	bl	0x43ad9780 <_binary_input_a7s_av_cam_bin_start+0x598780> @ imm = #0x320cca
437b8ab6:      	ldr	r3, [pc, #0x10]         @ 0x437b8ac8 <_binary_input_a7s_av_cam_bin_start+0x277ac8>
437b8ab8:      	movs	r2, #0x0
437b8aba:      	add	r3, pc
437b8abc:      	strb	r2, [r3]
437b8abe:      	ldr	r3, [pc, #0xc]          @ 0x437b8acc <_binary_input_a7s_av_cam_bin_start+0x277acc>
437b8ac0:      	add	r3, pc
437b8ac2:      	str	r2, [r3]
437b8ac4:      	pop	{r3, pc}
437b8ac6:      	nop
437b8ac8:      	cbnz	r5, 0x437b8aee <_binary_input_a7s_av_cam_bin_start+0x277aee> @ imm = #0x22
437b8aca:      	lsls	r6, r7, #0x1
437b8acc:      	movs	r7, #0xa8
437b8ace:      	lsls	r7, r5, #0x1
437b8ad0:      	ldr	r3, [pc, #0xc]          @ 0x437b8ae0 <_binary_input_a7s_av_cam_bin_start+0x277ae0>
437b8ad2:      	movs	r2, #0x0
437b8ad4:      	add	r3, pc
437b8ad6:      	strb	r2, [r3]
437b8ad8:      	ldr	r3, [pc, #0x8]          @ 0x437b8ae4 <_binary_input_a7s_av_cam_bin_start+0x277ae4>
437b8ada:      	add	r3, pc
437b8adc:      	str	r2, [r3]
437b8ade:      	bx	lr
437b8ae0:      	cbnz	r3, 0x437b8b00 <_binary_input_a7s_av_cam_bin_start+0x277b00> @ imm = #0x1c
437b8ae2:      	lsls	r6, r7, #0x1
437b8ae4:      	movs	r7, #0x8e
437b8ae6:      	lsls	r7, r5, #0x1
437b8ae8:      	push	{r4, lr}
437b8aea:      	mov.w	r1, #0x1000
437b8aee:      	mov	r4, r0
437b8af0:      	movs	r0, #0x1a
437b8af2:      	bl	0x4355f068 <_binary_input_a7s_av_cam_bin_start+0x1e068> @ imm = #-0x259a8e
437b8af6:      	ldr	r3, [pc, #0x8]          @ 0x437b8b00 <_binary_input_a7s_av_cam_bin_start+0x277b00>
437b8af8:      	add	r3, pc
437b8afa:      	str	r4, [r3]
437b8afc:      	pop	{r4, pc}
437b8afe:      	nop
437b8b00:      	cmp	r0, #0x80
437b8b02:      	lsls	r7, r5, #0x1
437b8b04:      	push	{r0, r1, r2, r3, r4, lr}
437b8b06:      	movs	r3, #0x5
437b8b08:      	movs	r0, #0x1a
437b8b0a:      	str	r3, [sp]
437b8b0c:      	mov.w	r1, #0x1000
437b8b10:      	movs	r2, #0x0
437b8b12:      	add	r3, sp, #0xc
437b8b14:      	bl	0x4355f0a0 <_binary_input_a7s_av_cam_bin_start+0x1e0a0> @ imm = #-0x259a78
437b8b18:      	cbz	r0, 0x437b8b22 <_binary_input_a7s_av_cam_bin_start+0x277b22> @ imm = #0x6
437b8b1a:      	ldr	r0, [pc, #0xc]          @ 0x437b8b28 <_binary_input_a7s_av_cam_bin_start+0x277b28>
437b8b1c:      	add	r0, pc
437b8b1e:      	bl	0x438f7114 <_binary_input_a7s_av_cam_bin_start+0x3b6114> @ imm = #0x13e5f2
437b8b22:      	add	sp, #0x14
437b8b24:      	pop	{pc}
437b8b26:      	nop
437b8b28:      	lsrs	r5, r4, #0x7
437b8b2a:      	lsls	r7, r1, #0x1
437b8b2c:      	ldr	r0, [pc, #0x4]          @ 0x437b8b34 <_binary_input_a7s_av_cam_bin_start+0x277b34>
437b8b2e:      	add	r0, pc
437b8b30:      	ldr	r0, [r0]
437b8b32:      	bx	lr
437b8b34:      	cmp	r0, #0x4a
437b8b36:      	lsls	r7, r5, #0x1
437b8b38:      	ldr	r3, [pc, #0x4]          @ 0x437b8b40 <_binary_input_a7s_av_cam_bin_start+0x277b40>
437b8b3a:      	add	r3, pc
437b8b3c:      	str	r0, [r3]
437b8b3e:      	bx	lr
437b8b40:      	movs	r7, #0x32
437b8b42:      	lsls	r7, r5, #0x1
437b8b44:      	push	{r4, lr}
437b8b46:      	mov	r1, r0
437b8b48:      	ldr	r4, [pc, #0x38]         @ 0x437b8b84 <_binary_input_a7s_av_cam_bin_start+0x277b84>
437b8b4a:      	ldr	r3, [pc, #0x3c]         @ 0x437b8b88 <_binary_input_a7s_av_cam_bin_start+0x277b88>
437b8b4c:      	add	r4, pc
437b8b4e:      	add	r3, pc
437b8b50:      	mov	r0, r4
437b8b52:      	ldrh	r2, [r4, #0x14]
437b8b54:      	str	r2, [r3]
437b8b56:      	mov.w	r2, #0x100
437b8b5a:      	blx	0x439b3918 <_binary_input_a7s_av_cam_bin_start+0x472918> @ imm = #0x1fadbc
437b8b5e:      	ldr	r0, [r4, #0x20]
437b8b60:      	bl	0x43aebe94 <_binary_input_a7s_av_cam_bin_start+0x5aae94> @ imm = #0x333330
437b8b64:      	ldr	r3, [pc, #0x24]         @ 0x437b8b8c <_binary_input_a7s_av_cam_bin_start+0x277b8c>
437b8b66:      	movs	r2, #0x1
437b8b68:      	add	r3, pc
437b8b6a:      	strb	r2, [r3, #0x4]
437b8b6c:      	ldrh	r2, [r4, #0x14]
437b8b6e:      	strh	r2, [r3, #0x6]
437b8b70:      	ldr	r2, [pc, #0x1c]         @ 0x437b8b90 <_binary_input_a7s_av_cam_bin_start+0x277b90>
437b8b72:      	add	r2, pc
437b8b74:      	ldr	r2, [r2]
437b8b76:      	str	r2, [r3, #0x8]
437b8b78:      	str	r0, [r3]
437b8b7a:      	ldr	r0, [r4, #0x20]
437b8b7c:      	pop.w	{r4, lr}
