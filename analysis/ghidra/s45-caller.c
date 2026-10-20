/* S41: read-only exports. */

/* 437b4df0 */

void FUN_437b4df0(undefined4 param_1,undefined4 param_2)

{
  short *psVar1;
  
  psVar1 = *(short **)(DAT_437b4e20 + 0x437b4df8 + DAT_437b4e24);
  *psVar1 = *psVar1 + 1;
  FUN_4383b520(0x13,0);
  FUN_437b5b14(param_1,param_2);
  FUN_4383b520(0x13,1);
  return;
}

