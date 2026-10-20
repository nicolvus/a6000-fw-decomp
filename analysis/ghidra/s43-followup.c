/* S41: read-only exports. */

/* 43ad95ce */

bool FUN_43ad95ce(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = *(undefined4 *)(param_1 + 0x294);
  uVar1 = FUN_43ad95ca(uVar3);
  uVar3 = FUN_43ad95c6(uVar3);
  iVar2 = FUN_43ad9438(param_1 + 0x18,param_2,uVar1,uVar3,param_4);
  return iVar2 != 0xff;
}


/* 43ad9262 */

void FUN_43ad9262(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  *(char *)(param_2 + 2) = (char)((uint)param_4 >> 8);
  *(char *)(param_3 + 2) = (char)param_4;
  return;
}


/* 436d67e4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 vtable_436d67e4(int param_1,ushort *param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  short sVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  ushort uVar12;
  uint uVar13;
  int iVar14;
  
  iVar5 = DAT_436d69a8;
  uVar8 = *(uint *)(param_1 + 0x170);
  iVar11 = _DAT_436d69a0 + 0x436d67f4;
  if (uVar8 == 0x11) {
    iVar5 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar5 != 0) {
      FUN_436d6738(0xbc,0,3,DAT_436d69a4 + 0x436d681c,*(undefined4 *)(param_1 + 0x170));
    }
    return 2;
  }
  uVar1 = *param_2;
  uVar13 = (uint)uVar1;
  uVar2 = param_2[1];
  uVar3 = param_2[2];
  *(uint *)(param_1 + 0x3ac) = uVar13;
  iVar5 = *(int *)(iVar11 + iVar5);
  uVar6 = (uint)*(byte *)(iVar5 + 99);
  if (uVar6 == 0xff) {
    uVar6 = (uint)(byte)param_2[3];
  }
  if (uVar6 < 0xc) {
    uVar12 = (ushort)*(byte *)(DAT_436d69ac + 0x436d6848 + uVar6);
  }
  else {
    uVar12 = 0;
  }
  iVar7 = *(int *)(iVar11 + DAT_436d69b4);
  if (uVar8 < 0x1b) {
    uVar8 = 1 << (uVar8 & 0xff);
    if ((uVar8 & DAT_436d6998) != 0) {
      sVar4 = uVar12 * 0x12 + 0x1ab;
      goto LAB_436d6886;
    }
    if ((uVar8 & DAT_436d699c) != 0) {
      sVar4 = uVar12 * 0x12 + 0xd3;
      goto LAB_436d6886;
    }
  }
  sVar4 = 0;
LAB_436d6886:
  *(char *)(*(int *)(iVar11 + DAT_436d69b0) + 2) = (char)sVar4;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xc0 | (byte)((ushort)sVar4 >> 8);
  if (*(char *)(iVar5 + 0x7f) == -1) {
    iVar5 = *(int *)(iVar11 + DAT_436d69bc);
    iVar14 = *(int *)(iVar11 + DAT_436d69c0);
    iVar7 = *(int *)(iVar11 + DAT_436d69c4);
    iVar9 = *(int *)(iVar11 + DAT_436d69c8);
    iVar10 = *(int *)(iVar11 + DAT_436d69cc);
    *(char *)(*(int *)(iVar11 + DAT_436d69b8) + 2) = (char)uVar1;
    *(byte *)(iVar5 + 2) = *(byte *)(iVar5 + 2) & 0xf0 | (byte)(uVar1 >> 8) & 0xf;
    *(char *)(iVar14 + 2) = (char)uVar2;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xc0 | (byte)(uVar2 >> 8) & 0x3f;
    *(char *)(iVar9 + 2) = (char)uVar3;
    *(byte *)(iVar10 + 2) = *(byte *)(iVar10 + 2) & 0xf0 | (byte)(uVar3 >> 8) & 0xf;
    *(byte *)(*(int *)(iVar11 + DAT_436d69d0) + 2) =
         *(byte *)(*(int *)(iVar11 + DAT_436d69d0) + 2) & 0xf0 | (byte)uVar12 & 0xf;
    iVar5 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar5 != 0) {
      iVar5 = *(int *)(param_1 + 0x174);
      if ((iVar5 != *(int *)(param_1 + 0x170)) || (*(int *)(param_1 + 0x178) != iVar5)) {
        FUN_436d6738(0xbc,0,3,DAT_436d69d4 + 0x436d6946,*(int *)(param_1 + 0x178),iVar5,
                     *(int *)(param_1 + 0x170),uVar13,uVar2,uVar3,(char)param_2[3],uVar12);
      }
    }
    iVar5 = FUN_436d9f70(param_1 + 0xfc,8);
    if (iVar5 == 0) {
      return 0;
    }
    FUN_436d6738(0xbc,0,3,DAT_436d69d8 + 0x436d6986,*(undefined4 *)(param_1 + 0x178),
                 *(undefined4 *)(param_1 + 0x174),*(undefined4 *)(param_1 + 0x170),uVar13,uVar2,
                 uVar3,(char)param_2[3],uVar12);
  }
  return 0;
}

