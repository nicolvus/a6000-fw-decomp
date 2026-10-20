/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "4390366c" */

int FUN_4390366c(undefined2 *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined2 *puVar5;
  undefined1 auStack_88 [4];
  undefined2 uStack_84;
  byte bStack_80;
  undefined4 auStack_78 [25];
  
  iVar2 = FUN_43ae9674(param_2);
  if (iVar2 == 0) {
    iVar2 = -6;
    FUN_43902984(5,1,1,&DAT_43cceb98);
    FUN_43902718(s_MemoryHandle__AllocShare__DMM_UN_43cceba3);
  }
  else {
    iVar2 = FUN_43902df8(*(undefined4 *)(param_2 + 2),*param_2,param_3,auStack_88,param_4);
    if (iVar2 == 0) {
      *param_1 = uStack_84;
      *(undefined4 *)(param_1 + 2) = *(undefined4 *)(param_2 + 2);
      *(byte *)(param_1 + 1) = bStack_80;
      if (4 < bStack_80) {
        FUN_43902984(5,1,1,&DAT_43ccebcf,bStack_80,4);
        FUN_43902718(s_MemoryHandle__AllocShare__ERR_EX_43ccebda,*(undefined1 *)(param_1 + 1),4);
        *(undefined1 *)(param_1 + 1) = 4;
      }
      bVar1 = *(byte *)(param_1 + 1);
      puVar4 = auStack_78;
      puVar5 = param_1;
      for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
        *(undefined4 *)(puVar5 + 4) = *puVar4;
        *(undefined4 *)(puVar5 + 6) = puVar4[1];
        puVar5 = puVar5 + 4;
        puVar4 = puVar4 + 2;
      }
      *(undefined1 *)((int)param_1 + 3) = 1;
    }
  }
  return iVar2;
}


/* query "43902df8" */

undefined4
FUN_43902df8(undefined4 param_1,short param_2,int param_3,undefined4 param_4,ushort param_5)

{
  uint *puVar1;
  byte *pbVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  int iStack_98;
  short sStack_94;
  short sStack_92;
  undefined4 uStack_90;
  short sStack_8c;
  int iStack_84;
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined2 uStack_24;
  
  FUN_439c5a04(&iStack_98,0,0x78);
  pbVar2 = DAT_44024494;
  iStack_98 = (uint)param_5 << 0x10;
  sStack_94 = 2;
  uStack_80 = 0x55;
  uStack_24 = 0x70;
  uStack_7e = (undefined2)param_3;
  uVar6 = *DAT_44024494 & 1;
  sStack_92 = param_2;
  uStack_90 = param_1;
  if ((*DAT_44024494 & 1) != 0) {
    uVar6 = thunk_FUN_436cd00c();
    puVar1 = DAT_44021a44;
    uVar5 = *DAT_44021c44;
    if (uVar5 < 0x20) {
      *DAT_44021c44 = uVar5 + 1;
      *puVar1 = 1 << (uVar5 & 0xff) | *puVar1;
    }
  }
  FUN_43561524(&iStack_98);
  puVar1 = DAT_44021a44;
  if ((*pbVar2 & 1) != 0) {
    if (*DAT_44021c44 != 0) {
      uVar5 = *DAT_44021c44 - 1;
      *DAT_44021c44 = uVar5;
      *puVar1 = *puVar1 & ~(1 << (uVar5 & 0xff));
    }
    iVar3 = thunk_FUN_436cd00c();
    if (*(uint *)(DAT_4401f718 + 8) < iVar3 - uVar6) {
      *(uint *)(DAT_4401f718 + 8) = iVar3 - uVar6;
      *(undefined4 *)(DAT_44020cec + 8) = param_1;
    }
  }
  if (sStack_92 == 0) {
    if ((sStack_94 == -0x7ffe) && (uStack_90._2_2_ == 0x55)) {
      if ((short)uStack_90 == -1) {
        FUN_43902984(5,1,1,&DAT_43cce8cc);
        FUN_43902718(s_AllocShare__ERR_DMM_HANDLE__43cce8d7);
        uVar4 = 0xfffffffa;
      }
      else if ((param_3 == 1) && ((sStack_8c == 0 || (iStack_84 == 0)))) {
        FUN_43902984(5,1,1,&DAT_43cce8f3);
        FUN_43902718(s_AllocShare__ERR_DMM_OPEN__43cce8fe);
        uVar4 = 0xfffffff9;
      }
      else {
        FUN_439c5320(param_4,&sStack_94,0x70);
        uVar4 = 0;
      }
    }
    else {
      FUN_43902984(5,1,1,&DAT_43cce885,sStack_94,0x8001);
      FUN_43902718(s_AllocShare__ERR_DMM_DIFFERENT_CO_43cce890,sStack_94,0x8001);
      uVar4 = 0xfffffffb;
    }
  }
  else {
    FUN_43902984(5,1,1,&DAT_43cce858,(int)sStack_92);
    FUN_43902718(s_AllocShare__ERR_DMM_RET_CODE_____43cce863,(int)sStack_92);
    uVar4 = 0xfffffffc;
  }
  return uVar4;
}


/* query "43790b68" */

void s32_candidate_43790b68(uint param_1)

{
  short sVar1;
  int iVar2;
  char *pcVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  int iStack_b0;
  undefined4 uStack_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined4 uStack_a0;
  undefined2 uStack_9c;
  undefined2 uStack_9a;
  undefined1 auStack_98 [20];
  undefined1 auStack_84 [20];
  undefined4 uStack_70;
  int iStack_6c;
  undefined2 uStack_68;
  undefined2 uStack_66;
  undefined2 uStack_64;
  undefined2 uStack_62;
  undefined4 uStack_60;
  undefined1 uStack_5c;
  undefined1 uStack_5b;
  uint uStack_58;
  undefined4 uStack_54;
  undefined1 auStack_50 [4];
  undefined4 uStack_4c;
  undefined2 uStack_48;
  undefined2 uStack_46;
  undefined2 uStack_44;
  undefined1 uStack_42;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 auStack_30 [4];
  undefined2 auStack_2c [4];
  
  iVar2 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    switch(DAT_43e9d027) {
    case 0:
      pcVar3 = s_HS0_Seq_S_43ca328e;
      break;
    case 1:
      pcVar3 = s_HS1_Seq_S_43ca3298;
      break;
    case 2:
      pcVar3 = s_HS2_Seq_S_43ca32a2;
      break;
    case 3:
      pcVar3 = s_HS3_Seq_S_43ca32ac;
      break;
    default:
      goto switchD_43790b96_default;
    }
    FUN_43561540(pcVar3);
  }
switchD_43790b96_default:
  uVar7 = param_1 >> 8;
  param_1 = param_1 & 0xff;
  if ((uVar7 != *DAT_43e9920c) || (param_1 != DAT_43e9d027)) {
    iVar4 = thunk_FUN_436cd00c();
    uVar8 = iVar4 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca32b6,uVar7,param_1,*DAT_43e9920c,DAT_43e9d027,uVar8);
    FUN_43902718(s_HS_Sequence__start_delayed__dV___43ca32ca,uVar7,param_1,*DAT_43e9920c,
                 DAT_43e9d027,uVar8);
    if (param_1 < 4) {
      uVar6 = *(undefined4 *)(&DAT_43bc42b8 + param_1 * 4);
    }
    else {
      uVar6 = 0xc;
    }
    FUN_4378f988(3,uVar6,uVar8);
    if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
      FUN_43561540(s_HS_Seq_S_OF_43ca32fd);
    }
    if ((*(byte *)(iVar2 + 0x1b) & 0x40) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  FUN_43ae1292(4);
  iVar4 = FUN_43ae8d4e();
  if (iVar4 == 0) {
    FUN_43901778();
    if (DAT_4401e926 != '\0') {
      DAT_43f9a4b8 = '\x01';
    }
    DAT_4401e926 = 0;
  }
  else {
    DAT_4401e926 = 1;
  }
  if ((*(char *)(DAT_43e99210 + 0x1ed) != '\0') && (*(char *)(DAT_43e99228 + 2) != '\0')) {
    FUN_437949f8();
  }
  FUN_4378f7a0(0x1175);
  iVar4 = FUN_43b039fc(&DAT_43e9948c,&DAT_43e994d0);
  if (iVar4 == 0) {
    uVar6 = 0;
  }
  else if ((DAT_43e994a4 == 1) && (DAT_43f9a4b8 == '\0')) {
    if (DAT_43e9bb18 == 0) {
LAB_43790d22:
      uVar6 = 0x43e99490;
    }
    else if (DAT_43e9bcd9 == '\0') {
      uVar6 = 0;
    }
    else {
      if (DAT_43e9d028 != '\0') goto LAB_43790d22;
      uVar6 = 0;
    }
  }
  else {
    uVar6 = 0;
  }
  uVar5 = FUN_43ae8cd0(DAT_44025f5c);
  FUN_437965ec(uVar5,uVar6,&DAT_43e99208);
  FUN_4378f7a0(0x1184);
  iVar4 = FUN_437999e4(1,0xd);
  if ((iVar4 != 0) && (DAT_43e9bb18 == 0)) {
    uStack_60 = FUN_43ae9332(DAT_43e9bb30);
    uStack_5c = 0;
    uStack_5b = 0;
    iVar4 = FUN_43795610(DAT_43e9bcd9);
    if (((iVar4 != 0) && (DAT_43f9a4b8 == '\0')) &&
       ((DAT_43e9bb20 == 0 || ((DAT_43e9bce8 != '\0' && (DAT_43e9d028 != '\0')))))) {
      uStack_5b = 1;
    }
    uStack_58 = (uint)(*(int *)(DAT_43e99208 + 0x548) != 0);
    uStack_54 = *(undefined4 *)(DAT_43e99208 + 0x54c);
    iVar4 = FUN_437956c8(&DAT_43e9bba4,&uStack_60);
    if (iVar4 != 0) {
      FUN_4378eb78(3,9,1,&DAT_43ca3309,iVar4);
      FUN_43902718(s__DFE_SetParam_Error_0x_x_43ca331d,iVar4);
    }
  }
  FUN_4378f7a0(0x11ac);
  if ((*(byte *)(iVar2 + 0x12) & 1) != 0) {
    FUN_43561540(s_Imgng__HS_Drv_S_43ca3336);
  }
  FUN_43796848(&DAT_43e99208);
  if ((*(byte *)(iVar2 + 0x12) & 1) != 0) {
    FUN_43561540(s_Imgng__HS_Drv_E_43ca3346);
  }
  FUN_4378f7a0(0x11b0);
  if ((DAT_43e9bb18 == 0) || (DAT_43e9d028 != '\0')) {
    iVar4 = FUN_437999e4(1,0);
    if (iVar4 == 0) {
      uStack_38 = 0;
      uStack_34 = 0;
      iVar4 = FUN_43799a94(1,0,0,*DAT_43e9920c,DAT_43e9d027,0,1,0,2,&uStack_38,0);
      if (iVar4 != 0) {
        FUN_43795de0(1);
      }
    }
    iVar4 = FUN_437999e4(1,0);
    if (iVar4 != 0) {
      if ((DAT_43e9bb30 == 0x11) && (DAT_43e9d028 != '\0')) {
        uVar8 = DAT_43e9920c[4];
        if (DAT_43e9920c[0xf] == 1) {
          uVar8 = DAT_43e9920c[0xc];
        }
        FUN_43795d94(uVar8 == 3);
        FUN_43795a8c(1);
      }
      if ((DAT_43e9bb34 != '\0') &&
         (((((DAT_43e9bd54 & 0x40) != 0 || (sVar1 = *(short *)(DAT_43e99208 + 0x10), sVar1 == 0xa10)
            ) || (sVar1 == 0xa11)) || ((sVar1 == 0xa12 || (sVar1 == 0xa13)))))) {
        FUN_43795a8c(2);
        FUN_43795de0(1);
      }
      uStack_40 = 0;
      uStack_3c = 0;
      if ((DAT_43e9bdb2 != '\0') &&
         ((DAT_43e9bb20 == 0 || ((DAT_43e9bce8 != '\0' && (DAT_43e9d028 != '\0')))))) {
        iStack_b0 = DAT_43e9bb18;
        uStack_ac = DAT_43e9bcd4;
        uStack_a8 = DAT_43e9bcdc;
        uStack_9c = DAT_43e9d02a;
        uStack_a4 = *(undefined4 *)(DAT_43e99214 + 0x70);
        uStack_a0 = *(undefined4 *)(DAT_43e99214 + 100);
        uStack_9a = DAT_43e9d030;
        thunk_FUN_43af5002(&iStack_b0,auStack_30);
        FUN_439c5320(&uStack_48,DAT_43e9922c + 0x16,8);
        uStack_42 = auStack_30[0];
        FUN_43ae939a(&uStack_48);
        if ((*(byte *)(iVar2 + 0x26) & 8) != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca3356,*(undefined2 *)(DAT_43e99228 + 10),
                       *(undefined4 *)(DAT_43e99210 + 0x1f0),uStack_48,uStack_46,uStack_44,uStack_42
                      );
          FUN_43902718(s_ZAF_img_id__04X__shut__d__svd__d_43ca336a,
                       *(undefined2 *)(DAT_43e99228 + 10),*(undefined4 *)(DAT_43e99210 + 0x1f0),
                       uStack_48,uStack_46,uStack_44,uStack_42);
        }
        iVar4 = FUN_437999e4(1,0xd);
        if ((iVar4 != 0) && (iVar4 = FUN_437955f8(), iVar4 != 0)) {
          uStack_70 = DAT_43e9bcd4;
          iStack_6c = DAT_43e9bb20;
          uStack_68 = *(undefined2 *)(DAT_43e99214 + 0x3c);
          uStack_66 = *(undefined2 *)(DAT_43e99214 + 0x3e);
          uStack_64 = DAT_43e9d02a;
          uStack_62 = DAT_43e9d02e;
          thunk_FUN_43af5040(&uStack_70,auStack_50);
          auStack_2c[0] = *(undefined2 *)(DAT_43e9922c + 0x1e);
          FUN_43ae93b4(auStack_2c);
          uStack_3c = uStack_4c;
          uStack_40._0_2_ = CONCAT11(auStack_50[0],1);
          if ((*(byte *)(iVar2 + 0x26) & 8) != 0) {
            FUN_4378eb78(3,9,1,&DAT_43ca33a6,*(undefined2 *)(DAT_43e99228 + 8),auStack_2c[0],
                         auStack_50[0],uStack_4c);
            FUN_43902718(s_ZAF_img_id__04X__a_gain__04X__pu_43ca33ba,
                         *(undefined2 *)(DAT_43e99228 + 8),auStack_2c[0],uStack_40._1_1_,uStack_3c);
          }
          uVar6 = FUN_43795604();
          FUN_437d9ab4(&DAT_43e99208,uVar6);
        }
      }
      iVar4 = FUN_43795ac8();
      if (iVar4 == 1) {
        FUN_43795de0(0);
      }
      FUN_43795e9c(DAT_43e9bb28,DAT_43e9bb18,DAT_43e9920c[3],DAT_43e9bcd9);
      iVar4 = FUN_437999e4(1,0xd);
      if (iVar4 != 0) {
        FUN_4379572c(&uStack_40);
      }
      FUN_437957d4();
      FUN_43795ad4();
      if ((*(byte *)(iVar2 + 0x26) & 2) != 0) {
        iVar4 = thunk_FUN_436cd00c();
        uVar8 = DAT_43e9920c[2];
        FUN_4378eb78(3,9,1,&DAT_43ca33ec,iVar4 - uVar8);
        FUN_43902718(s_Imager_Execute__dus_43ca3400,iVar4 - uVar8);
      }
    }
    FUN_43795ab8();
  }
  FUN_43ae129a(4);
  if (*(char *)(iVar2 + 0x11) != '\0') {
    uVar6 = thunk_FUN_436cd00c();
    *DAT_44024f64 = uVar6;
  }
  if ((uVar7 != *DAT_43e9920c) || (param_1 != DAT_43e9d027)) {
    iVar4 = thunk_FUN_436cd00c();
    uVar8 = iVar4 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca3414,uVar7,param_1,*DAT_43e9920c,DAT_43e9d027,uVar8);
    FUN_43902718(s_HS_Sequence__overflow__dV___d__>_43ca3428,uVar7,param_1,*DAT_43e9920c,
                 DAT_43e9d027,uVar8);
    if (param_1 < 4) {
      uVar6 = *(undefined4 *)(&DAT_43bc42a8 + param_1 * 4);
    }
    else {
      uVar6 = 0xc;
    }
    FUN_4378f988(4,uVar6,uVar8);
    if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
      FUN_43561540(s_HS_Seq_E_OF_43ca3456);
    }
    if ((*(byte *)(iVar2 + 0x1b) & 0x40) != 0) {
      FUN_4378ec60();
    }
  }
  switch(DAT_43e9d027) {
  case 0:
    uVar6 = 1;
    break;
  case 1:
    uVar6 = 2;
    break;
  case 2:
    uVar6 = 3;
    break;
  case 3:
    uVar6 = 4;
    break;
  default:
    goto switchD_43791216_default;
  }
  FUN_43901480(uVar6);
switchD_43791216_default:
  iVar4 = FUN_43ae916c();
  if (iVar4 != 0) {
    FUN_4379bb90(&DAT_43e99208);
  }
  if (DAT_43e9d027 == 0) {
    FUN_43ada220(auStack_84,0x4379155d);
    FUN_439018b0(&DAT_43e992fc,auStack_84,*DAT_43e9920c,0);
  }
  if (DAT_43e9d028 != '\0') {
    FUN_43ae9130(auStack_98,&LAB_4378e9cc_1);
    FUN_439018b0(&DAT_43e99380,auStack_98,0,0);
  }
  if ((*(byte *)(iVar2 + 0x12) & 1) != 0) {
    switch(DAT_43e9d027) {
    case 0:
      pcVar3 = s_HS0_Seq_E_43ca3462;
      break;
    case 1:
      pcVar3 = s_HS1_Seq_E_43ca346c;
      break;
    case 2:
      pcVar3 = s_HS2_Seq_E_43ca3476;
      break;
    case 3:
      pcVar3 = s_HS3_Seq_E_43ca3480;
      break;
    default:
      goto switchD_437912a2_default;
    }
    FUN_43561540(pcVar3);
  }
switchD_437912a2_default:
  return;
}


/* query "4381bf38" */

void FUN_4381bf38(int param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  iVar3 = param_1 + 4;
  iStack_20 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  FUN_43560d38(0x1b,0xffffffff);
  uStack_1c = FUN_43afc5b6(iVar3);
  iStack_20 = FUN_43afc5a8(iVar3);
  FUN_43b04990(&uStack_1c,&iStack_20,0x43b048b3);
  FUN_43560d1c(0x1b);
  uVar1 = FUN_43afbfc2(iVar3);
  for (uVar4 = 0; uVar4 < uVar1; uVar4 = uVar4 + 1) {
    FUN_43560d38(0x1b,0xffffffff);
    uVar2 = FUN_43afc5c6(iVar3);
    FUN_43560d1c(0x1b);
    FUN_43b047d0(uVar2);
  }
  return;
}


/* query "4381bd4c" */

int * FUN_4381bd4c(int *param_1,int param_2,undefined2 param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iStack_2c;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  int iStack_1c;
  
  piVar1 = (int *)FUN_43b0473e(&DAT_43eeaf5c);
  if (piVar1 == (int *)0x0) {
    if (4 < DAT_43eeaf58) {
      return (int *)0x0;
    }
    DAT_43eeaf58 = DAT_43eeaf58 + 1;
    uVar5 = DAT_43eeaf58;
    FUN_4381b9d0(5,3,1,&DAT_43cb442b,DAT_43eeaf58);
    FUN_43902718(s_Image__Create_Image_NULL__d_43cb443a,DAT_43eeaf58);
    if (DAT_43eeaf58 == 1) {
      FUN_43901a8c(3,0,0,0x2c);
    }
    if (DAT_43eeaf58 == 5) {
      FUN_4381b9d0(5,3,1,&LAB_43cb437e_1,uVar5);
      FUN_43902718(s_Image_NULL_log_end_43cb438e);
    }
  }
  else {
    *(undefined2 *)(piVar1 + 8) = param_3;
    *piVar1 = param_2;
    *(undefined1 *)((int)piVar1 + 0x23) = 0;
    *(undefined1 *)((int)piVar1 + 0x22) = 1;
    iVar2 = param_1[1];
    iVar3 = param_1[2];
    iVar4 = param_1[3];
    piVar1[2] = *param_1;
    piVar1[3] = iVar2;
    piVar1[4] = iVar3;
    piVar1[5] = iVar4;
    piVar1[6] = param_1[4];
    FUN_437965ac(piVar1,param_1[5]);
    piVar1[0xe] = 0;
    piVar1[0xf] = 0;
    FUN_43b02fcc(&iStack_2c,0);
    piVar1[9] = iStack_2c;
    piVar1[10] = iStack_28;
    piVar1[0xb] = iStack_24;
    piVar1[0xc] = iStack_20;
    piVar1[0xd] = iStack_1c;
    if (param_1[5] == 4) {
      piVar1[7] = 5;
    }
    else {
      piVar1[7] = 0;
    }
    if (*piVar1 != 0) {
      return piVar1;
    }
    if (DAT_43eeaf58 < 5) {
      DAT_43eeaf58 = DAT_43eeaf58 + 1;
      uVar5 = DAT_43eeaf58;
      FUN_4381b9d0(5,3,1,&DAT_43cb4456,DAT_43eeaf58);
      FUN_43902718(s_Image__Create_ImageParam_NULL__d_43cb4465,DAT_43eeaf58);
      if (DAT_43eeaf58 == 1) {
        FUN_43901a8c(3,0,1,0x4f);
      }
      if (DAT_43eeaf58 == 5) {
        FUN_4381b9d0(5,3,1,&LAB_43cb437e_1,uVar5);
        FUN_43902718(s_Image_NULL_log_end_43cb438e);
      }
    }
    FUN_4381ba7c(piVar1);
  }
  return (int *)0x0;
}


/* query "43ae9674" */

bool FUN_43ae9674(short *param_1)

{
  return *param_1 != -1;
}


/* query "43b03a5e" */

undefined4 FUN_43b03a5e(undefined4 param_1)

{
  FUN_439c5a04(param_1,0,0x104);
  return param_1;
}


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


/* query "43561524" */

void FUN_43561524(void)

{
  (**(code **)(*(int *)(DAT_440205c0 + 0x14) + 0x2e4))();
  return;
}


/* query "43561604" */

void FUN_43561604(void)

{
  (**(code **)(*(int *)(DAT_440205c0 + 0x14) + 0x308))();
  return;
}


/* query "439035e0" */

int FUN_439035e0(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined2 param_6)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined2 *puVar5;
  undefined1 auStack_80 [4];
  undefined2 uStack_7c;
  byte bStack_78;
  undefined4 auStack_70 [24];
  
  iVar2 = FUN_43902c2c(param_2,param_3,param_4,param_5,auStack_80,param_6);
  if (iVar2 == 0) {
    *(undefined4 *)(param_1 + 2) = param_2;
    *param_1 = uStack_7c;
    *(byte *)(param_1 + 1) = bStack_78;
    if (4 < bStack_78) {
      FUN_43902984(5,1,1,&DAT_43cceb4c,bStack_78,4);
      FUN_43902718(s_MemoryHandle__AllocRendezvous__E_43cceb57,*(undefined1 *)(param_1 + 1),4);
      *(undefined1 *)(param_1 + 1) = 4;
    }
    bVar1 = *(byte *)(param_1 + 1);
    puVar4 = auStack_70;
    puVar5 = param_1;
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
      *(undefined4 *)(puVar5 + 4) = *puVar4;
      *(undefined4 *)(puVar5 + 6) = puVar4[1];
      puVar5 = puVar5 + 4;
      puVar4 = puVar4 + 2;
    }
    *(undefined1 *)((int)param_1 + 3) = 1;
  }
  return iVar2;
}

