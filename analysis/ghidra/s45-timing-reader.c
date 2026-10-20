/* S41: read-only exports. */

/* 43ad91c6 */

void FUN_43ad91c6(int *param_1,undefined2 *param_2,undefined4 param_3)

{
  undefined2 uVar1;
  undefined4 uVar2;
  float fStack_c;
  
  fStack_c = 0.0;
  (**(code **)(*param_1 + 0x6c))(param_1,&fStack_c,param_3,*(code **)(*param_1 + 0x6c),param_1);
  if (fStack_c <= 0.0) {
    uVar1 = 0;
  }
  else {
    uVar2 = VectorFloatToUnsigned((double)fStack_c + 0.5,3);
    uVar1 = (undefined2)uVar2;
  }
  *param_2 = uVar1;
  return;
}

