/* S41: read-only exports. */

/* 437ff064 */

undefined8 FUN_437ff064(undefined4 param_1,undefined4 param_2,undefined1 param_3,undefined1 param_4)

{
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_13 = (undefined1)((uint)param_2 >> 8);
  uStack_14 = 5;
  uStack_c = CONCAT13(param_4,CONCAT12(param_3,CONCAT11((char)param_2,(char)param_1)));
  uStack_12 = 0x40ab;
  uStack_10 = 0;
  FUN_437fefb8(DAT_437ff094,&uStack_14,0xc);
  return CONCAT26(uStack_12,CONCAT15(uStack_13,CONCAT14(uStack_14,param_1)));
}


/* 43561260 */

void FUN_43561260(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_43561274 + 0x43561268 + DAT_43561278) + 0x14) + 0x1e0))();
  return;
}


/* 435612ec */

void FUN_435612ec(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_43561300 + 0x435612f6 + DAT_43561304) + 0x14) + 500))();
  return;
}


/* 43561340 */

void FUN_43561340(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_43561354 + 0x4356134a + DAT_43561358) + 0x14) + 0x204))();
  return;
}

