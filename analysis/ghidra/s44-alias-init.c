/* S41: read-only exports. */

/* 43859944 */

void FUN_43859944(int param_1,int param_2,int param_3)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = DAT_438599d0 + 0x43859956;
  iVar3 = *(int *)(iVar4 + DAT_438599d4);
  if (*(char *)(iVar3 + 5) != '\x01') {
    *(int *)(DAT_438599d8 + 0x43859962) = param_1;
    if (param_2 != 0) {
      bVar1 = *(byte *)(iVar3 + 0xf);
      if ((bVar1 & 0x10) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599dc),param_2 + 700,0x6b0);
      }
      if ((bVar1 & 0x20) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599e0),param_2 + 4,0x2b8);
      }
      if ((bVar1 & 0x40) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599e4),param_2 + 0x96c,0x1128);
      }
    }
    if (param_3 != 0) {
      FUN_43afa660(DAT_438599e8 + 0x438599b6,param_3);
    }
    if (param_1 < 0x40) {
      uVar2 = 0x40;
    }
    else {
      uVar2 = 0x80;
    }
    FUN_43859710(uVar2);
    return;
  }
  return;
}


/* 437b2580 */

void FUN_437b2580(int param_1,int param_2,undefined2 *param_3,undefined4 param_4,byte *param_5,
                 undefined1 *param_6)

{
  short sVar1;
  undefined1 uVar2;
  short sVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 *puVar8;
  undefined4 uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  bool bVar14;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  ushort uStack_2c;
  byte bStack_2a;
  byte bStack_29;
  
  uVar7 = *(undefined4 *)(param_2 + 0x4a5c);
  iVar10 = DAT_437b2794 + 0x437b25a6;
  iVar11 = *(int *)(iVar10 + DAT_437b2798);
  FUN_439c5a04(iVar11,0,0x184);
  if (**(char **)(iVar10 + DAT_437b279c) == '\0') {
    bVar14 = false;
  }
  else if (param_6 == (undefined1 *)0x0) {
    bVar14 = false;
  }
  else {
    bVar14 = param_5 != (byte *)0x0;
  }
  uVar4 = param_3[1];
  *(undefined2 *)(iVar11 + 0x128) = *param_3;
  puVar8 = *(undefined4 **)(param_3 + 2);
  *(undefined2 *)(iVar11 + 0x12a) = uVar4;
  uVar5 = puVar8[1];
  uVar6 = puVar8[2];
  uVar9 = puVar8[3];
  *(undefined4 *)(iVar11 + 0x130) = *puVar8;
  *(undefined4 *)(iVar11 + 0x134) = uVar5;
  *(undefined4 *)(iVar11 + 0x138) = uVar6;
  *(undefined4 *)(iVar11 + 0x13c) = uVar9;
  uVar5 = puVar8[5];
  uVar6 = puVar8[6];
  uVar9 = puVar8[7];
  *(undefined4 *)(iVar11 + 0x140) = puVar8[4];
  *(undefined4 *)(iVar11 + 0x144) = uVar5;
  *(undefined4 *)(iVar11 + 0x148) = uVar6;
  *(undefined4 *)(iVar11 + 0x14c) = uVar9;
  uVar5 = puVar8[9];
  uVar6 = puVar8[10];
  uVar9 = puVar8[0xb];
  *(undefined4 *)(iVar11 + 0x150) = puVar8[8];
  *(undefined4 *)(iVar11 + 0x154) = uVar5;
  *(undefined4 *)(iVar11 + 0x158) = uVar6;
  *(undefined4 *)(iVar11 + 0x15c) = uVar9;
  FUN_43857ecc(0x299,*(undefined1 *)(param_3 + 1));
  iVar12 = *(int *)(iVar10 + DAT_437b27a0);
  if (bVar14) {
    uStack_2c = (ushort)*param_5 + *(short *)(param_1 + 0x32a) + (ushort)param_5[1] * 0x100;
    if ((*(int *)(param_1 + 0x30c) == 0x15) && (10000 < uStack_2c)) {
      uStack_2c = uStack_2c + 0xd8f0;
    }
    bStack_2a = param_5[2];
    bStack_29 = param_5[3];
    FUN_438fb33c(&uStack_2c);
    *(byte *)(param_1 + 0x30a) = param_5[4];
    *(ushort *)(param_1 + 0x334) =
         (ushort)param_5[10] + *(short *)(param_1 + 0x32a) + (ushort)param_5[0xb] * 0x100;
    *(byte *)(param_1 + 0x344) = param_5[2];
    *(byte *)(param_1 + 0x345) = param_5[3];
    *(byte *)(iVar12 + 0xe) = param_5[2];
    *(byte *)(iVar12 + 0xf) = param_5[3];
    *(byte *)(iVar12 + 0x10) = param_5[4];
  }
  uVar5 = *(undefined4 *)(iVar10 + DAT_437b27a8);
  iVar13 = *(int *)(iVar10 + DAT_437b27b0);
  FUN_4385d874(param_1 + 700,uVar5,*(undefined4 *)(iVar10 + DAT_437b27ac),iVar13,
               *(undefined4 *)(iVar10 + DAT_437b27a4),iVar11,uVar7);
  *(undefined2 *)(iVar12 + 2) = 0;
  *(undefined2 *)(iVar12 + 4) = 0;
  uVar4 = *(undefined2 *)(iVar13 + 0x15e);
  *(undefined2 *)(iVar12 + 6) = 0;
  sVar1 = *(short *)(param_1 + 0x2e2);
  sVar3 = FUN_4382fefc(uVar4);
  FUN_437b061c(0,sVar1 - sVar3,*(undefined4 *)(param_3 + 2),uVar5,&uStack_34,param_2 + 0xd00,
               param_2 + 0x1108);
  *(undefined2 *)(iVar11 + 0x178) = uStack_34;
  *(undefined2 *)(iVar11 + 0x17a) = uStack_32;
  *(undefined1 *)(iVar11 + 0x17c) = 0;
  *(undefined1 *)(iVar11 + 0x17d) = 1;
  *(undefined2 *)(iVar11 + 0x17e) = uStack_2e;
  *(undefined2 *)(iVar11 + 0x180) = uStack_30;
  uVar4 = FUN_439027ec(uStack_30,0x100);
  *(undefined2 *)(param_1 + 0x4e0) = uVar4;
  if (bVar14) {
    *param_6 = (char)*(undefined4 *)(param_1 + 800);
    uVar2 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x2f8));
    param_6[1] = uVar2;
    uVar2 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x2f8));
    param_6[2] = uVar2;
    uVar2 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x2f8));
    param_6[3] = uVar2;
  }
  *(char *)(*(int *)(iVar10 + DAT_437b27b4) + 0x23c) = (char)*(undefined4 *)(param_1 + 0x30c);
  FUN_43857048(param_1 + 700);
  FUN_43859944(10,param_1,param_2 + 0x1b8);
  return;
}


/* 437b27b8 */

void FUN_437b27b8(int param_1,int param_2,undefined2 *param_3,ushort *param_4,undefined1 *param_5)

{
  undefined2 uVar1;
  undefined2 uVar2;
  char cVar3;
  undefined1 uVar4;
  ushort uVar5;
  int iVar6;
  undefined4 uVar7;
  byte bVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  undefined4 *puVar15;
  bool bVar16;
  undefined2 uStack_2c;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  
  iVar12 = DAT_437b2acc + 0x437b27ce;
  iVar13 = param_2 + 0x764;
  bVar16 = false;
  if ((**(char **)(iVar12 + DAT_437b2ad0) != '\0') && (bVar16 = false, param_5 != (undefined1 *)0x0)
     ) {
    bVar16 = true;
  }
  iVar11 = *(int *)(iVar12 + DAT_437b2ad4);
  *(undefined2 *)(iVar11 + 0x128) = *param_3;
  *(undefined2 *)(iVar11 + 0x12a) = param_3[1];
  *(undefined1 *)(iVar11 + 0x12d) = *(undefined1 *)(param_3 + 2);
  *(undefined1 *)(iVar11 + 300) = *(undefined1 *)((int)param_3 + 5);
  FUN_43857ecc(0x29a,*(undefined1 *)(param_3 + 1));
  uVar7 = *(undefined4 *)(iVar11 + 0x17c);
  *(undefined4 *)(param_4 + 6) = *(undefined4 *)(iVar11 + 0x178);
  param_4[8] = (ushort)uVar7;
  FUN_4383c638(*(undefined2 *)(iVar11 + 0x17e),iVar13,param_2 + 0x1008);
  iVar6 = FUN_43aef24a(iVar13);
  if (iVar6 == 0) {
    uVar7 = 0;
  }
  else {
    uVar7 = 2;
  }
  FUN_43aef22e(iVar13,uVar7);
  FUN_438527f8();
  iVar13 = *(int *)(iVar12 + DAT_437b2ad8);
  uVar5 = FUN_4385de94(*(undefined4 *)(iVar11 + 0x134),*(undefined1 *)(iVar13 + 0x4b8),
                       *(undefined1 *)(param_1 + 0x348));
  *param_4 = uVar5;
  FUN_4385dee4(param_1 + 700,iVar11,iVar13);
  iVar13 = *(int *)(iVar11 + 0x134);
  uVar1 = *(undefined2 *)(param_1 + 0x4da);
  *(undefined4 *)(param_4 + 2) = *(undefined4 *)(iVar11 + 0x164);
  if (iVar13 == 0) {
    iVar13 = 1;
  }
  uVar5 = *param_4;
  uVar7 = FUN_4382fa94(uVar1);
  iVar13 = FUN_4355faf0(uVar7,iVar13);
  *(undefined1 *)(iVar11 + 0x170) = 0;
  *(undefined1 *)(iVar11 + 0x171) = 0;
  *(undefined2 *)(iVar11 + 0x16c) = 0;
  *(undefined2 *)(iVar11 + 0x16e) = 0;
  puVar15 = *(undefined4 **)(param_4 + 4);
  uVar14 = (uint)uVar5 - iVar13 & 0xffff;
  if (uVar14 < *(ushort *)(iVar11 + 0x144)) {
    *(uint *)(iVar11 + 0x168) = (uint)*(ushort *)(iVar11 + 0x144);
  }
  else {
    *(uint *)(iVar11 + 0x168) = uVar14;
  }
  uVar7 = *(undefined4 *)(iVar11 + 0x16c);
  uVar9 = *(undefined4 *)(iVar11 + 0x170);
  uVar10 = *(undefined4 *)(iVar11 + 0x174);
  *puVar15 = *(undefined4 *)(iVar11 + 0x168);
  puVar15[1] = uVar7;
  puVar15[2] = uVar9;
  puVar15[3] = uVar10;
  if (!bVar16) goto LAB_437b2aa6;
  iVar13 = *(int *)(param_1 + 0x30c);
  if (iVar13 < 0x14) {
    if (iVar13 < 0x12) {
      if (0 < iVar13) {
        if (iVar13 < 3) {
          uVar4 = 2;
          goto LAB_437b2916;
        }
        bVar16 = iVar13 == 0x11;
LAB_437b2902:
        if (bVar16) goto LAB_437b2904;
      }
LAB_437b2914:
      uVar4 = 0;
    }
    else {
      uVar4 = 4;
    }
  }
  else {
    if (iVar13 != 0x17) {
      if (iVar13 < 0x18) {
        if (0x15 < iVar13) goto LAB_437b2914;
        uVar4 = 3;
        goto LAB_437b2916;
      }
      if (iVar13 != 0x21) {
        bVar16 = iVar13 == 0x23;
        goto LAB_437b2902;
      }
    }
LAB_437b2904:
    uVar4 = 1;
  }
LAB_437b2916:
  *param_5 = uVar4;
  iVar13 = DAT_437b2adc;
  bVar8 = *(byte *)(iVar11 + 0x126);
  if (3 < bVar8) {
    bVar8 = 0;
  }
  *(byte *)(param_1 + 0x336) = bVar8;
  uVar1 = *(undefined2 *)(param_1 + 0x4ae);
  uVar2 = *(undefined2 *)(param_1 + 0x4a6);
  iVar13 = *(int *)(iVar12 + iVar13);
  if (bVar8 == 1) {
    *(undefined2 *)(param_1 + 0x4b0) = uVar1;
    *(undefined2 *)(param_1 + 0x4a8) = uVar2;
    *(undefined2 *)(param_1 + 0x4c6) = *(undefined2 *)(param_1 + 0x4c4);
    *(undefined2 *)(iVar13 + 2) = uVar2;
  }
  else if (bVar8 == 2) {
    *(undefined2 *)(param_1 + 0x4b2) = uVar1;
    *(undefined2 *)(param_1 + 0x4aa) = uVar2;
    *(undefined2 *)(param_1 + 0x4c8) = *(undefined2 *)(param_1 + 0x4c4);
    *(undefined2 *)(iVar13 + 4) = uVar2;
  }
  else {
    *(undefined2 *)(param_1 + 0x4b4) = uVar1;
    *(undefined2 *)(param_1 + 0x4ac) = uVar2;
    *(undefined2 *)(param_1 + 0x4ca) = *(undefined2 *)(param_1 + 0x4c4);
    *(undefined2 *)(iVar13 + 6) = uVar2;
  }
  iVar13 = *(int *)(param_1 + 0x31c);
  if (*(int *)(param_1 + 0x30c) - 0x12U < 2) {
    if (iVar13 == 1) {
      cVar3 = FUN_43b076d0(*(undefined2 *)(param_1 + 0x4ca),*(undefined2 *)(param_1 + 0x2d0));
      param_5[1] = cVar3 - *(char *)(param_1 + 0x30a);
      cVar3 = FUN_43b076d0(*(undefined2 *)(param_1 + 0x4c6),*(undefined2 *)(param_1 + 0x2d0));
      param_5[2] = cVar3 - *(char *)(param_1 + 0x30a);
      cVar3 = FUN_43b076d0(*(undefined2 *)(param_1 + 0x4c8),*(undefined2 *)(param_1 + 0x2d0));
      cVar3 = cVar3 - *(char *)(param_1 + 0x30a);
      goto LAB_437b2a7a;
    }
    uVar4 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x4ca));
    param_5[1] = uVar4;
    uVar4 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x4c6));
    param_5[2] = uVar4;
    uVar4 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x4c8));
    param_5[3] = uVar4;
  }
  else {
    if (*(int *)(param_1 + 0x30c) - 0x14U < 2) {
      if (iVar13 == 1) {
        cVar3 = FUN_43b076d0(*(undefined2 *)(param_1 + 0x4c8),*(undefined2 *)(param_1 + 0x2d0));
        param_5[1] = cVar3 - *(char *)(param_1 + 0x30a);
        cVar3 = FUN_43b076d0(*(undefined2 *)(param_1 + 0x4c6),*(undefined2 *)(param_1 + 0x2d0));
        param_5[2] = cVar3 - *(char *)(param_1 + 0x30a);
        param_5[3] = 0;
        if ((*(int *)(param_1 + 0x30c) == 0x15) && (*(char *)(iVar11 + 0x126) == '\x01')) {
          uStack_2c = *(undefined2 *)(param_1 + 0x334);
          uStack_2a = *(undefined1 *)(param_1 + 0x344);
          uStack_29 = *(undefined1 *)(param_1 + 0x345);
          FUN_438fb33c(&uStack_2c);
        }
        goto LAB_437b2a7c;
      }
      uVar4 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x4c8));
      param_5[1] = uVar4;
      uVar4 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x4c6));
      cVar3 = '\0';
      param_5[2] = uVar4;
    }
    else {
      if (iVar13 == 1) {
        cVar3 = FUN_43b076d0(*(undefined2 *)(param_1 + 0x4c6),*(undefined2 *)(param_1 + 0x2d0));
        param_5[1] = cVar3 - *(char *)(param_1 + 0x30a);
      }
      else {
        uVar4 = FUN_43b075ec(*(undefined2 *)(param_1 + 0x4c6));
        param_5[1] = uVar4;
      }
      cVar3 = '\0';
      param_5[2] = 0;
    }
LAB_437b2a7a:
    param_5[3] = cVar3;
  }
LAB_437b2a7c:
  param_5[4] = (char)*(undefined2 *)(param_1 + 0x2d0);
  param_5[5] = (char)((ushort)*(undefined2 *)(param_1 + 0x2d0) >> 8);
  param_5[6] = (char)*(undefined2 *)(param_1 + 0x2ce);
  param_5[7] = (char)((ushort)*(undefined2 *)(param_1 + 0x2ce) >> 8);
  param_5[8] = (char)*(undefined2 *)(param_1 + 0x4cc);
  param_5[9] = (char)((ushort)*(undefined2 *)(param_1 + 0x4cc) >> 8);
LAB_437b2aa6:
  if (*(char *)(param_1 + 0x346) == '\x01') {
    **(undefined1 **)(iVar12 + DAT_437b2adc) = 1;
    FUN_437b5ae0();
  }
  FUN_43859944(0xb,param_1,param_2 + 0x1b8);
  return;
}


/* 438403e4 */

void FUN_438403e4(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = DAT_43840790 + 0x438403f6;
  if ((**(char **)(iVar7 + DAT_43840794) == '\0') &&
     ((*(char **)(iVar7 + DAT_43840794))[0x15] == '\0')) {
    return;
  }
  FUN_43857f40(0x38b,*(undefined4 *)(param_2 + 0x1b8));
  uVar1 = FUN_4383fb6c(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  iVar8 = param_1 + 700;
  iVar2 = FUN_4383fc48(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  uVar3 = FUN_4383fbc4(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  uVar4 = FUN_4383fb40(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  uVar5 = FUN_4383fb98(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  iVar6 = FUN_436ef7f4();
  *(undefined2 *)(iVar2 + 0x576) = *(undefined2 *)(iVar6 + 0x58);
  FUN_437b3cec(iVar2,uVar3,uVar4,param_1 + 4,iVar8,uVar1,0,*(undefined4 *)(param_2 + 0x4a54),
               param_2 + 0x1b8);
  uVar4 = FUN_43b09ccc(param_2);
  FUN_437b1048(iVar2,uVar3,*(undefined4 *)(iVar7 + DAT_43840798),
               *(undefined4 *)(iVar7 + DAT_4384079c),uVar5,param_1 + 4,iVar8,uVar1,0,
               *(undefined4 *)(param_2 + 0x4a58),*(undefined4 *)(param_2 + 0x4a5c),uVar4);
  FUN_437b2f18(iVar8,param_2);
  iVar7 = FUN_43b09cd4(param_2);
  if (iVar7 != 0) {
    *(undefined1 *)(iVar7 + 499) = *(undefined1 *)(param_1 + 8);
    *(undefined1 *)(iVar7 + 500) = *(undefined1 *)(param_1 + 9);
    *(undefined1 *)(iVar7 + 0x1f5) = *(undefined1 *)(param_1 + 10);
    *(undefined1 *)(iVar7 + 0x1f6) = *(undefined1 *)(param_1 + 0xb);
    *(undefined1 *)(iVar7 + 0x237) = *(undefined1 *)(param_1 + 0x44);
    *(undefined1 *)(iVar7 + 0x238) = *(undefined1 *)(param_1 + 0x45);
  }
  FUN_43842440(iVar7);
  FUN_438553a0(iVar7);
  if (iVar7 != 0) {
    iVar6 = FUN_436ef7f4();
    iVar8 = FUN_436efa1c();
    *(undefined1 *)(iVar7 + 0xff) = *(undefined1 *)(iVar6 + 0x3e9);
    *(undefined1 *)(iVar7 + 0x100) = *(undefined1 *)(iVar6 + 0x3ea);
    *(undefined1 *)(iVar7 + 0x101) = *(undefined1 *)(iVar6 + 1000);
    *(undefined1 *)(iVar7 + 0x102) = *(undefined1 *)(iVar6 + 0x3eb);
    *(undefined1 *)(iVar7 + 0x103) = *(undefined1 *)(iVar6 + 0x3ec);
    *(undefined1 *)(iVar7 + 0x104) = *(undefined1 *)(iVar6 + 0x3ee);
    *(undefined1 *)(iVar7 + 0x105) = *(undefined1 *)(iVar6 + 0x3ef);
    *(undefined1 *)(iVar7 + 0x106) = *(undefined1 *)(iVar6 + 0x3f0);
    *(undefined1 *)(iVar7 + 0x107) = *(undefined1 *)(iVar6 + 0x3f1);
    *(undefined1 *)(iVar7 + 0x108) = *(undefined1 *)(iVar6 + 0x3f2);
    *(undefined1 *)(iVar7 + 0x109) = *(undefined1 *)(iVar6 + 0x3f3);
    *(undefined1 *)(iVar7 + 0x10a) = *(undefined1 *)(iVar6 + 0x3f4);
    *(undefined1 *)(iVar7 + 0x10b) = *(undefined1 *)(iVar6 + 0x3f5);
    *(undefined1 *)(iVar7 + 0x111) = *(undefined1 *)(iVar8 + 0x6e);
    *(undefined1 *)(iVar7 + 0x112) = *(undefined1 *)(iVar8 + 0x6f);
    *(undefined1 *)(iVar7 + 0x113) = *(undefined1 *)(iVar8 + 0x70);
    *(undefined1 *)(iVar7 + 0x114) = *(undefined1 *)(iVar8 + 0x71);
    *(undefined1 *)(iVar7 + 0x115) = *(undefined1 *)(iVar8 + 0x72);
    *(undefined1 *)(iVar7 + 0x116) = *(undefined1 *)(iVar8 + 0x73);
    *(undefined1 *)(iVar7 + 0x117) = *(undefined1 *)(iVar8 + 0x74);
    *(undefined1 *)(iVar7 + 0x118) = *(undefined1 *)(iVar8 + 0x75);
    *(undefined1 *)(iVar7 + 0x119) = *(undefined1 *)(iVar8 + 0x76);
    *(undefined1 *)(iVar7 + 0x11a) = *(undefined1 *)(iVar8 + 0x77);
    *(undefined1 *)(iVar7 + 0x11b) = *(undefined1 *)(iVar8 + 0x78);
    *(undefined1 *)(iVar7 + 0x11c) = *(undefined1 *)(iVar8 + 0x79);
    *(undefined1 *)(iVar7 + 0x11d) = *(undefined1 *)(iVar8 + 0x7a);
    *(undefined1 *)(iVar7 + 0x11e) = *(undefined1 *)(iVar8 + 0x7c);
    *(undefined1 *)(iVar7 + 0x11f) = *(undefined1 *)(iVar8 + 0x7d);
    *(undefined1 *)(iVar7 + 0x120) = *(undefined1 *)(iVar8 + 0x7e);
    *(undefined1 *)(iVar7 + 0x121) = *(undefined1 *)(iVar8 + 0x7f);
    *(undefined1 *)(iVar7 + 0x122) = *(undefined1 *)(iVar8 + 0x80);
    *(undefined1 *)(iVar7 + 0x123) = *(undefined1 *)(iVar8 + 0x81);
    *(undefined1 *)(iVar7 + 0x124) = *(undefined1 *)(iVar8 + 0x82);
    *(undefined1 *)(iVar7 + 0x125) = *(undefined1 *)(iVar8 + 0x83);
    *(undefined1 *)(iVar7 + 0x126) = *(undefined1 *)(iVar8 + 0x84);
    *(undefined1 *)(iVar7 + 0x127) = *(undefined1 *)(iVar8 + 0x85);
    *(undefined1 *)(iVar7 + 0x128) = *(undefined1 *)(iVar8 + 0x86);
    *(undefined1 *)(iVar7 + 0x129) = *(undefined1 *)(iVar8 + 0x88);
    *(undefined1 *)(iVar7 + 0x12a) = *(undefined1 *)(iVar8 + 0x89);
    *(undefined1 *)(iVar7 + 299) = *(undefined1 *)(iVar8 + 0x8a);
    *(undefined1 *)(iVar7 + 300) = *(undefined1 *)(iVar8 + 0x8b);
    *(undefined1 *)(iVar7 + 0x12d) = *(undefined1 *)(iVar8 + 0x8c);
    *(undefined1 *)(iVar7 + 0x12e) = *(undefined1 *)(iVar8 + 0x8d);
    *(undefined1 *)(iVar7 + 0x12f) = *(undefined1 *)(iVar8 + 0x8e);
    *(undefined1 *)(iVar7 + 0x130) = *(undefined1 *)(iVar8 + 0x8f);
    *(undefined1 *)(iVar7 + 0x131) = *(undefined1 *)(iVar8 + 0x90);
    *(undefined1 *)(iVar7 + 0x132) = *(undefined1 *)(iVar8 + 0x91);
    *(undefined1 *)(iVar7 + 0x133) = *(undefined1 *)(iVar8 + 0x92);
    *(undefined1 *)(iVar7 + 0x134) = *(undefined1 *)(iVar8 + 0x93);
    *(undefined1 *)(iVar7 + 0x135) = *(undefined1 *)(iVar8 + 0x94);
    *(undefined1 *)(iVar7 + 0x136) = *(undefined1 *)(iVar8 + 0x95);
    *(undefined1 *)(iVar7 + 0x137) = *(undefined1 *)(iVar8 + 0x96);
    *(undefined1 *)(iVar7 + 0x138) = *(undefined1 *)(iVar8 + 0x97);
    *(undefined1 *)(iVar7 + 0x139) = *(undefined1 *)(iVar8 + 0x98);
    *(undefined1 *)(iVar7 + 0x13a) = *(undefined1 *)(iVar8 + 0x99);
    *(undefined1 *)(iVar7 + 0x13b) = *(undefined1 *)(iVar8 + 0x9a);
    *(undefined1 *)(iVar7 + 0x13c) = *(undefined1 *)(iVar8 + 0x9b);
    *(undefined1 *)(iVar7 + 0x13d) = *(undefined1 *)(iVar8 + 0x9c);
    *(undefined1 *)(iVar7 + 0x13e) = *(undefined1 *)(iVar8 + 0x9e);
    *(undefined1 *)(iVar7 + 0x13f) = *(undefined1 *)(iVar8 + 0x9f);
    *(undefined1 *)(iVar7 + 0x140) = *(undefined1 *)(iVar8 + 0xa0);
    *(undefined1 *)(iVar7 + 0x141) = *(undefined1 *)(iVar8 + 0xa1);
    *(undefined1 *)(iVar7 + 0x142) = *(undefined1 *)(iVar8 + 0xa2);
    *(undefined1 *)(iVar7 + 0x143) = *(undefined1 *)(iVar8 + 0xa3);
    *(undefined1 *)(iVar7 + 0x144) = *(undefined1 *)(iVar8 + 0xa4);
    *(undefined1 *)(iVar7 + 0x145) = *(undefined1 *)(iVar8 + 0xa5);
    *(undefined1 *)(iVar7 + 0x146) = *(undefined1 *)(iVar8 + 0xa6);
    *(undefined1 *)(iVar7 + 0x147) = *(undefined1 *)(iVar8 + 0xa7);
    *(undefined1 *)(iVar7 + 0x148) = *(undefined1 *)(iVar8 + 0xa8);
    *(undefined1 *)(iVar7 + 0x149) = *(undefined1 *)(iVar8 + 0xa9);
    *(undefined1 *)(iVar7 + 0x14a) = *(undefined1 *)(iVar8 + 0xaa);
    *(undefined1 *)(iVar7 + 0x14b) = *(undefined1 *)(iVar8 + 0xab);
    *(undefined1 *)(iVar7 + 0x14c) = *(undefined1 *)(iVar8 + 0xac);
  }
  FUN_4384a554(iVar2,uVar3);
  FUN_43859944(0x16,param_1,param_2 + 0x1b8);
  return;
}

