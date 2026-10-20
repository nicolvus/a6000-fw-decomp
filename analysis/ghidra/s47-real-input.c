/* S41: read-only exports. */

/* 438d0c84 */

void FUN_438d0c84(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  if ((*(char *)(param_1 + 0x74f) != '\0') &&
     (iVar1 = FUN_437db858(6,*(undefined4 *)(param_1 + 0x4ad8),param_3,param_1 + 0x4a00,param_1,
                           param_2,param_3), iVar1 != 0)) {
    iVar1 = DAT_438d0cd0 + 0x438d0cac;
    FUN_438cffb8(5,1,1,DAT_438d0ccc + 0x438d0caa,iVar1,0x2b0);
    FUN_43902718(DAT_438d0cd4 + 0x438d0cc0,iVar1,0x2b0);
    return;
  }
  return;
}


/* 43ae769a */

void FUN_43ae769a(int param_1,undefined2 param_2)

{
  FUN_43901a8c(2,param_2,
               (uint)*(ushort *)(param_1 + 0x1d8) | *(int *)(param_1 + 0x4b68) << 0x18 |
               (uint)*(byte *)(param_1 + 0x4b97) << 0x10,
               (uint)*(ushort *)(param_1 + 0x4b64) | *(int *)(param_1 + 0x1e0) << 0x10);
  return;
}


/* 43ae75dc */

undefined4 FUN_43ae75dc(undefined4 *param_1)

{
  return *param_1;
}

