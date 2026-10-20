/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43ad7ea6" */

void FUN_43ad7ea6(int param_1)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar1 = *(int *)(param_1 + 8) + 4;
  if (uVar1 < 0x140) {
    if (0x16 < uVar1) goto LAB_43ad7ec2;
    uVar2 = 1;
  }
  else {
    uVar2 = 0xffffffff;
  }
  *(undefined4 *)(param_1 + 0xc) = uVar2;
LAB_43ad7ec2:
  iVar3 = *(int *)(param_1 + 8) + *(int *)(param_1 + 0xc) * 4;
  *(int *)(param_1 + 8) = iVar3;
  uVar2 = FUN_43ad6e42(param_1 + 4);
  FUN_436d2528(uVar2,iVar3);
  uVar2 = FUN_43ad6e42(param_1 + 4);
  FUN_436d2518(uVar2,*(undefined4 *)(param_1 + 8));
  return;
}


/* query "436d2598" */

int * FUN_436d2598(int *param_1,int param_2)

{
  undefined4 uVar1;
  
  *param_1 = DAT_4402236c + 8;
  if (param_2 == 0) {
    uVar1 = 0xfc000000;
  }
  else {
    if (param_2 != 1) goto LAB_436d25c0;
    uVar1 = 0xfc001000;
  }
  FUN_43ad6f32(param_1 + 1,uVar1);
LAB_436d25c0:
  param_1[3] = 1;
  param_1[2] = 1;
  return param_1;
}


/* query "436d8774" */

int * FUN_436d8774(int *param_1)

{
  int in_stack_0000002c;
  int in_stack_00000030;
  int in_stack_00000034;
  
  FUN_436d99b8();
  *param_1 = DAT_44022e64 + 8;
  param_1[0x12] = in_stack_00000034;
  param_1[0x10] = in_stack_0000002c;
  param_1[0x11] = in_stack_00000030;
  *(undefined1 *)(param_1 + 0x13) = 0;
  return param_1;
}

