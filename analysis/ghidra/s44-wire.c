/* S41: read-only exports. */

/* 436d75f8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void candidate_436d75f8(int param_1,int param_2,undefined4 *param_3)

{
  undefined2 *puVar1;
  int iVar2;
  
  *(char *)(param_1 + 0x348) = (char)param_2;
  iVar2 = param_1 + 0x298;
  if (param_2 == 2) {
    FUN_436d5b74(iVar2,param_1 + 0x348);
    while( true ) {
      puVar1 = (undefined2 *)*param_3;
      if (puVar1 == (undefined2 *)0x0) break;
      FUN_436d5e04(iVar2,*puVar1,*(undefined1 *)(puVar1 + 1));
      param_3 = param_3 + 1;
    }
    FUN_43ad8dca(iVar2);
  }
  else {
    candidate_436d58f4(*(undefined4 *)(_DAT_436d7674 + 0x436d763a + *(int *)(param_1 + 0x26c) * 4));
    func_0x43ad8d1c(iVar2);
    while( true ) {
      puVar1 = (undefined2 *)*param_3;
      if (puVar1 == (undefined2 *)0x0) break;
      candidate_43ad9004(iVar2,*puVar1,*(undefined1 *)(puVar1 + 1));
      param_3 = param_3 + 1;
    }
    FUN_43ad8d38(iVar2);
    candidate_43ad8de4(iVar2,param_1 + 0x348);
  }
  iVar2 = FUN_436d9f70(param_1 + 0xfc,2);
  *(bool *)(param_1 + 0x345) = iVar2 != 0;
  return;
}


/* 436d5bcc */

undefined8 FUN_436d5bcc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_c;
  
  iVar2 = 2;
  uStack_c = param_4;
  iVar1 = FUN_43560de0(0x18,*(uint *)(param_1 + 0xc) | *(uint *)(param_1 + 8),0,&uStack_c,2,param_2,
                       param_3);
  if (iVar1 != 0) {
    iVar2 = iVar1;
    FUN_436d5ac8(0xbc,0,1,DAT_436d5c04 + 0x436d5bf4);
    FUN_43902718(DAT_436d5c08 + 0x436d5bfe,iVar1);
  }
  return CONCAT44(param_2,iVar2);
}

