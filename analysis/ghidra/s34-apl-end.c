/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43814de0" */

undefined8 FUN_43814db4(char *param_1,undefined4 param_2,undefined4 param_3)

{
  switch(param_1) {
  case (char *)0x1:
    break;
  case (char *)0x2:
    param_2 = 2;
    break;
  case (char *)0x3:
    param_2 = 3;
    break;
  default:
    param_1 = s_EnumConverter_h_43cb0bbf;
    FUN_43814c78(5,0,1,&DAT_43c9b47c,s_EnumConverter_h_43cb0bbf,0xf4,param_3);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_EnumConverter_h_43cb0bbf,0xf4);
  case (char *)0x0:
    param_2 = 0;
  }
  return CONCAT44(param_1,param_2);
}


/* query "43814e00" */

/* query "438c7800" */

undefined4 FUN_438c7800(int param_1,uint *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  char *pcVar3;
  int iVar4;
  char *pcVar5;
  undefined1 *puVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  undefined4 *puVar10;
  undefined1 *puVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  undefined1 auStack_248 [44];
  undefined4 uStack_21c;
  undefined4 uStack_218;
  undefined4 uStack_214;
  undefined4 uStack_210;
  int iStack_1e8;
  undefined1 auStack_1d0 [120];
  undefined1 auStack_158 [44];
  undefined4 uStack_12c;
  undefined4 uStack_128;
  undefined1 auStack_f8 [44];
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined1 auStack_98 [38];
  undefined1 uStack_72;
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [8];
  undefined1 auStack_40 [8];
  uint uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined2 auStack_2a [3];
  
  FUN_43ae8220(auStack_1d0);
  iVar4 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0xb2) & 2) != 0) {
    FUN_438c7610(5,1,1,&LAB_43cc891a_1);
    FUN_43902718(s_ReadExecuteBase_43cc892a);
    FUN_438c7610(5,1,1,&DAT_43cc893a,*param_2);
    FUN_43902718(s_Cap_core_mode__0x_x__43cc8949,*param_2);
    if (param_2[2] != 0) {
      FUN_438c7610(5,1,1,&DAT_43cc895e,*(undefined1 *)(param_2[2] + 2));
      FUN_43902718(s_PGA_ON___x__43cc896d,*(undefined1 *)(param_2[2] + 2));
      FUN_438c7610(5,1,1,&DAT_43cc8979,*(undefined1 *)(param_2[2] + 1));
      FUN_43902718(s_SHD_ON___x__43cc8988,*(undefined1 *)(param_2[2] + 1));
      FUN_438c7610(5,1,1,&DAT_43cc8994,*(undefined1 *)param_2[2]);
      FUN_43902718(s_28Limit_ON___x__43cc89a3,*(undefined1 *)param_2[2]);
      FUN_438c7610(5,1,1,&DAT_43cc89b3,*(undefined4 *)(param_2[2] + 4));
      FUN_43902718(s_LongObMode___x__43cc89c2,*(undefined4 *)(param_2[2] + 4));
    }
    FUN_438c7610(5,1,1,&DAT_43cc89d2,*(undefined4 *)(param_1 + 0x748));
    FUN_43902718(s_SnrCtrlMode___x__43cc89e1,*(undefined4 *)(param_1 + 0x748));
    FUN_438c7610(5,1,1,&DAT_43cc89f2,(char)param_2[1]);
    FUN_43902718(s_opb_out___d__43cc8a01,(char)param_2[1]);
  }
  uVar9 = *param_2;
  bVar1 = *(byte *)(param_1 + 0x4b84);
  iVar7 = *(int *)(param_1 + 0x748);
  uVar8 = param_2[1];
  if (param_2[2] == 0) {
    uVar2 = 0xffff;
  }
  else {
    uVar2 = FUN_43b1e57c();
  }
  FUN_43901a8c(4,0xf013,(uint)bVar1 | uVar9 << 0x18 | iVar7 << 0x10 | (uint)(byte)uVar8 << 8,uVar2);
  if ((*param_2 & 1) != 0) {
    uVar2 = FUN_436d6118();
    iVar7 = FUN_436d64c8(uVar2,auStack_2a);
    if (iVar7 != 0) {
      auStack_2a[0] = 0xffff;
    }
    *(undefined2 *)(param_1 + 0x766) = auStack_2a[0];
    FUN_43795a60(*(undefined4 *)(param_1 + 0x4d0),*(undefined1 *)(param_1 + 0x4d4),
                 *(undefined1 *)(param_1 + 0x4d5),auStack_40);
    iVar7 = FUN_43a12c64();
    if (iVar7 == 3) {
      uVar2 = FUN_436d6118();
      candidate_436d62e4(uVar2,auStack_40);
      uVar2 = FUN_436d6118();
      FUN_43ad911c(uVar2,1);
    }
    if (*(char *)((int)param_2 + 5) != '\0') {
      *(undefined2 *)(param_1 + 0x650) = 0;
      *(undefined4 *)(param_1 + 0x64c) = 0;
      *(undefined2 *)(param_1 + 0x652) = 0;
      *(undefined1 *)(param_1 + 0x654) = 0;
      *(undefined1 *)(param_1 + 0x655) = 4;
      *(undefined2 *)(param_1 + 0x6b8) = *(undefined2 *)(param_1 + 0x12f8);
      uVar2 = FUN_436d6118();
      FUN_436d6320(uVar2,param_1 + 0x64c,0);
      if (*(int *)(param_1 + 0x504) == 0) {
        FUN_436d6118();
        FUN_43ad9116();
        *(undefined4 *)(param_1 + 0x64c) = 8;
      }
    }
    uVar2 = FUN_436d6118();
    FUN_436d61a4(uVar2,auStack_40,param_1 + 0x548);
    FUN_43795a40(*(undefined1 *)(param_1 + 0x4d4),*(undefined1 *)(param_1 + 0x4d5),param_1 + 0x564);
    uVar2 = FUN_436d6118();
    FUN_436d6398(uVar2,param_1 + 0x6bc,0);
    uVar2 = FUN_436d6118();
    FUN_43ad911c(uVar2,1);
  }
  if (*(int *)(param_1 + 0x4b80) == 2) {
    FUN_43a1227c();
  }
  uVar2 = *(undefined4 *)(param_1 + 0x570);
  uVar13 = *(undefined4 *)(param_1 + 0x56c);
  puVar10 = (undefined4 *)(param_1 + 0x4e60);
  FUN_437dcd28(auStack_248);
  iVar7 = *(int *)(param_1 + 0x4b80);
  if (iVar7 == 2) {
    if (*(char *)(param_1 + 0x4b84) == '\x01') goto LAB_438c7aa2;
LAB_438c7ab8:
    iStack_1e8 = FUN_437f54c0(param_1);
    uStack_21c = 0;
    uStack_218 = 1;
    uStack_214 = *puVar10;
    uStack_210 = puVar10[1];
    if (((*param_2 & 2) != 0) && (iStack_1e8 == 0)) {
      if (*(byte *)(iVar4 + 0x71) == 0) {
        iVar7 = *(int *)(param_1 + 0x56c) << 1;
      }
      else {
        iVar7 = (uint)*(byte *)(iVar4 + 0x71) * 10 + *(int *)(param_1 + 0x56c);
      }
      *(int *)(param_1 + 0x56c) = iVar7;
    }
    if ((*(int *)(param_1 + 0x740) == 1) && (*(char *)((int)param_2 + 5) != '\0')) {
      *(int *)(param_1 + 0x570) = *(int *)(param_1 + 0x570) << 1;
    }
    FUN_4364d404(auStack_f8);
    puVar11 = (undefined1 *)0x0;
    if ((*param_2 & 0x40) != 0) {
      puVar11 = auStack_f8;
      uStack_cc = 2;
      uStack_c8 = 0;
    }
    FUN_4364d404(auStack_158);
    uStack_30 = FUN_43b2e084();
    puVar6 = (undefined1 *)0x0;
    if ((*param_2 & 0x20) != 0) {
      iVar7 = FUN_437874e0(auStack_1d0,5,&uStack_30);
      if (iVar7 != 0) {
        uStack_12c = 2;
        puVar6 = auStack_158;
        uStack_128 = uStack_30;
        goto LAB_438c7b70;
      }
      FUN_438c7610(5,1,1,&DAT_43cc8a0e,s_ReadExecuteBase_43cc8c7d);
      pcVar3 = s__s__IIB_Acquire_Error__43cc8a1d;
      pcVar5 = s_ReadExecuteBase_43cc8c7d;
      goto LAB_438c7dc2;
    }
LAB_438c7b70:
    uStack_34 = 0;
    iVar7 = FUN_437f5a04(param_1,*param_2,(char)param_2[1],&uStack_34,puVar11,auStack_248,puVar6,
                         auStack_1d0);
    if (iVar7 == 0) {
LAB_438c7ee4:
      uVar2 = 0;
      goto LAB_438c7eea;
    }
    if ((*param_2 & 0x10) != 0) {
      FUN_43afa606(param_1 + 0x1e8,auStack_248);
      FUN_437f6b28(param_1,param_1 + 0x4efa);
    }
    if ((*param_2 & 0x20) != 0) {
      FUN_43acdd52(param_1 + 0x3e0,auStack_158);
      FUN_43affcf2(param_1,param_1 + 0x4f36);
    }
    uStack_38 = 0;
    if (((*param_2 & 0x20) != 0) &&
       (iVar7 = FUN_437f918c(param_1,&uStack_30,&uStack_38,auStack_1d0), iVar7 == 0)) {
      FUN_438c7610(5,1,1,&DAT_43cc8a34);
      FUN_43902718(s_AfterViewContRcStart_ERROR__43cc8a43);
      goto LAB_438c7ee8;
    }
    if (*(int *)(param_1 + 0x758) == 0) {
      FUN_43aefd3c();
    }
    else {
      FUN_43aefcee(param_1 + 0x20,param_1 + 0x4d8);
    }
    FUN_437f8be0(param_1,param_2[2],(*param_2 & 0x3f) >> 5);
    FUN_43affa58(param_1);
    if ((*param_2 & 1) != 0) {
      pcVar5 = (char *)FUN_43ae92ee(*(undefined4 *)(param_1 + 0x6c4),auStack_98);
      if (pcVar5 != (char *)0x0) {
        FUN_438c7610(5,1,1,&DAT_43cc8a5f,pcVar5);
        pcVar3 = s__DFE__GetDfeDrvParam_Error__d_43cc8a6e;
        goto LAB_438c7dc2;
      }
      thunk_FUN_43af50fc(param_1 + 0x3388,param_1 + 0x20,auStack_98,auStack_48);
    }
    if ((*param_2 & 0x40) != 0) {
      FUN_43acdd52(param_1 + 0x380,auStack_f8);
      iVar7 = FUN_437f6820(param_1,uStack_34,(*param_2 & 0xf) >> 3);
      if (iVar7 == 0) goto LAB_438c7ee4;
    }
    if ((*(char *)(iVar4 + 0xbd) != '\0') && (iVar4 = FUN_43acc0c4(uStack_34), iVar4 != 0)) {
      FUN_43ad0fc6();
    }
    uVar8 = *param_2;
    if ((uVar8 & 1) == 0) {
      iVar4 = 0;
      iVar7 = 0;
      uVar12 = 0;
    }
    else {
      iVar4 = DAT_4402282c;
      iVar7 = DAT_440201bc;
      uVar12 = DAT_4401f160;
      if ((*(char *)((int)param_2 + 5) == '\0') &&
         (uVar12 = 0, iVar7 = DAT_4401fb6c, *(int *)(param_1 + 0x4b80) != 3)) {
        iVar7 = 0;
      }
    }
    *(undefined4 *)(param_1 + 0x4eec) = 1;
    if ((uVar8 & 0x40) != 0) {
      *(undefined4 *)(param_1 + 0x4eec) = 0x401;
    }
    if ((uVar8 & 0x20) != 0) {
      *(uint *)(param_1 + 0x4eec) = uStack_38 | *(uint *)(param_1 + 0x4eec);
    }
    if (iVar4 != 0) {
      *(uint *)(param_1 + 0x4eec) = *(uint *)(param_1 + 0x4eec) | 0x200;
    }
    if (iVar7 != 0) {
      *(uint *)(param_1 + 0x4eec) = *(uint *)(param_1 + 0x4eec) | 2;
    }
    if (*(char *)((int)param_2 + 6) != '\0') {
      FUN_43aff79a(2,1);
    }
    FUN_43ae963c();
    if ((*param_2 & 1) != 0) {
      FUN_436d6118();
      FUN_43ad9132();
    }
    if (*(char *)((int)param_2 + 5) == '\0') {
      FUN_438d0acc(param_1);
    }
    pcVar5 = (char *)FUN_43acc65e(*(undefined4 *)(param_1 + 0x4ba8));
    if (pcVar5 == (char *)0x0) {
      if ((*param_2 & 1) != 0) {
        auStack_48[0] = uStack_72;
        pcVar5 = (char *)FUN_43ae9300(*(undefined4 *)(param_1 + 0x4bac),auStack_48,iVar4);
        if (pcVar5 != (char *)0x0) {
          FUN_438c7610(5,1,1,&DAT_43cc8ab6,pcVar5);
          pcVar3 = s__DFE__Start_Error__d_43cc8ac5;
          goto LAB_438c7dc2;
        }
        FUN_43acac1a(auStack_5c,iVar7);
        FUN_43acac1a(auStack_70,uVar12);
        FUN_43795dec(3,param_1 + 0x548,0,auStack_5c,auStack_70);
      }
      *(undefined4 *)(param_1 + 0x56c) = uVar13;
      *(undefined4 *)(param_1 + 0x570) = uVar2;
      if ((*(byte *)(DAT_4402546c + 0xb2) & 2) != 0) {
        FUN_438c7610(5,1,1,&DAT_43cc8ada,*(undefined4 *)(param_1 + 0x4eec),0x73a);
        FUN_43902718(s_Callback_waiflg__0x_x___LINE__d__43cc8ae9,*(undefined4 *)(param_1 + 0x4eec),
                     0x73a);
      }
      FUN_43affb9c(param_1 + 0x4fd4,param_1 + 0x1e8);
      if (*(int *)(param_1 + 0x4b70) == 2) {
        FUN_43a13794(*(undefined4 *)(param_1 + 0x4e60),*(undefined2 *)(param_1 + 0x4aec),
                     *(undefined2 *)(param_1 + 0x1f0),*(undefined2 *)(param_1 + 0x1ec));
      }
      FUN_43af6440(param_1 + 0x30e0,param_1 + 0x20);
      FUN_43aefa54(param_1 + 0x20);
      FUN_437872f8(auStack_1d0,0,*(undefined4 *)(param_1 + 0x4ba8));
      if ((*param_2 & 1) != 0) {
        FUN_437872f8(auStack_1d0,8,*(undefined4 *)(param_1 + 0x4bac));
      }
      if ((*param_2 & 0x20) != 0) {
        FUN_437872f8(auStack_1d0,1,*(undefined4 *)(param_1 + 0x5058));
        FUN_437872f8(auStack_1d0,5,*(undefined4 *)(param_1 + 0x410));
        if (*(short *)(param_1 + 0x4b2c) != -1) {
          FUN_43ae82a0(auStack_1d0);
        }
      }
      *(uint *)(param_1 + 0x4fe4) = *param_2;
      uVar2 = 1;
      goto LAB_438c7eea;
    }
    FUN_438c7610(5,1,1,&DAT_43cc8a8c,pcVar5);
    pcVar3 = s_CamCore_Start_Error____02x_43cc8a9b;
LAB_438c7dc2:
    FUN_43902718(pcVar3,pcVar5);
  }
  else {
    if ((((iVar7 != 3) && (iVar7 != 1)) || (*(char *)(iVar4 + 0x6c) == '\0')) ||
       (*(char *)(param_1 + 0x4b84) != '\0')) goto LAB_438c7ab8;
LAB_438c7aa2:
    iVar7 = FUN_437dd520(param_1);
    if (iVar7 != 0xffff) {
      puVar10 = (undefined4 *)(param_1 + 0x4e78);
      goto LAB_438c7ab8;
    }
  }
LAB_438c7ee8:
  uVar2 = 0;
LAB_438c7eea:
  FUN_43787180(auStack_1d0);
  return uVar2;
}


/* query "43b1c6d6" */

undefined4 FUN_43b1c6d6(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  undefined1 *puVar9;
  int iVar10;
  undefined1 auStack_114 [44];
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined1 auStack_b4 [38];
  undefined1 uStack_8e;
  undefined1 auStack_8c [20];
  undefined1 auStack_78 [4];
  undefined1 auStack_74 [16];
  ushort auStack_64 [2];
  int iStack_60;
  int iStack_5c;
  undefined2 uStack_58;
  undefined2 uStack_56;
  undefined4 uStack_50;
  undefined1 uStack_4c;
  undefined1 uStack_4b;
  undefined1 uStack_4a;
  undefined1 uStack_49;
  undefined1 auStack_44 [8];
  undefined4 auStack_3c [2];
  undefined4 uStack_34;
  byte bStack_30;
  undefined1 uStack_2f;
  undefined1 auStack_2c [12];
  
  uVar3 = FUN_43afdf16();
  switch(uVar3) {
  case 0:
    uVar3 = FUN_438cc4b4(param_1);
    return uVar3;
  case 1:
  case 3:
  case 5:
    break;
  case 2:
    uVar3 = FUN_43ae75dc();
    FUN_43afb42e(auStack_74);
    FUN_43afb476(auStack_74,DAT_440209fc);
    bStack_30 = 0;
    iStack_60 = 3;
    uStack_34 = FUN_43afbf44(param_1);
    FUN_43ae841c(auStack_2c,DAT_4401f518);
    uVar2 = FUN_43ae821c(uVar3);
    iVar1 = FUN_437dcfc8(auStack_2c,uVar2,uVar3);
    if (iVar1 == 0) {
      FUN_438cc324(5,1,1,&DAT_43cc6dde);
      FUN_43902718(s_ImageParam_Capture__Create_Error_43cc6ded);
      uVar3 = 2;
    }
    else {
      FUN_4381bbf0(param_1,auStack_74,iVar1);
      FUN_43b04730();
      uVar3 = 0;
    }
    return uVar3;
  case 4:
    uVar3 = FUN_43ae75dc();
    FUN_43afb42e(auStack_74);
    FUN_43afb476(auStack_74,DAT_44024218);
    bStack_30 = 0;
    iStack_60 = 3;
    uStack_34 = FUN_43afbf44(param_1);
    FUN_43ae841c(auStack_2c,DAT_4401f518);
    uVar2 = FUN_43ae821c(uVar3);
    iVar1 = FUN_437dcfc8(auStack_2c,uVar2,uVar3);
    if (iVar1 == 0) {
      FUN_438cc324(5,1,1,&DAT_43cc6dde);
      FUN_43902718(s_ImageParam_Capture__Create_Error_43cc6ded);
      uVar3 = 2;
    }
    else {
      FUN_4381bbf0(param_1,auStack_74,iVar1);
      FUN_43b04730();
      uVar3 = 0;
    }
    return uVar3;
  case 6:
    iVar1 = FUN_43ae75dc();
    FUN_43ae769a(iVar1,7);
    if (*(int *)(iVar1 + 0x4eec) != 0) {
      FUN_43aff79a(*(int *)(iVar1 + 0x4eec),1);
    }
    FUN_437f5970(iVar1);
    uVar3 = FUN_43ae9332(*(undefined4 *)(iVar1 + 0x4d0));
    *(undefined4 *)(iVar1 + 0x6c4) = uVar3;
    FUN_43afb2d0(iVar1,4,2);
    FUN_43afb2d0(iVar1,5,2);
    FUN_43560dc4(0x13,0xfeffffef);
    if (*(char *)(DAT_4402546c + 0xbe) != '\0') {
      FUN_43783284(0x65,*(undefined2 *)(iVar1 + 0x4aec),iVar1 + 0x1e8,
                   *(undefined1 *)(iVar1 + 0x54c4));
      iVar5 = *(int *)(iVar1 + 0x1f0) * *(int *)(iVar1 + 0x1ec);
      FUN_43783218(0x66,*(undefined2 *)(iVar1 + 0x4aec),iVar5,iVar5);
    }
    return 0;
  case 7:
    uVar3 = FUN_437ed568(param_1);
    return uVar3;
  default:
    return 5;
  }
  iVar1 = FUN_43ae75dc(param_1);
  FUN_43ae769a(iVar1,6);
  FUN_43560cc8(1);
  if (*(char *)(iVar1 + 0x4b98) == '\0') {
    FUN_438d060c(iVar1);
  }
  uVar3 = FUN_437f80b4(iVar1);
  FUN_43795a60(uVar3,*(undefined1 *)(iVar1 + 0x4d4),*(undefined1 *)(iVar1 + 0x4d5),auStack_3c);
  uVar3 = FUN_436d6118();
  candidate_436d62e4(uVar3,auStack_3c);
  uVar3 = FUN_436d6118();
  FUN_436d61a4(uVar3,auStack_3c,iVar1 + 0x548);
  FUN_43795a40(*(undefined1 *)(iVar1 + 0x4d4),*(undefined1 *)(iVar1 + 0x4d5),iVar1 + 0x564);
  bStack_30 = *(byte *)(iVar1 + 0x4b98);
  uStack_34 = CONCAT22(*(undefined2 *)(iVar1 + 0x1d8),*(undefined2 *)(iVar1 + 0x4b54));
  uStack_2f = (uint)bStack_30 == *(byte *)(iVar1 + 0x550) + 1;
  iStack_5c = iVar1 + 0x64c;
  iVar5 = *(int *)(iVar1 + 0x4ad8);
  if (iVar5 != 0) {
    iVar5 = iVar5 + 0x12e;
  }
  iVar7 = iVar1 + 0x20;
  FUN_437b27b8(iVar1 + 0x1198,iVar7,&uStack_34,auStack_64,iVar5);
  *(undefined2 *)(iVar1 + 0x6bc) = uStack_58;
  *(undefined2 *)(iVar1 + 0x6be) = uStack_56;
  *(undefined2 *)(iVar1 + 0x6b8) = *(undefined2 *)(iVar1 + 0x12f8);
  uVar3 = FUN_436d6118();
  FUN_436d6320(uVar3,iVar1 + 0x64c,*(undefined1 *)(iVar1 + 0x4b98));
  uVar3 = FUN_436d6118();
  FUN_436d6398(uVar3,iVar1 + 0x6bc,*(undefined1 *)(iVar1 + 0x4b98));
  uVar3 = FUN_436d6118();
  FUN_43ad911c(uVar3,1);
  uVar3 = *(undefined4 *)(iVar1 + 0x570);
  *(uint *)(iVar1 + 0x570) = (uint)auStack_64[0];
  if (iStack_60 == 0) {
    *(char *)(iVar1 + 0x4ba1) = *(char *)(iVar1 + 0x4b98) + '\x03';
    *(char *)(iVar1 + 0x4ba3) = *(char *)(iVar1 + 0x4b98) + '\x01';
  }
  else if (iStack_60 == 1) {
    *(char *)(iVar1 + 0x4ba2) = *(char *)(iVar1 + 0x4b98) + '\x03';
    *(char *)(iVar1 + 0x4ba4) = *(char *)(iVar1 + 0x4b98) + '\x01';
  }
  FUN_4364d404(auStack_114);
  iVar5 = 0;
  if (*(char *)(iVar1 + 0x4ba3) == *(char *)(iVar1 + 0x4b98)) {
    iVar10 = *(int *)(iVar1 + 0x4e98);
    if (*(char *)(DAT_4402546c + 0xbe) == '\0') {
LAB_438ccb7c:
      uStack_e4 = 0;
      uStack_e8 = 2;
      puVar9 = auStack_114;
      goto LAB_438ccb7e;
    }
LAB_438cc95c:
    uStack_e4 = 0;
    uStack_e8 = 2;
    iVar6 = iVar1 + 0x1e8;
    *(undefined4 *)(iVar1 + 0x248) = 2;
    *(undefined4 *)(iVar1 + 0x214) = 0;
    *(undefined4 *)(iVar1 + 0x218) = 1;
    puVar9 = auStack_114;
    *(int *)(iVar1 + 0x21c) = iVar5 + *(int *)(iVar1 + 0x4e60);
    *(int *)(iVar1 + 0x220) = *(int *)(iVar1 + 0x4e64) - iVar5;
  }
  else {
    if (*(char *)(iVar1 + 0x4ba4) == *(char *)(iVar1 + 0x4b98)) {
      iVar10 = *(int *)(iVar1 + 0x4ea0);
      if (*(char *)(DAT_4402546c + 0xbe) != '\0') {
        iVar5 = *(int *)(iVar1 + 0x1ec) * *(int *)(iVar1 + 0x1f0);
        goto LAB_438cc95c;
      }
      goto LAB_438ccb7c;
    }
    iVar10 = 0;
    puVar9 = (undefined1 *)0x0;
LAB_438ccb7e:
    iVar6 = 0;
  }
  iVar5 = FUN_437f581c(iVar1,puVar9,iVar6,0);
  if (iVar5 == 0) {
LAB_438ccb6e:
    uVar3 = 2;
  }
  else {
    iVar5 = *(int *)(iVar1 + 0x4ad0);
    if (iVar5 != 0) {
      iVar5 = iVar5 + 0x1448;
    }
    auStack_2c[0] = 0;
    FUN_4379ee04(iVar1 + 0x2c2c,iVar7,iVar5,auStack_2c);
    if (iVar10 != 0) {
      FUN_43acdd52(iVar1 + 0x380,puVar9);
      iVar5 = FUN_437f6714(iVar1,iVar10);
      if (iVar5 == 0) goto LAB_438ccb6e;
    }
    iVar5 = iVar1 + 0x30e0;
    FUN_43af640c(iVar5,iVar7);
    uStack_50 = auStack_3c[0];
    uStack_4c = *(undefined1 *)(iVar1 + 0x54d);
    uStack_4b = *(undefined1 *)(iVar1 + 0x54c);
    uStack_4a = *(undefined1 *)(iVar1 + 0x54f);
    uStack_49 = *(undefined1 *)(iVar1 + 0x54e);
    FUN_437d857c(iVar5,iVar7,&uStack_50);
    FUN_436d6118();
    FUN_43ad9132();
    if (*(byte *)(iVar1 + 0x4b98) == 0) {
      FUN_43af6412(iVar5,iVar7);
      uVar8 = 0;
    }
    else {
      if (*(byte *)(iVar1 + 0x550) + 2 <= (uint)*(byte *)(iVar1 + 0x4b98)) {
        FUN_43af6418(iVar5,iVar7);
      }
      iVar5 = FUN_43acc65e(*(undefined4 *)(iVar1 + 0x4ba8));
      if (iVar5 != 0) {
        FUN_438cc324(5,1,1,&DAT_43cc8a8c,iVar5);
        FUN_43902718(s_CamCore_Start_Error____02x_43cc8a9b,iVar5);
      }
      iVar5 = FUN_43ae92e6();
      if (iVar5 != 0) {
        iVar5 = FUN_43ae92ee(*(undefined4 *)(iVar1 + 0x6c4),auStack_b4);
        if (iVar5 != 0) {
          FUN_438cc324(5,1,1,&DAT_43cc8a5f,iVar5);
          FUN_43902718(s__DFE__GetDfeDrvParam_Error__d_43cc8a6e,iVar5);
        }
        auStack_44[0] = uStack_8e;
        iVar5 = FUN_43ae9300(*(undefined4 *)(iVar1 + 0x4bac),auStack_44,0);
        if (iVar5 != 0) {
          FUN_438cc324(5,1,1,&DAT_43cc8ab6,iVar5);
          FUN_43902718(s__DFE__Start_Error__d_43cc8ac5,iVar5);
        }
      }
      uVar8 = 0x80;
    }
    FUN_43acac1a(auStack_78,DAT_4401fb6c);
    FUN_43acac1a(auStack_8c,DAT_4401f160);
    FUN_43795dec(3,iVar1 + 0x548,0,auStack_78,auStack_8c);
    *(undefined4 *)(iVar1 + 0x570) = uVar3;
    if (iStack_60 == 4) {
      FUN_438d0660(iVar1);
    }
    else if (iStack_60 == 3) {
      FUN_438d0660(iVar1);
      FUN_438d060c(iVar1);
    }
    if (*(char *)(iVar1 + 0x4b98) != '\0') {
      FUN_43aff79a(*(undefined4 *)(iVar1 + 0x4eec),1);
    }
    *(uint *)(iVar1 + 0x4eec) = uVar8 | 2;
    if (iStack_60 == 3) {
      cVar4 = *(char *)(iVar1 + 0x550);
    }
    else if (((iStack_60 == 4) ||
             (cVar4 = *(char *)(iVar1 + 0x4b98), *(char *)(iVar1 + 0x4ba1) == cVar4)) ||
            (*(char *)(iVar1 + 0x4ba2) == cVar4)) {
      *(char *)(iVar1 + 0x4b98) = *(char *)(iVar1 + 0x4b98) + '\x01';
      return 0;
    }
    uVar3 = 1;
    *(char *)(iVar1 + 0x4b98) = cVar4 + '\x01';
  }
  return uVar3;
}


/* query "4365dde0" */

int FUN_4365dde0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar1 = *(int *)(param_1 + 0x458);
  iVar2 = *(int *)(param_1 + 0x44c);
  iVar4 = (iVar1 + 2) - iVar2;
  if ((*(int *)(param_1 + iVar4 * 4 + 0x47c) != 1) && (*(int *)(param_1 + iVar4 * 4 + 0x46c) != 1))
  {
    if (iVar1 + 1 == iVar2) {
      iVar2 = *(int *)(param_2 + 0x10);
      *(int *)(param_1 + 0x458) = iVar1 + 1;
      if (*(int *)(*(int *)(iVar2 + 8) + 0x9c) == 1) {
        iVar1 = FUN_4365d550();
        if (iVar1 != 0) {
          FUN_435ab880(s__SDF__INT_ERROR__IntErrCode__0x__43c79f98,iVar1,s_ExecCallBackApl_43c7f0ea,
                       s_ModuleOnePassCcnrEncode_cpp_43c7eefe,0xbb0);
          FUN_435ab880(s__SDF__INT_ERROR__43c79fec);
          uVar5 = 0xbb2;
          uVar3 = 0x4bf;
          goto LAB_4365df1a;
        }
        *(undefined4 *)(param_1 + 0x484) = 1;
      }
      else {
        *(undefined4 *)(param_1 + 0x484) = 3;
      }
    }
    else {
      if (iVar1 != iVar2) {
        FUN_43639190(0x40,0,0x6012,0x4da,4,0x80000000,0,0xbc0);
        uVar3 = *(undefined4 *)(param_1 + 0x458);
        uVar5 = 0xbc1;
        goto LAB_4365df76;
      }
      *(undefined4 *)(param_1 + 0x488) = 4;
    }
    iVar1 = *(int *)(param_1 + 0x454) + 1;
    if (iVar1 == *(int *)(param_1 + 0x44c)) {
      iVar2 = *(int *)(param_2 + 0x10);
      *(int *)(param_1 + 0x454) = iVar1;
      if (*(int *)(*(int *)(iVar2 + 8) + 0x80) == 1) {
        iVar1 = FUN_4365cfcc(param_1,param_2);
        if (iVar1 == 0) {
          iVar1 = *(int *)(param_2 + 0x10);
          *(undefined4 *)(param_1 + 0x474) = 1;
          *(undefined4 *)(param_1 + 0x438) = *(undefined4 *)(*(int *)(iVar1 + 8) + 0x88);
          return 0;
        }
        FUN_435ab880(s__SDF__INT_ERROR__IntErrCode__0x__43c79f98,iVar1,s_ExecCallBackApl_43c7f0ea,
                     s_ModuleOnePassCcnrEncode_cpp_43c7eefe,0xbcf);
        FUN_435ab880(s__SDF__INT_ERROR__43c79fec);
        uVar5 = 0xbd1;
        uVar3 = 0x4c0;
LAB_4365df1a:
        FUN_43639190(0x40,0,0x6012,uVar3,4,iVar1,0,uVar5);
        return iVar1;
      }
      *(undefined4 *)(param_1 + 0x474) = 3;
    }
    else {
      if (*(int *)(param_1 + 0x454) != *(int *)(param_1 + 0x44c)) {
        FUN_43639190(0x40,0,0x6012,0x4db,4,0x80000000,0,0xbe2);
        uVar3 = *(undefined4 *)(param_1 + 0x454);
        uVar5 = 0xbe3;
LAB_4365df76:
        FUN_43639204(0x80,0,0x6012,*(undefined4 *)(param_1 + 0x44c),uVar3,0,uVar5);
        return -0x80000000;
      }
      *(undefined4 *)(param_1 + 0x478) = 4;
    }
  }
  return 0;
}


/* query "43659fce" */

void s32_candidate_43659fce(undefined4 param_1,undefined4 param_2,int param_3,int param_4)

{
  FUN_435ab880(param_1,param_2,param_3 + 0x43659fd2,param_4 + 0x43659fd4);
  FUN_435ab880(s__SDF__ERROR__43c7e90e);
  FUN_435610a0();
  FUN_43560da8();
  return;
}


/* query "436cd2c4" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cd2c4(void)

{
  _DAT_f3c30100 = 0;
  _DAT_f3c300f8 = 0x3ff;
  return;
}


/* query "43ad6002" */

void FUN_43ad6002(undefined4 *param_1,undefined4 param_2)

{
  *param_1 = param_2;
  return;
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


/* query "4380e2e8" */

void FUN_4380e2e8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8,
                 undefined4 param_9,undefined4 param_10,int param_11)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined1 auStack_3c [24];
  
  iVar1 = param_11;
  *(undefined4 *)(param_11 + 4) = param_1;
  *(undefined4 *)(param_11 + 8) = param_2;
  *(undefined4 *)(param_11 + 0xc) = param_3;
  *(undefined4 *)(param_11 + 0x10) = param_4;
  *(undefined4 *)(param_11 + 0x14) = param_5;
  *(undefined4 *)(param_11 + 0x1c) = param_6;
  *(undefined4 *)(param_11 + 0x20) = param_7;
  *(undefined4 *)(param_11 + 0x24) = param_8;
  *(undefined4 *)(param_11 + 0x28) = param_9;
  *(undefined4 *)(param_11 + 0x2c) = param_10;
  FUN_43b03a2e(auStack_3c);
  iVar2 = thunk_FUN_43ad2ea8(&param_6,auStack_3c);
  if (iVar2 == 0) {
    FUN_43b03a3c(iVar1 + 0x30,DAT_44025aec);
  }
  else {
    FUN_43afb43a(&uStack_50,0);
    *(undefined4 *)(iVar1 + 0x30) = uStack_50;
    *(undefined4 *)(iVar1 + 0x34) = uStack_4c;
    *(undefined4 *)(iVar1 + 0x38) = uStack_48;
    *(undefined4 *)(iVar1 + 0x3c) = uStack_44;
    *(undefined4 *)(iVar1 + 0x40) = uStack_40;
  }
  return;
}

