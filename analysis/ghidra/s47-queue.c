/* S41: read-only exports. */

/* 43ada210 */

void FUN_43ada210(undefined4 *param_1,undefined4 param_2)

{
  *param_1 = param_2;
  return;
}


/* 436e7d3c */

void FUN_436e7d3c(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DAT_436e7d6c;
  FUN_43acabf4();
  *param_1 = *(undefined4 *)(iVar1 + 0x436e7d52 + DAT_436e7d70);
  param_1[1] = 0;
  param_1[2] = param_2;
  param_1[3] = param_3;
  param_1[4] = param_4;
  return;
}


/* 43af6860 */

void FUN_43af6860(int param_1)

{
  *(undefined4 *)(param_1 + 600) = 0;
  *(undefined4 *)(param_1 + 0x25c) = 0;
  *(undefined4 *)(param_1 + 0x260) = 0;
  return;
}


/* 43af6870 */

void FUN_43af6870(int param_1,ushort *param_2,int param_3,uint param_4)

{
  ushort *puVar1;
  int iVar2;
  
  iVar2 = 0;
  puVar1 = (ushort *)0x0;
  while (iVar2 < param_3) {
    iVar2 = iVar2 + 1;
    if (*param_2 == param_4) {
      puVar1 = param_2;
    }
    param_2 = param_2 + 6;
  }
  if (puVar1 == (ushort *)0x0) {
    *(undefined4 *)(param_1 + 0x128) = 0;
  }
  else {
    if (*(int *)(puVar1 + 2) != 0) {
      *(int *)(param_1 + 0x25c) = *(int *)(puVar1 + 2);
      *(undefined4 *)(param_1 + 0x260) = *(undefined4 *)(puVar1 + 4);
      return;
    }
    *(undefined4 *)(param_1 + 0x128) = 0;
  }
  FUN_4378a048(param_1 + 0x128);
  return;
}

