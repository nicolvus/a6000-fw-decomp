/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436cf0c8" */

undefined4 FUN_436cf0c8(uint param_1,undefined4 param_2)

{
  if (param_1 < 0xe) {
    if (*(int *)(&DAT_43e7ebf0 + param_1 * 4) == 0) {
      *(undefined4 *)(&DAT_43e7ebf0 + param_1 * 4) = param_2;
      switch(param_1) {
      case 1:
        FUN_43ad696c();
        break;
      case 2:
        FUN_43ad6980();
        break;
      case 3:
        FUN_43ad6994();
        break;
      case 4:
        FUN_43ad69a8();
        break;
      case 5:
        FUN_43ad69ba();
        break;
      case 6:
        FUN_43ad69cc();
        break;
      case 7:
        FUN_43ad69de();
        break;
      case 8:
        FUN_43ad69f0();
        break;
      case 9:
        FUN_43ad6a0c();
        break;
      case 10:
        FUN_43ad6a20();
        break;
      case 0xb:
        FUN_43ad6a34();
        break;
      case 0xc:
        FUN_43ad6a48();
        break;
      case 0xd:
        FUN_43ad6a5c();
        break;
      default:
        FUN_43ad695a();
      }
      return 0;
    }
    FUN_436cf01c(0x165,1,1,&DAT_43c916f8,param_1,param_2);
    FUN_43902718(s__Err__DFE_INT__already_set_int___43c91703,param_1);
  }
  else {
    FUN_436cf01c(0x165,1,1,&DAT_43c916d1,param_1,param_2);
    FUN_43902718(s__Err__DFE_INT__NOT_SUPPORT_43c916dc);
  }
  return 1;
}


/* query "43ad690c" */

void FUN_43ad690c(int param_1,int param_2)

{
  *(int *)(param_1 + 0xa0008) = param_2 << 0x11;
  return;
}


/* query "436d30d8" */

void FUN_436d30d8(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0xa1610) = *(uint *)(param_1 + 0xa1610) & 0xfffffffe | param_2 & 1;
  return;
}


/* query "436d3294" */

void FUN_436d3294(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0xa1710) = *(uint *)(param_1 + 0xa1710) & 0xfffffffe | param_2 & 1;
  return;
}


/* query "436d26d4" */

void s32_candidate_436d26d4(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0xa1210) = *(uint *)(param_1 + 0xa1210) & 0xfffffffe | param_2 & 1;
  return;
}


/* query "436d23d0" */

void FUN_436d23d0(int param_1,uint param_2)

{
  *(uint *)(param_1 + 0xa1310) = *(uint *)(param_1 + 0xa1310) & 0xfffffffe | param_2 & 1;
  return;
}


/* query "fc0a0010" */

/* query "fc0a0014" */

/* query "fc0a0018" */

/* query "43bc1d58" */
