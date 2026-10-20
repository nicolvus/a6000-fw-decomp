/* S41: read-only exports. */

/* 437f88ec */

void FUN_437f88ec(int param_1)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined2 uStack_24;
  undefined2 uStack_22;
  int iStack_20;
  byte bStack_1c;
  int aiStack_18 [2];
  
  iVar3 = *(int *)(DAT_437f8988 + 0x437f88f4 + DAT_437f898c);
  bVar1 = *(byte *)(iVar3 + 0xc1);
  if ((bVar1 & 2) == 0) {
    uStack_24 = *(undefined2 *)(param_1 + 0x4b54);
    aiStack_18[0] = param_1 + 0x64c;
    uStack_22 = *(undefined2 *)(param_1 + 0x1d8);
    iVar2 = *(int *)(param_1 + 0x4ad0);
    iStack_20 = param_1 + 0x5c8;
    if (iVar2 != 0) {
      iVar2 = iVar2 + 0x20;
    }
    bStack_1c = bVar1 & 2;
    FUN_437b43b4(param_1 + 0x1198,param_1 + 0x20,&uStack_24,aiStack_18,iVar2);
    thunk_FUN_437d0b9c(param_1 + 0x20);
  }
  if ((*(byte *)(iVar3 + 0xc1) & 8) == 0) {
    iVar3 = *(int *)(param_1 + 0x4ad0);
    if (iVar3 != 0) {
      iVar3 = iVar3 + 0x1448;
    }
    FUN_4379ed34(param_1 + 0x2c2c,param_1 + 0x20,iVar3);
  }
  FUN_437d331c(param_1 + 0x20);
  return;
}


/* 43affe80 */

void FUN_43affe80(int param_1)

{
  int iVar1;
  int iVar2;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  int iStack_18;
  undefined1 uStack_14;
  int aiStack_10 [2];
  
  iStack_18 = param_1 + 0x5c8;
  uStack_1c = *(undefined2 *)(param_1 + 0x4b54);
  uStack_1a = 0;
  uStack_14 = 0;
  aiStack_10[0] = param_1 + 0x64c;
  iVar1 = *(int *)(param_1 + 0x4ad0);
  if (iVar1 != 0) {
    iVar1 = iVar1 + 0x20;
  }
  iVar2 = param_1 + 0x20;
  FUN_437b43b4(param_1 + 0x1198,iVar2,&uStack_1c,aiStack_10,iVar1);
  FUN_437d331c(iVar2);
  thunk_FUN_437d0b9c(iVar2);
  return;
}


/* 43ad3952 */

void FUN_43ad3952(int param_1,int param_2,int param_3)

{
  *(int *)(param_1 + 0x248) = param_3 * 0x10000 + param_2;
  return;
}


/* 43acee62 */

undefined4 FUN_43acee62(undefined4 *param_1)

{
  return *param_1;
}

