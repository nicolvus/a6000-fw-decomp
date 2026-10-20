/* S41: read-only exports. */

/* 43ad2bd6 */

void FUN_43ad2bd6(int param_1,int param_2,int param_3)

{
  *(int *)(param_1 + 0x220) = param_3 * 0x10000 + param_2;
  return;
}

