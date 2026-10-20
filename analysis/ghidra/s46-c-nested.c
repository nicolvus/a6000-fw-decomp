/* S41: read-only exports. */

/* 43b0394a */

void FUN_43b0394a(int param_1,int param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  puVar1 = *(undefined4 **)(*(int *)(param_1 + 0x50) + 8);
  uVar2 = puVar1[1];
  *(undefined4 *)(param_2 + 0x54) = *puVar1;
  *(undefined4 *)(param_2 + 0x58) = uVar2;
  return;
}

