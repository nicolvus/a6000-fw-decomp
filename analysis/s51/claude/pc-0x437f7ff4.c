
void FUN_437f7ff0(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_24 [4];
  undefined1 auStack_20 [4];
  undefined4 local_1c [2];
  
  iVar5 = DAT_437f80a4 + 0x437f8004;
  if (*(int *)(param_1 + 0x4b70) == 6) {
    uVar2 = 0x2f;
  }
  else {
    iVar1 = FUN_43a12c64();
    if (iVar1 == 3) {
      uVar2 = 1;
    }
    else {
      iVar1 = FUN_43affd86(param_1);
      if (iVar1 == 0) {
        uVar2 = FUN_437f7f98(*(undefined4 *)(param_1 + 0x1e0),*(undefined4 *)(param_1 + 0x6c8));
      }
      else {
        uVar2 = 0xb;
      }
    }
  }
  iVar1 = DAT_437f80a8;
  *(undefined4 *)(param_1 + 0x4d0) = uVar2;
  uVar4 = (uint)*(byte *)(*(int *)(iVar5 + iVar1) + 0x86);
  if (uVar4 != 0) {
    *(uint *)(param_1 + 0x4d0) = uVar4;
  }
  uVar2 = FUN_43ae9332(*(undefined4 *)(param_1 + 0x4d0));
  uVar6 = *(undefined4 *)(param_1 + 0x4d0);
  *(undefined4 *)(param_1 + 0x6c4) = uVar2;
  uVar2 = FUN_43affda2(*(undefined4 *)(param_1 + 0x6c));
  uVar3 = FUN_436d6118();
  iVar5 = FUN_43ad908e(uVar3,uVar2,uVar6,local_1c,auStack_20,auStack_24);
  if (iVar5 != 0) {
    FUN_437f7e44(5,1,1,DAT_437f80ac + 0x437f807c,iVar5,uVar2,uVar6);
    FUN_43902718(DAT_437f80b0 + 0x437f8090,iVar5,uVar2,uVar6);
    local_1c[0] = 0x1000;
  }
  *(undefined4 *)(param_1 + 0x6d0) = local_1c[0];
  return;
}

