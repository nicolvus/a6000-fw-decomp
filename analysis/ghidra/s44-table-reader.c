/* S41: read-only exports. */

/* 436d79b0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d79b0(void)

{
  return *(undefined4 *)(_DAT_436d79bc + 0x436d79b8 + _DAT_436d79c0);
}


/* 436d6450 */

undefined4 FUN_436d6450(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    iVar2 = DAT_436d6484 + 0x436d6462;
    FUN_436d6020(0xbc,0,1,DAT_436d6480 + 0x436d6460,iVar2,0);
    FUN_43902718(DAT_436d6488 + 0x436d646e,iVar2);
    uVar1 = 1;
  }
  else {
    uVar1 = (**(code **)(*(int *)*param_1 + 0x68))();
  }
  return uVar1;
}

