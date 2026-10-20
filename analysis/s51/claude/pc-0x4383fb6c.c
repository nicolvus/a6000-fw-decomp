
undefined4 FUN_4383fb6c(undefined4 param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_4383fb8c + 0x4383fb76;
  iVar1 = FUN_43b08d42();
  if ((iVar1 != 0) && ((param_2 & 1) != 0)) {
    return *(undefined4 *)(iVar2 + DAT_4383fb94);
  }
  return *(undefined4 *)(iVar2 + DAT_4383fb90);
}

