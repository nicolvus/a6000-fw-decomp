/* S41: read-only exports. */

/* 4378e334 */

void FUN_4378e334(int *param_1,int param_2,int param_3)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  bool bVar7;
  int iStack_30;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  int iStack_28;
  int iStack_24;
  
  iVar3 = *(int *)(param_2 + 8);
  iStack_28 = *param_1;
  iStack_24 = param_1[1];
  iVar6 = DAT_4378e598 + 0x4378e35a;
  FUN_43795a60(*(undefined4 *)(iVar3 + 0x44),*(undefined1 *)(iVar3 + 0x1bc),
               *(undefined1 *)(iVar3 + 0x1bd),&iStack_30);
  iVar4 = *(int *)(*(int *)(param_2 + 8) + 0x44);
  iVar3 = *(int *)(*(int *)(param_2 + 4) + 0x3c);
  *(undefined1 *)(param_1 + 2) = 1;
  *param_1 = iVar4;
  *(undefined1 *)((int)param_1 + 9) = 1;
  *(undefined1 *)((int)param_1 + 6) = uStack_2a;
  *(undefined1 *)((int)param_1 + 5) = uStack_2b;
  *(undefined1 *)(param_1 + 3) = 0;
  *(bool *)((int)param_1 + 0xd) = iVar3 != 0;
  iVar3 = *(int *)(iVar6 + DAT_4378e59c);
  if (iStack_30 == 0x11) {
    *(undefined1 *)((int)param_1 + 0xb) = 0;
    *(undefined1 *)((int)param_1 + 10) = 0;
    *(undefined1 *)((int)param_1 + 0xe) = 0;
    param_1[4] = 0;
    param_1[5] = 0;
    param_1[6] = 0;
    param_1[7] = 0;
    *(undefined1 *)(param_1 + 8) = 1;
    goto LAB_4378e53e;
  }
  if (param_3 == 0) {
    uVar2 = FUN_436d6118();
    iVar4 = FUN_436d6224(uVar2,&iStack_28,&iStack_30);
    if (iVar4 != 0) goto LAB_4378e3c2;
    if ((uint)param_1[6] < (uint)param_1[4]) {
      *(undefined1 *)((int)param_1 + 10) = 1;
      param_1[4] = param_1[4] - param_1[6];
      *(undefined1 *)(param_1 + 8) = 1;
    }
    else {
      param_1[4] = 0;
      *(undefined1 *)(param_1 + 8) = 0;
    }
  }
  else {
LAB_4378e3c2:
    iVar4 = *(int *)(param_2 + 8);
    *(undefined1 *)((int)param_1 + 10) = 1;
    bVar1 = *(byte *)(iVar4 + 0xc0);
    *(undefined1 *)(param_1 + 8) = 1;
    param_1[4] = (uint)bVar1;
  }
  if (*(int *)(*(int *)(iVar6 + DAT_4378e5a0) + 0x40) == 1) {
    if (iStack_30 == 0x12) {
      if ((iStack_28 != 1) && (iStack_28 != 3)) {
        bVar7 = iStack_28 == 0x39;
LAB_4378e414:
        if (!bVar7) goto LAB_4378e416;
      }
LAB_4378e438:
      *(undefined1 *)(param_1 + 3) = 1;
    }
    else {
      if (iStack_30 == 0x3f) {
        if (1 < iStack_28 - 0x30U) {
          bVar7 = iStack_28 == 0x3a;
          goto LAB_4378e414;
        }
        goto LAB_4378e438;
      }
LAB_4378e416:
      if (iStack_28 == 0x12) {
        if ((iStack_30 != 1) && (iStack_30 != 3)) {
          bVar7 = iStack_30 == 0x39;
LAB_4378e436:
          if (!bVar7) goto LAB_4378e43c;
        }
        goto LAB_4378e438;
      }
      if (iStack_28 == 0x3f) {
        if (1 < iStack_30 - 0x30U) {
          bVar7 = iStack_30 == 0x3a;
          goto LAB_4378e436;
        }
        goto LAB_4378e438;
      }
    }
LAB_4378e43c:
    if ((*(char *)((int)param_1 + 0xb) == '\0') || (*(char *)(iVar3 + 0x13) != '\0')) {
      *(undefined1 *)(param_1 + 3) = 0;
    }
    if ((((((iStack_30 != 1) && (iStack_30 != 0x30)) && (iStack_30 != 0x39)) &&
         ((iStack_30 != 0x3a && (iStack_30 != 3)))) && (iStack_30 != 0x31)) && (iStack_30 != 0x12))
    {
      bVar7 = iStack_30 == 0x3f;
      goto LAB_4378e48a;
    }
  }
  else {
    if ((iStack_30 == 8) && ((iStack_28 == 1 || (iStack_28 == 0x44)))) {
      *(undefined1 *)(param_1 + 3) = 1;
    }
    if ((*(char *)((int)param_1 + 0xb) == '\0') || (*(char *)(iVar3 + 0x13) != '\0')) {
      *(undefined1 *)(param_1 + 3) = 0;
    }
    bVar7 = iStack_30 == 1;
LAB_4378e48a:
    if ((!bVar7) && (iStack_30 != 0x44)) {
      *(undefined1 *)((int)param_1 + 0xb) = 0;
    }
  }
  uVar5 = (*(uint *)(*(int *)(param_2 + 8) + 0x264) & 0xfffff) >> 0xf;
  if ((8 < uVar5) || ((1 << uVar5 & 0x17eU) == 0)) {
    *(undefined1 *)(param_1 + 3) = 0;
    *(undefined1 *)((int)param_1 + 0xb) = 0;
  }
  if (param_3 != 0) {
    *(undefined1 *)(param_1 + 3) = 0;
    *(undefined1 *)((int)param_1 + 0xb) = 0;
  }
  if ((((iStack_30 == 8) || (iStack_30 == 0x12)) || (iStack_30 == 0x3f)) &&
     ((iStack_28 == 1 || (iStack_28 == 0x44)))) {
    iVar4 = (int)**(char **)(param_2 + 0x44);
  }
  else if (((iStack_28 == 8) || ((iStack_28 == 0x12 || (iStack_28 == 0x3f)))) &&
          ((iStack_30 == 1 || (iStack_30 == 0x44)))) {
    iVar4 = (int)*(char *)(*(int *)(param_2 + 0x44) + 1);
  }
  else if ((((iStack_28 == 5) || (iStack_28 == 7)) || (iStack_28 == 0x10)) &&
          ((iStack_30 == 1 || (iStack_30 == 3)))) {
    iVar4 = (int)*(char *)(*(int *)(param_2 + 0x44) + 5);
  }
  else if (((iStack_28 == 1) || (iStack_28 == 3)) &&
          (((iStack_30 == 5 || (iStack_30 == 7)) || (iStack_30 == 0x10)))) {
    iVar4 = (int)*(char *)(*(int *)(param_2 + 0x44) + 4);
  }
  else {
    iVar4 = -1;
  }
  param_1[5] = iVar4;
  *(char *)((int)param_1 + 0xe) = (char)param_3;
  param_1[6] = 0;
  param_1[7] = 0;
LAB_4378e53e:
  if (*(char *)(iVar3 + 0x26) < '\0') {
    FUN_4378e288(3,9,1,DAT_4378e5a4 + 0x4378e568,*(undefined4 *)(*(int *)(param_2 + 8) + 0x44),
                 *(undefined1 *)((int)param_1 + 0xd),param_1[4],param_1[5],
                 *(undefined1 *)((int)param_1 + 0xe));
    FUN_43902718(DAT_4378e5a8 + 0x4378e578,*(undefined4 *)(*(int *)(param_2 + 8) + 0x44),
                 *(undefined1 *)((int)param_1 + 0xd),param_1[4],param_1[5],
                 *(undefined1 *)((int)param_1 + 0xe));
  }
  return;
}


/* 437957ec */

void FUN_437957ec(int param_1,undefined4 param_2,undefined4 param_3,int param_4,int param_5)

{
  undefined1 uVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  int iStack_20;
  undefined4 uStack_1c;
  
  iStack_20 = param_1;
  uStack_1c = param_2;
  uVar1 = FUN_437959b8();
  uStack_1c = CONCAT31(CONCAT21(CONCAT11(uStack_1c._3_1_,(char)param_2),(char)param_3),uVar1);
  if (param_1 == 0x11) {
    FUN_439c5a04(param_4,0,0x104);
    FUN_439c5a04(param_5,0,0x28);
    uVar2 = 0;
    puVar3 = (undefined4 *)(DAT_4379588c + 0x43795874);
  }
  else {
    uVar2 = FUN_436d6118();
    FUN_436d61a4(uVar2,&iStack_20,param_4);
    uVar2 = FUN_43ae9332(param_1);
    FUN_43ae92ee(uVar2,param_5);
    FUN_43795a14(param_2,param_3,param_4 + 0x1c);
    if (*(char *)(param_5 + 0x26) == '\0') {
      puVar3 = (undefined4 *)(DAT_43795888 + 0x43795856);
      uVar2 = 0;
    }
    else if (*(char *)(param_4 + 0x19) == '\0') {
      uVar2 = 1;
      puVar3 = (undefined4 *)(DAT_43795884 + 0x43795850);
    }
    else {
      uVar2 = 2;
      puVar3 = (undefined4 *)(DAT_43795880 + 0x43795848);
    }
  }
  *puVar3 = uVar2;
  *(undefined1 *)(DAT_43795890 + 0x4379587c) = 0;
  return;
}


/* 4378ea78 */

void FUN_4378ea78(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  int iStack_28;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined4 uStack_14;
  
  iVar1 = DAT_4378eb60;
  puVar4 = (undefined4 *)(DAT_4378eb58 + 0x4378ea88);
  FUN_439c5320(puVar4,DAT_4378eb5c + 0x4378ea8e,0x44);
  iVar2 = DAT_4378eb64;
  uVar3 = *puVar4;
  *(undefined1 *)(DAT_4378eb64 + 0x4378f07e) = 4;
  *(undefined4 *)(iVar2 + 0x4378f082) = uVar3;
  FUN_437957ec(uVar3,*(undefined1 *)(iVar2 + 0x4378f1fa),*(undefined1 *)(iVar2 + 0x4378f1fb),
               iVar2 + 0x4378f0f6,iVar2 + 0x4378f2de);
  FUN_4378e334(*(undefined4 *)(iVar1 + 0x4378ea9c + DAT_4378eb68),DAT_4378eb6c + 0x4378eac8,param_1)
  ;
  iStack_28 = FUN_437955ec();
  iVar1 = DAT_4378eb70;
  if (((iStack_28 != 1) && (iStack_28 != 2)) && (iStack_28 != 0)) {
    iStack_28 = 0;
  }
  uStack_24 = *(undefined2 *)(DAT_4378eb70 + 0x4378f32e);
  uStack_22 = *(undefined2 *)(DAT_4378eb70 + 0x4378f332);
  uStack_20 = *(undefined2 *)((int)&DAT_4378f350 + DAT_4378eb70 + 2);
  uStack_1e = *(undefined2 *)(DAT_4378eb70 + 0x4378f1f6);
  uStack_1c = *(undefined2 *)(DAT_4378eb70 + 0x4378f1f8);
  uStack_1a = *(undefined2 *)(DAT_4378eb70 + 0x4378f1fa);
  uStack_18 = *(undefined2 *)(DAT_4378eb70 + 0x4378f240);
  uStack_16 = *(undefined2 *)(DAT_4378eb70 + 0x4378f242);
  thunk_FUN_43ae6916(&iStack_28,&uStack_14);
  FUN_43795d38(uStack_14);
  if ((*(ushort *)(*(int *)(DAT_4378eb74 + 0x4378eb40) + 0x264) & 0x1c0) == 0) {
    uVar3 = FUN_43794a78();
    *(undefined4 *)(&LAB_4378f2ea + iVar1) = uVar3;
  }
  else {
    *(undefined4 *)(&LAB_4378f2ea + iVar1) = 0;
  }
  return;
}


/* 43859ac4 */

undefined * FUN_43859ac4(void)

{
  return &UNK_43859aca + DAT_43859acc;
}


/* 436d64c8 */

undefined4 FUN_436d64c8(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    iVar2 = DAT_436d64fc + 0x436d64da;
    FUN_436d6020(0xbc,0,1,DAT_436d64f8 + 0x436d64d8,iVar2,0);
    FUN_43902718(DAT_436d6500 + 0x436d64e6,iVar2);
    uVar1 = 1;
  }
  else {
    uVar1 = (**(code **)(*(int *)*param_1 + 0x70))();
  }
  return uVar1;
}


/* 43b027c8 */

void FUN_43b027c8(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined1 *apuStack_24 [3];
  
  if (*(int *)(param_1 + 4) != 0) {
    FUN_43ae85ae(param_2);
    FUN_437876dc();
    iVar1 = FUN_43b00cb4();
    if (iVar1 == 1) {
      uVar2 = FUN_437876dc();
      iVar1 = FUN_43805854(uVar2,0x3034);
      if (iVar1 != 0) {
        FUN_437876dc();
        FUN_43805808();
      }
    }
    iVar1 = FUN_435612d0(*(undefined4 *)(param_1 + 4),apuStack_24,0xc,1);
    if (iVar1 == 0) {
      FUN_4380a044(apuStack_24[0]);
      *apuStack_24[0] = 1;
      *(undefined2 *)(apuStack_24[0] + 2) = 0x3034;
      *(undefined4 *)(apuStack_24[0] + 4) = param_2;
      *(undefined4 *)(apuStack_24[0] + 8) = param_3;
      iVar1 = FUN_4356120c(*(undefined4 *)(param_1 + 4));
      if (iVar1 == 0) {
        return;
      }
      uVar2 = 0xab;
      iVar3 = DAT_4380a110 + 0x4380a0fa;
      iVar4 = DAT_4380a114 + 0x4380a100;
    }
    else {
      uVar2 = 0x99;
      iVar3 = DAT_4380a108 + 0x4380a0c6;
      iVar4 = DAT_4380a10c + 0x4380a0ca;
    }
    FUN_43787b70(iVar3,uVar2,iVar4,1,iVar1,0,0);
  }
  return;
}

