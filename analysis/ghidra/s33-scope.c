/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

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


/* query "43796740" */

void FUN_4379671c(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_1;
  uStack_c = param_2;
  FUN_43ae96d4(&uStack_c,0);
  uStack_c = FUN_43ae96e0(&DAT_43e9d7a8);
  while( true ) {
    uStack_10 = FUN_43ae96f0(&DAT_43e9d7a8);
    iVar1 = FUN_43ae968e(&uStack_c,&uStack_10);
    if (iVar1 == 0) break;
    iVar1 = FUN_43ae969a(&uStack_c);
    if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
    }
    FUN_43ae9708(&uStack_c);
  }
  FUN_43ae973c(&DAT_43e9d7a8);
  return;
}


/* query "44021030" */

/* query "44024fdc" */

/* query "4401f57c" */

/* query "44020ae0" */

/* query "44022d28" */

/* query "44025204" */

/* query "44020e70" */

/* query "44021a2c" */

/* query "44020064" */

/* query "4401f058" */

/* query "44022478" */

/* query "4401f6bc" */
