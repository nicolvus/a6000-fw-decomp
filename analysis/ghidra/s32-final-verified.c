/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43ad6034" */

void FUN_43ad6034(int *param_1)

{
  int iVar1;
  code *pcVar2;
  
  iVar1 = param_1[1] >> 1;
  if ((param_1[1] & 1U) == 0) {
    pcVar2 = (code *)*param_1;
  }
  else {
    pcVar2 = *(code **)(*(int *)((int)param_1 + iVar1) + *param_1);
  }
  (*pcVar2)((int)param_1 + iVar1);
  return;
}


/* query "43ad6052" */

void thunk_FUN_43ad6034(int *param_1)

{
  int iVar1;
  code *pcVar2;
  
  iVar1 = param_1[1] >> 1;
  if ((param_1[1] & 1U) == 0) {
    pcVar2 = (code *)*param_1;
  }
  else {
    pcVar2 = *(code **)(*(int *)((int)param_1 + iVar1) + *param_1);
  }
  (*pcVar2)((int)param_1 + iVar1);
  return;
}


/* query "43b03a48" */

void FUN_43b03a48(int param_1,undefined4 param_2)

{
  (**(code **)(param_1 + 8))(param_2);
  return;
}


/* query "4380f5b4" */

void FUN_4380f5b4(undefined4 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  FUN_43acabf4();
  uVar1 = DAT_44023940;
  param_1[2] = param_2;
  *param_1 = uVar1;
  param_1[1] = 0;
  return;
}


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


/* query "437968b0" */

void FUN_437968b0(undefined4 param_1,undefined4 param_2)

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
    thunk_FUN_43ad6034(iVar1,*(undefined4 *)(iVar1 + 0x14));
    iVar1 = FUN_43ae969a(&uStack_c);
    if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
    }
    FUN_43ae9708(&uStack_c);
  }
  FUN_43ae973c(&DAT_43e9d7a8);
  return;
}


/* query "437967e8" */

void FUN_437967e8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_1;
  uStack_c = param_2;
  FUN_43ae96d4(&uStack_c,0);
  uStack_c = FUN_43ae96e0(&DAT_43e9d7e4);
  while( true ) {
    uStack_10 = FUN_43ae96f0(&DAT_43e9d7e4);
    iVar1 = FUN_43ae968e(&uStack_c,&uStack_10);
    if (iVar1 == 0) break;
    iVar1 = FUN_43ae969a(&uStack_c);
    thunk_FUN_43ad6034(iVar1,*(undefined4 *)(iVar1 + 0x14));
    iVar1 = FUN_43ae969a(&uStack_c);
    if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
    }
    FUN_43ae9708(&uStack_c);
  }
  FUN_43ae973c(&DAT_43e9d7e4);
  return;
}


/* query "43796954" */

undefined2 FUN_43796954(int param_1,int param_2,int *param_3)

{
  byte bVar1;
  int iVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  char cVar8;
  undefined2 *puVar9;
  byte bVar10;
  bool bVar11;
  undefined1 auStack_3c [24];
  
  uVar4 = FUN_43799f3c();
  if ((*(short *)*param_3 == 0x138) || (*(short *)*param_3 == 0x144)) {
    iVar5 = FUN_43799f88(uVar4,1);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,1);
    }
    iVar5 = FUN_43799f88(uVar4,0);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,0);
    }
    iVar5 = FUN_43799f88(uVar4,4);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,4);
    }
    iVar5 = FUN_43799f88(uVar4,5);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,5);
    }
  }
  if (((*(byte *)(param_3[2] + 0x268) & 2) == 0) || (iVar5 = FUN_43ae916c(), iVar5 != 0)) {
    bVar11 = false;
  }
  else {
    bVar11 = true;
  }
  iVar5 = param_3[2];
  bVar1 = *(byte *)(iVar5 + 0x268);
  bVar10 = bVar1 & 2;
  if ((bVar1 & 2) != 0) {
    if ((*(ushort *)(iVar5 + 0x264) & 0x1c0) == 0) {
      bVar10 = *(int *)(iVar5 + 0x1c) == 4;
    }
    else {
      bVar10 = 0;
    }
  }
  if (((bVar1 & 4) == 0) || (iVar5 = FUN_43ae916c(), iVar5 != 0)) {
    iVar5 = 0;
  }
  else {
    iVar5 = 1;
  }
  iVar2 = DAT_4402546c;
  if (((*(char *)(DAT_4402546c + 0x4a) != '\0') && (*(int *)(*param_3 + 0xb8) == 1)) &&
     (*(int *)(*param_3 + 0xb4) - 1U < 2)) {
    if (bVar11 != false) {
      bVar11 = (*(byte *)(param_3[2] + 0x220) & 3) == 2;
    }
    if ((iVar5 != 0) && ((*(byte *)(param_3[2] + 0x220) & 5) != 4)) {
      iVar5 = 0;
    }
  }
  iVar6 = FUN_437286bc();
  bVar1 = *(byte *)(iVar2 + 10);
  if (iVar6 == 0) {
    bVar11 = false;
  }
  if ((bVar1 & 1) == 0) {
    if ((bVar1 & 2) != 0) {
      bVar11 = true;
    }
  }
  else {
    bVar11 = false;
  }
  if ((bVar1 & 4) == 0) {
    if ((bVar1 & 8) != 0) {
      bVar10 = 1;
    }
  }
  else {
    bVar10 = 0;
  }
  if ((bVar1 & 0xf0) == 0x10) {
    iVar5 = 0;
  }
  else if ((bVar1 & 0xf0) == 0x20) {
    iVar5 = 1;
  }
  iVar6 = FUN_43ae916c();
  if (iVar6 == 0) {
    FUN_4379bb68(0,bVar11);
    FUN_4379bb68(1,iVar5);
    FUN_4379bb68(2,iVar5);
    FUN_4379bb68(3,bVar10);
  }
  if (param_1 == 0) {
    iVar5 = FUN_437999e4(1,1);
    if (((iVar5 != 0) || (iVar5 = FUN_437999e4(1,2), iVar5 != 0)) &&
       ((iVar5 = FUN_43ae8c4a(DAT_43e9d744 + 1), iVar5 == *(int *)param_3[1] &&
        (((DAT_43e9d768 != iVar5 && (iVar5 = FUN_43794a44(param_3), iVar5 == 0)) &&
         (*(int *)(param_3[2] + 0xd8) != 1)))))) {
      FUN_437961d8(3,9,1,&DAT_43ca3e70,*(undefined4 *)param_3[1],((undefined4 *)param_3[1])[2],
                   DAT_43e9d768,DAT_43e9d740);
      FUN_43902718(s_Lost_CAMOUT_V_now_vfc__d_frc__d__43ca3e84,*(undefined4 *)param_3[1],
                   ((undefined4 *)param_3[1])[2],DAT_43e9d768,DAT_43e9d740);
      FUN_437964d4();
    }
  }
  else if ((*(byte *)(param_3[2] + 0x268) & 8) == 0) {
    FUN_43b04914(&DAT_43e9de14);
  }
  if (*(int *)(param_3[2] + 0x2c) != 0) {
    FUN_43796284(param_3 + 2,param_1);
  }
  iVar5 = FUN_43798414();
  if (((iVar5 != 0) && (*(int *)(param_3[2] + 0x2c) != 0)) &&
     (iVar5 = FUN_437999e4(1,5), iVar5 != 0)) {
    FUN_43b0417e(1,0xffffffff,0,0);
    FUN_43b0417e(2,0xffffffff,0,0);
    FUN_437961d8(3,9,1,&DAT_43ca3ebd);
    FUN_43902718(s_RCV_overflow_VD_Seq_Refresh__43ca3ed1);
  }
  iVar5 = FUN_43798434();
  if (((iVar5 != 0) && (*(int *)(param_3[2] + 0x2c) != 0)) &&
     (iVar5 = FUN_437999e4(1,0xb), iVar5 != 0)) {
    FUN_43b0419c(0,0);
    FUN_437961d8(3,9,1,&DAT_43ca3eee);
    FUN_43902718(s_SDVGA_SRC_overflow_VD_Seq_Refres_43ca3f02);
  }
  if (param_2 != 0) {
    if (*(int *)(param_3[2] + 0x44) != 0x11) {
      FUN_43ae9786(auStack_3c,DAT_44022a88);
      FUN_43796910(0,auStack_3c,param_3[2] + 0xb8);
      FUN_43795b10();
    }
    uVar7 = FUN_4380d708(param_2 + 0x18,param_2 + 0x2c,0);
    iVar5 = FUN_4381bd4c(param_2,uVar7,(uint)*(byte *)(param_3[2] + 0x30) << 8);
    if (iVar5 != 0) {
      FUN_43b04730();
    }
  }
  FUN_4381bf38(&DAT_43e9de14);
  FUN_43797410();
  iVar5 = FUN_4379742c();
  if (iVar5 != 0) {
    FUN_4372a540(7);
  }
  iVar5 = FUN_43ae916c();
  if (iVar5 == 0) {
    FUN_4379bb90(param_3);
  }
  puVar9 = (undefined2 *)*param_3;
  uVar3 = *puVar9;
  switch(uVar3) {
  case 0x100:
  case 0x101:
  case 0x10e:
  case 0x110:
  case 0x14a:
    goto switchD_43796ca8_caseD_100;
  default:
    if ((*(char *)(param_3[2] + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) {
      return uVar3;
    }
    break;
  case 0x104:
  case 0x141:
    iVar5 = FUN_437284b4();
    goto LAB_43796f38;
  case 0x105:
  case 0x106:
    if (((*(char *)(param_3[2] + 0x1ed) != '\0') &&
        (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) &&
       ((iVar5 = FUN_43ae916c(), iVar5 == 0 || (iVar5 = FUN_43795b04(), iVar5 != 0)))) {
      puVar9 = (undefined2 *)*param_3;
      if ((*(int *)(puVar9 + 0x5a) == 2) &&
         (iVar5 = param_3[2], (ushort)(*(short *)(iVar5 + 0x224) - 0x100U) < 2)) goto LAB_43796ea8;
      goto LAB_43796fc0;
    }
    break;
  case 0x10d:
  case 0x132:
    iVar5 = FUN_437fe4f4();
    if ((iVar5 == 0) && (*(char *)(param_3[2] + 0x1ed) != '\0')) {
      bVar11 = *(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4);
      goto LAB_43796fbc;
    }
    break;
  case 0x10f:
    if (*(int *)(puVar9 + 0x5a) != 2) {
      if (*(int *)(param_3[1] + 0x40) == 2) {
        return 0x10f;
      }
      break;
    }
    iVar5 = param_3[2];
    if (*(char *)(iVar5 + 0x23c) != '\0') {
      return 0x10f;
    }
    goto LAB_43796fda;
  case 0x112:
    iVar5 = FUN_437fe50c();
    goto LAB_43796f38;
  case 0x121:
    iVar5 = FUN_4379ada0();
    bVar11 = iVar5 == 7;
    goto LAB_43796fbc;
  case 0x123:
  case 0x128:
    iVar5 = FUN_4379ad7c();
    if (iVar5 == 0) {
LAB_43796dae:
      FUN_4379a898();
      iVar5 = FUN_43ae9674();
      if (iVar5 == 0) {
        iVar5 = FUN_4379a898();
        iVar5 = FUN_43ae9674(iVar5 + 0x28);
        goto LAB_43796f38;
      }
    }
    break;
  case 0x124:
    iVar5 = FUN_4379ada0();
    bVar11 = iVar5 == 5;
LAB_43796fbc:
    if (!bVar11) break;
    goto LAB_43796fbe;
  case 0x125:
    iVar5 = FUN_4379ad7c();
    if ((iVar5 != 0) && (iVar5 = FUN_4379ad88(), iVar5 == 1)) goto LAB_43796dae;
    break;
  case 0x126:
    iVar5 = FUN_4379ad7c();
    if ((iVar5 != 0) && (iVar5 = FUN_4379ad88(), iVar5 == 1)) {
      FUN_4379a898();
      iVar5 = FUN_43ae9674();
      if (iVar5 == 0) {
        iVar5 = FUN_4379a898();
        iVar5 = FUN_43ae9674(iVar5 + 0x28);
        if (iVar5 == 0) {
          iVar5 = FUN_4379a320();
          cVar8 = *(char *)(iVar5 + 0xac0);
          goto LAB_43796f7c;
        }
      }
    }
    break;
  case 0x129:
    if ((*(char *)(param_3[2] + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) {
      return 0x129;
    }
    break;
  case 0x12a:
    iVar5 = FUN_4379a320();
    cVar8 = *(char *)(iVar5 + 0xab2);
    goto LAB_43796f7c;
  case 299:
    iVar5 = FUN_4379a320();
    cVar8 = *(char *)(iVar5 + 0xab3);
    goto LAB_43796f7c;
  case 300:
    iVar5 = FUN_4379a320();
    cVar8 = *(char *)(iVar5 + 0xab4);
LAB_43796f7c:
    if (cVar8 == '\0') break;
    goto LAB_43796fbe;
  case 0x138:
  case 0x144:
    iVar5 = FUN_43799f88(uVar4,1);
    if (((iVar5 != 0) && (iVar5 = FUN_43799f88(uVar4,0), iVar5 != 0)) &&
       (iVar5 = FUN_43799f88(uVar4,4), iVar5 != 0)) {
      iVar5 = FUN_43799f88(uVar4,5);
      goto LAB_43796fa0;
    }
    break;
  case 0x139:
  case 0x145:
    if (*(char *)(param_3[2] + 0x1ed) != '\0') {
      if (1 < *(int *)(param_3[1] + 0x10) - 2U) {
        return uVar3;
      }
      if (*(int *)(param_3[1] + 0xc) == 1) {
        return uVar3;
      }
      if (1 < *(uint *)(param_3[2] + 0x3c)) {
        return uVar3;
      }
    }
    break;
  case 0x13a:
  case 0x146:
    iVar5 = FUN_43799f88(uVar4,4);
    goto LAB_43796f38;
  case 0x13b:
  case 0x13f:
switchD_43796ca8_caseD_13b:
    iVar5 = FUN_437dfeb4(uVar3);
LAB_43796fa0:
    if (iVar5 == 0) break;
    goto LAB_43796fbe;
  case 0x13c:
    if (*(char *)(param_3[0x15] + 9) == '\x01') {
      return 0x13c;
    }
    break;
  case 0x13d:
    if ((((*(char *)param_3[5] != '\0') || (*(int *)((char *)param_3[5] + 4) == 0)) ||
        (*(int *)(param_3[2] + 0x248) != 0)) || (*(char *)(iVar2 + 0xec) != '\0')) {
      uVar3 = 0x13d;
      goto switchD_43796ca8_caseD_13b;
    }
    break;
  case 0x13e:
    iVar5 = FUN_437dfa2c();
LAB_43796f38:
    if (iVar5 == 0) {
LAB_43796fbe:
      puVar9 = (undefined2 *)*param_3;
LAB_43796fc0:
      return *puVar9;
    }
    break;
  case 0x142:
    iVar5 = param_3[2];
    if ((*(char *)(iVar5 + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(iVar5 + 0x1d4))) {
      if ((*(char *)(iVar2 + 0x4a) == '\0') ||
         ((*(int *)(puVar9 + 0x5a) != 1 || ((*(byte *)(iVar5 + 0x220) & 3) == 2)))) {
        if (*(int *)(puVar9 + 0x5a) != 1) {
          return 0x142;
        }
        if (*(short *)(iVar5 + 0x240) == 0x142) {
          return 0x142;
        }
      }
LAB_43796ea8:
      return *(undefined2 *)(iVar5 + 0x26c);
    }
    break;
  case 0x143:
    iVar5 = param_3[2];
    if ((*(char *)(iVar5 + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(iVar5 + 0x1d4))) {
      if ((*(char *)(iVar2 + 0x4a) == '\0') ||
         ((*(int *)(puVar9 + 0x5a) != 1 || ((*(byte *)(iVar5 + 0x220) & 5) == 4)))) {
        if (*(int *)(puVar9 + 0x5a) != 1) {
          return 0x143;
        }
        if (*(short *)(iVar5 + 0x240) == 0x143) {
          return 0x143;
        }
      }
      goto LAB_43796ea8;
    }
  }
  iVar5 = param_3[2];
LAB_43796fda:
  uVar3 = *(undefined2 *)(iVar5 + 0x26c);
switchD_43796ca8_caseD_100:
  return uVar3;
}


/* query "4379bb90" */

void FUN_4379bb90(int *param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined1 uVar4;
  char cVar5;
  ushort uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined4 uVar9;
  char *pcVar10;
  int iVar11;
  byte bVar12;
  int iVar13;
  uint uVar14;
  undefined4 uVar15;
  int iVar16;
  uint uVar17;
  undefined2 *puVar18;
  int *piVar19;
  undefined *puVar20;
  int iVar21;
  undefined4 *puVar22;
  int *piVar23;
  uint uVar24;
  uint uVar25;
  int iVar26;
  uint uVar27;
  bool bVar28;
  undefined1 auStack_434 [244];
  undefined1 auStack_340 [216];
  undefined1 auStack_268 [132];
  undefined1 auStack_1e4 [76];
  undefined1 auStack_198 [64];
  undefined1 auStack_158 [44];
  undefined1 auStack_12c [40];
  undefined1 auStack_104 [8];
  undefined1 auStack_fc [4];
  undefined4 uStack_f8;
  undefined1 auStack_dc [36];
  undefined1 auStack_b8 [32];
  undefined1 auStack_98 [32];
  undefined1 auStack_78 [28];
  undefined1 auStack_5c [28];
  undefined1 auStack_40 [28];
  
  iVar21 = 0;
  piVar23 = (int *)&DAT_43e9f7d8;
  do {
    piVar23 = piVar23 + 1;
    if (*piVar23 != 2) {
      FUN_43b2a296(&DAT_43e9f0d8 + iVar21 * 0x28,5);
    }
    iVar21 = iVar21 + 1;
  } while (iVar21 != 4);
  iVar21 = 0;
  while (*(int *)((int)&DAT_43e9f7dc + iVar21) != 2) {
    iVar21 = iVar21 + 4;
    if (iVar21 == 0x10) {
      return;
    }
  }
  iVar21 = FUN_43aea1b6(param_1);
  if (iVar21 != 0) goto LAB_4379c298;
  iVar13 = param_1[0x12];
  DAT_43e9f204 = *(undefined4 *)(iVar13 + 0xc);
  DAT_43e9f208 = *(undefined4 *)(iVar13 + 0x10);
  DAT_43e9f2da = *(undefined1 *)(iVar13 + 0xe2);
  uVar25 = (uint)*(byte *)(param_1[0x12] + 0xe3);
  if (7 < uVar25) {
    uVar25 = 8;
  }
  DAT_43e9f2db = (undefined1)uVar25;
  uVar14 = *(byte *)(param_1[0x12] + 0xe7) - 1 & 0xff;
  if (uVar14 < 3) {
    uVar27 = (uint)*(ushort *)(&DAT_43bef288 + uVar14 * 2);
    uVar14 = (uint)*(ushort *)(&DAT_43bef28e + uVar14 * 2);
  }
  else {
    uVar14 = 0x280;
    uVar27 = 0x1e0;
  }
  puVar22 = &DAT_43e9f204;
  for (uVar24 = 0; iVar13 = param_1[0x12], uVar24 < uVar25; uVar24 = uVar24 + 1) {
    iVar16 = uVar24 * 0x14;
    iVar13 = iVar13 + iVar16;
    uVar4 = *(undefined1 *)(iVar13 + 0x20);
    uVar6 = *(ushort *)(iVar13 + 0x14);
    *(undefined2 *)((int)puVar22 + 10) = *(undefined2 *)(iVar13 + 0x16);
    uVar1 = *(ushort *)(iVar13 + 0x18);
    uVar2 = *(undefined2 *)(iVar13 + 0x1a);
    *(undefined1 *)(puVar22 + 5) = uVar4;
    iVar13 = param_1[0x12];
    *(undefined2 *)((int)puVar22 + 0xe) = uVar2;
    *(ushort *)(puVar22 + 2) = uVar6;
    *(ushort *)(puVar22 + 3) = uVar1;
    uVar4 = *(undefined1 *)(iVar13 + iVar16 + 0x21);
    puVar22[4] = *(undefined4 *)(iVar13 + iVar16 + 0x1c);
    *(undefined1 *)((int)puVar22 + 0x15) = uVar4;
    *(undefined1 *)((int)puVar22 + 0x16) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x22);
    *(undefined1 *)((int)puVar22 + 0x17) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x23);
    *(undefined1 *)(puVar22 + 6) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x24);
    *(undefined1 *)((int)puVar22 + 0x19) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x25);
    *(undefined1 *)((int)puVar22 + 0x1a) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x26);
    *(undefined1 *)((int)puVar22 + 0x1b) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x27);
    uVar17 = (uint)uVar6 + (uint)uVar1;
    if ((uVar14 < uVar17) ||
       (uVar27 < (uint)*(ushort *)((int)puVar22 + 0xe) + (uint)*(ushort *)((int)puVar22 + 10))) {
      FUN_4379b300(3,9,1,&DAT_43ca4df2,uVar17,
                   (uint)*(ushort *)((int)puVar22 + 0xe) + (uint)*(ushort *)((int)puVar22 + 10));
      FUN_43902718(s_PIN_YC_FACE_face_param_error__d__43ca4e06,
                   (uint)*(ushort *)(puVar22 + 2) + (uint)*(ushort *)(puVar22 + 3),
                   (uint)*(ushort *)((int)puVar22 + 0xe) + (uint)*(ushort *)((int)puVar22 + 10));
      *(undefined2 *)(puVar22 + 2) = 0;
      *(undefined2 *)((int)puVar22 + 10) = 0;
      *(undefined2 *)(puVar22 + 3) = 100;
      *(undefined2 *)((int)puVar22 + 0xe) = 100;
    }
    puVar22 = puVar22 + 5;
  }
  DAT_43e9f2ac = *(undefined4 *)(iVar13 + 0xb4);
  DAT_43e9f2b0 = *(undefined4 *)(iVar13 + 0xb8);
  DAT_43e9f2dc = *(undefined1 *)(iVar13 + 0xe4);
  DAT_43e9f2dd = *(undefined1 *)(param_1[0x12] + 0xe5);
  iVar13 = param_1[0x12];
  DAT_43e9f2b4 = *(undefined2 *)(iVar13 + 0xbc);
  DAT_43e9f2b6 = *(undefined2 *)(iVar13 + 0xbe);
  DAT_43e9f2b8 = *(undefined2 *)(iVar13 + 0xc0);
  DAT_43e9f2ba = *(undefined2 *)(iVar13 + 0xc2);
  DAT_43e9f2bc = *(undefined1 *)(iVar13 + 0xc4);
  DAT_43e9f2bd = *(undefined1 *)(param_1[0x12] + 0xc5);
  DAT_43e9f2be = *(undefined1 *)(param_1[0x12] + 0xc6);
  DAT_43e9f2bf = *(undefined1 *)(param_1[0x12] + 199);
  DAT_43e9f2c0 = *(undefined1 *)(param_1[0x12] + 200);
  iVar13 = param_1[0x12];
  DAT_43e9f2c4 = *(undefined4 *)(iVar13 + 0xcc);
  DAT_43e9f2c8 = *(undefined4 *)(iVar13 + 0xd0);
  DAT_43e9f2de = *(undefined1 *)(iVar13 + 0xe6);
  iVar13 = param_1[0x12];
  DAT_43e9f2cc = *(ushort *)(iVar13 + 0xd4);
  DAT_43e9f2ce = *(ushort *)(iVar13 + 0xd6);
  DAT_43e9f2d0 = *(ushort *)(iVar13 + 0xd8);
  DAT_43e9f2d2 = *(ushort *)(iVar13 + 0xda);
  DAT_43e9f2d4 = *(undefined1 *)(iVar13 + 0xdc);
  DAT_43e9f2d5 = *(undefined1 *)(param_1[0x12] + 0xdd);
  DAT_43e9f2d6 = *(undefined1 *)(param_1[0x12] + 0xde);
  DAT_43e9f2d7 = *(undefined1 *)(param_1[0x12] + 0xdf);
  DAT_43e9f2d8 = *(undefined1 *)(param_1[0x12] + 0xe0);
  uVar25 = *(byte *)(param_1[0x12] + 0xe9) - 1 & 0xff;
  if (uVar25 < 3) {
    uVar14 = (uint)*(ushort *)(&DAT_43bef294 + uVar25 * 2);
    uVar25 = (uint)*(ushort *)(&DAT_43bef29a + uVar25 * 2);
  }
  else {
    uVar25 = 0x280;
    uVar14 = 0x1e0;
  }
  if ((uVar25 < (uint)DAT_43e9f2d0 + (uint)DAT_43e9f2cc) ||
     (uVar14 < (uint)DAT_43e9f2d2 + (uint)DAT_43e9f2ce)) {
    FUN_4379b300(3,9,1,&DAT_43ca4e2a,(uint)DAT_43e9f2d0 + (uint)DAT_43e9f2cc,
                 (uint)DAT_43e9f2d2 + (uint)DAT_43e9f2ce);
    FUN_43902718(s_PIN_YC_FACE_trackingdata_param_e_43ca4e3e,(uint)DAT_43e9f2d0 + (uint)DAT_43e9f2cc
                 ,(uint)DAT_43e9f2d2 + (uint)DAT_43e9f2ce);
    DAT_43e9f2cc = 0;
    DAT_43e9f2ce = 0;
    DAT_43e9f2d0 = 100;
    DAT_43e9f2d2 = 100;
  }
  DAT_43e9f2df = *(char *)(param_1[0x12] + 0xe7);
  DAT_43e9f2e0 = *(char *)(param_1[0x12] + 0xe8);
  DAT_43e9f2e1 = *(char *)(param_1[0x12] + 0xe9);
  if (DAT_43e9f7e0 == 2) {
    puVar20 = &DAT_43e9f3c0;
LAB_4379cd50:
    cVar5 = puVar20[0x2e];
    if (cVar5 != DAT_43e9f2df) {
      DAT_43e9f2db = 0;
    }
    if (cVar5 != DAT_43e9f2e0) {
      DAT_43e9f2dc = 0;
    }
    if (cVar5 != DAT_43e9f2e1) {
      DAT_43e9f2de = 0;
    }
  }
  else if (DAT_43e9f7dc == 2) {
    puVar20 = &DAT_43e9f388;
    goto LAB_4379cd50;
  }
  DAT_43e9f178 = FUN_43ae8c4a(*(int *)param_1[1] + -1);
  DAT_43e9f17c = 0;
  iVar16 = param_1[3];
  DAT_43e9f180 = (uint)*(ushort *)(iVar16 + 0xe8);
  DAT_43e9f184 = (uint)*(ushort *)(iVar16 + 0xea);
  DAT_43e9f188 = (uint)*(ushort *)(iVar16 + 0xec);
  DAT_43e9f18c = (uint)*(ushort *)(iVar16 + 0xee);
  iVar13 = *(int *)(*param_1 + 0xe0);
  if (iVar13 == 3) {
    DAT_43e9f190 = 0xb;
  }
  else {
    if (iVar13 < 4) {
      if (iVar13 == 1) {
LAB_4379bf04:
        DAT_43e9f190 = 7;
        goto LAB_4379bf2c;
      }
      bVar28 = iVar13 == 2;
    }
    else {
      if (iVar13 == 0x27) goto LAB_4379bf04;
      bVar28 = iVar13 == 0x28;
    }
    if (bVar28) {
      DAT_43e9f190 = 8;
    }
    else if (*(char *)(iVar16 + 0x100) == '\x01') {
      DAT_43e9f190 = 0xb;
    }
    else {
      DAT_43e9f190 = 0;
    }
  }
LAB_4379bf2c:
  DAT_43e9f192 = *(undefined1 *)(iVar16 + 0xf4);
  DAT_43e9f194 = 0;
  DAT_43e9f198 = 0;
  DAT_43e9f19c = (uint)*(ushort *)(param_1[3] + 0xfc);
  DAT_43e9f1a4 = 0;
  DAT_43e9f1a0 = (uint)*(ushort *)(param_1[3] + 0xfe);
  DAT_43e9f1a8 = 0;
  DAT_43e9f1ac = 0x20;
  DAT_43e9f1ae = (ushort)(*(int *)(*param_1 + 0x3d4) != 0);
  switch(*(undefined4 *)(*param_1 + 0x3c8)) {
  case 0:
  case 0x12:
    DAT_43e9f1b0 = 0;
    break;
  case 1:
    DAT_43e9f1b0 = 5;
    break;
  case 2:
    DAT_43e9f1b0 = 6;
    break;
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
  case 0xd:
  case 0xe:
  case 0xf:
    DAT_43e9f1b0 = 10;
    break;
  case 10:
  case 0xb:
  case 0xc:
  case 0x10:
    DAT_43e9f1b0 = 4;
    break;
  default:
    FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,799);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,799);
    DAT_43e9f1b0 = 0;
  }
  DAT_43e9f1b2 = (ushort)*(byte *)(param_1[0xf] + 0x1e0);
  if (0x18 < *(byte *)(param_1[0xf] + 0x1e0)) {
    DAT_43e9f1b2 = 0;
  }
  DAT_43e9f1b4 = 0;
  if (*(uint *)(*param_1 + 0x2c4) < 8) {
    uVar25 = 1 << (*(uint *)(*param_1 + 0x2c4) & 0xff);
    if ((uVar25 & 0xbe) != 0) goto LAB_4379c062;
    if ((uVar25 & 0x41) == 0) goto LAB_4379c032;
    DAT_43e9f1b6 = 1;
  }
  else {
LAB_4379c032:
    FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,0x33a);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,0x33a);
LAB_4379c062:
    DAT_43e9f1b6 = 0;
  }
  DAT_43e9f1b7 = *(int *)(param_1[2] + 0x1c8) != 1;
  if (*(int *)(param_1[10] + 0x94) < 0) {
    DAT_43e9f1b8 = 0xffffffff;
  }
  else {
    DAT_43e9f1b8 = FUN_4355fd68(*(int *)(param_1[10] + 0x94),10);
  }
  DAT_43e9f1bc = 100;
  DAT_43e9f1c8 = *(uint *)(param_1[3] + 0xf8) & 0x1ffffff;
  DAT_43e9f1cc = (uint)(*(char *)(param_1[0xb] + 0x8c) != '\0');
  if (*(int *)(*param_1 + 0x488) == 1) {
    DAT_43e9f1cc = DAT_43e9f1cc | 0x10;
  }
  bVar12 = 0;
  DAT_43e9f1d0 = 0;
  DAT_43e9f1d1 = 0;
  DAT_43e9f1cc = (*(short *)(param_1[0xb] + 0x92) + 8) * 0x10 & 0xfff00U | DAT_43e9f1cc;
  iVar13 = *param_1;
  iVar16 = param_1[10];
  cVar5 = *(char *)(param_1[0xb] + 0x2c);
  if (*(char *)(iVar16 + 0x34) == '\0') {
    if (*(char *)(iVar16 + 0x33) == '\0') {
      bVar12 = 0;
    }
    else {
LAB_4379c140:
      bVar12 = *(byte *)(iVar16 + 0x35) + 1;
    }
  }
  else {
    if (*(char *)(iVar16 + 0x34) != '\x01') goto LAB_4379c140;
    if (*(char *)(iVar16 + 0x33) != '\x01') {
      bVar12 = ~*(byte *)(iVar16 + 0x35);
    }
  }
  DAT_43e9f1e4 = bVar12 & 0x1f;
  if ((*(int *)(iVar13 + 0x448) != 0) && ((*(uint *)(param_1[0xb] + 0x28) & 0xff) != 0)) {
    if (*(int *)(iVar13 + 0x2dc) == 0) {
      bVar12 = 0;
    }
    else {
      bVar12 = *(char *)(iVar13 + 0x2d8) + 1;
      if ('\a' < (char)bVar12) {
        bVar12 = 8;
      }
      if (*(int *)(iVar13 + 0x2dc) == 2) {
        bVar12 = -bVar12;
      }
    }
    DAT_43e9f1e4 = bVar12 & 0x1f;
    if ((*(char *)(iVar16 + 0x167) != '\0') && (cVar5 == '\x01')) {
      DAT_43e9f1e4 = 0;
    }
    DAT_43e9f1e4 = DAT_43e9f1e4 | 0x40;
  }
  if (*(char *)(iVar16 + 0x166) == '\0') {
    if (*(int *)(iVar13 + 0x448) == 0) {
      if (*(char *)(iVar16 + 0x167) != '\0') goto LAB_4379c1ba;
    }
    else if (cVar5 == '\x01') goto LAB_4379c1ba;
  }
  else {
LAB_4379c1ba:
    DAT_43e9f1e4 = DAT_43e9f1e4 | 0x80;
  }
  DAT_43e9f1e6 = FUN_4355faf0(*(int *)(param_1[0xb] + 0x5c) << 4,
                              *(undefined4 *)(param_1[0xb] + 0x58));
  puVar22 = &DAT_43e9f4c4;
  iVar13 = 0;
  do {
    iVar26 = param_1[0xb];
    *(undefined4 *)((int)&DAT_43e9f4c4 + iVar13) = *(undefined4 *)(param_1[10] + 0x9c);
    iVar16 = iVar13 + 0xc4;
    *(undefined4 *)((int)&DAT_43e9f4c8 + iVar13) = 0;
    puVar22[2] = *(undefined4 *)(iVar26 + 0x58);
    puVar22[3] = *(undefined4 *)(iVar26 + 0x5c);
    uVar9 = FUN_43ae8c4a(*(int *)param_1[1] + -1);
    uVar4 = *(undefined1 *)(iVar26 + 7);
    puVar22[5] = 0;
    *(undefined1 *)(puVar22 + 6) = uVar4;
    puVar18 = (undefined2 *)param_1[0xd];
    uVar15 = *(undefined4 *)(puVar18 + 0x74);
    uVar2 = *puVar18;
    puVar22[8] = 0;
    puVar22[7] = uVar15;
    uVar3 = puVar18[7];
    *(undefined2 *)(puVar22 + 9) = uVar2;
    *(undefined2 *)((int)puVar22 + 0x26) = uVar3;
    puVar22[4] = uVar9;
    uVar2 = puVar18[0x72];
    *(undefined2 *)(puVar22 + 10) = puVar18[0x73];
    *(undefined2 *)((int)puVar22 + 0x2a) = uVar2;
    *(undefined1 *)(puVar22 + 0x2e) = *(undefined1 *)(param_1[0xb] + 0xce);
    *(undefined1 *)((int)puVar22 + 0xb9) = *(undefined1 *)(param_1[0xb] + 0xcf);
    *(undefined1 *)((int)puVar22 + 0xba) = *(undefined1 *)(param_1[0xb] + 0xd0);
    *(undefined1 *)(puVar22 + 0x2f) = *(undefined1 *)(param_1[0xb] + 0xd2);
    uVar4 = *(undefined1 *)(param_1[0xb] + 0xd1);
    *(undefined2 *)((int)puVar22 + 0xbe) = *(undefined2 *)(param_1[0xb] + 0xd4);
    *(undefined1 *)((int)puVar22 + 0xbb) = uVar4;
    *(undefined2 *)(puVar22 + 0x30) = *(undefined2 *)(param_1[10] + 0x10);
    *(char *)((int)puVar22 + 0xc2) = (char)*(undefined4 *)(*param_1 + 0xe0);
    *(char *)((int)puVar22 + 0xc3) = (char)*(undefined4 *)(*param_1 + 0xa4);
    puVar22 = puVar22 + 0x31;
    iVar13 = iVar16;
  } while (iVar16 != 0x310);
LAB_4379c298:
  DAT_43e9f4bc = FUN_43797344();
  if (DAT_43e9f4bc == 0) {
    iVar13 = DAT_43e9f474;
    if (DAT_43e9f3bb == '\x01') {
      iVar13 = DAT_43e9f474 + DAT_43e9f478;
    }
    FUN_43796438((1 - *(int *)param_1[1]) + iVar13);
  }
  iVar13 = 0;
  puVar22 = (undefined4 *)&DAT_43e9f46c;
  puVar20 = &DAT_43e9f388;
  piVar23 = &DAT_43e9f7dc;
  do {
    if (*piVar23 == 2) {
      FUN_43ae7558(auStack_104);
      iVar16 = FUN_43903558(auStack_104,0xe0b00,1,0,5);
      if (iVar16 == 0) {
        uVar9 = FUN_43b2a252(auStack_fc);
        FUN_439c5a04(uVar9,0,0x20);
        FUN_435a9288(auStack_dc,uVar9,uStack_f8,0);
        FUN_435a91d0(auStack_1e4);
        FUN_43a4941e(auStack_1e4,&DAT_43e9f388 + iVar13 * 0x38);
        thunk_FUN_43a49ba4(auStack_dc,auStack_1e4);
        FUN_435a91b0(auStack_1e4);
        FUN_435a922c(auStack_5c);
        FUN_43a49548(auStack_5c,&DAT_43f9a4d5 + iVar13 * 6);
        thunk_FUN_43a49ba4(auStack_dc,auStack_5c);
        FUN_435a920c(auStack_5c);
        FUN_435a9174(auStack_12c);
        FUN_43a493cc(auStack_12c,&DAT_43e9f46c + iVar13 * 0x14);
        thunk_FUN_43a49ba4(auStack_dc,auStack_12c);
        FUN_435a9154(auStack_12c);
        if (iVar21 == 0) {
          FUN_439cc9ec(auStack_340);
          FUN_43b660e0(auStack_340,&DAT_43e9f4c4 + iVar13 * 0x31);
          thunk_FUN_43a49ba4(auStack_dc,auStack_340);
          FUN_439cc9cc(auStack_340);
        }
        if (((*(uint *)(param_1[2] + 0x268) & 0x10004) == 0x10004) &&
           (iVar16 = FUN_43aea1aa(iVar13), iVar16 != 0)) {
          FUN_439cc774(auStack_98);
          iVar16 = FUN_4379b408(iVar13);
          FUN_43b65fe4(auStack_98,&DAT_43f79b86 + iVar16 * 10);
          FUN_43a49ba4(auStack_dc,auStack_98);
          FUN_439cc754(auStack_98);
        }
        if (iVar21 == 0) {
          FUN_439cc884(auStack_434);
          FUN_43b66058(auStack_434,&DAT_43e9f204);
          thunk_FUN_43a49ba4(auStack_dc,auStack_434);
          FUN_439cc864(auStack_434);
          FUN_439cc718(auStack_268);
          FUN_43b65fbc(auStack_268,&DAT_43e9f178);
          thunk_FUN_43a49ba4(auStack_dc,auStack_268);
          FUN_439cc6f8(auStack_268);
          iVar16 = FUN_4379b3f4(iVar13);
          if (iVar16 != 0) {
            FUN_439cc8e0(auStack_198);
            FUN_43b66080(auStack_198,&DAT_43f9a4ee);
            thunk_FUN_43a49ba4(auStack_dc,auStack_198);
            FUN_439cc8c0(auStack_198);
          }
        }
        iVar16 = FUN_43aea1aa(iVar13);
        if ((iVar16 != 0) &&
           ((iVar16 = FUN_4379b408(iVar13), (&DAT_43e9f0c0)[iVar16 * 0xc] == '\x02' ||
            (iVar16 = FUN_4379b408(iVar13), (&DAT_43e9f0c1)[iVar16 * 0xc] == '\x02')))) {
          FUN_439cc990(auStack_b8);
          iVar16 = FUN_4379b408(iVar13);
          FUN_43b660b6(auStack_b8,&DAT_43e9f0c0 + iVar16 * 0xc);
          thunk_FUN_43a49ba4(auStack_dc,auStack_b8);
          FUN_439cc970(auStack_b8);
        }
        iVar16 = FUN_4379b3f4(iVar13);
        if (iVar16 != 0) {
          FUN_439cc7d0(auStack_78);
          FUN_43b6600c(auStack_78,&DAT_43e9f4bc);
          thunk_FUN_43a49ba4(auStack_dc,auStack_78);
          FUN_439cc7b0(auStack_78);
        }
        iVar16 = FUN_4379b3f4(iVar13);
        if ((iVar16 != 0) && (DAT_43e9f1e8 != -1)) {
          FUN_439cca48(auStack_158);
          FUN_43b66118(auStack_158,&DAT_43e9f1e8);
          thunk_FUN_43a49ba4(auStack_dc,auStack_158);
          FUN_439cca28(auStack_158);
        }
        iVar16 = FUN_4379b3f4(iVar13);
        if ((iVar16 != 0) && (DAT_43e9f1e8 != -1)) {
          FUN_439cc93c(auStack_40);
          FUN_43b6609e(auStack_40,&DAT_43e9f7d8);
          thunk_FUN_43a49ba4(auStack_dc,auStack_40);
          if ((DAT_43e9f0bc == -1) || (DAT_43f9a51a != DAT_43e9f7d8)) {
            FUN_43901a8c(4,0x2040,DAT_43e9f1e8,DAT_43e9f7d8);
            DAT_43e9f0bc = DAT_43e9f1e8;
            DAT_43f9a51a = DAT_43e9f7d8 != 0;
          }
          FUN_439cc91c(auStack_40);
        }
        FUN_43b2a258(auStack_104,5);
        if (iVar13 == 2) {
          iVar16 = FUN_43797b24(auStack_104,0);
        }
        else if (iVar13 == 3) {
          iVar16 = FUN_43797b38(auStack_104,0);
        }
        else if (iVar13 == 1) {
          iVar16 = FUN_43797b10(auStack_104,0);
        }
        else {
          iVar16 = FUN_43797afc(auStack_104,0);
        }
        iVar26 = DAT_4402546c;
        if ((*(byte *)(DAT_4402546c + 3) & 4) != 0) {
          iVar11 = thunk_FUN_436cd00c();
          uVar9 = DAT_43e9f7ec;
          iVar11 = iVar11 - *(int *)(param_1[1] + 8);
          if (iVar13 == 2) {
            FUN_4379b300(3,9,1,&DAT_43ca5011,iVar16,iVar11,DAT_43e9f2e4);
            FUN_43902718(s_PROXY_PIN_send_err_code__d__frc__43ca5025,iVar16,iVar11,DAT_43e9f2e4);
            piVar19 = &DAT_43e9f2e4;
          }
          else if (iVar13 == 3) {
            FUN_4379b300(3,9,1,&DAT_43ca505d,iVar16,iVar11,DAT_43e9f7d4);
            FUN_43902718(s_4K_EE_PIN_send_err_code__d__frc__43ca5071,iVar16,iVar11,DAT_43e9f7d4);
            piVar19 = &DAT_43e9f7d4;
          }
          else if (iVar13 == 1) {
            FUN_4379b300(3,9,1,&DAT_43ca4fc7,iVar16,iVar11,DAT_43e9f200);
            FUN_43902718(s_REC_PIN_send_err_code__d__frc_co_43ca4fdb,iVar16,iVar11,DAT_43e9f200);
            piVar19 = &DAT_43e9f200;
          }
          else {
            uVar15 = FUN_43797344();
            FUN_4379b300(3,9,1,&DAT_43ca4f6f,iVar16,iVar11,uVar9,uVar15);
            uVar9 = DAT_43e9f7ec;
            uVar15 = FUN_43797344();
            FUN_43902718(s_EE_PIN_send_err_code__d__frc_cou_43ca4f83,iVar16,iVar11,uVar9,uVar15);
            piVar19 = &DAT_43e9f7ec;
          }
          *piVar19 = *piVar19 + 1;
        }
        iVar11 = FUN_4379b3f4(iVar13);
        if ((iVar11 != 0) && ((*(byte *)(iVar26 + 3) & 0x40) != 0)) {
          FUN_4379b300(3,9,1,&DAT_43ca50a9,iVar13,*(undefined2 *)(puVar20 + 0x20),
                       *(undefined2 *)(puVar20 + 0x22),*(undefined2 *)(puVar20 + 0x14),
                       *(undefined2 *)(puVar20 + 0x16));
          FUN_43902718(s__EE__d__Pin__vx__d__vy__d__rx__d_43ca50bd,iVar13,
                       *(undefined2 *)(puVar20 + 0x20),*(undefined2 *)(puVar20 + 0x22),
                       *(undefined2 *)(puVar20 + 0x14),*(undefined2 *)(puVar20 + 0x16));
          FUN_4379b300(3,9,1,&DAT_43ca50e6,*puVar22,puVar20[0x10],puVar22[2],puVar22[3],
                       puVar20[0x11]);
          FUN_43902718(s_CRT__d__d__TRS__d__d__DLY__d_43ca50fa,*puVar22,puVar20[0x10],puVar22[2],
                       puVar22[3],puVar20[0x11]);
        }
        iVar11 = FUN_43aea1aa(iVar13);
        if ((iVar11 != 0) && (*(char *)(iVar26 + 3) < '\0')) {
          if (iVar13 == 1) {
            FUN_4379b300(3,9,1,&DAT_43ca5117,DAT_43e9f3e0,DAT_43e9f3e2,DAT_43e9f3d4,DAT_43e9f3d6);
            pcVar10 = s__RECPin__vx__d__vy__d__rx__d__ry_43ca512b;
            uVar7 = DAT_43e9f3e0;
            uVar3 = DAT_43e9f3e2;
            uVar2 = DAT_43e9f3d4;
            uVar8 = DAT_43e9f3d6;
LAB_4379ca92:
            FUN_43902718(pcVar10,uVar7,uVar3,uVar2,uVar8);
          }
          else if (iVar13 == 2) {
            FUN_4379b300(3,9,1,&DAT_43ca5150,DAT_43e9f418,DAT_43e9f41a,DAT_43e9f40c,DAT_43e9f40e);
            pcVar10 = s__PROXYPin__vx__d__vy__d__rx__d__r_43ca5164;
            uVar7 = DAT_43e9f418;
            uVar3 = DAT_43e9f41a;
            uVar2 = DAT_43e9f40c;
            uVar8 = DAT_43e9f40e;
            goto LAB_4379ca92;
          }
          FUN_4379b300(3,9,1,&DAT_43ca50e6,*puVar22,puVar20[0x10],puVar22[2],puVar22[3],
                       puVar20[0x11]);
          FUN_43902718(s_CRT__d__d__TRS__d__d__DLY__d_43ca50fa,*puVar22,puVar20[0x10],puVar22[2],
                       puVar22[3],puVar20[0x11]);
        }
        if (iVar16 < -0x1a) {
LAB_4379cbf4:
          FUN_4379b300(3,9,1,&DAT_43ca51cd,iVar13,iVar16);
          FUN_43902718(s_SendYCPin__d__is_error__x__43ca51e1,iVar13,iVar16);
        }
        else if (-0x18 < iVar16) {
          if (iVar16 != 0) goto LAB_4379cbf4;
          iVar16 = thunk_FUN_436cd00c();
          uVar25 = iVar16 - *(int *)(param_1[1] + 8);
          if (((*(uint *)(param_1[1] + 0x24) >> 1 < uVar25) &&
              (1 < *(int *)(param_1[2] + 0x1d4) - 4U)) && (*(int *)(param_1[2] + 0x1c) != 4)) {
            uVar25 = uVar25 >> 1;
            FUN_4379b300(3,9,1,&DAT_43ca518b,uVar25,iVar13);
            FUN_43902718(s_VD_Sequence__YC_out_window_overf_43ca519f,uVar25,iVar13);
            if (DAT_43e9f468 < 5) {
              DAT_43e9f468 = DAT_43e9f468 + 1;
              FUN_43901a8c(3,4,0xffffffff,uVar25);
            }
          }
          FUN_43ae7542(auStack_104);
          FUN_43ae7542(&DAT_43e9f0d8 + iVar13 * 0x28);
          iVar16 = FUN_43aea1aa(iVar13);
          if (iVar16 != 0) {
            FUN_43ae7542(&DAT_43e9f2e8 + iVar13 * 0x28);
          }
          iVar16 = FUN_4379b3f4(iVar13);
          if (iVar16 != 0) {
            iVar16 = FUN_437973c4();
            if (iVar16 != 0) {
              iVar16 = FUN_43ae8c4a(DAT_43e9f474 - *(int *)param_1[1]);
              iVar16 = iVar16 + (uint)*(byte *)(DAT_4401f1d0 + 0x84);
              if (DAT_43e9f3bb == '\x01') {
                iVar16 = iVar16 + DAT_43e9f478;
              }
              FUN_437973f8(iVar16);
            }
            iVar16 = FUN_43797390();
            if ((iVar16 != 0) || (iVar16 = FUN_43797344(), iVar16 == 0)) {
              FUN_43901a8c(4,0x200f,0,0);
            }
            FUN_43797370();
            if (DAT_43f9a4ed == '\0') {
              FUN_43901a8c(4,0x2002,0,0);
              DAT_43f9a4ed = '\x01';
            }
          }
        }
        *piVar23 = 1;
        FUN_435a9268(auStack_dc);
      }
      else {
        FUN_4379b300(3,9,1,&DAT_43ca4f46,iVar13);
        FUN_43902718(s_Can_t_get_sds_mem__d_43ca4f5a,iVar13);
      }
      FUN_43ae7534(auStack_104);
    }
    else if ((*(byte *)(DAT_4402546c + 3) & 2) != 0) {
      iVar16 = iVar13;
      if (iVar13 == 2) {
        FUN_4379b300(3,9,1,&DAT_43ca4ed6,2);
        pcVar10 = s_PROXY_PIN_OUT_STATE_is_not_READY_43ca4eea;
      }
      else if (iVar13 == 3) {
        FUN_4379b300(3,9,1,&DAT_43ca4f0e,3);
        pcVar10 = s_4K_EE_PIN_OUT_STATE_is_not_READY_43ca4f22;
      }
      else if (iVar13 == 1) {
        FUN_4379b300(3,9,1,&DAT_43ca4ea0,1);
        pcVar10 = s_REC_PIN_OUT_STATE_is_not_READY___43ca4eb4;
      }
      else {
        FUN_4379b300(3,9,1,&DAT_43ca4e6a,0);
        pcVar10 = s_EE_PIN_OUT_STATE_is_not_READY__d_43ca4e7e;
        iVar16 = 0;
      }
      FUN_43902718(pcVar10,iVar16);
    }
    iVar13 = iVar13 + 1;
    puVar22 = puVar22 + 5;
    puVar20 = puVar20 + 0x38;
    piVar23 = piVar23 + 1;
    if (iVar13 == 4) {
      iVar21 = 0;
      do {
        FUN_43b2a296(&DAT_43e9f0d8 + iVar21 * 0x28,5);
        iVar13 = FUN_43aea1aa(iVar21);
        if (iVar13 != 0) {
          FUN_43b2a296(&DAT_43e9f2e8 + iVar21 * 0x28,5);
        }
        iVar21 = iVar21 + 1;
      } while (iVar21 != 4);
      return;
    }
  } while( true );
}


/* query "4379b44c" */

void FUN_4379b44c(int param_1,int param_2,undefined4 param_3)

{
  undefined1 *puVar1;
  undefined2 *puVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  short sVar5;
  short sVar6;
  undefined2 uVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  char cVar11;
  undefined *puVar12;
  undefined4 *puVar13;
  int iVar14;
  undefined1 uVar15;
  
  if ((&DAT_43e9f7dc)[param_1] == 0) {
    return;
  }
  (&DAT_43e9f7dc)[param_1] = 2;
  iVar9 = param_1;
  iVar14 = param_2;
  if ((*(int *)(param_2 + 0x10) != 0) && (iVar8 = FUN_43ae9674(), iVar8 != 0)) {
    FUN_43b2a296(&DAT_43e9f0d8 + param_1 * 0x28,5);
    FUN_4390366c(&DAT_43e9f0d8 + param_1 * 0x28,*(undefined4 *)(param_2 + 0x10),0,5);
  }
  iVar8 = FUN_43aea1aa(param_1);
  if ((iVar8 != 0) && (*(char *)(param_2 + 200) == '\x01')) {
    FUN_43b2a296(&DAT_43e9f2e8 + param_1 * 0x28,5);
    FUN_4390366c(&DAT_43e9f2e8 + param_1 * 0x28,*(undefined4 *)(param_2 + 0xd4),0,5,iVar9,iVar14,
                 param_3);
  }
  if ((*(int *)(param_2 + 0x10) == 0) || (iVar9 = FUN_43ae9674(), iVar9 == 0)) {
    iVar9 = param_1 * 0x38;
    (&DAT_43e9f388)[iVar9] = 0;
    *(undefined4 *)(&DAT_43e9f38c + iVar9) = 0;
    *(undefined2 *)(&DAT_43e9f390 + iVar9) = 0xffff;
    *(undefined4 *)(&DAT_43e9f394 + iVar9) = 0;
  }
  else {
    iVar9 = param_1 * 0x38;
    (&DAT_43e9f388)[iVar9] = 1;
    uVar4 = *(undefined2 *)(&DAT_43e9f0d8 + param_1 * 0x28);
    uVar10 = *(undefined4 *)(&DAT_43e9f0dc + param_1 * 0x28);
    *(undefined4 *)(&DAT_43e9f394 + iVar9) = 0;
    *(undefined2 *)(&DAT_43e9f390 + iVar9) = uVar4;
    *(undefined4 *)(&DAT_43e9f38c + iVar9) = uVar10;
  }
  iVar9 = param_1 * 0x38;
  (&DAT_43e9f398)[iVar9] = *(undefined1 *)(param_2 + 0x1c);
  (&DAT_43e9f399)[iVar9] = *(undefined1 *)(param_2 + 0x1d);
  (&DAT_43e9f39b)[iVar9] = *(int *)(param_2 + 0xe4) == 1;
  uVar4 = *(undefined2 *)(param_2 + 0x24);
  iVar9 = param_1 * 0x38;
  *(undefined2 *)(&DAT_43e9f3a0 + iVar9) = *(undefined2 *)(param_2 + 0x22);
  *(undefined2 *)(&DAT_43e9f3a2 + iVar9) = uVar4;
  sVar5 = *(short *)(DAT_4402546c + 0x96);
  if ((sVar5 == 0) || (sVar6 = *(short *)(DAT_4402546c + 0x98), sVar6 == 0)) {
    uVar4 = *(undefined2 *)(param_2 + 0x20);
    uVar7 = *(undefined2 *)(param_2 + 0x26);
    iVar9 = param_1 * 0x38;
    *(undefined2 *)(&DAT_43e9f39c + iVar9) = *(undefined2 *)(param_2 + 0x1e);
    *(undefined2 *)(&DAT_43e9f39e + iVar9) = uVar4;
    uVar4 = *(undefined2 *)(param_2 + 0x28);
    uVar3 = *(undefined2 *)(param_2 + 0x2a);
    *(undefined2 *)(&DAT_43e9f3a4 + iVar9) = uVar7;
    *(undefined2 *)(&DAT_43e9f3a6 + iVar9) = uVar4;
    uVar4 = *(undefined2 *)(param_2 + 0x2c);
    uVar7 = *(undefined2 *)(param_2 + 0x2e);
    *(undefined2 *)(&DAT_43e9f3a8 + iVar9) = uVar3;
    uVar3 = *(undefined2 *)(param_2 + 0x30);
    *(undefined2 *)(&DAT_43e9f3aa + iVar9) = uVar4;
    *(undefined2 *)(&DAT_43e9f3ac + iVar9) = uVar7;
    *(undefined2 *)(&DAT_43e9f3ae + iVar9) = uVar3;
    uVar4 = *(undefined2 *)(param_2 + 0x32);
    *(undefined2 *)(&DAT_43e9f3b2 + iVar9) = *(undefined2 *)(param_2 + 0x34);
    *(undefined2 *)(&DAT_43e9f3b0 + iVar9) = uVar4;
  }
  else {
    uVar4 = *(undefined2 *)(DAT_4402546c + 0x92);
    uVar7 = *(undefined2 *)(DAT_4402546c + 0x94);
    *(short *)(&DAT_43e9f3a8 + iVar9) = sVar5;
    *(short *)(&DAT_43e9f3b0 + iVar9) = sVar5;
    *(undefined2 *)(&DAT_43e9f3a6 + iVar9) = uVar7;
    *(short *)(&DAT_43e9f3b2 + iVar9) = sVar6;
    *(undefined2 *)(&DAT_43e9f3a4 + iVar9) = uVar4;
    *(short *)(&DAT_43e9f39c + iVar9) = sVar5;
    cVar11 = *(char *)(param_2 + 0x3e);
    *(short *)(&DAT_43e9f3aa + iVar9) = sVar6;
    *(undefined2 *)(&DAT_43e9f3ac + iVar9) = 0;
    *(undefined2 *)(&DAT_43e9f3ae + iVar9) = 0;
    *(short *)(&DAT_43e9f39e + iVar9) = sVar6;
    if (cVar11 != '\0') {
      *(short *)(&DAT_43e9f39e + iVar9) = sVar6 << 1;
    }
  }
  (&DAT_43e9f3b4)[param_1 * 0x38] = 0;
  (&DAT_43e9f3b5)[param_1 * 0x38] = 0;
  switch(*(undefined4 *)(param_2 + 0x38)) {
  case 0:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 2;
    break;
  case 1:
    goto LAB_4379b67c;
  case 2:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 1;
    break;
  case 3:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 5;
    break;
  case 4:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 3;
    break;
  case 5:
    puVar12 = &DAT_43e9f388 + param_1 * 0x38;
    uVar15 = 4;
    break;
  default:
    FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,0x109);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,0x109);
LAB_4379b67c:
    (&DAT_43e9f3b6)[param_1 * 0x38] = 0;
    goto LAB_4379b67e;
  }
  puVar12[0x2e] = uVar15;
LAB_4379b67e:
  if (*(char *)(param_2 + 0x3c) == '\0') {
    (&DAT_43e9f3b7)[param_1 * 0x38] = 0;
  }
  else {
    (&DAT_43e9f3b7)[param_1 * 0x38] = 1;
  }
  if (*(char *)(param_2 + 0x3d) == '\0') {
    (&DAT_43e9f3bb)[param_1 * 0x38] = 0;
  }
  else {
    (&DAT_43e9f3bb)[param_1 * 0x38] = 1;
  }
  cVar11 = *(char *)(param_2 + 0x3e);
  iVar9 = param_1 * 0x38;
  *(undefined2 *)(&DAT_43e9f3bc + iVar9) = 0x40;
  if (cVar11 == '\0') {
    (&DAT_43e9f3b8)[iVar9] = 1;
    uVar15 = 2;
    (&DAT_43e9f3b9)[iVar9] = 1;
LAB_4379b706:
    (&DAT_43e9f3ba)[iVar9] = uVar15;
  }
  else {
    (&DAT_43e9f3b8)[iVar9] = 0;
    (&DAT_43e9f3b9)[iVar9] = 0;
    if (*(int *)(param_2 + 0x40) == 0) {
      uVar15 = 1;
      goto LAB_4379b706;
    }
    (&DAT_43e9f3ba)[iVar9] = 0;
  }
  (&DAT_43f9a4d5)[param_1 * 6] = *(int *)(param_2 + 0x4c) != 1;
  if (*(int *)(param_2 + 0x44) == 1) {
    uVar15 = 3;
  }
  else {
    if (*(int *)(param_2 + 0x44) == 2) {
      (&DAT_43f9a4d6)[param_1 * 6] = 2;
      goto LAB_4379b770;
    }
    if (*(int *)(param_2 + 0x48) == 1) {
      (&DAT_43f9a4d6)[param_1 * 6] = 1;
      goto LAB_4379b770;
    }
    uVar15 = 0;
  }
  (&DAT_43f9a4d6)[param_1 * 6] = uVar15;
LAB_4379b770:
  if (*(char *)(param_2 + 0x50) == '\0') {
    (&DAT_43f9a4d7)[param_1 * 6] = 1;
  }
  else {
    (&DAT_43f9a4d7)[param_1 * 6] = 0;
  }
  if (*(char *)(param_2 + 0x3e) == '\0') {
    (&DAT_43f9a4d8)[param_1 * 6] = 1;
  }
  else {
    (&DAT_43f9a4d8)[param_1 * 6] = 0;
  }
  (&DAT_43f9a4d9)[param_1 * 6] = 0;
  (&DAT_43f9a4da)[param_1 * 6] = 5;
  iVar9 = param_1 * 0x14;
  *(undefined4 *)(&DAT_43e9f46c + iVar9) = *(undefined4 *)(param_2 + 4);
  *(undefined4 *)(&DAT_43e9f470 + iVar9) = *(undefined4 *)(param_2 + 0xc);
  (&DAT_43e9f474)[param_1 * 5] = *(undefined4 *)(param_2 + 0x14);
  (&DAT_43e9f478)[param_1 * 5] = *(undefined4 *)(param_2 + 0x18);
  uVar10 = FUN_43ae2c02(param_2);
  *(undefined4 *)(&DAT_43e9f47c + iVar9) = uVar10;
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 != 0) {
    DAT_43e9f1c0 = *(undefined4 *)(param_2 + 0x5c);
    DAT_43e9f1c4 = *(undefined4 *)(param_2 + 0x60);
  }
  iVar9 = param_1 * 0xc4;
  puVar13 = &DAT_43e9f4c4 + param_1 * 0x31;
  (&DAT_43e9f4f0)[iVar9] = *(undefined1 *)(param_2 + 100);
  if (*(char *)(param_2 + 100) == '\x01') {
    cVar11 = '\x14';
    *(undefined4 *)(&DAT_43e9f4f4 + iVar9) = *(undefined4 *)(param_2 + 0x68);
    *(undefined4 *)(&DAT_43e9f4f8 + iVar9) = 0;
    iVar9 = param_2;
    do {
      cVar11 = cVar11 + -1;
      *(undefined1 *)(puVar13 + 0xe) = *(undefined1 *)(iVar9 + 0x6c);
      *(undefined1 *)(puVar13 + 0x13) = *(undefined1 *)(iVar9 + 0x80);
      puVar1 = (undefined1 *)(iVar9 + 0x94);
      iVar9 = iVar9 + 1;
      *(undefined1 *)(puVar13 + 0x18) = *puVar1;
      puVar13 = (undefined4 *)((int)puVar13 + 1);
    } while (cVar11 != '\0');
  }
  iVar9 = param_1 * 0xc4;
  puVar13 = &DAT_43e9f4c4 + param_1 * 0x31;
  (&DAT_43e9f538)[iVar9] = *(undefined1 *)(param_2 + 0xa8);
  if (*(char *)(param_2 + 0xa8) == '\x01') {
    *(undefined4 *)(&DAT_43e9f53c + iVar9) = *(undefined4 *)(param_2 + 0xac);
    *(undefined4 *)(&DAT_43e9f540 + iVar9) = 0;
    iVar9 = param_2;
    do {
      *(undefined2 *)(puVar13 + 0x20) = *(undefined2 *)(iVar9 + 0xb0);
      puVar2 = (undefined2 *)(iVar9 + 0xb2);
      iVar9 = iVar9 + 4;
      *(undefined2 *)((int)puVar13 + 0x82) = *puVar2;
      puVar13 = puVar13 + 1;
    } while (iVar9 != param_2 + 0x18);
  }
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 == 0) {
    iVar9 = param_1 * 0xc4;
    (&DAT_43e9f55c)[iVar9] = *(undefined1 *)(param_2 + 200);
    if (*(char *)(param_2 + 200) == '\x01') {
      uVar10 = *(undefined4 *)(param_2 + 0xcc);
      *(undefined4 *)(&DAT_43e9f564 + iVar9) = 0;
      *(undefined4 *)(&DAT_43e9f560 + iVar9) = uVar10;
      (&DAT_43e9f568)[iVar9] = *(undefined1 *)(param_2 + 0xd0);
      uVar10 = *(undefined4 *)(&DAT_43e9f2ec + param_1 * 0x28);
      *(undefined2 *)(&DAT_43e9f570 + iVar9) = *(undefined2 *)(&DAT_43e9f2e8 + param_1 * 0x28);
      *(undefined4 *)(&DAT_43e9f56c + iVar9) = uVar10;
    }
  }
  else {
    (&DAT_43e9f55c)[param_1 * 0xc4] = 0;
  }
  iVar9 = param_1 * 0xc4;
  (&DAT_43e9f572)[iVar9] = *(undefined1 *)(param_2 + 0xd8);
  (&DAT_43e9f573)[iVar9] = *(undefined1 *)(param_2 + 0xd9);
  (&DAT_43e9f574)[iVar9] = *(undefined1 *)(param_2 + 0xda);
  uVar4 = *(undefined2 *)(param_2 + 0xdc);
  (&DAT_43e9f578)[iVar9] = *(undefined1 *)(param_2 + 0xde);
  uVar15 = *(undefined1 *)(param_2 + 0xdf);
  *(undefined2 *)(&DAT_43e9f576 + iVar9) = uVar4;
  (&DAT_43e9f579)[iVar9] = uVar15;
  *(undefined2 *)(&DAT_43e9f57a + iVar9) = *(undefined2 *)(param_2 + 0xe0);
  iVar9 = FUN_43aea1aa(param_1);
  if (iVar9 != 0) {
    iVar9 = FUN_4379b408(param_1);
    iVar14 = *(int *)(param_2 + 0x54);
    if (iVar14 + 2U < 2) {
      uVar15 = 1;
    }
    else {
      uVar15 = 2;
    }
    (&DAT_43e9f0c0)[iVar9 * 0xc] = uVar15;
    iVar8 = *(int *)(param_2 + 0x58);
    if ((iVar8 == -1) || (iVar14 == -2)) {
      uVar15 = 1;
    }
    else {
      uVar15 = 2;
    }
    (&DAT_43e9f0c1)[iVar9 * 0xc] = uVar15;
    *(int *)(&DAT_43e9f0c4 + iVar9 * 0xc) = iVar14;
    *(int *)(&DAT_43e9f0c8 + iVar9 * 0xc) = iVar8;
  }
  iVar9 = FUN_43aea1aa(param_1);
  if (iVar9 != 0) {
    iVar9 = FUN_4379b408(param_1);
    iVar9 = iVar9 * 10;
    *(undefined2 *)(&DAT_43f79b86 + iVar9) = *(undefined2 *)(param_2 + 0xe8);
    uVar4 = *(undefined2 *)(param_2 + 0xea);
    uVar7 = *(undefined2 *)(param_2 + 0xec);
    *(undefined2 *)(&DAT_43f79b8c + iVar9) = *(undefined2 *)(param_2 + 0xee);
    uVar15 = *(undefined1 *)(param_2 + 0xf0);
    *(undefined2 *)(&DAT_43f79b88 + iVar9) = uVar4;
    *(undefined2 *)(&DAT_43f79b8a + iVar9) = uVar7;
    (&DAT_43f79b8e)[iVar9] = uVar15;
  }
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 != 0) {
    DAT_43e9f1e8 = *(undefined4 *)(param_2 + 0xf4);
    if (*(char *)(param_2 + 0x100) == '\0') {
      if (*(int *)(param_2 + 0xf8) == 2) {
        DAT_43e9f1ec = 1;
      }
      else if (*(int *)(param_2 + 0xf8) == 3) {
        DAT_43e9f1ec = 0;
      }
      else {
        DAT_43e9f1ec = 2;
      }
    }
    else if (*(int *)(param_2 + 0xfc) == 1) {
      DAT_43e9f1ec = 3;
    }
    else if (*(int *)(param_2 + 0xfc) == 2) {
      DAT_43e9f1ec = 4;
    }
    else {
      FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,0x1e0);
      FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,0x1e0);
    }
    DAT_43e9f1f0 = 0;
    DAT_43e9f1f8 = 0;
    DAT_43e9f1f4 = 0x1020;
    DAT_43e9f1fc = 1;
  }
  iVar9 = FUN_4379b3f4(param_1);
  if (iVar9 != 0) {
    DAT_43e9f7d8 = (uint)(*(char *)(param_2 + 0x101) != '\0');
  }
  return;
}


/* query "43797afc" */

void FUN_43797afc(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9de9c,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* query "43797b10" */

void FUN_43797b10(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9de64,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* query "43797b24" */

void FUN_43797b24(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9dee0,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* query "43797b38" */

void FUN_43797b38(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9df18,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* query "435a9928" */

undefined4 FUN_435a9928(int param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined1 auStack_15c [272];
  undefined1 auStack_4c [8];
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined4 uStack_1c;
  
  if (*(int *)(param_1 + 0x28) == 1) {
    uVar1 = 0xffffffe6;
    FUN_435aa628(0x204e4950,0x1de,0xffffffe6);
  }
  else if (*(int *)(param_1 + 0x28) == 2) {
    uVar1 = 0xffffffe8;
    FUN_435aa628(0x204e4950,0x1e2,0xffffffe8);
  }
  else if (*(int *)(param_1 + 0x1c) == 1) {
    uVar1 = 0xffffffea;
    FUN_435aa628(0x204e4950,0x1e8,0xffffffea);
  }
  else {
    FUN_435a92e0(auStack_15c);
    FUN_43a3bd46(auStack_4c);
    uStack_44 = *(undefined4 *)(param_1 + 0x18);
    uStack_40 = *(undefined4 *)(param_1 + 0x1c);
    uStack_3c = *(undefined4 *)(param_1 + 0x20);
    uStack_38 = *(undefined4 *)(param_1 + 0x24);
    uStack_34 = *(undefined4 *)(param_1 + 8);
    uStack_30 = *(undefined4 *)(param_1 + 0xc);
    uStack_2c = *(undefined4 *)(param_1 + 0x10);
    uStack_28 = *(undefined4 *)(param_1 + 0x14);
    uStack_1e = 0;
    uStack_24 = param_2;
    uStack_20 = param_3;
    uStack_1c = param_4;
    FUN_435a9460(auStack_15c,auStack_4c,0x34);
    FUN_43a49628(auStack_15c,*(undefined4 *)(param_1 + 0x24));
    uVar1 = FUN_435aa20c(*(undefined4 *)(param_1 + 4),*(undefined4 *)(param_1 + 0x14),auStack_15c);
    FUN_435a92c8(auStack_15c);
  }
  return uVar1;
}


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


/* query "43ad60cc" */

undefined4 s32_candidate_43ad60cc(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = thunk_FUN_43ad2e90(param_1 + 3);
  if (iVar1 == 0) {
    uVar2 = func_0x436cd1ec(*param_1);
    thunk_FUN_43ad6034(param_1 + 3,uVar2);
    return 1;
  }
  return 0;
}

