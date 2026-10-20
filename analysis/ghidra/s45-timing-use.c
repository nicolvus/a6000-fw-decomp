/* S41: read-only exports. */

/* 438c828c */

undefined4 FUN_438c828c(int param_1)

{
  undefined2 uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  bool bVar9;
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [24];
  
  FUN_43ae769a(param_1,0xe);
  uVar2 = FUN_437f8a50(param_1);
  iVar6 = DAT_438c8460 + 0x438c82a6;
  iVar3 = FUN_43a12c64();
  if ((iVar3 == 2) || (iVar3 = FUN_43a12c64(), iVar3 == 3)) {
    *(undefined1 *)(param_1 + 0x655) = 0;
    *(undefined2 *)(param_1 + 0x650) = 0;
    *(undefined4 *)(param_1 + 0x64c) = 2;
    *(undefined2 *)(param_1 + 0x652) = 0;
    *(undefined1 *)(param_1 + 0x654) = 0;
  }
  if (*(int *)(param_1 + 0x4b9c) == 0) {
    FUN_43b1e520(param_1);
    uVar1 = *(undefined2 *)(param_1 + 0x650);
    if (*(int *)(param_1 + 0x504) == 1) {
      *(undefined2 *)(param_1 + 0x650) = 0;
    }
    *(undefined2 *)(param_1 + 0x6b8) = *(undefined2 *)(param_1 + 0x12f8);
    uVar4 = FUN_436d6118();
    FUN_436d6320(uVar4,param_1 + 0x64c,*(undefined2 *)(param_1 + 0x4b9c));
    uVar4 = FUN_436d6118();
    FUN_436d6398(uVar4,param_1 + 0x6bc,*(undefined2 *)(param_1 + 0x4b9c));
    FUN_436d6118();
    FUN_43ad9116();
    uVar4 = FUN_436d6118();
    FUN_43ad911c(uVar4,1);
    *(undefined2 *)(param_1 + 0x650) = uVar1;
  }
  else {
    uVar4 = FUN_436d6118();
    FUN_43ad911c(uVar4,0);
  }
  uVar4 = *(undefined4 *)(param_1 + 0x570);
  if (*(int *)(param_1 + 0x740) == 0) {
    iVar3 = FUN_43a12c64();
    if (iVar3 != 3) {
      iVar7 = *(int *)(param_1 + 0x56c);
      FUN_436d6118();
      iVar3 = FUN_43ad90b6();
      FUN_436c2270();
      uVar5 = FUN_436c28d0();
      iVar3 = DAT_438c845c * (iVar3 + 1);
      uVar5 = FUN_4355faf0(iVar7 * 1000,uVar5);
      uVar5 = FUN_4355faf0(iVar3,uVar5);
      *(undefined4 *)(param_1 + 0x570) = uVar5;
    }
  }
  else if (*(char *)(param_1 + 0x60c) == '\0') {
    *(uint *)(param_1 + 0x570) = uVar2 & 0xffff;
  }
  FUN_43901a8c(2,0x107,(uint)*(ushort *)(param_1 + 0x4b64) | *(int *)(param_1 + 0x1d8) << 0x10,
               *(uint *)(param_1 + 0x56c) | *(int *)(param_1 + 0x570) << 0x10);
  if (((*(int *)(param_1 + 0x740) == 0) &&
      (*(undefined2 *)(param_1 + 0x650) = 0, *(char *)(param_1 + 0x4b84) == '\0')) &&
     (*(char *)(param_1 + 0x74f) != '\0')) {
    if (*(char *)(*(int *)(iVar6 + DAT_438c8464) + 0x60) == '\0') {
      uVar5 = 4;
    }
    else {
      uVar5 = 3;
    }
  }
  else {
    uVar5 = 3;
  }
  if (*(int *)(param_1 + 0x4b9c) == 0) {
    FUN_436d6118();
    FUN_43ad9132();
  }
  iVar3 = DAT_438c846c;
  if (*(int *)(param_1 + 0x740) == 0) {
    iVar3 = DAT_438c8468;
  }
  uVar8 = *(undefined4 *)(iVar6 + iVar3);
  if (*(int *)(param_1 + 0x504) == 1) {
    bVar9 = *(int *)(param_1 + 0x4b9c) != 0;
  }
  else {
    bVar9 = false;
  }
  FUN_43acac1a(auStack_34,*(undefined4 *)(iVar6 + DAT_438c8470));
  FUN_43acac1a(auStack_48,uVar8);
  FUN_43795dec(uVar5,param_1 + 0x548,bVar9,auStack_34,auStack_48);
  *(undefined4 *)(param_1 + 0x570) = uVar4;
  return 1;
}

