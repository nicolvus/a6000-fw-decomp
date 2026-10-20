/* S41: read-only exports. */

/* 437d9f9c */

void FUN_437d9f9c(int param_1)

{
  short sVar1;
  short sVar2;
  int iVar3;
  char *pcVar4;
  
  sVar1 = *(short *)(param_1 + 0x1a);
  sVar2 = *(short *)(param_1 + 0x18);
  if (*(char *)(*(int *)(DAT_437da058 + 0x437d9fa6 + DAT_437da05c) + 0x9b) == '\0') {
    FUN_437da100(DAT_437da060 + 0x437d9fbe,sVar2,sVar1,param_1 + 0x1c);
    iVar3 = FUN_437d9ea8(sVar2,sVar1);
    if (iVar3 == 0xa000) {
      pcVar4 = (char *)(DAT_437da068 + 0x437d9fe2);
      if ((*pcVar4 != '\0') && (sVar1 == 0)) {
LAB_437da02c:
        *pcVar4 = (char)sVar1;
        FUN_437fc35c(0x3003);
        return;
      }
      FUN_4378a148(0xafff);
    }
    else {
      *(undefined1 *)(DAT_437da064 + 0x437d9fd6) = 1;
      FUN_437fc35c();
    }
  }
  else {
    FUN_437da100(DAT_437da06c + 0x437d9ffc,sVar2,sVar1,param_1 + 0x1c);
    iVar3 = FUN_437d9ea8(sVar2,sVar1);
    if (iVar3 == 0xa000) {
      pcVar4 = (char *)(DAT_437da074 + 0x437da020);
      if (((*pcVar4 != '\0') && (sVar1 == 0)) && (sVar2 == 0x404)) goto LAB_437da02c;
      FUN_4378a148(0xafff);
    }
    else {
      *(undefined1 *)(DAT_437da070 + 0x437da014) = 1;
      FUN_437fc35c();
    }
    if (sVar2 != 0x404) goto LAB_437da04c;
  }
  if (sVar1 == 0) {
    return;
  }
LAB_437da04c:
  thunk_FUN_437e1b60(0);
  return;
}


/* 437da078 */

void FUN_437da078(undefined4 *param_1,uint *param_2)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  ushort *puVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  code *pcVar8;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  int iVar9;
  undefined4 unaff_r6;
  undefined4 unaff_lr;
  
  bVar1 = *(byte *)(*(int *)(DAT_437da0b4 + 0x437da080 + DAT_437da0b8) + 1);
  if ((ushort)bVar1 != *(ushort *)(DAT_437da0bc + 0x437da08c)) {
    *(ushort *)((int)&DAT_437da0b4 + DAT_437da0c0) = (ushort)bVar1;
    FUN_437d9f9c();
  }
  iVar3 = DAT_437da0c8;
  puVar4 = (ushort *)(DAT_437da0c8 + 0x437da0ac);
  *(ushort *)(DAT_437da0c4 + 0x437da0aa) = (ushort)bVar1;
  iVar9 = DAT_437da354 + 0x437da2e8;
  if (((*(int *)(iVar3 + 0x437da308) != 0) && (iVar7 = *(int *)(iVar3 + 0x437da304), -1 < iVar7)) &&
     (iVar7 < *(int *)(iVar3 + 0x437da30c))) {
    pcVar8 = *(code **)(*(int *)(iVar3 + 0x437da308) + iVar7 * 4);
    *param_2 = (uint)*puVar4;
    param_2[1] = (uint)*(ushort *)(iVar3 + 0x437da0ae);
    param_2[2] = iVar3 + 0x437da0b0;
    param_2[4] = iVar3 + 0x437da1d8;
    iVar7 = (*pcVar8)(param_1,param_2,param_2,pcVar8,unaff_r4,unaff_r5,unaff_r6,unaff_lr);
    if (iVar7 == 0) {
      *(int *)(iVar3 + 0x437da304) = *(int *)(iVar3 + 0x437da304) + 1;
      return;
    }
    if (iVar7 == 2) {
      FUN_43af6860(puVar4);
      *(undefined4 *)(iVar3 + 0x437da1d4) = *(undefined4 *)(param_1[0x14] + 0xc);
      FUN_4378a048(iVar3 + 0x437da1d4);
      cVar2 = *(char *)(*(int *)(iVar9 + DAT_437da358) + 0x8d);
      if (cVar2 != '\0') {
        uVar5 = *param_1;
        uVar6 = FUN_437e0560(uVar5,0,0,cVar2,unaff_r4,unaff_lr);
        FUN_437e1d40(uVar5,uVar6);
        return;
      }
    }
  }
  return;
}


/* 43af6860 */

void FUN_43af6860(int param_1)

{
  *(undefined4 *)(param_1 + 600) = 0;
  *(undefined4 *)(param_1 + 0x25c) = 0;
  *(undefined4 *)(param_1 + 0x260) = 0;
  return;
}

