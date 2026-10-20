/* S41: read-only exports. */

/* 43ae8450 */

int FUN_43ae8450(void)

{
  byte bVar1;
  short sVar2;
  undefined1 uVar3;
  short *psVar4;
  int *piVar5;
  int iVar6;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  piVar5 = (int *)FUN_437876dc();
  uStack_14 = 1;
  iVar6 = DAT_43806324 + 0x4380629a;
  if (piVar5[0x15a] == 1) {
    if (*piVar5 == 0) {
      return 1;
    }
    uStack_18 = piVar5;
    psVar4 = (short *)FUN_43ae847c();
    if (((ushort)(*psVar4 - 0x142U) < 2) && (piVar5[0x163] == 0)) {
      iVar6 = *(int *)(iVar6 + DAT_43806328);
      bVar1 = *(byte *)(iVar6 + 0x47);
      if ((bVar1 & 4) == 0) {
        if (*(char *)(iVar6 + 0x49) == '\0') {
          piVar5[0x163] = 1;
        }
        else {
          piVar5[0x163] = bVar1 & 4;
        }
        uStack_18 = (int *)CONCAT31(uStack_18._1_3_,6);
        uVar3 = FUN_43b00cb4(piVar5);
        sVar2 = *(short *)((int)piVar5 + 0x57a);
        uStack_14 = 1;
        *(short *)((int)piVar5 + 0x57a) = sVar2 + 1;
        uStack_18 = (int *)CONCAT22(sVar2,CONCAT11(uVar3,(undefined1)uStack_18));
        iVar6 = FUN_438061c4(piVar5,&uStack_18,8);
        if (iVar6 != 0) {
          return iVar6;
        }
        piVar5[0x163] = 0;
        return 0;
      }
    }
  }
  return 1;
}


/* 43b00ed8 */

uint FUN_43b00ed8(uint param_1,int param_2)

{
  ushort uVar1;
  short sVar2;
  undefined1 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  undefined1 uStack_c;
  undefined1 auStack_b [3];
  
  if (*(int *)(param_1 + 0x568) == 1) {
    uVar5 = *(ushort *)(*(int *)(param_2 + 8) + 0x26c) - 0x120;
    sVar2 = (short)uVar5;
    uVar4 = uVar5 & 0xffff;
    if ((0xe < uVar4) || (uVar5 = 0, (1 << ((int)sVar2 & 0xffU) & 0x7f9bU) == 0)) {
      if ((*(int *)(param_1 + 0x568) == 1) &&
         ((*(int *)(param_1 + 0x56c) == 0 &&
          ((*(byte *)(*(int *)(DAT_438063f8 + 0x438063a6 + DAT_438063fc) + 0x47) & 1) == 0)))) {
        *(undefined4 *)(param_1 + 0x56c) = 1;
        auStack_b = SUB43(uVar5 >> 8,0);
        _uStack_c = CONCAT31(auStack_b,9);
        uVar4 = param_1;
        uVar3 = FUN_43b00cb4();
        uVar1 = *(ushort *)(param_1 + 0x57a);
        iVar6 = uVar1 + 1;
        *(short *)(param_1 + 0x57a) = (short)iVar6;
        _uStack_c = CONCAT11(uVar3,uStack_c);
        _uStack_c = CONCAT22(uVar1,_uStack_c);
        uVar4 = FUN_438061c4(param_1,&uStack_c,4,iVar6,uVar4);
        if (uVar4 == 0) {
          *(undefined4 *)(param_1 + 0x56c) = 0;
          return 0;
        }
        return uVar4;
      }
      return 1;
    }
  }
  else {
    uVar4 = param_1;
    if ((*(int *)(param_1 + 0x568) == 2) && (1 < *(ushort *)(*(int *)(param_2 + 8) + 0x224) - 0x125)
       ) {
      if ((*(int *)(param_1 + 0x568) == 2) && (*(int *)(param_1 + 0x56c) == 0)) {
        if ((*(byte *)(*(int *)(DAT_43806390 + 0x4380633a + DAT_43806394) + 0x47) & 1) == 0) {
          *(undefined4 *)(param_1 + 0x56c) = 1;
          auStack_b = SUB43((uint)param_2 >> 8,0);
          _uStack_c = CONCAT31(auStack_b,9);
          uVar3 = FUN_43b00cb4();
          uVar1 = *(ushort *)(param_1 + 0x57a);
          iVar6 = uVar1 + 1;
          *(short *)(param_1 + 0x57a) = (short)iVar6;
          _uStack_c = CONCAT11(uVar3,uStack_c);
          _uStack_c = CONCAT22(uVar1,_uStack_c);
          uVar4 = FUN_438061c4(param_1,&uStack_c,4,iVar6,uVar4);
          if (uVar4 == 0) {
            *(undefined4 *)(param_1 + 0x56c) = 0;
          }
        }
        else {
          uVar4 = 1;
        }
      }
      else {
        uVar4 = 1;
      }
      return uVar4;
    }
  }
  return uVar4;
}


/* 43b00ed8 */

uint FUN_43b00ed8(uint param_1,int param_2)

{
  ushort uVar1;
  short sVar2;
  undefined1 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  undefined1 uStack_c;
  undefined1 auStack_b [3];
  
  if (*(int *)(param_1 + 0x568) == 1) {
    uVar5 = *(ushort *)(*(int *)(param_2 + 8) + 0x26c) - 0x120;
    sVar2 = (short)uVar5;
    uVar4 = uVar5 & 0xffff;
    if ((0xe < uVar4) || (uVar5 = 0, (1 << ((int)sVar2 & 0xffU) & 0x7f9bU) == 0)) {
      if ((*(int *)(param_1 + 0x568) == 1) &&
         ((*(int *)(param_1 + 0x56c) == 0 &&
          ((*(byte *)(*(int *)(DAT_438063f8 + 0x438063a6 + DAT_438063fc) + 0x47) & 1) == 0)))) {
        *(undefined4 *)(param_1 + 0x56c) = 1;
        auStack_b = SUB43(uVar5 >> 8,0);
        _uStack_c = CONCAT31(auStack_b,9);
        uVar4 = param_1;
        uVar3 = FUN_43b00cb4();
        uVar1 = *(ushort *)(param_1 + 0x57a);
        iVar6 = uVar1 + 1;
        *(short *)(param_1 + 0x57a) = (short)iVar6;
        _uStack_c = CONCAT11(uVar3,uStack_c);
        _uStack_c = CONCAT22(uVar1,_uStack_c);
        uVar4 = FUN_438061c4(param_1,&uStack_c,4,iVar6,uVar4);
        if (uVar4 == 0) {
          *(undefined4 *)(param_1 + 0x56c) = 0;
          return 0;
        }
        return uVar4;
      }
      return 1;
    }
  }
  else {
    uVar4 = param_1;
    if ((*(int *)(param_1 + 0x568) == 2) && (1 < *(ushort *)(*(int *)(param_2 + 8) + 0x224) - 0x125)
       ) {
      if ((*(int *)(param_1 + 0x568) == 2) && (*(int *)(param_1 + 0x56c) == 0)) {
        if ((*(byte *)(*(int *)(DAT_43806390 + 0x4380633a + DAT_43806394) + 0x47) & 1) == 0) {
          *(undefined4 *)(param_1 + 0x56c) = 1;
          auStack_b = SUB43((uint)param_2 >> 8,0);
          _uStack_c = CONCAT31(auStack_b,9);
          uVar3 = FUN_43b00cb4();
          uVar1 = *(ushort *)(param_1 + 0x57a);
          iVar6 = uVar1 + 1;
          *(short *)(param_1 + 0x57a) = (short)iVar6;
          _uStack_c = CONCAT11(uVar3,uStack_c);
          _uStack_c = CONCAT22(uVar1,_uStack_c);
          uVar4 = FUN_438061c4(param_1,&uStack_c,4,iVar6,uVar4);
          if (uVar4 == 0) {
            *(undefined4 *)(param_1 + 0x56c) = 0;
          }
        }
        else {
          uVar4 = 1;
        }
      }
      else {
        uVar4 = 1;
      }
      return uVar4;
    }
  }
  return uVar4;
}


/* 43806590 */

void FUN_43806590(int param_1,undefined2 param_2)

{
  int iVar1;
  undefined1 uStack_18;
  undefined1 uStack_17;
  short sStack_16;
  undefined2 uStack_14;
  
  uStack_18 = 0xb;
  uStack_17 = FUN_43b00cb4();
  sStack_16 = *(short *)(param_1 + 0x57a);
  *(short *)(param_1 + 0x57a) = sStack_16 + 1;
  uStack_14 = param_2;
  iVar1 = FUN_438064c8(param_1,&uStack_18,6);
  if (iVar1 == 0) {
    iVar1 = DAT_438065f4 + 0x438065d4;
    FUN_43805604(3,0xd,1,DAT_438065f0 + 0x438065d2,iVar1,0x73f);
    FUN_43902718(DAT_438065f8 + 0x438065e8,iVar1,0x73f);
  }
  return;
}


/* 438065fc */

void FUN_438065fc(int param_1,undefined2 param_2)

{
  int iVar1;
  undefined1 uStack_18;
  undefined1 uStack_17;
  short sStack_16;
  undefined2 uStack_14;
  
  uStack_18 = 5;
  uStack_17 = FUN_43b00cb4();
  sStack_16 = *(short *)(param_1 + 0x57a);
  *(short *)(param_1 + 0x57a) = sStack_16 + 1;
  uStack_14 = param_2;
  iVar1 = FUN_438064c8(param_1,&uStack_18,6);
  if (iVar1 == 0) {
    iVar1 = DAT_43806660 + 0x43806640;
    FUN_43805604(3,0xd,1,DAT_4380665c + 0x4380663e,iVar1,0x72a);
    FUN_43902718(DAT_43806664 + 0x43806654,iVar1,0x72a);
  }
  return;
}


/* 43806668 */

void FUN_43806668(int param_1,undefined2 param_2)

{
  int iVar1;
  undefined1 uStack_18;
  undefined1 uStack_17;
  short sStack_16;
  undefined2 uStack_14;
  
  uStack_18 = 2;
  uStack_17 = FUN_43b00cb4();
  sStack_16 = *(short *)(param_1 + 0x57a);
  *(short *)(param_1 + 0x57a) = sStack_16 + 1;
  uStack_14 = param_2;
  iVar1 = FUN_438064c8(param_1,&uStack_18,6);
  if (iVar1 == 0) {
    iVar1 = DAT_438066cc + 0x438066ac;
    FUN_43805604(3,0xd,1,DAT_438066c8 + 0x438066aa,iVar1,0x6fd);
    FUN_43902718(DAT_438066d0 + 0x438066c0,iVar1,0x6fd);
  }
  return;
}


/* 43b00fa4 */

void FUN_43b00fa4(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 2) {
    *(undefined1 *)(param_1 + 0xe54) = 4;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 0xe56) = sVar1;
    *(short *)(param_1 + 0xd5c) = sVar1;
    *(undefined1 *)(param_1 + 0xe55) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 0xe54,0x18);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0xd58) = 0;
    }
  }
  return;
}


/* 43b01026 */

void FUN_43b01026(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    *(undefined1 *)(param_1 + 4) = 1;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 6) = sVar1;
    *(short *)(param_1 + 0x578) = sVar1;
    *(undefined1 *)(param_1 + 5) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 4,0x564);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0x574) = 0;
    }
  }
  return;
}


/* 43809f58 */

void FUN_43809f58(undefined4 param_1,char *param_2,undefined4 param_3,undefined1 *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int aiStack_1c [2];
  
  FUN_437876dc();
  iVar2 = FUN_43b00cb4();
  if ((iVar2 != 2) ||
     (((cVar1 = *param_2, cVar1 != '\x04' && (cVar1 != '\x06')) &&
      ((cVar1 != '\x01' || (param_4 != &DAT_00020002)))))) {
    FUN_437876dc();
    iVar2 = FUN_43b00cb4();
    if ((iVar2 == 1) && (*param_2 == '\x01')) {
      uVar3 = FUN_437876dc();
      iVar2 = FUN_43805854(uVar3,*(undefined2 *)(param_2 + 2));
      if (iVar2 != 0) {
        FUN_437876dc();
        FUN_43805808();
      }
    }
    FUN_43ae8594(*param_2,*(undefined4 *)(param_2 + 4),*(undefined2 *)(param_2 + 2));
    iVar2 = FUN_435612d0(param_4,aiStack_1c,param_3,1);
    if (iVar2 == 0) {
      *(undefined4 *)(aiStack_1c[0] + -4) = DAT_4380a018;
      FUN_439c5320(aiStack_1c[0],param_2,param_3);
      iVar2 = FUN_4356120c(param_4,aiStack_1c[0]);
      if (iVar2 == 0) {
        return;
      }
      uVar3 = 0x20a;
      iVar4 = DAT_4380a024 + 0x4380a00c;
      iVar5 = DAT_4380a028 + 0x4380a010;
    }
    else {
      uVar3 = 0x1fa;
      iVar4 = DAT_4380a01c + 0x43809fda;
      iVar5 = DAT_4380a020 + 0x43809fde;
    }
    FUN_43787b70(iVar4,uVar3,iVar5,1,iVar2,0,0);
  }
  return;
}


/* 4380a044 */

void FUN_4380a044(int param_1)

{
  *(undefined4 *)(param_1 + -4) = DAT_4380a04c;
  return;
}

