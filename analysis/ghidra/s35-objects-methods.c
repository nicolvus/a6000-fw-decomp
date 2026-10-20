/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436d30e8" */

void s32_candidate_436d30e8(int param_1)

{
  int iVar1;
  
  FUN_43ad6e42(param_1 + 4);
  iVar1 = FUN_436d30c8();
  if (iVar1 != 0) {
    func_0x436d301c(0x165,1,1,0x43c9296c);
    FUN_43902718(0x43c92977);
  }
  iVar1 = FUN_43ad6e42(param_1 + 4);
  *(uint *)(iVar1 + 0xa1610) = *(uint *)(iVar1 + 0xa1610) & 0xfffffffe | 1;
  return;
}


/* query "436d32a4" */

void s32_candidate_436d32a4(int param_1)

{
  int iVar1;
  
  FUN_43ad6e42(param_1 + 4);
  iVar1 = FUN_436d3284();
  if (iVar1 != 0) {
    func_0x436d31c0(0x165,1,1,0x43c929d5);
    FUN_43902718(0x43c929e0);
  }
  iVar1 = FUN_43ad6e42(param_1 + 4);
  *(uint *)(iVar1 + 0xa1710) = *(uint *)(iVar1 + 0xa1710) & 0xfffffffe | 1;
  return;
}


/* query "436d26e4" */

void s32_candidate_436d26e4(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  if (*(int *)(param_1 + 0xc) == 0) {
    FUN_43ad6e42(param_1 + 4);
    iVar1 = FUN_436d26c4();
    if (iVar1 != 0) {
      func_0x436d25f0(0x165,1,1,0x43c92752,*(undefined1 *)(param_1 + 8),param_2,param_3);
      FUN_43902718(0x43c9275d,*(undefined1 *)(param_1 + 8));
    }
    iVar1 = FUN_43ad6e42(param_1 + 4);
    *(uint *)(iVar1 + 0xa1210) = *(uint *)(iVar1 + 0xa1210) & 0xfffffffe | 1;
    return;
  }
  return;
}


/* query "436d23e0" */

void s32_candidate_436d23e0(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  FUN_43ad6e42(param_1 + 4);
  iVar1 = FUN_436d23c0();
  if (iVar1 != 0) {
    func_0x436d2314(0x165,1,1,0x43c926ab,*(undefined1 *)(param_1 + 8),param_2,param_3);
    FUN_43902718(0x43c926b6,*(undefined1 *)(param_1 + 8));
  }
  iVar1 = FUN_43ad6e42(param_1 + 4);
  *(uint *)(iVar1 + 0xa1310) = *(uint *)(iVar1 + 0xa1310) & 0xfffffffe | 1;
  return;
}


/* query "43ad6f32" */

void FUN_43ad6f32(undefined4 *param_1,undefined4 param_2)

{
  *param_1 = param_2;
  return;
}


/* query "436d247c" */

int * FUN_436d247c(int *param_1,int param_2)

{
  undefined4 uVar1;
  
  FUN_436d1914();
  *param_1 = DAT_44020298 + 8;
  if (param_2 == 0) {
    uVar1 = 0xfc000000;
  }
  else {
    if (param_2 != 1) goto LAB_436d24aa;
    uVar1 = 0xfc001000;
  }
  FUN_43ad6f32(param_1 + 1,uVar1);
LAB_436d24aa:
  param_1[3] = 0x3a;
  return param_1;
}


/* query "43fcbf78" */

/* query "43fcbe68" */

/* query "43fcbfb8" */

/* query "43fcbfe8" */

/* query "43fcbee0" */

/* query "43fcbd70" */

/* query "43fcbd38" */
