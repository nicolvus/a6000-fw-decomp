
void FUN_4384031c(int param_1,int param_2,code *param_3)

{
  int iVar1;
  undefined4 uVar2;
  char *pcVar3;
  int iVar4;
  
  iVar4 = DAT_438403d0 + 0x4384032e;
  pcVar3 = *(char **)(iVar4 + DAT_438403d4);
  if ((*pcVar3 == '\0') && (pcVar3[0x15] == '\0')) {
    (*param_3)(*(undefined4 *)(param_2 + 0x1b8));
    return;
  }
  iVar1 = FUN_4383fbc4(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  if (*(char *)(param_1 + 0x2be) == '\x01') {
    if (*(char *)(*(int *)(iVar4 + DAT_438403d8) + 0xec) == '\x02') {
      uVar2 = 0x15;
    }
    else {
      uVar2 = 0x14;
    }
    FUN_4383f8c0(uVar2);
    FUN_4383f8c0(1);
  }
  if (((*(int *)(DAT_438403dc + 0x43840378) == 1) ||
      ((*(int *)(DAT_438403dc + 0x43840378) == 3 && (*(char *)(DAT_438403e0 + 0x43840386) == '\x01')
       ))) && (*(char *)(param_1 + 0x10) != '\0')) {
    FUN_43aef28a(*(undefined2 *)(iVar1 + 0x15e),*(undefined2 *)(iVar1 + 0x162),1);
  }
  FUN_43aef28a(*(undefined2 *)(iVar1 + 0x15e),*(undefined2 *)(iVar1 + 0x162),1);
  FUN_43857f40(0x388,*(undefined4 *)(param_2 + 0x1b8));
  FUN_43859944(0x13,param_1,param_2 + 0x1b8);
  FUN_4383f548(*(undefined2 *)(param_2 + 0x1b8),param_3);
  return;
}

