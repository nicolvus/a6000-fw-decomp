/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436d2528" */

void FUN_436d2528(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0xa3310) =
       *(uint *)(param_1 + 0xa3310) & 0xe000ffff | (param_2 & 0x1fff) << 0x10;
  return;
}


/* query "436d2518" */

void FUN_436d2518(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0xa3310) = *(uint *)(param_1 + 0xa3310) & 0xffffe000 | param_2 & 0x1fff;
  return;
}

