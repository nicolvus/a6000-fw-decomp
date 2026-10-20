/* S41: read-only exports. */

/* 43859ac4 */

undefined * FUN_43859ac4(void)

{
  return &UNK_43859aca + DAT_43859acc;
}


/* 4355faf0 */

uint FUN_4355faf0(uint param_1,uint param_2)

{
  uint uVar1;
  undefined4 uVar2;
  
  if (param_2 - 1 == 0) {
    return param_1;
  }
  if (param_2 == 0) {
    uVar2 = 0;
    if (param_1 != 0) {
      uVar2 = 0xffffffff;
    }
    FUN_43a3aa58(uVar2);
    FUN_43a3aa58();
    uVar1 = FUN_43a3aa58();
    return uVar1;
  }
  if (param_1 <= param_2) {
    return (uint)(param_1 == param_2);
  }
  if ((param_2 & param_2 - 1) == 0) {
    return param_1 >> (0x1fU - LZCOUNT(param_2) & 0xff);
  }
                    /* WARNING: Could not recover jumptable at 0x4355fb20. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  uVar1 = (*(code *)(&UNK_4355fb28 + (0x1f - (LZCOUNT(param_2) - LZCOUNT(param_1))) * 0x10))
                    (param_1,param_2,0);
  return uVar1;
}


/* 4380e0cc */

void FUN_4380e0cc(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 *puVar4;
  
  iVar1 = DAT_4380e134;
  if (*(char *)(*(int *)(DAT_4380e120 + 0x4380e0d4 + DAT_4380e124) + 0x4c) != '\0') {
    iVar3 = *(int *)(param_1 + 8);
    if (((((*(byte *)(iVar3 + 0x268) & 1) == 0) ||
         (*(char *)(*(int *)(param_1 + 0x50) + 0x2c) != '\0')) || (*(int *)(iVar3 + 0x1e4) != 0)) ||
       ((*(uint *)(iVar3 + 0x2c) < 2 || (*(char *)(DAT_4380e128 + 0x4380e102) != '\0')))) {
      uVar2 = 0;
      puVar4 = (undefined4 *)(DAT_4380e130 + 0x4380e114);
    }
    else {
      uVar2 = 1;
      puVar4 = (undefined4 *)(DAT_4380e12c + 0x4380e10c);
    }
    *puVar4 = uVar2;
    *(undefined4 *)(DAT_437fe508 + 0x437fe506) = *(undefined4 *)(iVar1 + 0x4380e11a);
    return;
  }
  return;
}


/* 4383fbc4 */

undefined4 FUN_4383fbc4(undefined4 param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_4383fbe4 + 0x4383fbce;
  iVar1 = FUN_43b08d42();
  if ((iVar1 != 0) && ((param_2 & 1) != 0)) {
    return *(undefined4 *)(iVar2 + DAT_4383fbec);
  }
  return *(undefined4 *)(iVar2 + DAT_4383fbe8);
}

