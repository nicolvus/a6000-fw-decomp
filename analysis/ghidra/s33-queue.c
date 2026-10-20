/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43b04730" */

void FUN_43b04730(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  code *pcVar1;
  
  pcVar1 = *(code **)**(undefined4 **)(param_1 + 4);
  (*pcVar1)(*(undefined4 **)(param_1 + 4),param_1,param_3,pcVar1,param_4);
  return;
}


/* query "43b048cc" */

void FUN_43b048cc(int param_1)

{
  *(undefined1 *)(param_1 + 0x22) = 0;
  return;
}


/* query "43ae7558" */

undefined4 FUN_43ae7558(undefined4 param_1)

{
  FUN_43ae7542();
  return param_1;
}


/* query "437298e8" */

undefined4
FUN_437298e8(uint param_1,undefined4 param_2,int param_3,int param_4,int param_5,byte param_6,
            int param_7,byte param_8,uint *param_9,undefined4 *param_10)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  char *pcVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  int *piVar13;
  int *piVar14;
  int iVar15;
  char *pcVar16;
  undefined4 *puVar17;
  int iVar18;
  int iVar19;
  uint uVar20;
  int *piVar21;
  undefined8 uVar22;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined2 uStack_48;
  undefined2 uStack_46;
  int iStack_44;
  int iStack_40;
  int iStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 auStack_30 [4];
  undefined2 *apuStack_2c [2];
  
  uVar8 = (uint)param_6;
  uVar9 = (uint)param_8;
  iVar19 = param_3 * 0x100 + param_4;
  for (uVar11 = param_5 * 0x100 + iVar19 + uVar8; 3 < (uVar11 & 0xff); uVar11 = uVar11 + 0xfc) {
  }
  for (uVar12 = param_7 * 0x100 + iVar19 + uVar9; 3 < (uVar12 & 0xff); uVar12 = uVar12 + 0xfc) {
  }
  if (0x23 < param_1) {
    return 0;
  }
  if ((int)(uVar12 - uVar11) < 1) {
    return 0;
  }
  iVar2 = FUN_43729884(param_1,iVar19,uVar11);
  iVar18 = DAT_440223c4;
  if (iVar2 != 0) {
    return 0;
  }
  if ((param_1 == 4) && (*(char *)(DAT_440223c4 + 0xb1) != '\0')) {
    uVar3 = FUN_43ae9332(*(undefined4 *)(DAT_440223c4 + 0xbc));
    uVar4 = FUN_43ae9332(param_2);
    iVar2 = thunk_FUN_43b04570(uVar3,uVar4);
    if (iVar2 != 0) {
      FUN_43728dec(4,0);
    }
  }
  iVar2 = iVar18 + param_1 * 0x2c;
  if (*(char *)(iVar2 + 1) != '\0') goto LAB_4372a254;
  if (*(char *)(iVar2 + 0x1c) != '\0') {
    piVar21 = (int *)(param_1 * 0x2c + iVar18 + 0x20);
    iVar2 = 0;
    piVar14 = piVar21;
    iVar15 = 0;
    uVar20 = uVar12;
    while (iVar2 < (int)(uint)*(byte *)(iVar18 + param_1 * 0x2c + 0x1c)) {
      iVar5 = FUN_43729828(*piVar14,iVar19,param_1);
      piVar13 = piVar14 + 1;
      iVar2 = iVar2 + 1;
      uVar10 = *(uint *)(*piVar14 * 0x2c + iVar18 + 0x14);
      if ((int)uVar20 < (int)uVar10) {
        uVar20 = uVar10;
      }
      piVar14 = piVar13;
      if (iVar15 < iVar5) {
        iVar15 = iVar5;
      }
    }
    if (iVar15 == 1) {
      puVar17 = (undefined4 *)(iVar18 + param_1 * 0x2c + 0x1c);
      for (iVar19 = 0; iVar19 < (int)(uint)*(byte *)(param_1 * 0x2c + iVar18 + 0x1c);
          iVar19 = iVar19 + 1) {
        puVar17 = puVar17 + 1;
        FUN_43728974(*puVar17,param_1,uVar20);
      }
      return 0;
    }
    if (iVar15 != 3) {
      iVar19 = 0;
      if (iVar15 != 0) {
        return 0;
      }
      for (; iVar19 < (int)(uint)*(byte *)(param_1 * 0x2c + iVar18 + 0x1c); iVar19 = iVar19 + 1) {
        FUN_43728dec(*piVar21,0);
        FUN_43728994(*piVar21);
        piVar21 = piVar21 + 1;
      }
    }
  }
  iVar19 = DAT_4402546c;
  switch(param_1) {
  case 0:
    FUN_437287f0(0,*(undefined4 *)(DAT_4402546c + 0xf0),*(undefined4 *)(DAT_4402546c + 0xf4));
    uVar4 = DAT_44026b0c;
    uVar3 = DAT_44020394;
    puVar17 = DAT_4401f880;
    iVar2 = FUN_43acc844(0,0,iVar18 + 8,DAT_4401f880,DAT_44026b0c,DAT_44020394);
    if (iVar2 == 0) {
LAB_43729b86:
      iVar19 = FUN_4378f9c0();
      if (*(int *)(iVar19 + 0x2c) == 0) {
        iVar19 = FUN_4378f9c0();
        *(undefined4 *)(iVar19 + 0x2d0) = *puVar17;
        iVar19 = FUN_4378f9c0();
        FUN_439c5320(iVar19 + 0x2d4,uVar4,0x59c);
        iVar19 = FUN_4378f9c0();
        uVar4 = 0x305;
        iVar19 = iVar19 + 0x870;
        goto LAB_4372a1e6;
      }
      goto LAB_4372a214;
    }
    FUN_43728744(3,9,1,&DAT_43c9bd47,iVar2);
    pcVar16 = s_SyncResMgr__Get__MODE_EE_0___CAM_43c9bd5b;
    break;
  case 1:
    FUN_437287f0(0,*(undefined4 *)(DAT_4402546c + 0xf0),*(undefined4 *)(DAT_4402546c + 0xf4));
    uVar4 = DAT_44026b0c;
    uVar3 = DAT_44020394;
    puVar17 = DAT_4401f880;
    iVar2 = FUN_43acc844(0,1,iVar18 + 0x34,DAT_4401f880,DAT_44026b0c,DAT_44020394);
    if (iVar2 == 0) goto LAB_43729b86;
    FUN_43728744(3,9,1,&DAT_43c9bd8c,iVar2);
    pcVar16 = s_SyncResMgr__Get__MODE_EE_1___CAM_43c9bda0;
    break;
  case 2:
    FUN_437287f0(0,*(undefined4 *)(DAT_4402546c + 0xf0),*(undefined4 *)(DAT_4402546c + 0xf4));
    FUN_437287f0(1,*(undefined4 *)(iVar19 + 0xf8),*(undefined4 *)(iVar19 + 0xfc));
    FUN_437287f0(2,*(undefined4 *)(iVar19 + 0xf0),*(undefined4 *)(iVar19 + 0xf4));
    uVar4 = DAT_44026b0c;
    uVar3 = DAT_44020394;
    puVar17 = DAT_4401f880;
    iVar2 = FUN_43acc844(10,0,iVar18 + 0x60,DAT_4401f880,DAT_44026b0c,DAT_44020394);
    if (iVar2 == 0) {
      iVar2 = FUN_4378f9c0();
      if (*(int *)(iVar2 + 0x2c) == 0) {
        iVar2 = FUN_4378f9c0();
        *(undefined4 *)(iVar2 + 0x2d0) = *puVar17;
        iVar2 = FUN_4378f9c0();
        FUN_439c5320(iVar2 + 0x2d4,uVar4,0x59c);
        iVar2 = FUN_4378f9c0();
        FUN_439c5320(iVar2 + 0x870,uVar3,0x305);
      }
      if (*(char *)(iVar19 + 0x70) == '\0') {
        thunk_FUN_439f9860(apuStack_2c);
        puVar1 = apuStack_2c[0];
        if ((apuStack_2c[0] == (undefined2 *)0x0) &&
           (iVar19 = FUN_43b716aa(apuStack_2c), iVar19 != 0)) {
          apuStack_2c[0] = puVar1;
          FUN_43728744(3,9,1,&DAT_43c9be17,iVar19);
          FUN_43902718(s_SyncResMgr__Get__MODE_EE_01___ID_43c9be2b,iVar19);
        }
        if (apuStack_2c[0] != (undefined2 *)0x0) {
          FUN_436c4560(*puVar17,*apuStack_2c[0]);
        }
      }
      goto LAB_4372a214;
    }
    FUN_43728744(3,9,1,&DAT_43c9bdd1,iVar2);
    pcVar16 = s_SyncResMgr__Get__MODE_EE_01___CA_43c9bde5;
    break;
  default:
    pcVar16 = s_Resource_CamSyncResource_cpp_43c9b494;
    FUN_43728744(5,0,1,&DAT_43c9b47c,s_Resource_CamSyncResource_cpp_43c9b494,0x340);
    param_1 = 0x340;
    pcVar7 = s_FATAL___s__d_43c9b487;
LAB_4372a20e:
    FUN_43902718(pcVar7,pcVar16,param_1);
    return 0;
  case 4:
    uVar6 = FUN_43ae9332(param_2);
    uVar4 = DAT_44025df4;
    uVar3 = DAT_44021810;
    iVar2 = FUN_43795648(uVar6,iVar18 + 0xb8,DAT_44025df4,DAT_44021810);
    if (iVar2 == 0) {
      iVar19 = FUN_4378f9c0();
      if (*(int *)(iVar19 + 0x2c) != 0) goto LAB_4372a214;
      iVar19 = FUN_4378f9c0();
      FUN_439c5320(iVar19 + 0xb78,uVar4,0x100);
      iVar19 = FUN_4378f9c0();
      uVar4 = 0x70;
      iVar19 = iVar19 + 0xc78;
LAB_4372a1e6:
      FUN_439c5320(iVar19,uVar3,uVar4);
      goto LAB_4372a214;
    }
    FUN_43728744(3,9,1,&DAT_43c9c395,iVar2);
    pcVar16 = s_SyncResMgr__Get__IMAGER0__DFE_ER_43c9c3a9;
    break;
  case 5:
    goto switchD_43729a76_caseD_5;
  case 6:
    FUN_43ae9416();
    goto LAB_4372a214;
  case 7:
  case 0xd:
    if (param_1 == 7) {
      uVar8 = 0x10000;
    }
    else {
      uVar8 = 0x40000;
    }
    pcVar16 = (char *)FUN_43940e7c(uVar8 | 0x201,iVar18 + param_1 * 0x2c + 8,auStack_30);
    if (pcVar16 != (char *)0x0) {
      FUN_43728744(3,9,1,s__CAMERA_MAIN_SYNC___SyncResMgr___43c9be5e,pcVar16,param_1);
      pcVar7 = s__CAMERA_MAIN_SYNC___SyncResMgr___43c9be5e + 0x14;
      goto LAB_4372a20e;
    }
    iVar19 = FUN_43941b0c(*(undefined4 *)(iVar18 + param_1 * 0x2c + 8));
    if (iVar19 != 0) {
      FUN_43728744(3,9,1,&DAT_43c9bead,iVar19,param_1);
      pcVar16 = s_SyncResMgr__Get__RC_ERR_0x_02x_r_43c9bec1;
LAB_43729daa:
      FUN_43902718(pcVar16,iVar19,param_1);
    }
    goto LAB_4372a214;
  case 8:
  case 0xe:
    if (param_1 == 8) {
      uVar8 = 0x10000;
    }
    else {
      uVar8 = 0x40000;
    }
    pcVar16 = (char *)FUN_43940e7c(uVar8 | 0x226,iVar18 + param_1 * 0x2c + 8,auStack_30);
    if (pcVar16 != (char *)0x0) {
      FUN_43728744(3,9,1,s__CAMERA_MAIN_SYNC___SyncResMgr___43c9bef6,pcVar16,param_1);
      pcVar7 = s__CAMERA_MAIN_SYNC___SyncResMgr___43c9bef6 + 0x14;
      goto LAB_4372a20e;
    }
    iVar19 = FUN_43941528(*(undefined4 *)(iVar18 + param_1 * 0x2c + 8));
    if (iVar19 != 0) {
      FUN_43728744(3,9,1,&DAT_43c9bf44,iVar19,param_1);
      pcVar16 = s_SyncResMgr__Get__RC_ERR_0x_02x_r_43c9bf58;
      goto LAB_43729daa;
    }
    goto LAB_4372a214;
  case 9:
  case 0xf:
    if (param_1 == 9) {
      uVar8 = 0x10000;
    }
    else {
      uVar8 = 0x40000;
    }
    pcVar16 = (char *)FUN_43940e7c(uVar8 | 0x346,iVar18 + param_1 * 0x2c + 8,auStack_30);
    if (pcVar16 != (char *)0x0) {
      FUN_43728744(3,9,1,s__CAMERA_MAIN_SYNC___SyncResMgr___43c9bf8c,pcVar16,param_1);
      pcVar7 = s__CAMERA_MAIN_SYNC___SyncResMgr___43c9bf8c + 0x14;
      goto LAB_4372a20e;
    }
    iVar19 = FUN_439416d4(*(undefined4 *)(iVar18 + param_1 * 0x2c + 8));
    if (iVar19 != 0) {
      FUN_43728744(3,9,1,&DAT_43c9bfda,iVar19,param_1);
      pcVar16 = s_SyncResMgr__Get__RC_ERR_0x_02x_r_43c9bfee;
      goto LAB_43729daa;
    }
    goto LAB_4372a214;
  case 0x10:
  case 0x11:
    if (param_1 == 0x10) {
      uStack_6c = 1;
    }
    else {
      uStack_6c = 2;
    }
    uStack_64 = 1;
    uStack_68 = 3;
    uStack_60 = 1;
    uStack_58 = 1;
    uStack_5c = 1;
    uStack_54 = 1;
    iVar2 = FUN_439509e4(&uStack_6c,param_1 * 0x2c + iVar18 + 8);
    if (iVar2 == 0) goto LAB_4372a214;
    FUN_43728744(3,9,1,&DAT_43c9bc1b,iVar2);
    pcVar16 = s_SyncResMgr__Get__SPC_ERR_0x_02x_S_43c9bc2f;
    break;
  case 0x12:
  case 0x13:
    iVar2 = FUN_43957748(0xc,0,param_1 * 0x2c + iVar18 + 8);
    if (iVar2 == 0) goto LAB_4372a214;
    FUN_43728744(3,9,1,&DAT_43c9c06d,iVar2);
    pcVar16 = s_SyncResMgr__Get__VFX_ERR_CODE_0x_43c9c081;
    break;
  case 0x14:
  case 0x15:
    if (param_1 == 0x14) {
      uVar3 = 1;
    }
    else {
      uVar3 = 2;
    }
    iVar2 = FUN_436bd92c(iVar18 + param_1 * 0x2c + 8,uVar3,0);
    if (iVar2 == 0) {
      uStack_46 = 0;
      uStack_4c = 7;
      uStack_48 = 0x80;
      uStack_50 = 2;
      iStack_44 = iVar2;
      iStack_40 = iVar2;
      iStack_3c = iVar2;
      iVar19 = FUN_43acb8ae(*(undefined4 *)(iVar18 + param_1 * 0x2c + 8),0,&uStack_50);
      if (iVar19 != 0) {
        FUN_43728744(3,9,1,&DAT_43c9c112,iVar19);
        FUN_43902718(s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c126,iVar19);
      }
      uStack_50 = 2;
      iStack_3c = 1;
      iVar19 = FUN_43acb8ae(*(undefined4 *)(param_1 * 0x2c + iVar18 + 8),4,&uStack_50);
      if (iVar19 != 0) {
        FUN_43728744(3,9,1,&DAT_43c9c162,iVar19);
        FUN_43902718(s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c176,iVar19);
      }
      uStack_50 = 4;
      iStack_3c = 1;
      iVar19 = FUN_43acb8ae(*(undefined4 *)(param_1 * 0x2c + iVar18 + 8),9,&uStack_50);
      if (iVar19 != 0) {
        FUN_43728744(3,9,1,&DAT_43c9c1b2,iVar19);
        FUN_43902718(s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c1c6,iVar19);
      }
      uStack_50 = 4;
      iStack_3c = 1;
      iVar19 = FUN_43acb8ae(*(undefined4 *)(param_1 * 0x2c + iVar18 + 8),0xd,&uStack_50);
      if (iVar19 != 0) {
        FUN_43728744(3,9,1,&DAT_43c9c202,iVar19);
        FUN_43902718(s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c216,iVar19);
      }
      uStack_50 = 2;
      iStack_3c = 1;
      iVar19 = FUN_43acb8ae(*(undefined4 *)(param_1 * 0x2c + iVar18 + 8),10,&uStack_50);
      if (iVar19 != 0) {
        FUN_43728744(3,9,1,&DAT_43c9c252,iVar19);
        FUN_43902718(s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c266,iVar19);
      }
      uStack_50 = 4;
      iStack_3c = 1;
      iVar19 = FUN_43acb8ae(*(undefined4 *)(param_1 * 0x2c + iVar18 + 8),0xb,&uStack_50);
      if (iVar19 != 0) {
        FUN_43728744(3,9,1,&DAT_43c9c2a6,iVar19);
        FUN_43902718(s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c2ba,iVar19);
      }
      goto LAB_4372a214;
    }
    FUN_43728744(3,9,1,&DAT_43c9c0c7,iVar2);
    pcVar16 = s_SyncResMgr__Get__APL_ERR_0x_02x_a_43c9c0db;
    break;
  case 0x16:
    iVar19 = FUN_43728d78(0x18);
    if (iVar19 == 0) {
      uStack_38 = 0;
      uStack_34 = 0;
      iVar19 = FUN_437298e8(0x18,0,param_3,param_4,param_5,uVar8,param_7,uVar9,&uStack_38,0);
      if (iVar19 == 0) {
        return 0;
      }
    }
    if ((*(char *)(DAT_4402546c + 0x70) == '\0') && (iVar19 = FUN_439e2888(), iVar19 != 0)) {
      FUN_43728744(3,9,1,&DAT_43c9c2fc);
      FUN_43902718(s_SyncResMgr__Get__IDT_OPD_TOP_Syn_43c9c310);
      return 0;
    }
    goto LAB_4372a214;
  case 0x17:
    iVar19 = FUN_43728d78(0x18);
    if (iVar19 == 0) {
      uStack_38 = 0;
      uStack_34 = 0;
      iVar19 = FUN_437298e8(0x18,0,param_3,param_4,param_5,uVar8,param_7,uVar9,&uStack_38,0);
      if (iVar19 == 0) {
        return 0;
      }
    }
    if (*(char *)(DAT_4402546c + 0x70) == '\0') {
      FUN_439ce840();
      FUN_439d8520();
    }
    goto LAB_4372a214;
  case 0x18:
    if (*(char *)(DAT_4402546c + 0x70) == '\0') {
      FUN_439fd6ac(2);
    }
    goto LAB_4372a214;
  case 0x19:
    iVar2 = FUN_43940e7c(0x101,iVar18 + 0x454,auStack_30);
    if (iVar2 == 0) goto LAB_4372a214;
    FUN_43728744(3,9,1,&DAT_43c9c021,iVar2);
    pcVar16 = s_SyncResMgr__Get__RC_ERR_0x_02x_r_43c9c035;
    break;
  case 0x1b:
  case 0x1c:
  case 0x1d:
  case 0x1e:
  case 0x1f:
  case 0x20:
  case 0x21:
  case 0x22:
  case 0x23:
    iVar19 = FUN_4390b270(param_2);
    iVar15 = param_1 * 0x2c + iVar18;
    *(int *)(iVar15 + 8) = iVar19;
    iVar2 = FUN_43b2e084();
    if ((iVar2 <= iVar19) || (*(int *)(iVar15 + 8) < 0)) {
      iVar18 = param_1 * 0x2c + iVar18;
      FUN_43728744(3,9,1,&DAT_43c9c344,*(undefined4 *)(iVar18 + 8),param_1);
      pcVar16 = *(char **)(iVar18 + 8);
      pcVar7 = s_SyncResMgr__Get__PBL_IIB_PORT_0x_43c9c358;
      goto LAB_4372a20e;
    }
    FUN_43728814(param_1);
LAB_4372a214:
    iVar19 = param_1 * 0x2c + iVar18;
    *(undefined4 *)(iVar19 + 4) = 0xff;
    *(undefined1 *)(iVar19 + 1) = 1;
    *(undefined4 *)(iVar19 + 0x18) = 0;
    *(undefined4 *)(iVar19 + 0xc) = param_2;
    iVar19 = FUN_437286f4(param_1);
    if (iVar19 != 0) {
      uVar3 = FUN_43728718(param_1);
      FUN_43728744(3,9,1,&DAT_43c9c3d2,uVar3);
      FUN_43902718(s_SyncResMgr__Get___s__43c9c3e6,uVar3);
    }
LAB_4372a254:
    uVar22 = FUN_439caf08(1,0,param_1);
    iVar18 = param_1 * 0x2c + iVar18;
    *param_9 = *param_9 | (uint)uVar22;
    param_9[1] = param_9[1] | (uint)((ulonglong)uVar22 >> 0x20);
    *(uint *)(iVar18 + 0x10) = uVar11;
    *(uint *)(iVar18 + 0x14) = uVar12;
    if (param_10 != (undefined4 *)0x0) {
      *param_10 = *(undefined4 *)(iVar18 + 8);
    }
    return 1;
  }
  FUN_43902718(pcVar16,iVar2);
switchD_43729a76_caseD_5:
  return 0;
}


/* query "43b0404a" */

void FUN_43b0404a(undefined4 param_1,uint param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((param_3 == 0) ||
     ((((((param_2 & 1) == 0 || (iVar1 = FUN_43799a38(param_1,5,param_4,0), iVar1 == 0)) &&
        (((param_2 & 2) == 0 || (iVar1 = FUN_43799a38(param_1,9,param_4,0), iVar1 == 0)))) &&
       (((param_2 & 4) == 0 || (iVar1 = FUN_43799a38(param_1,10,param_4,0), iVar1 == 0)))) &&
      (((param_2 & 8) == 0 || (iVar1 = FUN_43799a38(param_1,7,param_4,0), iVar1 == 0)))))) {
    if ((param_2 & 1) != 0) {
      FUN_43799b74(param_1,5);
    }
    if ((param_2 & 4) != 0) {
      FUN_43799b74(param_1,10);
    }
    if ((param_2 & 8) != 0) {
      FUN_43799b74(param_1,7);
    }
    if ((param_2 & 2) != 0) {
      FUN_43799b74(param_1,9);
      FUN_43799b74(param_1,0x11);
    }
    if ((param_2 & 4) != 0) {
      FUN_43799b74(param_1,0x14);
    }
    if ((param_2 & 8) != 0) {
      FUN_43799b74(param_1,0x12);
      return;
    }
  }
  return;
}

