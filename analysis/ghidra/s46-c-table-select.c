/* S41: read-only exports. */

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

