/* S41: read-only exports. */

/* 436d6320 */

undefined4 FUN_436d6320(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    iVar2 = DAT_436d6354 + 0x436d6332;
    FUN_436d6020(0xbc,0,1,DAT_436d6350 + 0x436d6330,iVar2,0);
    FUN_43902718(DAT_436d6358 + 0x436d633e,iVar2);
    uVar1 = 1;
  }
  else {
    uVar1 = (**(code **)(*(int *)*param_1 + 0x28))();
  }
  return uVar1;
}

