/* S41: read-only exports. */

/* 437feef8 */

undefined4 FUN_437feef8(char *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_437876dc();
  iVar1 = FUN_43b00cb4();
  if ((iVar1 != 2) || ((*param_1 != '\x04' && (*param_1 != '\x06')))) {
    FUN_437876dc();
    iVar1 = FUN_43b00cb4();
    if ((iVar1 == 1) && (*param_1 == '\x01')) {
      uVar2 = FUN_437876dc();
      iVar1 = FUN_43805854(uVar2,*(undefined2 *)(param_1 + 2));
      if (iVar1 != 0) {
        FUN_437876dc();
        FUN_43805808();
      }
    }
    if (param_2 - 8U < 0x400) {
      iVar1 = FUN_435612d0(param_3,&uStack_14,param_2,1);
      if (iVar1 != 0) {
        return 0xffffffff;
      }
      FUN_43b0091c(uStack_14,DAT_437fefac);
      FUN_439c5320(uStack_14,param_1,param_2);
      iVar1 = FUN_4356120c(param_3,uStack_14);
      if (iVar1 == 0) {
        return 0;
      }
      return 0xffffffff;
    }
    if (param_2 == 0) {
      return 0;
    }
    FUN_437fed58(3,9,1,DAT_437fefb0 + 0x437fef8e,param_2);
    FUN_43902718(DAT_437fefb4 + 0x437fef9a,param_2);
  }
  return 0;
}


/* 437ff038 */

void FUN_437ff038(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uStack_14;
  undefined1 auStack_13 [3];
  undefined4 uStack_10;
  undefined1 uStack_c;
  undefined3 uStack_b;
  
  _uStack_c = CONCAT31((int3)((uint)param_4 >> 8),(char)param_1);
  _uStack_14 = CONCAT31(SUB43((uint)param_2 >> 8,0),5);
  _uStack_14 = CONCAT22(0x402d,_uStack_14);
  uStack_10 = 0;
  FUN_437fefb8(DAT_437ff060,&uStack_14,9,0,param_1);
  return;
}


/* 43805870 */

undefined4 FUN_43805870(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 auStack_1c [2];
  
  iVar1 = FUN_435612d0(DAT_43805910,auStack_1c,param_3,1);
  if (iVar1 == 0) {
    FUN_43b00b42(auStack_1c[0],DAT_43805914);
    FUN_439c5320(auStack_1c[0],param_2,param_3);
    iVar1 = FUN_4356120c(DAT_43805910,auStack_1c[0]);
    if (iVar1 == 0) {
      uVar2 = 1;
    }
    else {
      FUN_435612ec(DAT_43805910,auStack_1c[0]);
      iVar3 = DAT_43805928 + 0x438058ee;
      FUN_43805604(3,0xd,1,DAT_43805924 + 0x438058ec,iVar1,iVar3,0x765);
      FUN_43902718(DAT_4380592c + 0x43805902,iVar1,iVar3,0x765);
      uVar2 = 0;
    }
  }
  else {
    iVar3 = DAT_4380591c + 0x43805898;
    FUN_43805604(3,0xd,1,DAT_43805918 + 0x43805894,iVar1,iVar3,0x756);
    FUN_43902718(DAT_43805920 + 0x438058ae,iVar1,iVar3,0x756);
    uVar2 = 0;
  }
  return uVar2;
}


/* 4356120c */

void FUN_4356120c(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_43561220 + 0x43561216 + DAT_43561224) + 0x14) + 0x1d4))();
  return;
}


/* 4390406c */

void FUN_4390406c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  byte *pbVar4;
  int *piVar5;
  
  iVar2 = FUN_435612d0();
  if (iVar2 != 0) {
    pbVar4 = (byte *)(DAT_439040e4 + 0x4390408e);
    piVar5 = (int *)(DAT_439040e8 + 0x43904092);
    bVar1 = *pbVar4;
    iVar3 = DAT_439040ec + 0x43904096;
    *piVar5 = iVar2;
    *pbVar4 = bVar1 + 1;
    FUN_43903f5c(5,0,1,iVar3,iVar2,bVar1 + 1);
    FUN_43902718(DAT_439040f0 + 0x439040b4,*piVar5,*pbVar4);
    if (*pbVar4 < 6) {
      FUN_43901a8c(3,2,*piVar5);
    }
    FUN_435612d0(param_1,param_2,param_3,1);
    return;
  }
  return;
}


/* 43b0091c */

void FUN_43b0091c(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + -4) = param_2;
  return;
}

