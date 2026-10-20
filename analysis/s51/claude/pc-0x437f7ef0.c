
void FUN_437f7ef0(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = DAT_437f7f8c + 0x437f7ef8;
  if ((((*(int *)(*(int *)(iVar2 + DAT_437f7f90) + 0x34) == 1) ||
       ((*(byte *)(*(int *)(iVar2 + DAT_437f7f94) + 0x78) & 0x40) != 0)) &&
      ((*(int *)(param_1 + 0x4b70) != 0 || (*(int *)(param_1 + 0x3c) != 0)))) &&
     ((((*(uint *)(param_1 + 0x1e0) < 0x1d &&
        ((1 << (*(uint *)(param_1 + 0x1e0) & 0xff) & DAT_437f7f88) != 0)) &&
       (*(char *)(param_1 + 0x73a) == '\0')) &&
      ((*(int *)(param_1 + 0x4b80) == 0 &&
       (*(char *)(*(int *)(iVar2 + DAT_437f7f94) + 0x86) == '\0')))))) {
    if (*(int *)(param_1 + 0x4d0) == 0x35) {
      uVar1 = 0x38;
    }
    else {
      if (*(int *)(param_1 + 0x4d0) != 0xb) {
        return;
      }
      uVar1 = 0x37;
    }
    *(undefined4 *)(param_1 + 0x4d0) = uVar1;
    uVar1 = FUN_43ae9332();
    *(undefined4 *)(param_1 + 0x6c4) = uVar1;
    *(uint *)(param_1 + 0x778) = (uint)(*(int *)(param_1 + 0x4d0) - 0x37U < 2);
    return;
  }
  return;
}

