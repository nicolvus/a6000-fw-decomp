/* S41: read-only exports. */

/* 436d5d9c */

bool FUN_436d5d9c(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = *param_1;
  if (((*(int *)(iVar4 + 0x10) == iVar4 + 0x28) || (iVar1 = FUN_43ad8e4e(), iVar1 != param_2)) ||
     (*(char *)(iVar4 + 3) != *(char *)(iVar4 + 0x15))) {
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  *(undefined4 *)(iVar4 + 0x24) = uVar3;
  if (*(int *)(iVar4 + 0x24) == 0) {
    uVar2 = *(int *)(iVar4 + 0x10) + 2;
  }
  else {
    if (*(int *)(iVar4 + 0x24) != 1) {
      FUN_436d5ac8(0xbc,0,1,DAT_436d5dfc + 0x436d5dea,param_4);
      FUN_43902718(DAT_436d5e00 + 0x436d5df2);
      return false;
    }
    uVar2 = *(int *)(iVar4 + 0x10) + 7;
  }
  return uVar2 <= iVar4 + 0xa8U;
}


/* 43ad8fa2 */

undefined4 FUN_43ad8fa2(int *param_1,int param_2,undefined4 param_3)

{
  if (*(int *)(*param_1 + 0x24) != 0) {
    if (*(int *)(*param_1 + 0x24) != 1) {
      return 0;
    }
    FUN_43ad8e54();
    FUN_43ad8eb0(param_1,param_2);
  }
  FUN_43ad8f20(param_1,param_3);
  *(undefined1 *)(*param_1 + 0x15) = *(undefined1 *)(*param_1 + 3);
  FUN_43ad8e88(param_1,param_2 + 1U & 0xffff);
  return 1;
}


/* 43ad8c80 */

undefined4 FUN_43ad8c80(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_436d6000();
  if (iVar1 != 0) {
    return 0;
  }
  FUN_436d5fb0(param_1);
  if (param_1 == 0) {
    FUN_4356112c(0x26);
    return 1;
  }
  return 1;
}


/* 436d594c */

undefined4 FUN_436d594c(int param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  
  if (param_2 == 1) {
    if (*(int *)(DAT_436d59c8 + 0x436d5978) == 0) {
      *(int *)(DAT_436d59c8 + 0x436d5978) = param_1;
      return 1;
    }
    iVar2 = DAT_436d59cc + 0x436d598c;
LAB_436d59a4:
    FUN_436d5848(0xbc,0,3,iVar2);
    return 0;
  }
  if (param_2 == 2) {
    piVar1 = (int *)(DAT_436d59d0 + 0x436d5992);
    if (*piVar1 != 0) {
      iVar2 = DAT_436d59d4 + 0x436d59a6;
      goto LAB_436d59a4;
    }
  }
  else {
    if (param_2 != 0) {
      FUN_436d5848(0xbc,0,3,DAT_436d59d8 + 0x436d59b8);
      return 0;
    }
    piVar1 = (int *)(DAT_436d59c0 + 0x436d5962);
    if (*piVar1 != 0) {
      FUN_436d5848(0xbc,0,3,DAT_436d59c4 + 0x436d596e);
      return 0;
    }
  }
  *piVar1 = param_1;
  return 1;
}

