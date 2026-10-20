/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436d2c70" */

int * FUN_436d2c70(int *param_1,undefined4 param_2,int param_3,int param_4)

{
  int iVar1;
  
  FUN_436d1914();
  iVar1 = DAT_44021c18;
  param_1[3] = param_3;
  param_1[4] = param_4;
  *param_1 = iVar1 + 8;
  *(undefined1 *)(param_1 + 5) = 1;
  return param_1;
}


/* query "436d21fc" */

int * FUN_436d21fc(int *param_1,undefined4 param_2,int param_3,int param_4)

{
  FUN_436d1914();
  *param_1 = DAT_44026c8c + 8;
  FUN_436d2598(param_1 + 5,param_2);
  *(char *)(param_1 + 2) = (char)param_2;
  param_1[3] = param_3;
  param_1[4] = param_4;
  param_1[9] = 0;
  return param_1;
}


/* query "436d3168" */

int * FUN_436d3168(int *param_1,int param_2)

{
  undefined4 uVar1;
  
  FUN_436d1914();
  *param_1 = DAT_4402430c + 8;
  if (param_2 == 0) {
    uVar1 = 0xfc000000;
  }
  else {
    if (param_2 != 1) {
      return param_1;
    }
    uVar1 = 0xfc001000;
  }
  FUN_43ad6f32(param_1 + 1,uVar1);
  return param_1;
}


/* query "436d3328" */

int * FUN_436d3328(int *param_1,int param_2)

{
  undefined4 uVar1;
  
  FUN_436d1914();
  *param_1 = DAT_44026090 + 8;
  if (param_2 == 0) {
    uVar1 = 0xfc000000;
  }
  else {
    if (param_2 != 1) {
      return param_1;
    }
    uVar1 = 0xfc001000;
  }
  FUN_43ad6f32(param_1 + 1,uVar1);
  return param_1;
}


/* query "436d27e8" */

int * FUN_436d27e8(int *param_1,int param_2)

{
  undefined4 uVar1;
  
  FUN_436d1914();
  *param_1 = DAT_4401efd8 + 8;
  param_1[3] = 0;
  if (param_2 == 0) {
    uVar1 = 0xfc000000;
  }
  else {
    if (param_2 != 1) {
      return param_1;
    }
    uVar1 = 0xfc001000;
  }
  FUN_43ad6f32(param_1 + 1,uVar1);
  return param_1;
}


/* query "436d06ac" */

int * FUN_436d06ac(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_436d11c8(param_1,0,param_3,param_4,param_4);
  *param_1 = DAT_44026acc + 8;
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  return param_1;
}


/* query "436d11c8" */

int * FUN_436d11c8(int *param_1)

{
  FUN_436d247c();
  *param_1 = DAT_44025cf4 + 8;
  param_1[4] = 0;
  return param_1;
}


/* query "4401f4b8" */

/* query "44026440" */

/* query "4401fddc" */

/* query "4402002c" */

/* query "44021878" */

/* query "44024394" */

/* query "44024df0" */

/* query "440263d0" */
