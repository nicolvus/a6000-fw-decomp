/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "4379704c" */

void FUN_4379704c(int param_1,undefined4 *param_2,undefined4 param_3)

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
  FUN_43ae98d0(&DAT_43e9d7a8,&uStack_34);
  return;
}


/* query "43797090" */

void FUN_43797090(int param_1,undefined4 *param_2,undefined4 param_3)

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
  FUN_43ae98d0(&DAT_43e9d7e4,&uStack_34);
  return;
}


/* query "437970d4" */

void FUN_437970d4(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined1 auStack_3c [24];
  
  FUN_43ae97cc(&DAT_43e9d860);
  FUN_43ae9818(&DAT_43e9dd2c);
  FUN_43acac1a(auStack_3c,DAT_4402005c);
  FUN_43acac02(&DAT_43e9d790,0x47,auStack_3c);
  FUN_436e7d74(&DAT_43e9d76c,0x48,0x24);
  FUN_436e7d74(&DAT_43e9d7b8,0x6b,0x24);
  FUN_436e7d74(&DAT_43e9d844,0x72,0x38);
  FUN_436e7d74(&DAT_43e9dd08,0x66,0x38);
  FUN_436e7d74(&DAT_43e9ddf8,0x67,0x38);
  FUN_436e7d74(&DAT_43e9d74c,0x49,0x25);
  FUN_436e7d74(&DAT_43e9d724,0x4a,0x25);
  FUN_436e7d74(&DAT_43e9d7f4,0x4b,0x25);
  FUN_436e7d74(&DAT_43e9d824,0x4c,0x25);
  FUN_436e7d74(&DAT_43e9dcec,0x73,0x25);
  FUN_4379669c(&DAT_43e9de14,&DAT_43e9dd2c);
  uVar1 = DAT_44025794;
  uVar2 = DAT_440254cc;
  FUN_439b4244(&DAT_43e9de14,DAT_44025794,DAT_440254cc);
  FUN_4379669c(&DAT_43e9d810,&DAT_43e9dd2c);
  FUN_439b4244(&DAT_43e9d810,uVar1,uVar2);
  FUN_43796400(&DAT_43e9d788,&DAT_43e9d76c);
  FUN_43796400(&DAT_43e9d71c,&DAT_43e9d844);
  FUN_43796400(&DAT_43e9dd24,&DAT_43e9d74c);
  FUN_43ae96c4(&DAT_43e9d7e4,&DAT_43e9d860);
  uVar1 = DAT_440223c0;
  FUN_439b4244(&DAT_43e9d7e4,DAT_440223c0,uVar2);
  FUN_43ae96c4(&DAT_43e9d7a8,&DAT_43e9d860);
  FUN_439b4244(&DAT_43e9d7a8,uVar1,uVar2);
  FUN_43ae96c4(&DAT_43e9d7d4,&DAT_43e9d860);
  FUN_439b4244(&DAT_43e9d7d4,uVar1,uVar2);
  return;
}


/* query "43796522" */

int s32_candidate_43796522(void)

{
  uint uVar1;
  int iVar2;
  
  FUN_43b2a162(&DAT_43e9d790);
  FUN_43b2a162(&DAT_43e9d76c);
  FUN_43b2a162(&DAT_43e9d7b8);
  FUN_43b2a162(&DAT_43e9d844);
  FUN_43b2a162(&DAT_43e9dd08);
  FUN_43b2a162(&DAT_43e9ddf8);
  FUN_43b2a162(&DAT_43e9d74c);
  FUN_43b2a162(&DAT_43e9d724);
  FUN_43b2a162(&DAT_43e9d7f4);
  FUN_43b2a162(&DAT_43e9d824);
  uVar1 = FUN_43560bb0(uRam43e9dd00,&DAT_43e9dcec);
  iVar2 = 1 - uVar1;
  if (1 < uVar1) {
    iVar2 = 0;
  }
  return iVar2;
}


/* query "43ae9774" */

void FUN_43ae9774(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined8 uStack_10;
  
  FUN_43796770();
  uStack_10 = FUN_4379671c();
  iVar3 = (int)&uStack_10 + 4;
  FUN_43ae96d4(iVar3,0);
  uVar1 = FUN_43ae96e0(&DAT_43e9d7d4);
  uStack_10._4_4_ = uVar1;
  while( true ) {
    uStack_10._0_4_ = FUN_43ae96f0(&DAT_43e9d7d4);
    iVar2 = FUN_43ae968e(iVar3,&uStack_10);
    if (iVar2 == 0) break;
    iVar2 = FUN_43ae969a(iVar3);
    if (*(int **)(iVar2 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar2 + 0x18) + 0xc))();
    }
    FUN_43ae9708(iVar3);
  }
  FUN_43ae973c(&DAT_43e9d7d4);
  return;
}


/* query "43ae9888" */

undefined4 * FUN_43ae9888(int param_1,undefined4 *param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *puStack_1c;
  
  iVar5 = param_1;
  puStack_1c = param_2;
  iVar1 = FUN_43ae982a(*(undefined4 *)(param_1 + 0xc));
  if (iVar1 == 0) {
    puStack_1c = (undefined4 *)FUN_43ae9878(param_1);
  }
  else {
    uVar2 = param_3[1];
    uVar3 = param_3[2];
    uVar4 = param_3[3];
    *(undefined4 *)(iVar1 + 8) = *param_3;
    *(undefined4 *)(iVar1 + 0xc) = uVar2;
    *(undefined4 *)(iVar1 + 0x10) = uVar3;
    *(undefined4 *)(iVar1 + 0x14) = uVar4;
    uVar2 = param_3[5];
    uVar3 = param_3[6];
    *(undefined4 *)(iVar1 + 0x18) = param_3[4];
    *(undefined4 *)(iVar1 + 0x1c) = uVar2;
    *(undefined4 *)(iVar1 + 0x20) = uVar3;
    FUN_43ae984c(param_1,*param_2,iVar1,uVar4,iVar5);
    FUN_43ae96d4(&puStack_1c,iVar1);
  }
  return puStack_1c;
}


/* query "43ae98d0" */

void FUN_43ae98d0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_14 = param_2;
  uStack_10 = param_3;
  uStack_14 = FUN_43ae96f0();
  FUN_43ae9888(param_1,&uStack_14,param_2);
  return;
}


/* query "43797b60" */

undefined4 FUN_43797b60(undefined4 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_128 [272];
  
  FUN_435a92e0(auStack_128);
  iVar1 = FUN_43a49628(auStack_128,param_4);
  iVar2 = FUN_435a941c(auStack_128,param_4);
  iVar3 = FUN_435a9460(auStack_128,param_2,param_3);
  iVar4 = FUN_435aa20c(&DAT_43e9df50,param_1,auStack_128);
  uVar5 = 0;
  if (((iVar2 != 0 || iVar1 != 0) || iVar3 != 0) || iVar4 != 0) {
    uVar5 = 0xffffffff;
  }
  FUN_435a92c8(auStack_128);
  return uVar5;
}


/* query "4379744c" */

void FUN_4379744c(void)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined4 *puVar9;
  undefined1 auStack_2c0 [272];
  undefined1 auStack_1b0 [272];
  short sStack_a0;
  ushort uStack_9e;
  int iStack_98;
  int iStack_94;
  int iStack_90;
  int iStack_88;
  int iStack_84;
  int iStack_80;
  undefined1 auStack_50 [8];
  int iStack_48;
  int iStack_44;
  int iStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  FUN_435a92e0(auStack_1b0);
LAB_4379745e:
  while (iVar1 = FUN_435a9f4c(&DAT_43e9ded4,0x50004,auStack_1b0,0xffffffff), iVar1 != 0) {
    FUN_43797298(3,9,1,&DAT_43ca3f25,iVar1);
    FUN_43902718(s_PIN_msg_rcv_err_0x_02x__43ca3f39,iVar1);
  }
  iVar1 = FUN_435a93e8(auStack_1b0,&uStack_1c);
  if (iVar1 == 0) goto LAB_437974b4;
  FUN_43797298(3,9,1,&DAT_43ca3f51,iVar1);
  pcVar2 = s_PIN_msg_replyId_err_0x_02x__43ca3f65;
LAB_437974ae:
  FUN_43902718(pcVar2,iVar1);
LAB_437974b4:
  do {
    iVar3 = FUN_435a9348(auStack_1b0,&sStack_a0,0x50);
    uVar8 = uStack_1c;
    iVar1 = DAT_44025f2c;
    if (iVar3 == -0x1b) goto LAB_4379745e;
    if (iVar3 != 0) {
      FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x104);
      FUN_43902718(s_FATAL___s__d_43c9b487,s_InfraImaging_cpp_43ca3fd6,0x104);
      if (iVar3 == -0x1b) goto LAB_4379745e;
      goto LAB_437974b4;
    }
  } while (sStack_a0 != 0x1000);
  if (uStack_9e == 0x100) goto LAB_437978ae;
  if (uStack_9e < 0x101) {
    if (uStack_9e == 1) {
      puVar9 = (undefined4 *)(DAT_44025f2c + -4);
      iVar3 = 0;
      do {
        puVar9 = puVar9 + 1;
        FUN_43a49986(*puVar9,&iStack_30);
        if (((iStack_98 == iStack_30) && (iStack_94 == iStack_2c)) && (iStack_90 == iStack_28)) {
          iVar1 = FUN_435a9b30(*(undefined4 *)(iVar1 + iVar3 * 4),&sStack_a0,uVar8);
          FUN_43901a8c(4,0x201d,1,iVar1);
          if ((iVar1 + 0x19U < 0x1a) && ((1 << (iVar1 + 0x19U & 0xff) & 0x2000003U) != 0))
          goto LAB_437974b4;
          FUN_43797298(3,9,1,&DAT_43ca3fa9,iVar1);
          pcVar2 = s_REQ_CONNETCT_err_0x_02x__43ca3fbd;
          goto LAB_437974ae;
        }
        iVar3 = iVar3 + 1;
      } while (iVar3 != 5);
      FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x16d);
      uVar8 = 0x16d;
      goto LAB_4379795c;
    }
    if (uStack_9e == 0) {
      FUN_43a3b970(auStack_50);
      iVar3 = DAT_44025f2c;
      puVar9 = (undefined4 *)(DAT_44025f2c + -4);
      iVar1 = 0;
      do {
        puVar9 = puVar9 + 1;
        FUN_43a49986(*puVar9,&iStack_30);
        if (((iStack_98 == iStack_30) && (iStack_94 == iStack_2c)) && (iStack_90 == iStack_28)) {
          FUN_43a49980(*(undefined4 *)(iVar3 + iVar1 * 4),&uStack_20);
          iStack_48 = iStack_30;
          iStack_44 = iStack_2c;
          iStack_40 = iStack_28;
          uStack_3c = uStack_20;
          uStack_34 = 0;
          goto LAB_4379756a;
        }
        iVar1 = iVar1 + 1;
      } while (iVar1 != 5);
      uStack_34 = 0xffffffe0;
LAB_4379756a:
      uStack_38 = 0x50004;
      FUN_435a92e0(auStack_2c0);
      uVar4 = FUN_435a9460(auStack_2c0,auStack_50,0x20);
      uVar5 = FUN_435a941c(auStack_2c0,0x50004);
      uVar6 = FUN_43a49628(auStack_2c0,0x50004);
      uVar7 = FUN_435aa20c(&DAT_43e9df50,uVar8,auStack_2c0);
      uVar7 = uVar5 | uVar4 | uVar6 | uVar7;
      FUN_43901a8c(4,0x201d,0,uVar7);
      if (uVar7 != 0) {
        FUN_43797298(3,9,1,&DAT_43ca3f81,uVar7);
        FUN_43902718(s_PIN_GET_err_0x_02x__43ca3f95,uVar7);
      }
      FUN_435a92c8(auStack_2c0);
      goto LAB_437974b4;
    }
    if (uStack_9e == 2) {
      puVar9 = (undefined4 *)(DAT_44025f2c + -4);
      iVar3 = 0;
      do {
        puVar9 = puVar9 + 1;
        FUN_43a49986(*puVar9,&iStack_30);
        if (((iStack_98 == iStack_30) && (iStack_94 == iStack_2c)) && (iStack_90 == iStack_28)) {
          iVar1 = FUN_435a9830(*(undefined4 *)(iVar1 + iVar3 * 4),&sStack_a0,uVar8);
          FUN_43901a8c(4,0x201e,2,iVar1);
          if ((iVar1 + 0x1aU < 0x1b) && ((1 << (iVar1 + 0x1aU & 0xff) & 0x4000005U) != 0))
          goto LAB_437974b4;
          FUN_43797298(3,9,1,&DAT_43ca4015,iVar1);
          pcVar2 = s_REQ_DISCONNETCT_err_0x_02x__43ca4029;
          goto LAB_437974ae;
        }
        iVar3 = iVar3 + 1;
      } while (iVar3 != 5);
      FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x1ae);
      uVar8 = 0x1ae;
    }
    else {
LAB_43797936:
      FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x216);
      uVar8 = 0x216;
    }
  }
  else if (uStack_9e == 0x8100) {
    puVar9 = (undefined4 *)(DAT_44025f2c + -4);
    iVar3 = 0;
    do {
      puVar9 = puVar9 + 1;
      FUN_43a49986(*puVar9,&iStack_30);
      if (((iStack_98 == iStack_30) && (iStack_94 == iStack_2c)) && (iStack_90 == iStack_28)) {
        iVar1 = FUN_43a4975e(*(undefined4 *)(iVar1 + iVar3 * 4),&sStack_a0);
        FUN_43901a8c(4,0x201d,0x8100,iVar1);
        if (iVar1 == 0) goto LAB_437974b4;
        FUN_43797298(3,9,1,&DAT_43ca3fe7,iVar1);
        pcVar2 = s_CONNETCT_COMP_err_0x_02x__43ca3ffb;
        goto LAB_437974ae;
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 != 5);
    FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x18a);
    uVar8 = 0x18a;
  }
  else if (uStack_9e == 0x8101) {
    puVar9 = (undefined4 *)(DAT_44025f2c + -4);
    iVar3 = 0;
    do {
      puVar9 = puVar9 + 1;
      FUN_43a49986(*puVar9,&iStack_30);
      if (((iStack_98 == iStack_30) && (iStack_94 == iStack_2c)) && (iStack_90 == iStack_28)) {
        iVar1 = FUN_43a498ea(*(undefined4 *)(iVar1 + iVar3 * 4),&sStack_a0);
        FUN_43901a8c(4,0x201e,0x8101,iVar1);
        if (iVar1 == 0) goto LAB_437974b4;
        FUN_43797298(3,9,1,&DAT_43ca4071,iVar1);
        pcVar2 = s_DISCONNETCT_COMP_err_0x_02x__43ca4085;
        goto LAB_437974ae;
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 != 5);
    FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x1ed);
    uVar8 = 0x1ed;
  }
  else {
    if (uStack_9e != 0x101) goto LAB_43797936;
    puVar9 = (undefined4 *)(DAT_44025f2c + -4);
    iVar3 = 0;
    do {
      puVar9 = puVar9 + 1;
      FUN_43a49986(*puVar9,&iStack_30);
      if (((iStack_88 == iStack_30) && (iStack_84 == iStack_2c)) && (iStack_80 == iStack_28)) {
        iVar1 = FUN_43a497ec(*(undefined4 *)(iVar1 + iVar3 * 4),&sStack_a0);
        FUN_43901a8c(4,0x201e,0x101,iVar1);
        if ((iVar1 + 0x1aU < 0x1b) && ((1 << (iVar1 + 0x1aU & 0xff) & 0x4000005U) != 0))
        goto LAB_437974b4;
        FUN_43797298(3,9,1,&DAT_43ca4045,iVar1);
        pcVar2 = s_DISCONNETCT_err_0x_02x__43ca4059;
        goto LAB_437974ae;
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 != 5);
    FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x1d1);
    uVar8 = 0x1d1;
  }
  goto LAB_4379795c;
LAB_437978ae:
  puVar9 = (undefined4 *)(DAT_44025f2c + -4);
  iVar3 = 0;
  do {
    puVar9 = puVar9 + 1;
    FUN_43a49986(*puVar9,&iStack_30);
    if (((iStack_88 == iStack_30) && (iStack_84 == iStack_2c)) && (iStack_80 == iStack_28)) {
      iVar1 = FUN_43a499b2(*(undefined4 *)(iVar1 + iVar3 * 4),&sStack_a0);
      FUN_43901a8c(4,0x201d,0x100,iVar1);
      if ((iVar1 + 0x19U < 0x1a) && ((1 << (iVar1 + 0x19U & 0xff) & 0x2000003U) != 0))
      goto LAB_437974b4;
      FUN_43797298(3,9,1,&DAT_43ca40a2,iVar1);
      pcVar2 = s_CONNECT_err_0x_02x__43ca40b6;
      goto LAB_437974ae;
    }
    iVar3 = iVar3 + 1;
  } while (iVar3 != 5);
  FUN_43797298(5,0,1,&DAT_43c9b47c,s_InfraImaging_cpp_43ca3fd6,0x210);
  uVar8 = 0x210;
LAB_4379795c:
  FUN_43902718(s_FATAL___s__d_43c9b487,s_InfraImaging_cpp_43ca3fd6,uVar8);
  goto LAB_437974b4;
}


/* query "43797bcc" */

undefined4
FUN_43797bcc(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4,
            undefined4 param_5)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 auStack_120 [272];
  
  FUN_435a92e0(auStack_120);
  iVar1 = FUN_435a9f4c(&DAT_43e9ded4,param_4,auStack_120,param_5);
  if (iVar1 == 0) {
    uVar2 = FUN_43a49650(auStack_120);
    if (param_3 == uVar2) {
      iVar1 = FUN_435a9348(auStack_120,param_2,param_3 & 0xffff);
      if (iVar1 == -0x1b) {
        uVar3 = 0xfffffffb;
      }
      else {
        uVar3 = 0;
      }
    }
    else {
      uVar3 = 0xfffffffd;
    }
  }
  else {
    uVar3 = 0xfffffffe;
  }
  FUN_435a92c8(auStack_120);
  return uVar3;
}


/* query "43e9de64" */

/* query "43e9de9c" */

/* query "43e9dee0" */

/* query "43e9df18" */
