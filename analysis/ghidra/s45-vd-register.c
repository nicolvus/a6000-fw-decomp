/* S41: read-only exports. */

/* 43ad2bd6 */

void FUN_43ad2bd6(int param_1,int param_2,int param_3)

{
  *(int *)(param_1 + 0x220) = param_3 * 0x10000 + param_2;
  return;
}


/* 436c2270 */

undefined4 FUN_436c2270(void)

{
  return *(undefined4 *)(DAT_436c2278 + 0x436c2276);
}


/* 436c28d0 */

undefined4 FUN_436c28d0(void)

{
  return **(undefined4 **)(DAT_436c28dc + 0x436c28d8 + DAT_436c28e0);
}

