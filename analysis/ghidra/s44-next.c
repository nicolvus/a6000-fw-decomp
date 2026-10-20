/* S41: read-only exports. */

/* 436d79b0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d79b0(void)

{
  return *(undefined4 *)(_DAT_436d79bc + 0x436d79b8 + _DAT_436d79c0);
}


/* 436d6570 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void candidate_436d6570(int param_1,int param_2)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = _DAT_436d65ac + 0x436d6578;
  iVar3 = 0;
  while( true ) {
    iVar4 = *(int *)(iVar2 + _DAT_436d65b0);
    puVar1 = *(undefined1 **)(iVar3 + iVar4);
    if (puVar1 == (undefined1 *)0x0) break;
    iVar4 = param_2 + iVar4 + iVar3;
    iVar3 = iVar3 + 0x14;
    *puVar1 = *(undefined1 *)(iVar4 + 4);
  }
  iVar3 = 0;
  if (*(char *)(param_1 + 0x266) != '\0') {
    while( true ) {
      iVar4 = *(int *)(iVar2 + _DAT_436d65b4);
      puVar1 = *(undefined1 **)(iVar3 + iVar4);
      if (puVar1 == (undefined1 *)0x0) break;
      iVar4 = param_2 + iVar4 + iVar3;
      iVar3 = iVar3 + 0x14;
      *puVar1 = *(undefined1 *)(iVar4 + 4);
    }
  }
  return;
}


/* 435614d0 */

void FUN_435614d0(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_435614e4 + 0x435614da + DAT_435614e8) + 0x14) + 0x2c8))();
  return;
}

