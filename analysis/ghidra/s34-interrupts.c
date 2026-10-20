/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436cfafa" */

void FUN_436cfae0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = FUN_43ad68e0();
  iVar2 = 0;
  FUN_43560e1c(0x16);
  do {
    if ((&DAT_43e7ec2c)[iVar2 * 2] == 0) {
      if (iVar2 < 4) {
        (&DAT_43e7ec28)[iVar2 * 2] = uVar1;
        (&DAT_43e7ec2c)[iVar2 * 2] = param_2;
        DAT_43e7ec4c = DAT_43e7ec4c & ~uVar1;
        FUN_436cf844(uVar1);
        FUN_43560e38(0x16);
        if ((*(byte *)(DAT_44024944 + 0xf) & 1) == 0) {
          return;
        }
        FUN_436cf6d4(0x165,1,1,&DAT_43c9208a,param_1,iVar2,uVar1,param_4);
        FUN_43902718(s_setComplexCallBack_cond__x_No__d_43c92095,param_1,iVar2,uVar1);
        return;
      }
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 4);
  FUN_436cf6d4(0x165,1,1,&DAT_43c92046,DAT_43e7ec2c,DAT_43e7ec34,DAT_43e7ec3c,DAT_43e7ec44);
  FUN_43902718(s_DfeCoreErr_setComplexCallBack_Ca_43c92051,DAT_43e7ec2c,DAT_43e7ec34,DAT_43e7ec3c,
               DAT_43e7ec44);
  return;
}


/* query "436cfb46" */

void FUN_436cfae0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = FUN_43ad68e0();
  iVar2 = 0;
  FUN_43560e1c(0x16);
  do {
    if ((&DAT_43e7ec2c)[iVar2 * 2] == 0) {
      if (iVar2 < 4) {
        (&DAT_43e7ec28)[iVar2 * 2] = uVar1;
        (&DAT_43e7ec2c)[iVar2 * 2] = param_2;
        DAT_43e7ec4c = DAT_43e7ec4c & ~uVar1;
        FUN_436cf844(uVar1);
        FUN_43560e38(0x16);
        if ((*(byte *)(DAT_44024944 + 0xf) & 1) == 0) {
          return;
        }
        FUN_436cf6d4(0x165,1,1,&DAT_43c9208a,param_1,iVar2,uVar1,param_4);
        FUN_43902718(s_setComplexCallBack_cond__x_No__d_43c92095,param_1,iVar2,uVar1);
        return;
      }
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 4);
  FUN_436cf6d4(0x165,1,1,&DAT_43c92046,DAT_43e7ec2c,DAT_43e7ec34,DAT_43e7ec3c,DAT_43e7ec44);
  FUN_43902718(s_DfeCoreErr_setComplexCallBack_Ca_43c92051,DAT_43e7ec2c,DAT_43e7ec34,DAT_43e7ec3c,
               DAT_43e7ec44);
  return;
}


/* query "436cf7f4" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf844(uint param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = FUN_436cf7e8();
  if ((uVar1 & param_1) != 0) {
    FUN_436cf6d4(0x165,0,3,s__DFECore____setCamIntEnable0__al_43c91e9f,uVar1,param_1,param_3);
  }
  FUN_436cf7dc(param_1);
  _DAT_fc0a0018 = uVar1 | param_1;
  return;
}


/* query "436bf3a8" */

void FUN_436bf3a8(int param_1)

{
  char cVar1;
  
  param_1 = param_1 * 0xc;
  cVar1 = (&DAT_43e78d4c)[param_1];
  (&DAT_43e78d4c)[param_1] = cVar1 + 1U;
  if ((byte)(&DAT_43e78d44)[param_1] <= (byte)(cVar1 + 1U)) {
    (&DAT_43e78d4c)[param_1] = 0;
  }
  return;
}


/* query "436bf470" */

void FUN_436bf470(int param_1)

{
  char cVar1;
  int iVar2;
  
  iVar2 = param_1 * 0x40;
  cVar1 = (&DAT_43e78c0c)[iVar2];
  (&DAT_43e78c0c)[iVar2] = cVar1 + 1U;
  if ((byte)(&DAT_43f92393)[param_1] <= (byte)(cVar1 + 1U)) {
    (&DAT_43e78c0c)[iVar2] = 0;
  }
  return;
}


/* query "436bf664" */

void FUN_436bf664(int param_1)

{
  (&DAT_43e78d70)[param_1 * 0x54] =
       (&DAT_43e78d70)[param_1 * 0x54] & 0xfc | (&DAT_43e78d70)[param_1 * 0x54] + 1 & 3;
  return;
}


/* query "436bf7d0" */

void FUN_436bf7d0(int param_1)

{
  (&DAT_43e78c9c)[param_1 * 0x54] =
       (&DAT_43e78c9c)[param_1 * 0x54] & 0xfc | (&DAT_43e78c9c)[param_1 * 0x54] + 1 & 3;
  return;
}


/* query "43acb8ea" */

void FUN_43acb8ea(undefined4 param_1)

{
  char acStack_1c [20];
  
  FUN_436bf818(1,acStack_1c,param_1);
  if (acStack_1c[0] != '\0') {
    acStack_1c[0] = '\0';
    FUN_436bf7e8(1,acStack_1c,param_1);
  }
  return;
}


/* query "43acb2e8" */

void FUN_43acb2e8(undefined4 param_1)

{
  FUN_436c019c(0,param_1);
  FUN_436c019c(1,param_1);
  return;
}


/* query "436ccd9c" */

undefined4 FUN_436ccd9c(uint param_1)

{
  if (param_1 < 10) {
    FUN_43ad6006(&DAT_43e7e934 + param_1 * 0x1c);
    return 0;
  }
  return 1;
}


/* query "43ad6006" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_43ad6006(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = param_4[1];
  uVar2 = param_4[2];
  uVar3 = param_4[3];
  param_1[2] = *param_4;
  param_1[3] = uVar1;
  param_1[4] = uVar2;
  param_1[5] = uVar3;
  uVar1 = param_4[4];
  param_1[1] = param_2;
  param_1[6] = uVar1;
  switch(*param_1) {
  case 0:
    _DAT_f3c30114 = param_2;
    _DAT_f3c30110 = param_3;
    return;
  case 1:
    _DAT_f3c3011c = param_2;
    _DAT_f3c30118 = param_3;
    return;
  case 2:
    _DAT_f3c30124 = param_2;
    _DAT_f3c30120 = param_3;
    return;
  case 3:
    _DAT_f3c3012c = param_2;
    _DAT_f3c30128 = param_3;
    return;
  case 4:
    _DAT_f3c30134 = param_2;
    _DAT_f3c30130 = param_3;
    return;
  case 5:
    _DAT_f3c3013c = param_2;
    _DAT_f3c30138 = param_3;
    return;
  case 6:
    _DAT_f3c30144 = param_2;
    _DAT_f3c30140 = param_3;
    return;
  case 7:
    _DAT_f3c3014c = param_2;
    _DAT_f3c30148 = param_3;
    return;
  case 8:
    _DAT_f3c30154 = param_2;
    _DAT_f3c30150 = param_3;
    return;
  case 9:
    _DAT_f3c30158 = param_3;
    _DAT_f3c3015c = param_2;
  }
  return;
}


/* query "43ae8d3e" */

void s32_candidate_43ae8d3e(void)

{
  FUN_43560da8(0x1a,0x80);
  return;
}


/* query "43791a10" */

void s32_candidate_43791a10(int param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_38 [20];
  undefined1 auStack_24 [24];
  
  iVar3 = *DAT_43e9920c;
  uVar1 = (uint)DAT_43e9d027;
  if (DAT_43e9d028 == '\0') {
    iVar2 = DAT_43e9920c[10];
    FUN_43ae863c(auStack_24,0x43791a11);
    FUN_436ccd9c(4,param_1 + iVar2,1,auStack_24);
  }
  FUN_43ada220(auStack_38,&LAB_43790b68_1);
  FUN_439018b0(&DAT_43e9b528,auStack_38,uVar1 + iVar3 * 0x100,0);
  return;
}


/* query "437927c4" */

void FUN_437927c4(int param_1)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uStack_a0;
  undefined4 uStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined1 uStack_88;
  undefined1 auStack_84 [20];
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [24];
  
  DAT_43ff36bc = DAT_43ff36bc + 1;
  if ((DAT_43ff36bc & 1) != 0) goto LAB_43792826;
  if (DAT_43e9d027 == 1) {
    uVar2 = 2;
LAB_43792802:
    FUN_43901638(uVar2);
  }
  else {
    if (DAT_43e9d027 == 0) {
      uVar2 = 1;
      goto LAB_43792802;
    }
    if (DAT_43e9d027 == 2) {
      uVar2 = 3;
      goto LAB_43792802;
    }
  }
  DAT_43e9d027 = DAT_43e9d027 + 1;
  if ((uint)DAT_43e9d026 <= DAT_43e9d027 + 1) {
    DAT_43e9d028 = '\x01';
  }
LAB_43792826:
  iVar5 = *DAT_43e9920c;
  uVar4 = (uint)DAT_43e9d027;
  if (DAT_43ff36bc == DAT_43e9b544) {
    if (DAT_43ff36bc < 7) {
      DAT_43e9b544 = DAT_43ff36bc + 1;
      iVar3 = DAT_43e9920c[0xb];
      FUN_43ae863c(auStack_48,0x437927c5);
      FUN_436ccd9c(1,iVar3 + param_1,1,auStack_48);
    }
    if (DAT_43e99460 != (code *)0x0) {
      uStack_a0 = DAT_43ff36bc;
      iVar3 = FUN_4378f9b4();
      uStack_9c = *(undefined4 *)(*(int *)(iVar3 + 8) + 0x1e8);
      iVar3 = FUN_4378f9b4();
      uStack_98 = *(undefined4 *)(*(int *)(iVar3 + 8) + 0x3c);
      iVar3 = FUN_4378f9b4();
      uStack_8c = *(undefined4 *)(*(int *)(iVar3 + 4) + 0x18);
      iVar3 = FUN_4378f9b4();
      uStack_90 = *(undefined4 *)(*(int *)(iVar3 + 0xc) + 0x5c);
      uStack_88 = FUN_43ae1252();
      (*DAT_43e99460)(&uStack_a0);
    }
    if ((DAT_43ff36bc & 1) == 0) {
      iVar5 = uVar4 + iVar5 * 0x100;
      FUN_43ada220(auStack_5c,0x4378fef5);
      FUN_439018b0(&DAT_43e9b528,auStack_5c,iVar5,0);
      if (DAT_43e9bb18 == 0) {
        if (DAT_43e9baec != 1) {
          return;
        }
        if ((DAT_43e9d027 & 1) == 0) {
          return;
        }
        FUN_43ada220(auStack_84,&LAB_43790b68_1);
        puVar1 = &stack0x00000008;
      }
      else {
        if (DAT_43e9d028 == '\0') {
          return;
        }
        FUN_43ada220(auStack_70,&LAB_43790b68_1);
        puVar1 = &stack0x0000001c;
      }
      FUN_439018b0(&DAT_43e9b528,puVar1 + -0x8c,iVar5,0);
    }
  }
  else {
    FUN_43ae9130(auStack_34,DAT_44026384);
    FUN_439018b0(&DAT_43e9b528,auStack_34,0,0);
    FUN_4378eb78(3,9,1,&DAT_43ca3849,DAT_43e9b544,DAT_43ff36bc);
    FUN_43902718(s_int_HS_timing_error__d_8V_>_d_8V_43ca385d,DAT_43e9b544,DAT_43ff36bc);
  }
  return;
}


/* query "4378fef4" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void candidate_4378fef4(uint param_1)

{
  byte bVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  char *pcVar5;
  int iVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  undefined1 auStack_50 [20];
  undefined4 uStack_3c;
  uint uStack_38;
  int iStack_34;
  undefined1 auStack_30 [4];
  uint uStack_2c;
  undefined1 auStack_28 [4];
  undefined1 *apuStack_24 [2];
  
  iVar4 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    switch(DAT_43e9d027) {
    case 0:
      pcVar5 = s_HS0_Main_S_43ca2f8b;
      break;
    case 1:
      pcVar5 = s_HS1_Main_S_43ca2f96;
      break;
    case 2:
      pcVar5 = s_HS2_Main_S_43ca2fa1;
      break;
    case 3:
      pcVar5 = s_HS3_Main_S_43ca2fac;
      break;
    default:
      goto switchD_4378ff22_default;
    }
    FUN_43561540(pcVar5);
  }
switchD_4378ff22_default:
  uVar9 = param_1 >> 8;
  param_1 = param_1 & 0xff;
  if ((uVar9 != *DAT_43e9920c) || (param_1 != DAT_43e9d027)) {
    iVar6 = thunk_FUN_436cd00c();
    uVar8 = iVar6 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca2fb7,uVar9,param_1,*DAT_43e9920c,DAT_43e9d027,uVar8);
    FUN_43902718(s_HS_Main__start_delayed__dV___d___43ca2fcb,uVar9,param_1,*DAT_43e9920c,
                 DAT_43e9d027,uVar8);
    if (param_1 < 4) {
      uVar7 = *(undefined4 *)(&DAT_43bc42c8 + param_1 * 4);
    }
    else {
      uVar7 = 7;
    }
    FUN_4378f988(3,uVar7,uVar8);
    if ((*(byte *)(iVar4 + 0x12) & 4) != 0) {
      FUN_43561540(s_HS_Main_S_OF_43ca2ffa);
    }
    if ((*(byte *)(iVar4 + 0x1b) & 0x20) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  if (DAT_43e9d028 != '\0') {
    FUN_43acad44();
  }
  FUN_43ae1292(4);
  iVar6 = FUN_43ae8d4e();
  if (iVar6 == 0) {
    FUN_43901778();
    if (DAT_4401e926 != '\0') {
      DAT_43f9a4b8 = 1;
    }
    DAT_4401e926 = 0;
  }
  else {
    DAT_4401e926 = 1;
  }
  FUN_4378f7a0(0xf7c);
  if (DAT_43e9d028 != '\0') {
    FUN_43560e00(0x11,auStack_30);
    if ((uStack_2c & 2) == 0) {
      DAT_43e9d39c = FUN_437c1440();
      FUN_43ae8e44(&DAT_43e9b548,&DAT_43e99208);
    }
    sVar2 = DAT_43f79b84;
    if (DAT_43f9a426 == '\0') {
      DAT_43e9bd4c = uStack_2c & 2 | DAT_43e9bd4c & 0xfffffffd;
      if (DAT_43f79b84 != 0) {
        if ((uStack_2c & 2) == 0) {
          DAT_43f79b4a = 0;
        }
        else {
          DAT_43f79b68 = DAT_43f79b68 + 1;
          DAT_43f79b4a = DAT_43f79b4a + 1;
        }
      }
    }
    if ((DAT_43f79b84 != 0) || (*(char *)(iVar4 + 0xe) != '\0')) {
      if (DAT_43f79b64 != DAT_43f79b84) {
        iVar6 = 0;
        do {
          *(undefined2 *)((int)&DAT_43f79b2e + iVar6) = 0;
          *(undefined2 *)((int)&DAT_43f79b48 + iVar6) = 0;
          *(undefined2 *)((int)&DAT_43f79b66 + iVar6) = 0;
          iVar6 = iVar6 + 2;
        } while (iVar6 != 0x1a);
        DAT_43f79b64 = sVar2;
      }
      if ((sVar2 != 0) && (DAT_43f79b82 == sVar2)) {
        if ((*(byte *)(iVar4 + 0xe) & 1) != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca3007,sVar2,DAT_43f79b74,DAT_43f79b6a,DAT_43f79b68,DAT_43f79b6c
                       ,DAT_43f79b72,DAT_43f79b70,DAT_43f79b78);
          FUN_43902718(s_Detect__overflow__dV__FC__2d__EC_43ca301b,DAT_43f79b84,DAT_43f79b74,
                       DAT_43f79b6a,DAT_43f79b68,DAT_43f79b6c,DAT_43f79b72,DAT_43f79b70,DAT_43f79b78
                      );
        }
        FUN_43900368(0,(uint)DAT_43f79b6a * 0x10000 + (uint)DAT_43f79b68);
        FUN_43900368(1,(uint)DAT_43f79b6c * 0x10000 + (uint)DAT_43f79b72);
        FUN_43900368(2,(uint)DAT_43f79b70 * 0x10000 + (uint)DAT_43f79b78);
        FUN_43900368(3,(uint)DAT_43f79b74 << 0x10);
      }
      iVar6 = 0;
      do {
        if (*(ushort *)((int)&DAT_43f79b2e + iVar6) < *(ushort *)((int)&DAT_43f79b48 + iVar6)) {
          *(ushort *)((int)&DAT_43f79b2e + iVar6) = *(ushort *)((int)&DAT_43f79b48 + iVar6);
        }
        iVar6 = iVar6 + 2;
      } while (iVar6 != 0x1a);
      if ((DAT_43f79b84 != 0) && (DAT_43f79b82 == DAT_43f79b84)) {
        if ((*(byte *)(iVar4 + 0xe) & 2) != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca3069,DAT_43f79b82,DAT_43f79b3c,DAT_43f79b32,DAT_43f79b30,
                       DAT_43f79b34,DAT_43f79b3a,DAT_43f79b38,DAT_43f79b40);
          FUN_43902718(s_Detect__overflow__dV__seq_cnt_FC_43ca307d,DAT_43f79b84,DAT_43f79b3c,
                       DAT_43f79b32,DAT_43f79b30,DAT_43f79b34,DAT_43f79b3a,DAT_43f79b38,DAT_43f79b40
                      );
        }
        FUN_43900368(4,(uint)DAT_43f79b32 * 0x10000 + (uint)DAT_43f79b30);
        FUN_43900368(5,(uint)DAT_43f79b34 * 0x10000 + (uint)DAT_43f79b3a);
        FUN_43900368(6,(uint)DAT_43f79b38 * 0x10000 + (uint)DAT_43f79b40);
        FUN_43900368(7,(uint)DAT_43f79b3c << 0x10);
      }
      if ((((*(byte *)(iVar4 + 0xe) & 4) != 0) && (DAT_43e9bd4c != 0)) &&
         ((DAT_43e9bd4c & 0x6e) != 0)) {
        FUN_4378eb78(3,9,1,&DAT_43ca30d3,DAT_43e9bd4c);
        FUN_43902718(s_Detect__overflow__04x_43ca30e7,DAT_43e9bd4c);
      }
    }
    FUN_439c5320(&DAT_43e9948c,&DAT_43e99320,0x44);
  }
  DAT_43e9d029 = FUN_43ae8ccc(DAT_44025f5c);
  sVar2 = DAT_43e9d02a;
  DAT_43e9d02c = (ushort)DAT_43e9bb1c * 0x100;
  DAT_43e9d02a = DAT_43e9d02c;
  if (*(int *)(DAT_43e99210 + 0x2c) == 0) {
    bVar1 = DAT_43e9d027;
    if (DAT_43e9baec == 1) {
      bVar1 = DAT_43e9d027 >> 1;
    }
    DAT_43e9d02a = DAT_43e9d02c + (ushort)bVar1;
  }
  if ((*(char *)(DAT_43e99210 + 0x1ed) == '\0') || (*(char *)(DAT_43e99228 + 2) == '\0')) {
    if (*(int *)(DAT_43e99210 + 0x2c) == 0) {
      if (DAT_43e9baec == 1) {
        DAT_43e9d02c = DAT_43e9d02c + (short)(DAT_43e9d027 + 1 >> 1);
      }
      else {
        DAT_43e9d02c = DAT_43e9d02c + DAT_43e9d027 + 1;
      }
    }
  }
  else {
    DAT_43e9d02c = (DAT_43e9bb1c + 1) * 0x100;
  }
  iVar6 = FUN_437955ec();
  sVar3 = DAT_43e9d02a;
  if (iVar6 == 0) {
    DAT_43e9d02e = (ushort)DAT_43e9bb24 << 8;
    DAT_43e9d030 = DAT_43e9d02e;
  }
  else {
    DAT_43e9d02e = (ushort)DAT_43e9bb24 * 0x100;
    if (DAT_43e9bb20 == 0) {
      bVar1 = DAT_43e9d027;
      if (DAT_43e9baec == 1) {
        bVar1 = DAT_43e9d027 >> 1;
      }
      DAT_43e9d02e = DAT_43e9d02e + (ushort)bVar1;
    }
    if (((DAT_43e9bce8 == '\0') || (bVar1 = DAT_43e9bce0, DAT_43e9d028 == '\0')) &&
       (bVar1 = DAT_43e9bb24, DAT_43e9bb20 == 0)) {
      if (DAT_43e9baec == 1) {
        DAT_43e9d030 = (ushort)DAT_43e9bb24 * 0x100 + (short)(DAT_43e9d027 + 1 >> 1);
      }
      else {
        DAT_43e9d030 = DAT_43e9d027 + 1 + (ushort)DAT_43e9bb24 * 0x100;
      }
    }
    else {
      DAT_43e9d030 = (ushort)bVar1 << 8;
    }
  }
  if ((sVar2 != DAT_43e9d02a) && (*(char *)(iVar4 + 0x70) == '\0')) {
    FUN_439c5a04(&uStack_3c,0,0xc);
    uStack_38 = *DAT_43e9920c;
    uStack_3c._0_3_ = CONCAT12(1,sVar3);
    iStack_34 = DAT_43e9bb18;
    FUN_43b71696(uStack_3c,uStack_38,DAT_43e9bb18);
  }
  FUN_437999e4(1,0xd);
  FUN_437957a0();
  FUN_4378f7a0(0x105e);
  if (*(char *)(DAT_43e99228 + 2) != '\0') {
    if (((_DAT_43e9bd54 & 0x10000) != 0) &&
       (iVar6 = FUN_43560de0(0x1a,2,0,auStack_28,1), iVar6 != 0)) {
      FUN_43560e00(0x1a,auStack_30);
      FUN_4378eb78(3,9,1,&DAT_43ca30fd,*DAT_43e9920c,DAT_43e9d027,uStack_2c);
      FUN_43902718(s_HS_Main__TC__Last1st__ADC_flg_ti_43ca3111,*DAT_43e9920c,DAT_43e9d027,uStack_2c)
      ;
      FUN_43560da8(0x1a,3);
    }
    if ((*(byte *)(iVar4 + 0x12) & 8) != 0) {
      FUN_43561540(s_TC__HS_M_L1_S_43ca3145);
    }
    thunk_FUN_43ae74ca(&DAT_43e99208,&DAT_43e9d288);
  }
  if ((*(byte *)(iVar4 + 0x12) & 8) != 0) {
    FUN_43561540(s_YC__HS_M_S_43ca3153);
  }
  FUN_437d99a4(&DAT_43e99208,&DAT_43e9d384);
  FUN_4378f7a0(0x1073);
  if ((*(byte *)(iVar4 + 0x12) & 8) != 0) {
    FUN_43561540(s_EC__HS_M_S_43ca315e);
  }
  FUN_437b4e88(&DAT_43e99208,&DAT_43e9d034);
  FUN_4378f7a0(0x1078);
  iVar6 = thunk_FUN_43adaaf6();
  if (((iVar6 != 0) && ((_DAT_43e9bd54 & 0x40) == 0)) &&
     (iVar6 = FUN_43560de0(0x1a,1,0,auStack_28,1), iVar6 != 0)) {
    FUN_43560e00(0x1a,auStack_30);
    FUN_4378eb78(3,9,1,&DAT_43ca3169,*DAT_43e9920c,DAT_43e9d027,uStack_2c);
    FUN_43902718(s_HS_Main__BONOBO_flg_timeout__dV___43ca317d,*DAT_43e9920c,DAT_43e9d027,uStack_2c);
    FUN_43560da8(0x1a,3);
  }
  if ((*(byte *)(iVar4 + 0x12) & 8) != 0) {
    FUN_43561540(s_LC__HS_M_S_43ca31a7);
  }
  apuStack_24[0] = &LAB_43790ac0_1;
  FUN_437c1fcc(&DAT_43e99208,&DAT_43e9d114,apuStack_24);
  if (*(char *)(DAT_43e99228 + 2) != '\0') {
    if ((*(byte *)(iVar4 + 0x12) & 8) != 0) {
      FUN_43561540(s_Lens__HS_M_L_S_43ca31b2);
    }
    FUN_43721840();
    if (((_DAT_43e9bd54 & 0x10040) == 0) &&
       (iVar6 = FUN_43560de0(0x1a,2,0,auStack_28,1), iVar6 != 0)) {
      FUN_43560e00(0x1a,auStack_30);
      FUN_4378eb78(3,9,1,&DAT_43ca31c1,*DAT_43e9920c,DAT_43e9d027,uStack_2c);
      FUN_43902718(s_HS_Main__TC__Last2nd__ADC_flg_ti_43ca31d5,*DAT_43e9920c,DAT_43e9d027,uStack_2c)
      ;
      FUN_43560da8(0x1a,3);
    }
    if ((*(byte *)(iVar4 + 0x12) & 8) != 0) {
      FUN_43561540(s_TC__HS_M_L2_S_43ca3209);
    }
    thunk_FUN_4377f210(&DAT_43e99208,&DAT_43e9d288);
  }
  if (*(char *)(DAT_43e99228 + 2) != '\0') {
    FUN_437fc56c(0,*(undefined2 *)(DAT_43e99210 + 0x26c));
    FUN_437fc56c(2,*DAT_43e99214);
    FUN_437fc56c(1,*(undefined2 *)(DAT_43e99240 + 0x14));
    FUN_437fc56c(3,*DAT_43e99244);
    FUN_437fc56c(4,*DAT_43e99234);
    FUN_437fc56c(6,*(undefined2 *)(DAT_43e9921c + 0x2c));
    FUN_437fc56c(8,*DAT_43e99224);
    FUN_437fc56c(10,DAT_43e9d022);
    FUN_437fc56c(9,*DAT_43e99254);
    uVar7 = FUN_4377e500();
    FUN_437fc56c(0xb,uVar7);
    FUN_437fc56c(5,DAT_43e9b552);
    FUN_437fc56c(0xc,DAT_43e9d024);
    FUN_43b007ae();
    FUN_437fc580();
    FUN_43ae9130(auStack_50,&LAB_4378fa20_1);
    FUN_439018b0(&DAT_43e992e0,auStack_50,0,0);
  }
  if (DAT_43e9d027 == 1) {
    uVar7 = FUN_437876dc();
    iVar6 = FUN_43b00cba();
    if (iVar6 != 0) {
      FUN_43b00ed8(uVar7,&DAT_43e99208);
    }
  }
  FUN_43ae129a(4);
  if ((uVar9 != *DAT_43e9920c) || (param_1 != DAT_43e9d027)) {
    iVar6 = thunk_FUN_436cd00c();
    uVar8 = iVar6 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca3217,uVar9,param_1,*DAT_43e9920c,DAT_43e9d027,uVar8);
    FUN_43902718(s_HS_Main__overflow__dV___d__>__dV_43ca322b,uVar9,param_1,*DAT_43e9920c,
                 DAT_43e9d027,uVar8);
    if (param_1 < 4) {
      uVar7 = *(undefined4 *)(&DAT_43bc42d8 + param_1 * 4);
    }
    else {
      uVar7 = 7;
    }
    FUN_4378f988(4,uVar7,uVar8);
    if ((*(byte *)(iVar4 + 0x12) & 4) != 0) {
      FUN_43561540(s_HS_Main_E_OF_43ca3255);
    }
    if ((*(byte *)(iVar4 + 0x1b) & 0x20) != 0) {
      FUN_4378ec60();
    }
  }
  if ((DAT_43e9d028 == '\0') || (DAT_43e9920c[5] != 0)) {
    FUN_4378d3b4();
  }
  if (DAT_43e9d027 == 1) {
    if (DAT_43e9bb18 != 0) {
      uVar7 = 2;
      goto LAB_437908ac;
    }
  }
  else if (DAT_43e9d027 == 0) {
    if ((DAT_43e9bb18 != 0) || (DAT_43e9baec == 1)) {
      uVar7 = 1;
      goto LAB_437908ac;
    }
  }
  else if ((DAT_43e9d027 == 2) && ((DAT_43e9bb18 != 0 || (DAT_43e9baec == 1)))) {
    uVar7 = 3;
LAB_437908ac:
    FUN_43901480(uVar7);
  }
  if ((*(byte *)(iVar4 + 0x12) & 1) != 0) {
    switch(DAT_43e9d027) {
    case 0:
      pcVar5 = s_HS0_Main_E_43ca3262;
      break;
    case 1:
      pcVar5 = s_HS1_Main_E_43ca326d;
      break;
    case 2:
      pcVar5 = s_HS2_Main_E_43ca3278;
      break;
    case 3:
      pcVar5 = s_HS3_Main_E_43ca3283;
      break;
    default:
      goto switchD_437908ca_default;
    }
    FUN_43561540(pcVar5);
  }
switchD_437908ca_default:
  return;
}

