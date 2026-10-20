/* S41: read-only exports. */

/* 4381ad40 */

undefined4 FUN_4381ad40(uint param_1)

{
  if (param_1 < 3) {
    return *(undefined4 *)(DAT_4381ad54 + 0x4381ad4a + param_1 * 4);
  }
  return 0;
}


/* 4381a648 */

undefined4 FUN_4381a648(uint param_1)

{
  if (param_1 < 4) {
    return *(undefined4 *)(DAT_4381a65c + 0x4381a652 + param_1 * 4);
  }
  return 1;
}


/* 43794e0c */

void FUN_43794e0c(void)

{
  int iVar1;
  
  iVar1 = DAT_43794e50;
  FUN_43794ce4(DAT_43794e4c + 0x43794e14);
  iVar1 = **(int **)(iVar1 + 0x43794e1e + DAT_43794e54);
  if (iVar1 - 1U < 6) {
                    /* WARNING: Could not recover jumptable at 0x43794e26. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_43794e26::switchdataD_43794e2a + (uint)*(byte *)(iVar1 + 0x43794e29) * 2))()
    ;
    return;
  }
  return;
}


/* 4380f440 */

void FUN_4380f440(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  iVar1 = DAT_4380f4fc;
  puVar2 = (uint *)(DAT_4380f4f0 + 0x4380f452);
  if ((*puVar2 & 1) == 0) {
    FUN_43afb46a(&uStack_3c,*(undefined4 *)(DAT_4380f4f4 + 0x4380f45a + DAT_4380f4f8));
    FUN_43b03a2e(&uStack_50);
    FUN_43afb43a(&uStack_64,0);
    FUN_439c5a04(iVar1 + 0x4380f47e,0,0x44);
    *(undefined4 *)(iVar1 + 0x4380f482) = uStack_3c;
    *(undefined4 *)(iVar1 + 0x4380f486) = uStack_38;
    *(undefined4 *)(iVar1 + 0x4380f48a) = uStack_34;
    *(undefined4 *)(iVar1 + 0x4380f48e) = uStack_30;
    *(undefined4 *)(iVar1 + 0x4380f492) = uStack_2c;
    *(undefined4 *)(iVar1 + 0x4380f49a) = uStack_50;
    *(undefined4 *)(iVar1 + 0x4380f49e) = uStack_4c;
    *(undefined4 *)(iVar1 + 0x4380f4a2) = uStack_48;
    *(undefined4 *)(iVar1 + 0x4380f4a6) = uStack_44;
    *(undefined4 *)(iVar1 + 0x4380f4aa) = uStack_40;
    *(undefined4 *)(iVar1 + 0x4380f4ae) = uStack_64;
    *(undefined4 *)(iVar1 + 0x4380f4b2) = uStack_60;
    *(undefined4 *)(iVar1 + 0x4380f4b6) = uStack_5c;
    *(undefined4 *)(iVar1 + 0x4380f4ba) = uStack_58;
    *(undefined4 *)(iVar1 + 0x4380f4be) = uStack_54;
    *puVar2 = 1;
  }
  iVar1 = FUN_437c1d38(*(undefined2 *)(*param_1 + 4));
  if ((iVar1 == 0) || (*(int *)(DAT_4380f500 + 0x4380f4d2) == 0)) {
    FUN_4380e43c(param_1,param_3,param_4);
  }
  FUN_439c5320(param_2,DAT_4380f504 + 0x4380f4e8,0x44);
  return;
}


/* 43795a60 */

void FUN_43795a60(undefined4 param_1,byte param_2,byte param_3,undefined4 *param_4)

{
  byte bVar1;
  byte bVar2;
  undefined1 uVar3;
  
  bVar1 = *(byte *)(DAT_43795a88 + 0x43795aa6);
  bVar2 = *(byte *)(DAT_43795a88 + 0x43795aa7);
  *param_4 = param_1;
  uVar3 = FUN_437959b8();
  *(byte *)((int)param_4 + 6) = param_2 ^ bVar1;
  *(byte *)((int)param_4 + 5) = param_3 ^ bVar2;
  *(undefined1 *)(param_4 + 1) = uVar3;
  return;
}


/* 436d6b50 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d6b50(int *param_1,int *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  code *pcVar5;
  int *piVar6;
  undefined4 uVar7;
  undefined2 uStack_12;
  
  iVar3 = *param_2;
  iVar4 = _DAT_436d6c8c + 0x436d6b5a;
  if ((iVar3 == 0) || (0x47 < iVar3)) {
    uVar7 = 1;
  }
  else {
    param_1[0x5c] = iVar3;
    bVar1 = *(byte *)(param_2 + 1);
    *(byte *)((int)param_1 + 0x266) = bVar1;
    if (1 < bVar1) {
      *(undefined1 *)((int)param_1 + 0x266) = 0;
    }
    uVar7 = *(undefined4 *)(iVar4 + _DAT_436d6c94);
    if ((*(char *)(*(int *)(iVar4 + _DAT_436d6c90) + 0x7c) != -1) && (iVar3 == 0x11)) {
      pcVar5 = *(code **)(*param_1 + 0xa0);
      uVar2 = FUN_43ad9438(param_1 + 6,5,uVar7,0xd);
      (*pcVar5)(param_1,uVar2);
    }
    piVar6 = param_1 + 6;
    iVar3 = FUN_43ad9438(piVar6,param_1[0x5c],uVar7,0xd);
    *(char *)(param_1 + 0x5f) = (char)iVar3;
    if (iVar3 == 0xff) {
      uVar7 = 2;
    }
    else {
      (**(code **)(*param_1 + 0xa0))(param_1,iVar3);
      func_0x436d8e6c(piVar6,(char)param_1[0x5f],param_1[0x9b]);
      iVar3 = FUN_436d8a74(piVar6,param_1[0x5c]);
      if (iVar3 != 0) {
        *(char *)((int)param_1 + 10) = (char)param_1[0x5d];
        *(char *)((int)param_1 + 0xb) = (char)param_1[0x5c];
        uVar7 = FUN_436d6118();
        iVar3 = FUN_436d6450(uVar7,&uStack_12);
        if (iVar3 != 0) {
          uStack_12 = 0xffff;
        }
        *(undefined2 *)(param_1 + 1) = uStack_12;
      }
      iVar3 = FUN_436d9f70(param_1 + 0x3f,1);
      if (iVar3 != 0) {
        iVar3 = param_1[0x5d];
        if ((iVar3 != param_1[0x5c]) || (param_1[0x5e] != iVar3)) {
          FUN_436d6738(0xbc,0,3,_DAT_436d6c98 + 0x436d6c4c,param_1[0x5e],iVar3,param_1[0x5c],
                       *(undefined1 *)((int)param_1 + 0x266));
        }
      }
      iVar3 = FUN_436d9f70(param_1 + 0x3f,8);
      uVar7 = 0;
      if (iVar3 != 0) {
        FUN_436d6738(0xbc,0,3,_DAT_436d6c9c + 0x436d6c7c,param_1[0x5e],param_1[0x5d],param_1[0x5c],
                     *(undefined1 *)((int)param_1 + 0x266));
        uVar7 = 0;
      }
    }
  }
  return uVar7;
}


/* 436d6f6c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d6f6c(int param_1,ushort *param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  undefined1 uVar4;
  byte bVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  ushort *puVar10;
  byte bVar11;
  int iVar12;
  short sVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  undefined4 in_stack_ffffffa0;
  undefined2 uVar20;
  
  iVar7 = _DAT_436d72a0;
  uVar20 = (undefined2)((uint)in_stack_ffffffa0 >> 0x10);
  iVar18 = _DAT_436d7298 + 0x436d6f84;
  if (*(int *)(param_1 + 0x170) == 0x11) {
    iVar7 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar7 != 0) {
      FUN_436d6738(0xbc,0,3,_DAT_436d729c + 0x436d6fa6,*(undefined4 *)(param_1 + 0x170));
    }
    return 2;
  }
  uVar1 = param_2[2];
  uVar17 = (uint)uVar1;
  uVar2 = *param_2;
  uVar16 = (uint)uVar2;
  uVar3 = param_2[3];
  uVar4 = *(undefined1 *)((int)param_2 + 9);
  *(uint *)(param_1 + 0x3a8) = uVar17;
  iVar8 = *(int *)(iVar18 + _DAT_436d72a4);
  iVar19 = *(int *)(iVar18 + _DAT_436d72a8);
  iVar12 = *(int *)(iVar18 + _DAT_436d72ac);
  iVar14 = *(int *)(iVar18 + _DAT_436d72b0);
  iVar15 = *(int *)(iVar18 + _DAT_436d72b4);
  *(char *)(*(int *)(iVar18 + iVar7) + 2) = (char)uVar1;
  bVar11 = (byte)(uVar1 >> 8) & 0xf;
  *(byte *)(iVar8 + 2) = *(byte *)(iVar8 + 2) & 0xf0 | bVar11;
  bVar5 = (byte)(uVar2 >> 8) & 0x3f;
  *(char *)(iVar19 + 2) = (char)uVar2;
  bVar6 = (byte)(uVar3 >> 8) & 0xf;
  *(byte *)(iVar12 + 2) = *(byte *)(iVar12 + 2) & 0xc0 | bVar5;
  *(char *)(iVar14 + 2) = (char)uVar3;
  *(byte *)(iVar15 + 2) = *(byte *)(iVar15 + 2) & 0xf0 | bVar6;
  if (*(char *)(*(int *)(iVar18 + _DAT_436d72b8) + 0x7f) != -1) {
    iVar15 = *(int *)(iVar18 + _DAT_436d72c0);
    iVar8 = *(int *)(iVar18 + _DAT_436d72c4);
    iVar7 = *(int *)(iVar18 + _DAT_436d72c8);
    iVar12 = *(int *)(iVar18 + _DAT_436d72cc);
    iVar14 = *(int *)(iVar18 + _DAT_436d72d0);
    *(char *)(*(int *)(iVar18 + _DAT_436d72bc) + 2) = (char)uVar1;
    *(byte *)(iVar15 + 2) = *(byte *)(iVar15 + 2) & 0xf0 | bVar11;
    *(char *)(iVar8 + 2) = (char)uVar2;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xc0 | bVar5;
    *(char *)(iVar12 + 2) = (char)uVar3;
    *(byte *)(iVar14 + 2) = *(byte *)(iVar14 + 2) & 0xf0 | bVar6;
  }
  iVar7 = FUN_436d8a74(param_1 + 0x18,*(undefined4 *)(param_1 + 0x170));
  if (iVar7 != 0) {
    *(ushort *)(param_1 + 0x10) = uVar1;
    *(ushort *)(param_1 + 0x12) = uVar2;
  }
  iVar7 = *(int *)(iVar18 + _DAT_436d72d4);
  switch(uVar4) {
  case 0:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xfb;
    bVar11 = *(byte *)(iVar7 + 2) & 0x7f;
    break;
  case 1:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xef;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
    iVar7 = FUN_436d6f34(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
    uVar9 = uVar16 * (*(uint *)(iVar7 + 4) >> 8);
    goto code_r0x436d719e;
  case 2:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x10;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xbf;
    *(char *)(*(int *)(iVar18 + _UNK_436d72d8) + 2) = (char)param_2[4];
    *(char *)(*(int *)(iVar18 + _UNK_436d72dc) + 2) = (char)param_2[10];
    iVar7 = FUN_436d6f34(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
    sVar13 = FUN_4355faf0(*(uint *)(iVar7 + 4) >> 8,1000);
    sVar13 = uVar2 * sVar13 + 1 + (short)(((byte)param_2[10] + 1) * 0x26aa >> 0x10);
    goto code_r0x436d71e0;
  case 3:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x10;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
    uVar9 = (uint)param_2[8];
code_r0x436d719e:
    sVar13 = FUN_4355faf0(uVar9,1000);
    *(short *)(param_1 + 0x3a0) = sVar13 + 1;
    goto code_r0x436d71e4;
  case 4:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xfb;
    bVar11 = *(byte *)(iVar7 + 2) | 0x80;
    break;
  default:
    return 1;
  }
  *(byte *)(iVar7 + 2) = bVar11;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xef;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
  puVar10 = (ushort *)
            func_0x436d6f50(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
  sVar13 = (*puVar10 >> 8) + 1;
code_r0x436d71e0:
  *(short *)(param_1 + 0x3a0) = sVar13;
code_r0x436d71e4:
  iVar18 = param_1 + 0xfc;
  FUN_43ad9a40(iVar18,uVar17,uVar16,uVar3,uVar4,0);
  FUN_43ad99d4(iVar18,*(undefined4 *)(param_1 + 0x14c),*(undefined4 *)(param_1 + 0x150),
               *(undefined4 *)(param_1 + 0x154),*(undefined4 *)(param_1 + 0x158),
               *(undefined4 *)(param_1 + 0x15c),
               CONCAT22(uVar20,(short)*(undefined4 *)(param_1 + 0x160)));
  iVar7 = FUN_436d9f70(iVar18,1);
  if (iVar7 != 0) {
    iVar7 = *(int *)(param_1 + 0x174);
    if ((iVar7 != *(int *)(param_1 + 0x170)) || (*(int *)(param_1 + 0x178) != iVar7)) {
      FUN_436d6738(0xbc,0,3,&UNK_436d7246 + _UNK_436d72e0,*(int *)(param_1 + 0x178),iVar7,
                   *(int *)(param_1 + 0x170),uVar17,uVar16,uVar3,uVar4);
    }
  }
  iVar7 = FUN_436d9f70(iVar18,8);
  if (iVar7 != 0) {
    FUN_436d6738(0xbc,0,3,&UNK_436d7284 + _UNK_436d72e4,*(undefined4 *)(param_1 + 0x178),
                 *(undefined4 *)(param_1 + 0x174),*(undefined4 *)(param_1 + 0x170),uVar17,uVar16,
                 uVar3,uVar4);
  }
  return 0;
}

