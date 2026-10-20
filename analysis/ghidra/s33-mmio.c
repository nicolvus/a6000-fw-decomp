/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436c041c" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c041c(undefined4 param_1,int param_2)

{
  undefined1 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = &DAT_f3950400;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a50434 = param_1;
      }
      return;
    }
    puVar1 = &DAT_f3850400;
  }
  *(undefined4 *)(puVar1 + 0x34) = param_1;
  return;
}


/* query "436c06fc" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c06fc(undefined4 param_1,int param_2)

{
  undefined1 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = &DAT_f3950400;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a504a4 = param_1;
      }
      return;
    }
    puVar1 = &DAT_f3850400;
  }
  *(undefined4 *)(puVar1 + 0xa4) = param_1;
  return;
}


/* query "436c019c" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c019c(undefined4 param_1,int param_2)

{
  undefined4 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = (undefined4 *)&DAT_f3950500;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a50500 = param_1;
      }
      return;
    }
    puVar1 = (undefined4 *)&DAT_f3850500;
  }
  *puVar1 = param_1;
  return;
}


/* query "436bd404" */

undefined1 FUN_436bd404(int param_1)

{
  return (&DAT_43f922ef)[param_1];
}


/* query "43560934" */

uint FUN_43560934(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  iVar1 = 0;
  do {
    uVar2 = *(uint *)(iVar1 + DAT_44023cd0);
    if (uVar2 == 0xffffffff) {
      return 0;
    }
    uVar3 = *(uint *)(iVar1 + DAT_44023cd0 + 4);
    uVar4 = uVar2;
    if (param_2 == 0) {
      uVar4 = uVar3;
      uVar3 = uVar2;
    }
    iVar1 = iVar1 + 8;
  } while (uVar3 != (param_1 & 0xf0000000));
  return uVar4 | param_1 & 0xfffffff;
}


/* query "43560978" */

undefined4 FUN_43560978(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = 0;
  do {
    uVar2 = *(uint *)(iVar1 + DAT_44023cd0);
    if (uVar2 == 0xffffffff) {
      return 0;
    }
    if (param_2 != 0) {
      uVar2 = *(uint *)(iVar1 + DAT_44023cd0 + 4);
    }
    iVar1 = iVar1 + 8;
  } while (uVar2 != (param_1 & 0xf0000000));
  return 1;
}

