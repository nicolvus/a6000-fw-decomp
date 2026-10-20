/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43cb3b0c" */

/* query "43c7e8a3" */

/* query "43c7f0ea" */

/* query "437965ec" */

void FUN_437965ec(int param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_43ae916c();
  if (iVar1 != 0) {
    FUN_4379bb68(0,(*(byte *)(*(int *)(param_3 + 8) + 0x268) & 3) >> 1);
    FUN_4379bb68(1,(*(byte *)(*(int *)(param_3 + 8) + 0x268) & 7) >> 2);
    FUN_4379bb68(2,(*(byte *)(*(int *)(param_3 + 8) + 0x268) & 7) >> 2);
    FUN_4379bb68(3,0);
  }
  if (param_1 != 0) {
    FUN_43b04914(&DAT_43e9d810);
  }
  if (*(int *)(*(int *)(param_3 + 8) + 0x2c) == 0) {
    FUN_43796284(param_3 + 8,param_1);
  }
  if (param_2 != 0) {
    if (*(int *)(*(int *)(param_3 + 8) + 0x44) != 0x11) {
      FUN_43795d44(*(int *)(param_3 + 8) + 0xb8);
    }
    uVar2 = FUN_4380d708(param_2 + 0x18,param_2 + 0x2c,0);
    iVar1 = FUN_4381bd4c(param_2,uVar2,
                         (uint)*(byte *)(*(int *)(param_3 + 8) + 0x30) * 0x100 +
                         (uint)*(byte *)(*(int *)(param_3 + 0x20) + 1));
    if (iVar1 != 0) {
      FUN_43b04730();
    }
  }
  FUN_4381bf38(&DAT_43e9d810);
  return;
}


/* query "436ccdbc" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436ccdbc(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  if (param_1 == 0) {
    FUN_43b4b33e(0x25);
  }
  thunk_FUN_436ccffc();
  FUN_436ccfd4(param_1);
  FUN_436ccfe0(param_2);
  iVar1 = 0;
  do {
    iVar2 = iVar1;
    FUN_43ad6002(&DAT_43e7e934 + iVar2 * 0x1c,iVar2);
    iVar1 = iVar2 + 1;
  } while (iVar2 + 1 != 10);
  FUN_436cd2c4();
  FUN_4356112c(0x54);
  iVar1 = iVar2 + -9;
  do {
    iVar2 = iVar1 + 1;
    FUN_43ad6076(&DAT_43e7ea4c + iVar1 * 0x20,iVar1);
    iVar1 = iVar2;
  } while (iVar2 != 8);
  FUN_4356112c(0x53);
  _DAT_f3c300ec = 1;
  return;
}


/* query "43ae9300" */

void FUN_43ae9300(undefined4 param_1,char *param_2,undefined4 param_3)

{
  if (*param_2 != '\0') {
    FUN_43b045e8();
  }
  FUN_43ad6d74(param_1,param_3);
  FUN_43b0453c();
  return;
}


/* query "43ad8be4" */

uint FUN_43ad8be4(int param_1,int param_2)

{
  if (param_2 == 0) {
    return (*(uint *)(param_1 + 0x14) & 0x1f) >> 4;
  }
  if (param_2 == 1) {
    return (*(uint *)(param_1 + 0x14) & 0x3f) >> 5;
  }
  return 0;
}


/* query "43ad87c4" */

uint FUN_43ad87c4(int param_1,int param_2)

{
  if (param_2 == 0) {
    return *(uint *)(param_1 + 0x14) & 1;
  }
  if (param_2 == 1) {
    return (*(uint *)(param_1 + 0x14) & 3) >> 1;
  }
  return 0;
}


/* query "436d41e0" */

int FUN_436d41e0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 extraout_r2;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  while ((iVar2 = *(int *)(iVar3 + DAT_440249c8), iVar2 == 0 ||
         (iVar1 = FUN_43ad8b9c(iVar2,param_1,param_3,DAT_440249c8,param_4), param_3 = extraout_r2,
         iVar1 == 0))) {
    iVar3 = iVar3 + 4;
    if (iVar3 == 0x38) {
      return 0;
    }
  }
  return iVar2;
}


/* query "436d02cc" */

bool FUN_436d02cc(void)

{
  if (*DAT_44024944 == '\0') {
    return DAT_44024944[0x41] != '\0';
  }
  return true;
}


/* query "436d039c" */

undefined4 FUN_436d039c(void)

{
  uint *puVar1;
  undefined4 uVar2;
  
  uVar2 = DAT_440239d8;
  puVar1 = DAT_440211c4;
  if ((*DAT_440211c4 & 1) == 0) {
    FUN_436d4d2c(DAT_440239d8);
    *puVar1 = 1;
    FUN_439b4244(uVar2,DAT_44024c88,DAT_440254cc);
  }
  return uVar2;
}


/* query "43ad79ae" */

void FUN_43ad79ae(int param_1)

{
  FUN_43ad7ea6(param_1 + 0x14);
  (**(code **)(**(int **)(param_1 + 0x10) + 8))();
  (**(code **)(**(int **)(param_1 + 0xc) + 8))();
  return;
}


/* query "43ad828c" */

void FUN_43ad828c(int param_1)

{
  if (*(char *)(param_1 + 0x14) != '\0') {
    (**(code **)(**(int **)(param_1 + 0x10) + 8))();
    (**(code **)(**(int **)(param_1 + 0xc) + 8))();
  }
  return;
}


/* query "44021914" */

/* query "4402603c" */

/* query "44023400" */

/* query "44024d10" */
