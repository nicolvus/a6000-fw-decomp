/* S41: read-only exports. */

/* 437d99a4 */

void FUN_437d99a4(void)

{
  byte *pbVar1;
  
  FUN_437d97e4();
  pbVar1 = *(byte **)(DAT_437d99f4 + 0x437d99b2 + DAT_437d99f8);
  if ((*pbVar1 & 0x10) != 0) {
    **(undefined4 **)(pbVar1 + 0x20) = *(undefined4 *)(pbVar1 + 0x28);
  }
  if ((*pbVar1 & 1) != 0) {
    FUN_437d9884(3,7,1,DAT_437d99fc + 0x437d99dc,*(undefined4 **)(pbVar1 + 0x20),
                 **(undefined4 **)(pbVar1 + 0x20));
    FUN_43902718(DAT_437d9a00 + 0x437d99e8,*(undefined4 **)(pbVar1 + 0x20),
                 **(undefined4 **)(pbVar1 + 0x20));
    return;
  }
  return;
}


/* 437d9ae0 */

void FUN_437d9ae0(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  byte *pbVar7;
  undefined4 uVar8;
  int iVar9;
  undefined4 uVar10;
  int *piVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  
  iVar6 = DAT_437d9c90 + 0x437d9af2;
  uVar1 = *(undefined4 *)(iVar6 + DAT_437d9c94);
  uVar2 = *(undefined4 *)(iVar6 + DAT_437d9c9c);
  uVar3 = *(undefined4 *)(iVar6 + DAT_437d9ca4);
  uVar4 = *(undefined4 *)(iVar6 + DAT_437d9cac);
  uVar10 = *(undefined4 *)(iVar6 + DAT_437d9cb4);
  uVar5 = *(undefined4 *)(iVar6 + DAT_437d9cc4);
  uVar12 = *(undefined4 *)(iVar6 + DAT_437d9cdc);
  uVar13 = *(undefined4 *)(iVar6 + DAT_437d9ce4);
  iVar9 = *(int *)(iVar6 + DAT_437d9cec);
  piVar11 = *(int **)(iVar6 + DAT_437d9cf0);
  uVar8 = *(undefined4 *)(iVar6 + DAT_437d9cf4);
  FUN_438968c4(param_2,piVar11,uVar8,*(undefined4 *)(iVar6 + DAT_437d9cf8),uVar1,
               *(undefined4 *)(iVar6 + DAT_437d9c98),uVar2,*(undefined4 *)(iVar6 + DAT_437d9ca0),
               uVar3,*(undefined4 *)(iVar6 + DAT_437d9ca8),uVar4,
               *(undefined4 *)(iVar6 + DAT_437d9cb0),uVar10,*(undefined4 *)(iVar6 + DAT_437d9cb8),
               *(undefined4 *)(iVar6 + DAT_437d9cbc),*(undefined4 *)(iVar6 + DAT_437d9cc0),uVar5,
               *(undefined4 *)(iVar6 + DAT_437d9cc8),*(undefined4 *)(iVar6 + DAT_437d9ccc),
               *(undefined4 *)(iVar6 + DAT_437d9cd0),*(undefined4 *)(iVar6 + DAT_437d9cd4),
               *(undefined4 *)(iVar6 + DAT_437d9cd8),uVar12,*(undefined4 *)(iVar6 + DAT_437d9ce0),
               uVar13,*(undefined4 *)(iVar6 + DAT_437d9ce8),iVar9);
  FUN_43888268(uVar8,uVar10,param_2);
  pbVar7 = *(byte **)(iVar6 + DAT_437d9cfc);
  if (*piVar11 != 8) {
    FUN_43b158d8(param_1 + 0x135,param_2);
    FUN_43b14ff4(param_2,uVar12);
    FUN_43b14b0e(uVar8,uVar13);
    FUN_43b13a02(param_2,uVar2);
    FUN_43b16676(param_2);
    FUN_43b15cf4(param_1 + 0x134,param_2);
    FUN_4387d590(uVar8,param_2);
    FUN_43b13020(uVar8,uVar4,param_2);
    FUN_43b13984(param_2);
    FUN_43b15212(param_2,iVar9 + 2);
    FUN_43898a2c(uVar8,uVar3,param_2);
    FUN_438a4ec8(uVar8,uVar1,param_2);
    if (pbVar7[0x3a] == 0xff) {
      FUN_438b0854(param_2,iVar9 + 0xa8);
    }
    else {
      FUN_438b1a44(uVar8,uVar5,param_2);
    }
  }
  if ((*pbVar7 & 0x40) != 0) {
    **(undefined4 **)(pbVar7 + 0x20) = *(undefined4 *)(pbVar7 + 0x28);
  }
  if ((*pbVar7 & 4) != 0) {
    FUN_437d9884(3,7,1,DAT_437d9d00 + 0x437d9c74,*(undefined4 **)(pbVar7 + 0x20),
                 **(undefined4 **)(pbVar7 + 0x20));
    FUN_43902718(DAT_437d9d04 + 0x437d9c80,*(undefined4 **)(pbVar7 + 0x20),
                 **(undefined4 **)(pbVar7 + 0x20));
    return;
  }
  return;
}


/* 43acabf4 */

void FUN_43acabf4(int param_1)

{
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 0x10) = 0;
  return;
}


/* 436e7d74 */

int FUN_436e7d74(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined1 auStack_34 [20];
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  FUN_43acac1a(auStack_34,0);
  iVar1 = DAT_436e7dbc;
  FUN_43acac02(param_1,param_2,auStack_34);
  FUN_43ada210(param_1 + 0x18,param_3);
  uStack_20 = *(undefined4 *)(iVar1 + 0x436e7d9c + DAT_436e7dc0);
  uStack_1c = 0;
  FUN_436e7d3c(param_1,uStack_20,0,param_1);
  return param_1;
}

