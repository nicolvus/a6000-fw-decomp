/* S41: read-only exports. */

/* 43ad9438 */

uint FUN_43ad9438(undefined4 param_1,int param_2,int *param_3,uint param_4)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (param_4 <= uVar1) {
      return 0xff;
    }
    if (param_2 == *param_3) break;
    uVar1 = uVar1 + 1;
    param_3 = param_3 + 1;
  }
  return uVar1 & 0xff;
}


/* 43ad95ca */

undefined4 FUN_43ad95ca(int param_1)

{
  return *(undefined4 *)(param_1 + 8);
}


/* 43ad95c6 */

undefined4 FUN_43ad95c6(int param_1)

{
  return *(undefined4 *)(param_1 + 4);
}

