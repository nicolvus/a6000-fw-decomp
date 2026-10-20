/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43902c2c" */

undefined4
FUN_43902c2c(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,undefined4 param_5
            ,ushort param_6)

{
  uint *puVar1;
  byte *pbVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iStack_98;
  short sStack_94;
  short sStack_92;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  int iStack_84;
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined2 uStack_24;
  
  FUN_439c5a04(&iStack_98,0,0x78);
  pbVar2 = DAT_44024494;
  iStack_98 = (uint)param_6 << 0x10;
  sStack_94 = 0xc;
  uStack_80 = 0x55;
  uStack_24 = 0x70;
  uStack_7e = (undefined2)param_3;
  uVar5 = *DAT_44024494 & 1;
  uStack_90 = param_1;
  uStack_8c = param_2;
  uStack_88 = param_4;
  if ((*DAT_44024494 & 1) != 0) {
    uVar5 = thunk_FUN_436cd00c();
    puVar1 = DAT_44020960;
    uVar4 = *DAT_44022d98;
    if (uVar4 < 0x20) {
      *DAT_44022d98 = uVar4 + 1;
      *puVar1 = 1 << (uVar4 & 0xff) | *puVar1;
    }
  }
  FUN_43561524(&iStack_98);
  puVar1 = DAT_44020960;
  if ((*pbVar2 & 1) != 0) {
    if (*DAT_44022d98 != 0) {
      uVar4 = *DAT_44022d98 - 1;
      *DAT_44022d98 = uVar4;
      *puVar1 = *puVar1 & ~(1 << (uVar4 & 0xff));
    }
    iVar3 = thunk_FUN_436cd00c();
    if (*(uint *)(DAT_4401f718 + 4) < iVar3 - uVar5) {
      *(uint *)(DAT_4401f718 + 4) = iVar3 - uVar5;
      *(undefined4 *)(DAT_44020cec + 4) = param_1;
    }
  }
  if (sStack_92 != 6) {
    if (sStack_92 == 0) {
      if ((sStack_94 != -0x7ff4) || (uStack_90._2_2_ != 0x55)) {
        FUN_43902984(5,1,1,&DAT_43cce7c2,sStack_94,0x8001);
        FUN_43902718(s_AllocNewRdv__ERR_DMM_DIFFERENT_C_43cce7cd,sStack_94,0x8001);
        return 0xfffffffb;
      }
      if ((short)uStack_90 == -1) {
        FUN_43902984(5,1,1,&DAT_43cce80a);
        FUN_43902718(s_AllocNewRdv__ERR_DMM_HANDLE__43cce815);
        return 0xfffffffa;
      }
      if ((param_3 == 1) && (((short)uStack_8c == 0 || (iStack_84 == 0)))) {
        FUN_43902984(5,1,1,&DAT_43cce832);
        FUN_43902718(s_AllocNewRdv__ERR_DMM_OPEN__43cce83d);
        return 0xfffffff9;
      }
      FUN_439c5320(param_5,&sStack_94,0x70);
      return 0;
    }
    FUN_43902984(5,1,1,&DAT_43cce794,(int)sStack_92);
    FUN_43902718(s_AllocNewRdv__ERR_DMM_RET_CODE_____43cce79f,(int)sStack_92);
  }
  return 0xfffffffc;
}


/* query "43903118" */

undefined4
FUN_43903118(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            ushort param_5)

{
  byte *pbVar1;
  uint *puVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  int iStack_98;
  short sStack_94;
  short sStack_92;
  short sStack_8e;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined2 uStack_24;
  
  FUN_439c5a04(&iStack_98,0,0x78);
  pbVar1 = DAT_44024494;
  iStack_98 = (uint)param_5 << 0x10;
  sStack_94 = 0xd;
  uStack_80 = 0x55;
  uStack_24 = 0x70;
  sStack_92 = (short)param_1;
  uStack_7e = (undefined2)param_3;
  uVar6 = *DAT_44024494 & 1;
  uStack_8c = param_2;
  uStack_88 = param_4;
  if ((*DAT_44024494 & 1) != 0) {
    uVar6 = thunk_FUN_436cd00c();
    puVar2 = DAT_44024d8c;
    uVar5 = *DAT_44020ad8;
    if (uVar5 < 0x20) {
      *DAT_44020ad8 = uVar5 + 1;
      *puVar2 = 1 << (uVar5 & 0xff) | *puVar2;
    }
  }
  FUN_43561524(&iStack_98);
  puVar2 = DAT_44024d8c;
  if ((*pbVar1 & 1) != 0) {
    if (*DAT_44020ad8 != 0) {
      uVar5 = *DAT_44020ad8 - 1;
      *DAT_44020ad8 = uVar5;
      *puVar2 = *puVar2 & ~(1 << (uVar5 & 0xff));
    }
    iVar3 = thunk_FUN_436cd00c();
    if (*(uint *)(DAT_4401f718 + 0x10) < iVar3 - uVar6) {
      *(uint *)(DAT_4401f718 + 0x10) = iVar3 - uVar6;
      *(undefined4 *)(DAT_44020cec + 0x10) = param_1;
    }
  }
  if (sStack_92 == 0) {
    if ((sStack_94 != -0x7ff3) || (uVar4 = 0, sStack_8e != 0x55)) {
      FUN_43902984(5,1,1,&DAT_43cce9c2,sStack_94,0x8001,param_1,param_3);
      FUN_43902718(s_FreeRdv__ERR_DMM_DIFFERENT_COMP__43cce9cd,sStack_94,0x8001,param_1,param_3);
      uVar4 = 0xfffffffb;
    }
  }
  else {
    FUN_43902984(5,1,1,&DAT_43cce990,(int)sStack_92,param_1,param_3);
    FUN_43902718(s_FreeRdv__ERR_DMM_RET_CODE____d____43cce99b,(int)sStack_92,param_1,param_3);
    uVar4 = 0xfffffffc;
  }
  return uVar4;
}


/* query "43b0662c" */

bool FUN_43b0662c(int param_1)

{
  return *(char *)(param_1 + 2) != '\0';
}


/* query "43ae7542" */

void FUN_43ae7542(undefined2 *param_1)

{
  *(undefined1 *)(param_1 + 1) = 0;
  *param_1 = 0xffff;
  *(undefined4 *)(param_1 + 2) = 0;
  *(undefined1 *)((int)param_1 + 3) = 0;
  thunk_FUN_439c5a04(param_1 + 4,0,0x20);
  return;
}


/* query "43ae7534" */

undefined4 FUN_43ae7534(undefined4 param_1)

{
  FUN_43b2a296(param_1,5);
  return param_1;
}


/* query "43b03a5e" */

undefined4 FUN_43b03a5e(undefined4 param_1)

{
  FUN_439c5a04(param_1,0,0x104);
  return param_1;
}


/* query "43b03a70" */

int FUN_43b03a70(int param_1)

{
  return param_1 + 8;
}


/* query "43796910" */

void FUN_43796910(int param_1,undefined4 *param_2,undefined4 param_3)

{
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  int *piStack_1c;
  
  FUN_43ae9682(&uStack_34);
  uStack_34 = *param_2;
  uStack_30 = param_2[1];
  uStack_2c = param_2[2];
  uStack_28 = param_2[3];
  uStack_24 = param_2[4];
  uStack_20 = param_3;
  if (param_1 == 0) {
    piStack_1c = (int *)0x0;
  }
  else {
    piStack_1c = (int *)FUN_43ae75dc(param_1);
    (**(code **)(*piStack_1c + 8))();
  }
  FUN_43ae98d0(&DAT_43e9d7d4,&uStack_34);
  return;
}


/* query "440205c0" */
