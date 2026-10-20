/* S41: read-only exports. */

/* 43935348 */

void FUN_43935348(undefined4 param_1,undefined4 param_2,int param_3)

{
  undefined4 uVar1;
  
  uVar1 = FUN_43b4c8da();
  FUN_439c5320(uVar1,DAT_43935364 + 0x4393535c + param_3 * 0x80,param_2);
  return;
}


/* 43ae7564 */

void FUN_43ae7564(undefined4 param_1,int param_2)

{
  if (*(char *)(param_2 + 0x14) != '\0') {
    FUN_4377fe14(0);
  }
  if (*(char *)(param_2 + 0x16) != '\0') {
    FUN_4377fe14(1,param_2);
  }
  if ((*(uint *)(param_2 + 0x14) & 0xff00ff00) != 0) {
    FUN_4377fea4(param_2);
    return;
  }
  return;
}


/* 43ae8eae */

void FUN_43ae8eae(undefined4 param_1,undefined4 param_2)

{
  FUN_43ae8d56();
  FUN_43ae8e2c(param_1,param_2);
  FUN_43ae8e44(param_1,param_2);
  FUN_43ae8e5c(param_1,param_2);
  FUN_43ae8e74(param_1,param_2);
  FUN_43ae8e84(param_1,param_2);
  FUN_43ae8e9a(param_1,param_2);
  FUN_43ae8ea4(param_1,param_2);
  return;
}

