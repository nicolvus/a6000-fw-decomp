/* S41: read-only exports. */

/* 43ad8cb2 */

void FUN_43ad8cb2(undefined1 *param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4,
                 int param_5)

{
  int iVar1;
  int iVar2;
  
  param_1[2] = param_4;
  *param_1 = param_2;
  param_1[1] = param_3;
  param_1[3] = 0x81;
  *(int *)(param_1 + 4) = param_5;
  if (param_5 == 1) {
    iVar2 = 0x10;
  }
  else if (param_5 == 2) {
    iVar2 = 0x40;
  }
  else {
    iVar2 = 1;
  }
  *(int *)(param_1 + 8) = iVar2;
  *(int *)(param_1 + 0xc) = iVar2 * 2;
  *(undefined4 *)(param_1 + 0x24) = 1;
  param_1[0x20] = 1;
  param_1[0x15] = 0x81;
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  param_1[0x14] = 0;
  *(undefined4 *)(param_1 + 0x18) = 0;
  iVar2 = 0;
  do {
    iVar1 = iVar2 + 1;
    param_1[iVar2 + 0x28] = 0;
    iVar2 = iVar1;
  } while (iVar1 != 0x80);
  param_1[0xa8] = 0;
  param_1[0xa9] = 0;
  param_1[0xaa] = 0;
  param_1[0xab] = 0;
  param_1[0xac] = 0;
  param_1[0xad] = 0;
  return;
}


/* 436d8774 */

int * FUN_436d8774(int *param_1)

{
  int iVar1;
  int in_stack_0000002c;
  int in_stack_00000030;
  int in_stack_00000034;
  
  iVar1 = DAT_436d87d0 + 0x436d8782;
  FUN_436d99b8();
  *param_1 = *(int *)(iVar1 + DAT_436d87d4) + 8;
  param_1[0x12] = in_stack_00000034;
  param_1[0x10] = in_stack_0000002c;
  param_1[0x11] = in_stack_00000030;
  *(undefined1 *)(param_1 + 0x13) = 0;
  return param_1;
}


/* 43ad92d2 */

undefined4 FUN_43ad92d2(undefined4 param_1)

{
  FUN_436d86a8();
  FUN_439b4230(param_1);
  return param_1;
}

