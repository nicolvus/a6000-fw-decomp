/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "4379b44c" */

void FUN_4379b44c(int param_1,int param_2,undefined4 param_3)

{
  undefined1 *puVar1;
  undefined2 *puVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  short sVar5;
  short sVar6;
  undefined2 uVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  char cVar11;
  undefined *puVar12;
  undefined4 *puVar13;
  int iVar14;
  undefined1 uVar15;
  
  if ((&DAT_43e9f7dc)[param_1] == 0) {
    return;
  }
  (&DAT_43e9f7dc)[param_1] = 2;
  iVar9 = param_1;
  iVar14 = param_2;
  if ((*(int *)(param_2 + 0x10) != 0) && (iVar8 = FUN_43ae9674(), iVar8 != 0)) {
    FUN_43b2a296(&DAT_43e9f0d8 + param_1 * 0x28,5);
    FUN_4390366c(&DAT_43e9f0d8 + param_1 * 0x28,*(undefined4 *)(param_2 + 0x10),0,5);
  }
  iVar8 = FUN_43aea1aa(param_1);
  if ((iVar8 != 0) && (*(char *)(param_2 + 200) == '\x01')) {
    FUN_43b2a296(&DAT_43e9f2e8 + param_1 * 0x28,5);
    FUN_4390366c(&DAT_43e9f2e8 + param_1 * 0x28,*(undefined4 *)(param_2 + 0xd4),0,5,iVar9,iVar14,
                 param_3);
  }
  if ((*(int *)(param_2 + 0x10) == 0) || (iVar9 = FUN_43ae9674(), iVar9 == 0)) {
    iVar9 = param_1 * 0x38;
    (&DAT_43e9f388)[iVar9] = 0;
    *(undefined4 *)(&DAT_43e9f38c + iVar9) = 0;
    *(undefined2 *)(&DAT_43e9f390 + iVar9) = 0xffff;
    *(undefined4 *)(&DAT_43e9f394 + iVar9) = 0;
  }
  else {
    iVar9 = param_1 * 0x38;
    (&DAT_43e9f388)[iVar9] = 1;
    uVar4 = *(undefined2 *)(&DAT_43e9f0d8 + param_1 * 0x28);
    uVar10 = *(undefined4 *)(&DAT_43e9f0dc + param_1 * 0x28);
    *(undefined4 *)(&DAT_43e9f394 + iVar9) = 0;
    *(undefined2 *)(&DAT_43e9f390 + iVar9) = uVar4;
    *(undefined4 *)(&DAT_43e9f38c + iVar9) = uVar10;
  }
  iVar9 = param_1 * 0x38;
  (&DAT_43e9f398)[iVar9] = *(undefined1 *)(param_2 + 0x1c);
  (&DAT_43e9f399)[iVar9] = *(undefined1 *)(param_2 + 0x1d);
  (&DAT_43e9f39b)[iVar9] = *(int *)(param_2 + 0xe4) == 1;
  uVar4 = *(undefined2 *)(param_2 + 0x24);
  iVar9 = param_1 * 0x38;
  *(undefined2 *)(&DAT_43e9f3a0 + iVar9) = *(undefined2 *)(param_2 + 0x22);
  *(undefined2 *)(&DAT_43e9f3a2 + iVar9) = uVar4;
  sVar5 = *(short *)(DAT_4402546c + 0x96);
  if ((sVar5 == 0) || (sVar6 = *(short *)(DAT_4402546c + 0x98), sVar6 == 0)) {
    uVar4 = *(undefined2 *)(param_2 + 0x20);
    uVar7 = *(undefined2 *)(param_2 + 0x26);
    iVar9 = param_1 * 0x38;
    *(undefined2 *)(&DAT_43e9f39c + iVar9) = *(undefined2 *)(param_2 + 0x1e);
    *(undefined2 *)(&DAT_43e9f39e + iVar9) = uVar4;
    uVar4 = *(undefined2 *)(param_2 + 0x28);
    uVar3 = *(undefined2 *)(param_2 + 0x2a);
    *(undefined2 *)(&DAT_43e9f3a4 + iVar9) = uVar7;
    *(undefined2 *)(&DAT_43e9f3a6 + iVar9) = uVar4;
    uVar4 = *(undefined2 *)(param_2 + 0x2c);
    uVar7 = *(undefined2 *)(param_2 + 0x2e);
    *(undefined2 *)(&DAT_43e9f3a8 + iVar9) = uVar3;
    uVar3 = *(undefined2 *)(param_2 + 0x30);
    *(undefined2 *)(&DAT_43e9f3aa + iVar9) = uVar4;
    *(undefined2 *)(&DAT_43e9f3ac + iVar9) = uVar7;
    *(undefined2 *)(&DAT_43e9f3ae + iVar9) = uVar3;
    uVar4 = *(undefined2 *)(param_2 + 0x32);
    *(undefined2 *)(&DAT_43e9f3b2 + iVar9) = *(undefined2 *)(param_2 + 0x34);
    *(undefined2 *)(&DAT_43e9f3b0 + iVar9) = uVar4;
  }
  else {
    uVar4 = *(undefined2 *)(DAT_4402546c + 0x92);
    uVar7 = *(undefined2 *)(DAT_4402546c + 0x94);
    *(short *)(&DAT_43e9f3a8 + iVar9) = sVar5;
    *(short *)(&DAT_43e9f3b0 + iVar9) = sVar5;
    *(undefined2 *)(&DAT_43e9f3a6 + iVar9) = uVar7;
    *(short *)(&DAT_43e9f3b2 + iVar9) = sVar6;
    *(undefined2 *)(&DAT_43e9f3a4 + iVar9) = uVar4;
    *(short *)(&DAT_43e9f39c + iVar9) = sVar5;
    cVar11 = *(char *)(param_2 + 0x3e);
    *(short *)(&DAT_43e9f3aa + iVar9) = sVar6;
    *(undefined2 *)(&DAT_43e9f3ac + iVar9) = 0;
    *(undefined2 *)(&DAT_43e9f3ae + iVar9) = 0;
    *(short *)(&DAT_43e9f39e + iVar9) = sVar6;
    if (cVar11 != '\0') {
      *(short *)(&DAT_43e9f39e + iVar9) = sVar6 << 1;
    }
  }
  (&DAT_43e9f3b4)[param_1 * 0x38] = 0;
  (&DAT_43e9f3b5)[param_1 * 0x38] = 0;
  switch(*(undefined4 *)(param_2 + 0x38)) {
  case 0:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 2;
    break;
  case 1:
    goto LAB_4379b67c;
  case 2:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 1;
    break;
  case 3:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 5;
    break;
  case 4:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 3;
    break;
  case 5:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 4;
    break;
  default:
    FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,0x109);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,0x109);
LAB_4379b67c:
    (&DAT_43e9f3b6)[param_1 * 0x38] = 0;
    goto LAB_4379b67e;
  }
  puVar12[0x2e] = uVar15;
LAB_4379b67e:
  if (*(char *)(param_2 + 0x3c) == '\0') {
    (&DAT_43e9f3b7)[param_1 * 0x38] = 0;
  }
  else {
    (&DAT_43e9f3b7)[param_1 * 0x38] = 1;
  }
  if (*(char *)(param_2 + 0x3d) == '\0') {
    (&DAT_43e9f3bb)[param_1 * 0x38] = 0;
  }
  else {
    (&DAT_43e9f3bb)[param_1 * 0x38] = 1;
  }
  cVar11 = *(char *)(param_2 + 0x3e);
  iVar9 = param_1 * 0x38;
  *(undefined2 *)(&DAT_43e9f3bc + iVar9) = 0x40;
  if (cVar11 == '\0') {
    (&DAT_43e9f3b8)[iVar9] = 1;
    uVar15 = 2;
    (&DAT_43e9f3b9)[iVar9] = 1;
LAB_4379b706:
    (&DAT_43e9f3ba)[iVar9] = uVar15;
  }
  else {
    (&DAT_43e9f3b8)[iVar9] = 0;
    (&DAT_43e9f3b9)[iVar9] = 0;
    if (*(int *)(param_2 + 0x40) == 0) {
      uVar15 = 1;
      goto LAB_4379b706;
    }
    (&DAT_43e9f3ba)[iVar9] = 0;
  }
  (&DAT_43f9a4d5)[param_1 * 6] = *(int *)(param_2 + 0x4c) != 1;
  if (*(int *)(param_2 + 0x44) == 1) {
    uVar15 = 3;
  }
  else {
    if (*(int *)(param_2 + 0x44) == 2) {
      (&DAT_43f9a4d6)[param_1 * 6] = 2;
      goto LAB_4379b770;
    }
    if (*(int *)(param_2 + 0x48) == 1) {
      (&DAT_43f9a4d6)[param_1 * 6] = 1;
      goto LAB_4379b770;
    }
    uVar15 = 0;
  }
  (&DAT_43f9a4d6)[param_1 * 6] = uVar15;
LAB_4379b770:
  if (*(char *)(param_2 + 0x50) == '\0') {
    (&DAT_43f9a4d7)[param_1 * 6] = 1;
  }
  else {
    (&DAT_43f9a4d7)[param_1 * 6] = 0;
  }
  if (*(char *)(param_2 + 0x3e) == '\0') {
    (&DAT_43f9a4d8)[param_1 * 6] = 1;
  }
  else {
    (&DAT_43f9a4d8)[param_1 * 6] = 0;
  }
  (&DAT_43f9a4d9)[param_1 * 6] = 0;
  (&DAT_43f9a4da)[param_1 * 6] = 5;
  iVar9 = param_1 * 0x14;
  *(undefined4 *)(&DAT_43e9f46c + iVar9) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(&DAT_43e9f470 + iVar9) = *(undefined4 *)(param_2 + 0xc);
  (&DAT_43e9f474)[param_1 * 5] = *(undefined4 *)(param_2 + 0x14);
  (&DAT_43e9f478)[param_1 * 5] = *(undefined4 *)(param_2 + 0x18);
  uVar10 = FUN_43ae2c02(param_2);
  *(undefined4 *)(&DAT_43e9f47c + iVar9) = uVar10;
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 != 0) {
    DAT_43e9f1c0 = *(undefined4 *)(param_2 + 0x5c);
    DAT_43e9f1c4 = *(undefined4 *)(param_2 + 0x60);
  }
  iVar9 = param_1 * 0xc4;
  puVar13 = &DAT_43e9f4c4 + param_1 * 0x31;
  (&DAT_43e9f4f0)[iVar9] = *(undefined1 *)(param_2 + 100);
  if (*(char *)(param_2 + 100) == '\x01') {
    cVar11 = '\x14';
    *(undefined4 *)(&DAT_43e9f4f4 + iVar9) = *(undefined4 *)(param_2 + 0x68);
    *(undefined4 *)(&DAT_43e9f4f8 + iVar9) = 0;
    iVar9 = param_2;
    do {
      cVar11 = cVar11 + -1;
      *(undefined1 *)(puVar13 + 0xe) = *(undefined1 *)(iVar9 + 0x6c);
      *(undefined1 *)(puVar13 + 0x13) = *(undefined1 *)(iVar9 + 0x80);
      puVar1 = (undefined1 *)(iVar9 + 0x94);
      iVar9 = iVar9 + 1;
      *(undefined1 *)(puVar13 + 0x18) = *puVar1;
      puVar13 = (undefined4 *)((int)puVar13 + 1);
    } while (cVar11 != '\0');
  }
  iVar9 = param_1 * 0xc4;
  puVar13 = &DAT_43e9f4c4 + param_1 * 0x31;
  (&DAT_43e9f538)[iVar9] = *(undefined1 *)(param_2 + 0xa8);
  if (*(char *)(param_2 + 0xa8) == '\x01') {
    *(undefined4 *)(&DAT_43e9f53c + iVar9) = *(undefined4 *)(param_2 + 0xac);
    *(undefined4 *)(&DAT_43e9f540 + iVar9) = 0;
    iVar9 = param_2;
    do {
      *(undefined2 *)(puVar13 + 0x20) = *(undefined2 *)(iVar9 + 0xb0);
      puVar2 = (undefined2 *)(iVar9 + 0xb2);
      iVar9 = iVar9 + 4;
      *(undefined2 *)((int)puVar13 + 0x82) = *puVar2;
      puVar13 = puVar13 + 1;
    } while (iVar9 != param_2 + 0x18);
  }
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 == 0) {
    iVar9 = param_1 * 0xc4;
    (&DAT_43e9f55c)[iVar9] = *(undefined1 *)(param_2 + 200);
    if (*(char *)(param_2 + 200) == '\x01') {
      uVar10 = *(undefined4 *)(param_2 + 0xcc);
      *(undefined4 *)(&DAT_43e9f564 + iVar9) = 0;
      *(undefined4 *)(&DAT_43e9f560 + iVar9) = uVar10;
      (&DAT_43e9f568)[iVar9] = *(undefined1 *)(param_2 + 0xd0);
      uVar10 = *(undefined4 *)(&DAT_43e9f2ec + param_1 * 0x28);
      *(undefined2 *)(&DAT_43e9f570 + iVar9) = *(undefined2 *)(&DAT_43e9f2e8 + param_1 * 0x28);
      *(undefined4 *)(&DAT_43e9f56c + iVar9) = uVar10;
    }
  }
  else {
    (&DAT_43e9f55c)[param_1 * 0xc4] = 0;
  }
  iVar9 = param_1 * 0xc4;
  (&DAT_43e9f572)[iVar9] = *(undefined1 *)(param_2 + 0xd8);
  (&DAT_43e9f573)[iVar9] = *(undefined1 *)(param_2 + 0xd9);
  (&DAT_43e9f574)[iVar9] = *(undefined1 *)(param_2 + 0xda);
  uVar4 = *(undefined2 *)(param_2 + 0xdc);
  (&DAT_43e9f578)[iVar9] = *(undefined1 *)(param_2 + 0xde);
  uVar15 = *(undefined1 *)(param_2 + 0xdf);
  *(undefined2 *)(&DAT_43e9f576 + iVar9) = uVar4;
  (&DAT_43e9f579)[iVar9] = uVar15;
  *(undefined2 *)(&DAT_43e9f57a + iVar9) = *(undefined2 *)(param_2 + 0xe0);
  iVar9 = FUN_43aea1aa(param_1);
  if (iVar9 != 0) {
    iVar9 = FUN_4379b408(param_1);
    iVar14 = *(int *)(param_2 + 0x54);
    if (iVar14 + 2U < 2) {
      uVar15 = 1;
    }
    else {
      uVar15 = 2;
    }
    (&DAT_43e9f0c0)[iVar9 * 0xc] = uVar15;
    iVar8 = *(int *)(param_2 + 0x58);
    if ((iVar8 == -1) || (iVar14 == -2)) {
      uVar15 = 1;
    }
    else {
      uVar15 = 2;
    }
    (&DAT_43e9f0c1)[iVar9 * 0xc] = uVar15;
    *(int *)(&DAT_43e9f0c4 + iVar9 * 0xc) = iVar14;
    *(int *)(&DAT_43e9f0c8 + iVar9 * 0xc) = iVar8;
  }
  iVar9 = FUN_43aea1aa(param_1);
  if (iVar9 != 0) {
    iVar9 = FUN_4379b408(param_1);
    iVar9 = iVar9 * 10;
    *(undefined2 *)(&DAT_43f79b86 + iVar9) = *(undefined2 *)(param_2 + 0xe8);
    uVar4 = *(undefined2 *)(param_2 + 0xea);
    uVar7 = *(undefined2 *)(param_2 + 0xec);
    *(undefined2 *)(&DAT_43f79b8c + iVar9) = *(undefined2 *)(param_2 + 0xee);
    uVar15 = *(undefined1 *)(param_2 + 0xf0);
    *(undefined2 *)(&DAT_43f79b88 + iVar9) = uVar4;
    *(undefined2 *)(&DAT_43f79b8a + iVar9) = uVar7;
    (&DAT_43f79b8e)[iVar9] = uVar15;
  }
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 != 0) {
    DAT_43e9f1e8 = *(undefined4 *)(param_2 + 0xf4);
    if (*(char *)(param_2 + 0x100) == '\0') {
      if (*(int *)(param_2 + 0xf8) == 2) {
        DAT_43e9f1ec = 1;
      }
      else if (*(int *)(param_2 + 0xf8) == 3) {
        DAT_43e9f1ec = 0;
      }
      else {
        DAT_43e9f1ec = 2;
      }
    }
    else if (*(int *)(param_2 + 0xfc) == 1) {
      DAT_43e9f1ec = 3;
    }
    else if (*(int *)(param_2 + 0xfc) == 2) {
      DAT_43e9f1ec = 4;
    }
    else {
      FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,0x1e0);
      FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,0x1e0);
    }
    DAT_43e9f1f0 = 0;
    DAT_43e9f1f8 = 0;
    DAT_43e9f1f4 = 0x1020;
    DAT_43e9f1fc = 1;
  }
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 != 0) {
    DAT_43e9f7d8 = (uint)(*(char *)(param_2 + 0x101) != '\0');
  }
  return;
}


/* query "44023940" */

/* query "43acabf4" */

void FUN_43acabf4(int param_1)

{
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 0x10) = 0;
  return;
}


/* query "4380f594" */

void FUN_4380f508(undefined2 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 auStack_50 [6];
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined2 *puStack_30;
  
  iVar2 = FUN_435612d0(0x8f0139,&puStack_30,0x9a,0);
  puVar1 = puStack_30;
  if (iVar2 == 0) {
    puStack_30[1] = param_1;
    *puStack_30 = 1;
    *(undefined4 *)(puStack_30 + 2) = param_2;
    *(undefined4 *)(puStack_30 + 4) = 0;
    *(undefined4 *)(puStack_30 + 6) = 0;
    puStack_30[8] = param_3;
    FUN_439c5a04(auStack_50,0,0x20);
    auStack_50[0] = 0x20;
    FUN_43561244(0x910042,auStack_50);
    *(undefined4 *)(puVar1 + 4) = uStack_38;
    *(undefined4 *)(puVar1 + 6) = uStack_34;
    iVar2 = FUN_439c5004(puVar1 + 10,0x81,param_4,&stack0x00000000);
    if (iVar2 < 0) {
      FUN_435612ec(0x8f0139,puStack_30);
    }
    else {
      if (0x7f < iVar2) {
        iVar2 = 0x80;
      }
      puVar1[9] = (short)iVar2 + 1;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x14) = 10;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x15) = 0;
      *(undefined4 *)(puStack_30 + -2) = 0x8f0139;
      FUN_4356120c();
    }
  }
  return;
}


/* query "4378f410" */

void s32_candidate_4378f410(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_20 [4];
  undefined1 auStack_1c [8];
  
  iVar1 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Drive_S_43ca2e3d);
  }
  iVar2 = FUN_43560de0(0x1a,0x80,0,auStack_20,5);
  if (iVar2 != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca2e48,*DAT_43e9920c);
    FUN_43902718(s_VD_Drive__wait_timeout__dV_43ca2e5c,*DAT_43e9920c);
  }
  if (param_1 == *DAT_43e9920c) {
    FUN_43ae1292(2);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_437fe7b4();
    if (DAT_43e9bcc8 == '\0') {
      DAT_43f79b80 = 0;
      DAT_4401d33c = 0xffff;
    }
    else {
      FUN_437876dc();
      iVar2 = FUN_43b00e5a();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 1;
      }
      iVar2 = thunk_FUN_436e8334();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 0x800;
      }
      iVar2 = FUN_43af0d5e(&DAT_43e99208);
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 2;
      }
      iVar2 = thunk_FUN_4384a184();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 4;
      }
      if (DAT_4401d33c != DAT_43f79b80) {
        FUN_43901a8c(4,0x200d,0x807);
        DAT_4401d33c = DAT_43f79b80;
      }
    }
    if ((*(int *)(DAT_43e99208 + 0xb4) == 2) ||
       ((iVar2 = DAT_43e9bcc0, DAT_43e9bcc8 != '\0' && (DAT_43f79b80 != 0x807)))) {
      iVar2 = DAT_43e9920c[0xc];
    }
    FUN_4378dfdc(DAT_43e9bccc,iVar2);
    thunk_FUN_437d8f1c(&DAT_43e99208,&DAT_43e9ced8);
    thunk_FUN_437cf928(&DAT_43e99208,&DAT_43e9d018);
    if (((*(char *)(iVar1 + 0x70) == '\0') && (iVar2 = FUN_437999e4(1,0xe), iVar2 != 0)) &&
       ((DAT_43e9bb1f == '\0' || (DAT_43e9920c[3] != 0)))) {
      auStack_1c[0] = 1;
      FUN_439e3870(auStack_1c);
    }
    FUN_437968b0(&DAT_43e99208);
    if (*(char *)(iVar1 + 0xbf) == '\0') {
      FUN_43ae129a(2);
    }
    FUN_43901480(5);
    if (param_1 == *DAT_43e9920c) {
      iVar2 = FUN_43ae916c();
      if (iVar2 == 0) {
        FUN_4379ce0c();
        thunk_FUN_437b7fe4();
        FUN_4379ce24(&DAT_43e99208);
      }
    }
    else {
      iVar2 = FUN_43ae8d4e();
      if (iVar2 != 0) {
        iVar3 = *DAT_43e9920c;
        iVar2 = thunk_FUN_436cd00c();
        FUN_4378eb78(3,9,1,&DAT_43ca2eb3,param_1,iVar3,(uint)(iVar2 - DAT_43e9920c[2]) >> 1);
        iVar3 = *DAT_43e9920c;
        iVar2 = thunk_FUN_436cd00c();
        FUN_43902718(s_Imaging__VD_Drive__overflow__dV___43ca2ec7,param_1,iVar3,
                     (uint)(iVar2 - DAT_43e9920c[2]) >> 1);
        if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
          FUN_43561540(s_VD_Drive_E_OF_43ca2ef3);
        }
      }
    }
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Drive_E_43ca2f01);
    }
  }
  else {
    iVar2 = FUN_43ae8d4e();
    if (iVar2 != 0) {
      iVar3 = *DAT_43e9920c;
      iVar2 = thunk_FUN_436cd00c();
      FUN_4378eb78(3,9,1,&DAT_43ca2e77,param_1,iVar3,(uint)(iVar2 - DAT_43e9920c[2]) >> 1);
      iVar3 = *DAT_43e9920c;
      iVar2 = thunk_FUN_436cd00c();
      FUN_43902718(s_VD_Drive__start_delayed__dV__>___43ca2e8b,param_1,iVar3,
                   (uint)(iVar2 - DAT_43e9920c[2]) >> 1);
      if ((*(byte *)(iVar1 + 0x1b) & 0x10) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* query "4379210c" */

void FUN_4379210c(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  byte bVar8;
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined1 auStack_2c [4];
  uint uStack_28;
  undefined1 auStack_24 [4];
  
  iVar2 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Post_S_43ca2f4b);
  }
  if (param_1 == *DAT_43e9920c) {
    FUN_43ae1292(4);
    iVar3 = FUN_43ae8d4e();
    if (iVar3 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_43728c70();
    FUN_4378f7a0(0xd35);
    DAT_43e9d394 = FUN_4377fdf8();
    FUN_43560e00(0x11,auStack_2c);
    iVar3 = FUN_4378e90c();
    if (iVar3 != 0) {
      uStack_28 = uStack_28 & 0xfffffffb | DAT_43e9bd4c & 4;
    }
    DAT_43e9bd4c = uStack_28;
    if (DAT_43f79b84 != 0) {
      DAT_43f79b82 = DAT_43f79b82 + 1;
      if (DAT_43f79b84 < DAT_43f79b82) {
        DAT_43f79b82 = 1;
        iVar3 = 0;
        do {
          *(undefined2 *)((int)&DAT_43f79b2e + iVar3) = 0;
          *(undefined2 *)((int)&DAT_43f79b48 + iVar3) = 0;
          *(undefined2 *)((int)&DAT_43f79b66 + iVar3) = 0;
          iVar3 = iVar3 + 2;
        } while (iVar3 != 0x1a);
      }
    }
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      if ((DAT_43e9bd4c & 4) == 0) {
        DAT_43e9d398 = FUN_437b4d64();
        FUN_43ae8e2c(&DAT_43e9b548,&DAT_43e99208);
        DAT_43f79b4c = 0;
      }
      else {
        DAT_43f79b6a = DAT_43f79b6a + 1;
        DAT_43f79b4c = DAT_43f79b4c + 1;
      }
    }
    if ((DAT_43e9bd4c & 8) == 0) {
      DAT_43e9d3a0 = FUN_4379fc20();
      FUN_43ae8e5c(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b4e = 0;
    }
    else {
      DAT_43f79b6c = DAT_43f79b6c + 1;
      DAT_43f79b4e = DAT_43f79b4e + 1;
    }
    if ((DAT_43e9bd4c & 0x20) == 0) {
      DAT_43e9d3a4 = FUN_437d0bc8();
      FUN_43ae8e74(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b52 = 0;
    }
    else {
      DAT_43f79b70 = DAT_43f79b70 + 1;
      DAT_43f79b52 = DAT_43f79b52 + 1;
    }
    if ((DAT_43e9bd4c & 0x40) == 0) {
      DAT_43e9d3a8 = FUN_437d9930();
      FUN_43ae8e84(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b54 = 0;
    }
    else {
      DAT_43f79b72 = DAT_43f79b72 + 1;
      DAT_43f79b54 = DAT_43f79b54 + 1;
    }
    if ((DAT_43e9bd4c & 0x80) == 0) {
      DAT_43e9d3ac = FUN_437b6614();
      FUN_43ae8e9a(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b56 = 0;
    }
    else {
      DAT_43f79b74 = DAT_43f79b74 + 1;
      DAT_43f79b56 = DAT_43f79b56 + 1;
    }
    if ((DAT_43e9bd4c & 0x200) == 0) {
      DAT_43e9d3b0 = FUN_437b8230();
      FUN_43ae8ea4(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b5a = 0;
    }
    else {
      DAT_43f79b78 = DAT_43f79b78 + 1;
      DAT_43f79b5a = DAT_43f79b5a + 1;
    }
    FUN_4378f7a0(0xd96);
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      FUN_4378f7a0(0xda0);
      FUN_437b4e28(&DAT_43e99208);
      FUN_4378f7a0(0xda2);
    }
    FUN_437c1bb4(&DAT_43e99208);
    thunk_FUN_43b7c7da(&DAT_43e99208);
    FUN_437b0244(&DAT_43e99208,&DAT_43e9d022);
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      FUN_4378f7a0(0xda9);
      FUN_43aef444(&DAT_43e99208,&DAT_43e9c7d8);
      FUN_4378f7a0(0xdad);
    }
    FUN_437c1b98(&DAT_43e99208,&DAT_43e9cc78);
    thunk_FUN_43b7c7dc(&DAT_43e99208,&DAT_43e9ce19);
    iVar3 = FUN_43560de0(0x1a,0x100,0,auStack_24,4);
    if (iVar3 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,&DAT_43ca3777,*DAT_43e9920c,uStack_30);
      FUN_43902718(s_VD_Post__VD_Sequence_wait_timeou_43ca378b,*DAT_43e9920c,uStack_30);
      FUN_43560da8(0x1a,0x100);
    }
    if (*(char *)(iVar2 + 0x70) == '\0') {
      iVar3 = FUN_437999e4(1,0xe);
      if (iVar3 != 0) {
        if ((DAT_43e9bb1f == '\0') || (DAT_43e9920c[3] != 0)) {
          FUN_439e21c0();
        }
        FUN_439e2184();
      }
      FUN_439fd76c();
    }
    FUN_4378f7a0(0xdd0);
    FUN_437967e8(&DAT_43e99208);
    FUN_4378f7a0(0xdd3);
    FUN_43ada220(auStack_48,0x4378f411);
    FUN_439018b0(&DAT_43e99380,auStack_48,param_1,0);
    bVar8 = *(byte *)(iVar2 + 0x1f) & 8;
    if (((*(byte *)(iVar2 + 0x1f) & 8) == 0) &&
       (iVar4 = FUN_436e8328(), iVar3 = DAT_4401f1d0, iVar4 != 0)) {
      iVar4 = DAT_43e9920c[9];
      iVar5 = DAT_43e9920c[2];
      uVar1 = *(undefined2 *)(DAT_4401f1d0 + 0x2e);
      FUN_43ae863c(auStack_5c,bVar8);
      FUN_436ccd9c(6,iVar4 + iVar5,uVar1,auStack_5c);
      iVar5 = DAT_43e9920c[9];
      iVar6 = DAT_43e9920c[2];
      iVar4 = FUN_43ada230();
      uVar1 = *(undefined2 *)(iVar3 + 0x2c);
      FUN_43ae863c(auStack_70,bVar8);
      FUN_436ccd9c(7,iVar5 + iVar6 + iVar4 * 2,uVar1,auStack_70);
    }
    FUN_43ae129a(4);
    if (param_1 != *DAT_43e9920c) {
      iVar3 = thunk_FUN_436cd00c();
      uVar7 = (uint)(iVar3 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca37b7,param_1,*DAT_43e9920c,uVar7);
      FUN_43902718(s_VD_Post__overflow__dV__>__dV__du_43ca37cb,param_1,*DAT_43e9920c,uVar7);
      FUN_4378f988(4,2,uVar7);
      if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Post_E_OF_43ca37ed);
      }
      if ((*(byte *)(iVar2 + 0x1b) & 8) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43901480(0);
    if ((*(byte *)(iVar2 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Post_E_43ca2f58);
    }
  }
  else {
    iVar3 = thunk_FUN_436cd00c();
    uVar7 = (uint)(iVar3 - DAT_43e9920c[2]) >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca372f,param_1,*DAT_43e9920c,uVar7);
    FUN_43902718(s_VD_Post__start_delayed__dV__>__d_43ca3743,param_1,*DAT_43e9920c,uVar7);
    FUN_4378f988(3,2,uVar7);
    if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Post_S_OF_43ca376a);
    }
    if ((*(byte *)(iVar2 + 0x1b) & 8) != 0) {
      FUN_4378ec60();
    }
  }
  return;
}


/* query "4379155c" */

void FUN_4379155c(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uStack_44;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  uint uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 auStack_24 [8];
  
  iVar1 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Seq_S_43ca34b3);
  }
  if (param_1 == *DAT_43e9920c) {
    iVar2 = FUN_43560de0(0x1a,0x40,0,auStack_24,4);
    if (iVar2 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,&DAT_43ca3507,*DAT_43e9920c,uStack_30);
      FUN_43902718(s_VD_Sequence__VD_Pre_wait_timeout_43ca351b,*DAT_43e9920c,uStack_30);
    }
    FUN_43560dc4(0x1a,0xffffffbf);
    FUN_43ae1292(1);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = '\x01';
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_43560dc4(0x1a,0xfffffeff);
    iVar2 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
    if (iVar2 == 0) {
      uVar6 = 0;
    }
    else if (DAT_43e99338 == 0) {
      if (DAT_43f9a4b8 == '\0') {
        if (DAT_43e9bcd9 == '\0') {
          uVar6 = 0;
        }
        else {
          uVar6 = 0x43e99324;
        }
      }
      else {
        uVar6 = 0;
      }
    }
    else {
      uVar6 = 0;
    }
    puVar3 = (undefined1 *)FUN_4379ce18();
    thunk_FUN_43af2858(DAT_43e99230,puVar3);
    *puVar3 = 0;
    uVar4 = FUN_43ae8cd0(DAT_44025f5c);
    DAT_43e9bd58 = FUN_43796954(uVar4,uVar6,&DAT_43e99208);
    iVar2 = FUN_437999e4(1,0xd);
    if (((iVar2 != 0) && (DAT_43e9bb18 != 0)) && ((DAT_43e9bbb8 == 1 || (DAT_43e9920c[3] == 0)))) {
      uStack_44 = FUN_43ae9332(DAT_43e9bb30);
      uStack_40 = 0;
      uStack_3f = 0;
      iVar2 = FUN_43795610(DAT_43e9bcd9);
      if (((iVar2 != 0) && (DAT_43f9a4b8 == '\0')) && (DAT_43e9bce8 != '\0')) {
        uStack_3f = 1;
      }
      uStack_3c = (uint)(*(int *)(DAT_43e99208 + 0x548) != 0);
      uStack_38 = *(undefined4 *)(DAT_43e99208 + 0x54c);
      iVar2 = FUN_437956c8(&DAT_43e9bba4,&uStack_44);
      if (iVar2 != 0) {
        FUN_4378eb78(3,9,1,&DAT_43ca3309,iVar2);
        FUN_43902718(s__DFE_SetParam_Error_0x_x_43ca331d,iVar2);
      }
    }
    FUN_43900380();
    FUN_439cdbc8();
    uStack_28 = 0;
    uStack_2c = 0;
    FUN_43728c18(0,&uStack_28,&uStack_2c);
    FUN_43b6d334(uStack_28,uStack_2c);
    FUN_43560da8(0x1a,0x100);
    FUN_43ae129a(1);
    if ((param_1 != *DAT_43e9920c) && (iVar2 = FUN_43ae8d4e(), iVar2 != 0)) {
      iVar2 = thunk_FUN_436cd00c();
      uVar5 = (uint)(iVar2 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca3546,param_1,*DAT_43e9920c,uVar5);
      FUN_43902718(s_VD_Sequence__overflow__dV__>__dV_43ca355a,param_1,*DAT_43e9920c,uVar5);
      FUN_4378f988(4,1,uVar5);
      if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Seq_E_OF_43ca3580);
      }
      if ((*(byte *)(iVar1 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43791528();
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Seq_E_43ca358c);
    }
  }
  else {
    iVar2 = FUN_43ae8d4e();
    if (iVar2 != 0) {
      iVar2 = thunk_FUN_436cd00c();
      uVar5 = (uint)(iVar2 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca34bc,param_1,*DAT_43e9920c,uVar5);
      FUN_43902718(s_VD_Sequence__start_delayed__dV___43ca34d0,param_1,*DAT_43e9920c,uVar5);
      FUN_4378f988(3,1,uVar5);
      if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Seq_S_OF_43ca34fb);
      }
      if ((*(byte *)(iVar1 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}

