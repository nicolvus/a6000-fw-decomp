/* Static Ghidra pseudocode; not executable source.
 * SHA256: b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9
 * 43541000..43bc0000 marked read-only in analysis; bytes unchanged
 * Candidate entries inferred; changes discarded by -readOnly.
 */

/* ENTRY 4378f410 */

void candidate_4378f410(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_20 [4];
  undefined1 auStack_1c [8];
  
  iVar1 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Drive_S_43ca2e3d);
  }
  iVar2 = FUN_43560de0(0x1a,0x80,0,auStack_20,5);
  if (iVar2 != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca2e48,*DAT_43e9920c);
    FUN_43902718(s_VD_Drive__wait_timeout__dV_43ca2e5c,*DAT_43e9920c);
  }
  if (param_1 == *DAT_43e9920c) {
    FUN_43ae1292(2);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_437fe7b4();
    if (DAT_43e9bcc8 == '\0') {
      DAT_43f79b80 = 0;
      DAT_4401d33c = 0xffff;
    }
    else {
      FUN_437876dc();
      iVar2 = FUN_43b00e5a();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 1;
      }
      iVar2 = thunk_FUN_436e8334();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 0x800;
      }
      iVar2 = FUN_43af0d5e(&DAT_43e99208);
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 2;
      }
      iVar2 = thunk_FUN_4384a184();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 4;
      }
      if (DAT_4401d33c != DAT_43f79b80) {
        FUN_43901a8c(4,0x200d,0x807);
        DAT_4401d33c = DAT_43f79b80;
      }
    }
    if ((*(int *)(DAT_43e99208 + 0xb4) == 2) ||
       ((iVar2 = DAT_43e9bcc0, DAT_43e9bcc8 != '\0' && (DAT_43f79b80 != 0x807)))) {
      iVar2 = DAT_43e9920c[0xc];
    }
    FUN_4378dfdc(DAT_43e9bccc,iVar2);
    thunk_FUN_437d8f1c(&DAT_43e99208,&DAT_43e9ced8);
    thunk_FUN_437cf928(&DAT_43e99208,&DAT_43e9d018);
    if (((*(char *)(iVar1 + 0x70) == '\0') && (iVar2 = FUN_437999e4(1,0xe), iVar2 != 0)) &&
       ((DAT_43e9bb1f == '\0' || (DAT_43e9920c[3] != 0)))) {
      auStack_1c[0] = 1;
      FUN_439e3870(auStack_1c);
    }
    FUN_437968b0(&DAT_43e99208);
    if (*(char *)(iVar1 + 0xbf) == '\0') {
      FUN_43ae129a(2);
    }
    FUN_43901480(5);
    if (param_1 == *DAT_43e9920c) {
      iVar2 = FUN_43ae916c();
      if (iVar2 == 0) {
        FUN_4379ce0c();
        thunk_FUN_437b7fe4();
        FUN_4379ce24(&DAT_43e99208);
      }
    }
    else {
      iVar2 = FUN_43ae8d4e();
      if (iVar2 != 0) {
        iVar3 = *DAT_43e9920c;
        iVar2 = thunk_FUN_436cd00c();
        FUN_4378eb78(3,9,1,&DAT_43ca2eb3,param_1,iVar3,(uint)(iVar2 - DAT_43e9920c[2]) >> 1);
        iVar3 = *DAT_43e9920c;
        iVar2 = thunk_FUN_436cd00c();
        FUN_43902718(s_Imaging__VD_Drive__overflow__dV___43ca2ec7,param_1,iVar3,
                     (uint)(iVar2 - DAT_43e9920c[2]) >> 1);
        if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
          FUN_43561540(s_VD_Drive_E_OF_43ca2ef3);
        }
      }
    }
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Drive_E_43ca2f01);
    }
  }
  else {
    iVar2 = FUN_43ae8d4e();
    if (iVar2 != 0) {
      iVar3 = *DAT_43e9920c;
      iVar2 = thunk_FUN_436cd00c();
      FUN_4378eb78(3,9,1,&DAT_43ca2e77,param_1,iVar3,(uint)(iVar2 - DAT_43e9920c[2]) >> 1);
      iVar3 = *DAT_43e9920c;
      iVar2 = thunk_FUN_436cd00c();
      FUN_43902718(s_VD_Drive__start_delayed__dV__>___43ca2e8b,param_1,iVar3,
                   (uint)(iVar2 - DAT_43e9920c[2]) >> 1);
      if ((*(byte *)(iVar1 + 0x1b) & 0x10) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* ENTRY 4378f848 */

void candidate_4378f848(int param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iStack_20;
  uint uStack_1c;
  undefined4 uStack_18;
  
  iVar1 = DAT_4402546c;
  if (DAT_43e992dc != param_1) {
    iStack_20 = param_1;
    uStack_1c = param_2;
    uStack_18 = param_3;
    if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
      FUN_43561540(&DAT_43ca2f48);
    }
    FUN_43ae1292(4);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_4378f7a0(0xe23);
    FUN_43560e00(0x11,&iStack_20);
    DAT_43e9bd4c = uStack_1c & 4 | DAT_43e9bd4c & 0xfffffffb;
    if ((uStack_1c & 4) == 0) {
      DAT_43e9d398 = FUN_437b4d64();
      FUN_43ae8e2c(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b4c = 0;
    }
    else {
      DAT_43f79b6a = DAT_43f79b6a + 1;
      DAT_43f79b4c = DAT_43f79b4c + 1;
    }
    FUN_437b4e28(&DAT_43e99208);
    FUN_43aef444(&DAT_43e99208,&DAT_43e9c7d8);
    FUN_4378f7a0(0xe40);
    DAT_43e992dc = param_1;
    FUN_43ae129a(4);
    FUN_43901480(7);
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(&DAT_43ca2f55);
    }
  }
  return;
}


/* ENTRY 4378e6a0 */

bool FUN_4378e6a0(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  bool bVar3;
  
  iVar1 = FUN_437999e4(1,0,param_3,param_4,param_1,param_2);
  if (iVar1 == 0) {
    return false;
  }
  if (*(char *)(param_1 + 0x21) == '\0') {
    if (*(uint *)(param_1 + 0x18) == 0) {
      if (-1 < *(char *)(DAT_4402546c + 0x26)) {
        return false;
      }
      FUN_4378e288(3,9,1,&DAT_43ca2637);
      pcVar2 = s_No_Read__cause_no_expose_43ca264b;
LAB_4378e794:
      FUN_43902718(pcVar2);
      return false;
    }
    if (*(char *)(param_1 + 0xc) == '\0') {
      iVar1 = FUN_43ae8d02(param_1);
      if ((iVar1 == 0) && (*(int *)(*(int *)(param_2 + 8) + 0x44) != 0x44)) {
        if (-1 < *(char *)(DAT_4402546c + 0x26)) {
          return false;
        }
        FUN_4378e288(3,9,1,&DAT_43ca2664,*(undefined4 *)(param_1 + 0x18),
                     *(undefined4 *)(param_1 + 0x10));
        FUN_43902718(s_No_Read__cause_clamp__expcnt__d__43ca2678,*(undefined4 *)(param_1 + 0x18),
                     *(undefined4 *)(param_1 + 0x10));
        return false;
      }
      if (*(int *)(param_1 + 0x18) == 1) {
        if (*(char *)(param_1 + 0xd) != '\0') {
          if (*(char *)(DAT_4402546c + 0x26) < '\0') {
            FUN_4378e288(3,9,1,&DAT_43ca26a5);
            FUN_43902718(s_No_Read__cause_1st_expose_with_f_43ca26b9);
          }
          goto LAB_4378e7da;
        }
        iVar1 = FUN_43ae8d02(param_1);
        if (iVar1 == 0) {
          if (-1 < *(char *)(DAT_4402546c + 0x26)) {
            return false;
          }
          FUN_4378e288(3,9,1,&DAT_43ca26e7);
          pcVar2 = s_No_Read__cause_1st_expose_43ca26fb;
          goto LAB_4378e794;
        }
      }
      if (((*(int *)(param_1 + 0x1c) == 0) && (*(int *)(*(int *)(param_2 + 8) + 0x2c) == 0)) &&
         (*(char *)(*(int *)(param_2 + 0x20) + 2) == '\0')) {
        if (-1 < *(char *)(DAT_4402546c + 0x26)) {
          return false;
        }
        FUN_4378e288(3,9,1,&DAT_43ca2715,*(undefined1 *)(*(int *)(param_2 + 0x20) + 1));
        FUN_43902718(s_No_Read__cause_HS_1st_read_must_b_43ca2729,
                     *(undefined1 *)(*(int *)(param_2 + 0x20) + 1));
        return false;
      }
    }
    else if (*(int *)(*(int *)(param_2 + 8) + 0x44) == 8) {
      return 2 < *(uint *)(param_1 + 0x18);
    }
    bVar3 = true;
  }
  else {
LAB_4378e7da:
    bVar3 = false;
  }
  return bVar3;
}


/* ENTRY 43792a0c */

void FUN_43792a0c(uint param_1)

{
  char cVar1;
  uint uVar2;
  ushort uVar3;
  ushort uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined2 uVar13;
  undefined2 uVar14;
  undefined2 uVar15;
  uint uVar16;
  uint uVar17;
  undefined1 uVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  undefined4 uVar21;
  undefined4 uVar22;
  int iVar23;
  int iVar24;
  char *pcVar25;
  int iVar26;
  undefined4 uVar27;
  uint uVar28;
  undefined4 uVar29;
  undefined4 uVar30;
  undefined4 uVar31;
  short sVar32;
  int extraout_r1;
  uint uVar33;
  uint uVar34;
  undefined1 *puVar35;
  uint uVar36;
  undefined4 *puVar37;
  uint uVar38;
  uint uVar39;
  uint uVar40;
  uint uVar41;
  bool bVar42;
  bool bVar43;
  undefined1 *puVar44;
  undefined1 *puVar45;
  undefined1 *puVar46;
  undefined4 uStack_3b8;
  undefined4 uStack_3b4;
  undefined4 uStack_3b0;
  undefined4 uStack_3ac;
  undefined1 auStack_3a8 [96];
  undefined1 auStack_348 [96];
  undefined4 uStack_2e8;
  undefined4 uStack_2e4;
  undefined1 auStack_2e0 [96];
  undefined1 auStack_280 [96];
  undefined4 uStack_220;
  undefined4 uStack_21c;
  undefined1 auStack_218 [272];
  undefined1 auStack_108 [20];
  undefined1 auStack_f4 [20];
  undefined1 auStack_e0 [20];
  undefined1 auStack_cc [20];
  undefined1 auStack_b8 [20];
  undefined1 auStack_a4 [20];
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [2];
  undefined2 uStack_52;
  undefined1 uStack_4c;
  undefined1 auStack_48 [4];
  undefined4 uStack_44;
  undefined1 auStack_40 [4];
  byte bStack_3c;
  undefined1 auStack_38 [4];
  byte bStack_34;
  undefined4 uStack_30;
  undefined1 auStack_2c [8];
  
  iVar26 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Pre_S_43ca387e);
  }
  uVar19 = FUN_437876dc();
  if (*(char *)(iVar26 + 0xaa) != '\0') {
    DAT_43e9931c = DAT_43e9931c + 1;
    FUN_4355fd4c();
    if (extraout_r1 == 0) {
      uVar20 = FUN_43728564();
      uVar21 = FUN_437284b4();
      uVar22 = FUN_43ae0c38();
      FUN_4378eb78(5,2,1,&DAT_43ca3887,uVar20,uVar21,uVar22);
      uVar20 = FUN_43728564();
      uVar21 = FUN_437284b4();
      uVar22 = FUN_43ae0c38();
      FUN_43902718(s___d__d__d__43ca3896,uVar20,uVar21,uVar22);
    }
  }
  cVar1 = *(char *)(iVar26 + 0x1b);
  if (cVar1 != '\0') {
    puVar35 = &DAT_43f9a429;
    puVar37 = (undefined4 *)&DAT_f2804000;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != (undefined4 *)0xf2804110);
    puVar35 = &DAT_43f9a46d;
    puVar37 = (undefined4 *)0xf2804110;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != (undefined4 *)0xf28041e8);
    if (cVar1 == '\x01') {
      FUN_4378ec60();
      *(undefined1 *)(iVar26 + 0x1b) = 0;
    }
  }
  if (*(byte *)(iVar26 + 0x11) != 0) {
    uVar41 = (uint)*(byte *)(iVar26 + 0x11) * 100;
    uVar39 = DAT_43e9920c[2];
    uVar40 = uVar39 - *DAT_44024f64 >> 1;
    if (uVar40 < uVar41) {
      FUN_4378eb78(3,9,1,&DAT_43ca38a1,uVar40);
      FUN_43902718(s_HS3__process_margin_warning__dus_43ca38b5,uVar40);
      FUN_43561540(s_HS3_Warning_43ca38d6);
    }
    uVar40 = uVar39 - *DAT_44022338 >> 1;
    if (uVar40 < uVar41) {
      FUN_4378eb78(3,9,1,&DAT_43ca38e2,uVar40);
      FUN_43902718(s_HS3_IDT__process_margin_warning___43ca38f6,uVar40);
      FUN_43561540(s_HS3_IDT_Warning_43ca391b);
    }
    uVar39 = uVar39 - *DAT_44025cfc >> 1;
    if (uVar39 < uVar41) {
      FUN_4378eb78(3,9,1,&DAT_43ca392b,uVar39);
      FUN_43902718(s_HS3_RCH__process_margin_warning___43ca393f,uVar39);
      FUN_43561540(s_HS3_RCH_Warning_43ca3964);
    }
  }
  if (param_1 != *DAT_43e9920c) {
    iVar23 = thunk_FUN_436cd00c();
    uVar39 = iVar23 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca3974,param_1,*DAT_43e9920c,uVar39);
    FUN_43902718(s_VD_Pre__start_delayed__dV__>__dV_43ca3988,param_1,*DAT_43e9920c,uVar39);
    FUN_4378f988(3,0,uVar39);
    if ((*(byte *)(iVar26 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Pre_S_OF_43ca39ae);
    }
    if ((*(byte *)(iVar26 + 0x1b) & 2) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  FUN_43ae1292(4);
  iVar23 = FUN_43ae8d4e();
  if (iVar23 == 0) {
    FUN_43901778();
    if (DAT_4401e926 != '\0') {
      DAT_43f9a4b8 = '\x01';
    }
    DAT_4401e926 = 0;
  }
  else {
    DAT_4401e926 = 1;
  }
  if (*(byte *)(iVar26 + 0x20) == 0) {
    DAT_43f79b84 = 0;
  }
  else {
    if (DAT_43e9920c[5] - 1 < 2) {
      sVar32 = *(short *)(&DAT_43bef280 + (DAT_43e9920c[5] - 1) * 2);
    }
    else {
      sVar32 = 0x3c;
    }
    DAT_43f79b84 = sVar32 * (ushort)*(byte *)(iVar26 + 0x20);
  }
  DAT_43e9946c = DAT_43e9946c + 1;
  DAT_43f9a4a5 = 0;
  FUN_4378f7a0(0x708);
  iVar23 = FUN_437999e4(1,1);
  if (((iVar23 != 0) || (iVar23 = FUN_437999e4(1,2), iVar23 != 0)) &&
     ((DAT_43e9bbb8 < 2 || (DAT_43e9920c[3] != 0)))) {
    FUN_43aef52c(&DAT_43e99208,&DAT_43e9c7d8);
    FUN_437d9a04(&DAT_43e9ced8,&DAT_43e99208);
    if (((*(byte *)(iVar26 + 0x16) & 5) == 4) && (DAT_43e9bdbc != 0)) {
      FUN_43ad53b8(&DAT_43e9bdc0,DAT_43e9bdbc,0);
    }
  }
  FUN_43a0cb54();
  FUN_43b2a04a();
  FUN_437fdf5c();
  uVar15 = DAT_43e9b55e;
  uVar14 = DAT_43e9b55c;
  uVar13 = DAT_43e9b55a;
  uVar12 = DAT_43e9b558;
  uVar11 = DAT_43e9b556;
  uVar10 = DAT_43e9b554;
  uVar9 = DAT_43e9b552;
  uVar8 = DAT_43e9b550;
  uVar7 = DAT_43e9b54e;
  uVar6 = DAT_43e9b54c;
  uVar5 = DAT_43e9b54a;
  uVar3 = DAT_43e9b548;
  FUN_43804c5c(&DAT_43e9b548);
  DAT_43e9b548 = uVar3;
  DAT_43e9b54a = uVar5;
  DAT_43e9b54c = uVar6;
  DAT_43e9b54e = uVar7;
  DAT_43e9b550 = uVar8;
  DAT_43e9b552 = uVar9;
  DAT_43e9b554 = uVar10;
  DAT_43e9b556 = uVar11;
  DAT_43e9b558 = uVar12;
  DAT_43e9b55a = uVar13;
  DAT_43e9b55c = uVar14;
  DAT_43e9b55e = uVar15;
  FUN_43ae8fa2();
  FUN_43ae8f98();
  FUN_437fc404(&DAT_43e99208);
  FUN_437fc54c(1);
  FUN_4375dd04();
  iVar23 = FUN_437fc54c(0);
  FUN_4380c7f8(iVar23,auStack_38);
  bVar42 = false;
  if ((bStack_34 & 0x20) != 0) {
    if (*(uint *)(DAT_43e99214 + 0xc) < 2) {
      bVar42 = false;
      if (*(char *)(DAT_43e99214 + 0x11) != '\0') {
        bVar42 = *(int *)(DAT_43e99208 + 0x2c4) != 0;
      }
    }
    else {
      bVar42 = false;
    }
  }
  iVar24 = FUN_43b00cb4(uVar19);
  if ((((iVar24 == 1) && (iVar23 == 0x110)) &&
      (sVar32 = *(short *)(DAT_43e99210 + 0x240), sVar32 != 0x110)) && (sVar32 != 0x101)) {
    bVar43 = sVar32 != 0x100;
  }
  else {
    bVar43 = false;
  }
  if ((((DAT_43e9920c[3] == 1) || (DAT_43e9bb18 < 2)) || (bVar42)) && (!bVar43)) {
    DAT_43e9b548 = FUN_437fc54c();
    DAT_43e9b54a = FUN_437fc54c(2);
    DAT_43e9b54c = FUN_437fc54c(1);
    DAT_43e9b54e = FUN_437fc54c(3);
    DAT_43e9b552 = FUN_437fc54c(5);
    DAT_43e9b550 = FUN_437fc54c(4);
    DAT_43e9b554 = FUN_437fc54c(6);
    DAT_43e9b556 = FUN_437fc54c(8);
    DAT_43e9b55a = FUN_437fc54c(10);
    DAT_43e9b558 = FUN_437fc54c(9);
    DAT_43e9b55e = FUN_437fc54c(0xc);
    if (DAT_43e9920c[5] == DAT_43e9920c[0xd]) {
      DAT_43e9b55c = FUN_437fc54c(0xb);
    }
    FUN_4380c7f8(DAT_43e9b548,&DAT_43e9bd50);
  }
  iVar23 = DAT_43e99210;
  if (*(int *)(DAT_43e99208 + 0xb4) == 1) {
    DAT_43f9a4ba = DAT_43f9a427;
    DAT_43f9a4bb = DAT_43f9a428;
    FUN_43796044(&DAT_43f9a427);
    iVar24 = 0;
    if (DAT_43f9a428 != '\0') {
      if (DAT_43f9a4bb != '\0') goto LAB_43792f54;
      iVar24 = FUN_4378f9b4();
      iVar24 = **(int **)(iVar24 + 4) + 5;
    }
    *(int *)(iVar23 + 0x204) = iVar24;
  }
LAB_43792f54:
  iVar23 = FUN_43b00cba(uVar19);
  if (iVar23 != 0) {
    FUN_43b00dd4(uVar19);
    FUN_43805b04(uVar19,&DAT_43e99208,&DAT_43e9b548,&DAT_43e9baec);
    FUN_43b00e40(uVar19,&DAT_43e99208);
  }
  FUN_437da078(&DAT_43e99208,&DAT_43e9d3b4);
  FUN_43ae7564(&DAT_43e99208,&DAT_43e9d3b4);
  iVar24 = DAT_43e99210;
  iVar23 = DAT_43e99208;
  if (*(int *)(DAT_43e99208 + 0xb4) == 2) {
    *(undefined4 *)(DAT_43e99210 + 0x204) = *(undefined4 *)(DAT_43e99210 + 0x238);
    *(undefined1 *)(iVar24 + 0x202) = *(undefined1 *)(iVar24 + 0x234);
  }
  DAT_43e9bd08 = DAT_43e9bd55 & 0x40;
  if (((DAT_43e9bd55 & 0x40) != 0) && (DAT_43e9bd08 = 1, *(int *)(iVar23 + 0x30) != 1)) {
    DAT_43e9bd08 = 0;
  }
  if ((DAT_43f9a4b9 != DAT_43e9bd08) || (DAT_43e99378 != *(int *)(iVar23 + 0x34))) {
    FUN_43901a8c(4,0x203e,DAT_43e9bd08,*(undefined4 *)(iVar23 + 0x34));
    DAT_43f9a4b9 = DAT_43e9bd08;
    DAT_43e99378 = *(int *)(DAT_43e99208 + 0x34);
  }
  if ((*(byte *)(DAT_43e99210 + 0x266) & 0x20) == 0) {
    DAT_43e9bcf4 = 0;
  }
  else if ((ushort)(DAT_43e9b548 - 0x148) < 2) {
    switch(DAT_43e9b60c) {
    case 8:
      DAT_43e9bcf4 = 1;
      break;
    case 9:
      DAT_43e9bcf4 = 2;
      break;
    case 10:
      DAT_43e9bcf4 = 3;
      break;
    case 0xb:
      DAT_43e9bcf4 = 4;
    }
  }
  else {
    if ((DAT_43e9bd08 == 0) || (*(int *)(DAT_43e99208 + 0x34) != 0)) {
      DAT_43e9bcf4 = 0;
    }
    else if (DAT_43e9b60c == 8) {
      DAT_43e9bcf4 = 1;
    }
    else {
      DAT_43e9bcf4 = 0;
      if (DAT_43e9b60c == 9) {
        DAT_43e9bcf4 = 2;
      }
    }
    if (DAT_43e993a0 != DAT_43e9bcf4) {
      FUN_43901a8c(4,0x203f,DAT_43e9bcf4,0);
      DAT_43e993a0 = DAT_43e9bcf4;
    }
  }
  if (((DAT_43e9bd50 & 0xf8000) == 0x38000) && (*(int *)(DAT_43e99208 + 0x474) == 2)) {
    DAT_43e9bd31 = '\x01';
  }
  else {
    DAT_43e9bd31 = '\0';
  }
  if (DAT_43f9a4a8 != DAT_43e9bd31) {
    FUN_43901a8c(4,0x2043,DAT_43e9bd31,0);
    DAT_43f9a4a8 = DAT_43e9bd31;
  }
  switch(DAT_43e9bd50 & 7) {
  case 1:
    DAT_43e9bccc = 2;
    goto LAB_437931a0;
  case 2:
    DAT_43e9bccc = 1;
    DAT_43e9bcc0 = *(uint *)(DAT_44020e90 + 0x50);
    if (DAT_43e9bcc0 == 1) {
      DAT_43e9bcd0 = 1;
    }
    else {
      if ((((((DAT_43e9bd50 & 0x400000) == 0) || (iVar23 = FUN_43728564(), iVar23 != 0)) ||
           (*(int *)(DAT_43e99208 + 0x9c) != 0)) || (*(int *)(DAT_43e99208 + 0x94) != 0)) ||
         (((DAT_43e9bd50 & 0xf8000) == 0x10000 &&
          ((*(char *)(DAT_43e99240 + 0x74) != '\0' || (iVar23 = thunk_FUN_43ae69d6(), iVar23 != 0)))
          ))) goto LAB_437945b6;
      DAT_43e9bcd0 = 0;
    }
    break;
  case 3:
    DAT_43e9bccc = 1;
    if (DAT_43e9bcf4 == 0) {
      DAT_43e9bcc0 = *(uint *)(DAT_43e99208 + 0x20);
    }
    else if ((-1 < DAT_43e9bcf4) && (DAT_43e9bcf4 < 5)) {
      DAT_43e9bcc0 = 0;
    }
    goto LAB_437945b6;
  case 4:
    DAT_43e9bcc0 = 1;
    goto LAB_4379328a;
  case 5:
    DAT_43e9bcc0 = 0;
LAB_4379328a:
    DAT_43e9bccc = 1;
    DAT_43e9bcd0 = 1;
    break;
  case 6:
    DAT_43e9bccc = 1;
    DAT_43e9bcc0 = *(uint *)(DAT_44020e90 + 0x50);
    break;
  default:
    DAT_43e9bccc = 0;
LAB_437931a0:
    DAT_43e9bcc0 = DAT_43e9920c[0xc];
LAB_437945b6:
    DAT_43e9bcd0 = 1;
  }
  DAT_43e9bcc4 = FUN_43ae8c50(DAT_43e9bcc0);
  DAT_43e9bcc8 = DAT_43e9bcc4 != DAT_43e9920c[5];
  iVar23 = FUN_436e9234();
  DAT_43e9bcf8 = *(int *)(DAT_43e99208 + 0x178);
  DAT_43e9bcfc = *(undefined4 *)(&DAT_43bc42e8 + (iVar23 * 3 + *(int *)(DAT_43e99208 + 0x174)) * 4);
  DAT_43e9bd00 = (uint)*(byte *)(DAT_43e99208 + 0x17c);
  if ((DAT_43e99204 != DAT_43e9bcf8) || (DAT_43e992bc != DAT_43e9bd00)) {
    FUN_439d88c4();
    FUN_43901a8c(4,0x2030,DAT_43e9bcf8,0xff);
    uVar21 = *(undefined4 *)(DAT_43e99208 + 0x174);
    uVar20 = FUN_436e9234();
    FUN_43901a8c(4,0x2031,uVar21,uVar20);
    FUN_43901a8c(4,0x203c,DAT_43e9b5ac,DAT_43e9bd00);
    DAT_43e99204 = DAT_43e9bcf8;
    DAT_43e992bc = DAT_43e9bd00;
  }
  if ((DAT_43f9a4a6 == '\0') &&
     ((((DAT_43e9b548 == 0x11a || (DAT_43e9b548 == 0x118)) || (DAT_43e9b548 == 0x102)) ||
      (((DAT_43e9b548 == 0x11b || (DAT_43e9b548 == 0x119)) || (DAT_43e9b548 == 0x107)))))) {
    if (*(int *)(DAT_43e99208 + 0x174) == 1) {
      FUN_439c5a04(auStack_54,0,9);
      uStack_52 = 0x40d4;
      uStack_4c = (undefined1)DAT_43e9bcfc;
      auStack_54[0] = 5;
      FUN_435aa02c(auStack_2c);
      FUN_435a92e0(auStack_218);
      iVar23 = FUN_43a49628(auStack_218,0x30001);
      if (iVar23 == 0) {
        iVar23 = FUN_435a9304(auStack_218,auStack_54,9);
        if (iVar23 != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca39e6,iVar23);
          pcVar25 = s_VD_Pre__SetGlobalMsg_err__d_43ca39fa;
          goto LAB_43793456;
        }
        iVar23 = FUN_435aa20c(auStack_2c,0x30001,auStack_218);
        if (iVar23 != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca3a16,iVar23);
          pcVar25 = s_VD_Pre__SendASync_err__d_43ca3a2a;
          goto LAB_43793456;
        }
      }
      else {
        FUN_4378eb78(3,9,1,&DAT_43ca39ba,iVar23);
        pcVar25 = s_VD_Pre__SetSrcId_err__d_43ca39ce;
LAB_43793456:
        FUN_43902718(pcVar25,iVar23);
      }
      FUN_435a92c8(auStack_218);
      FUN_435aa014(auStack_2c);
    }
    DAT_43f9a4a6 = '\x01';
  }
  FUN_437c1740(&DAT_43e99208,&DAT_43e9cc78);
  uVar39 = (DAT_43e9bd50 & 0x3f) >> 4;
  if (uVar39 == 1) {
    DAT_43e9bb08 = DAT_43e9b564;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    DAT_43e9bb0c = DAT_43e9b570;
    DAT_43e9bb10 = 0;
    DAT_43e9bb14 = 0;
    DAT_43e9b590 = 0;
    iVar23 = FUN_43794a44(&DAT_43e99208);
    if (iVar23 != 0) {
      switch(DAT_43e9b9a0) {
      case 0:
        DAT_43e9bb14 = 0;
        break;
      case 1:
        DAT_43e9bb14 = 1;
        break;
      case 2:
        DAT_43e9bb14 = 2;
        break;
      case 3:
        DAT_43e9bb14 = 4;
        break;
      default:
        FUN_4378eb78(5,0,1,&DAT_43c9b47c,s_SyncTask_cpp_43ca3a43,0x93c);
        FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncTask_cpp_43ca3a43,0x93c);
      }
    }
    goto LAB_437937a2;
  }
  if (uVar39 == 2) {
    DAT_43e9bcb4 = DAT_43e9b9b8;
    if (DAT_43e9920c[4] == *(uint *)(DAT_43e99208 + 0x20)) {
      DAT_43e9bb08 = *(undefined4 *)(DAT_43e99208 + 0x1c);
      DAT_43e9bb14 = *(undefined4 *)(DAT_43e99208 + 0x24);
      DAT_43e9bb0c = *(int *)(DAT_43e99208 + 0x28);
      if ((DAT_43e9bd50 & 0x1c0) == 0) {
        DAT_43e9bb10 = (byte)((DAT_43e9bd50 << 0x17) >> 0x1d);
        if (((DAT_43e9bb0c == 1) && ((*(int *)(DAT_43e99208 + 0x538) != 1 || (DAT_43e9bcc0 != 0))))
           && (DAT_43e9bd31 == '\0')) {
          DAT_43e9bb10 = 1;
        }
      }
      else {
        DAT_43e9bb10 = 0;
      }
    }
    goto LAB_437937a2;
  }
  DAT_43e9bb08 = DAT_43e9b564;
  DAT_43e9bb0c = DAT_43e9b570;
  DAT_43e9bb10 = 0;
  iVar23 = FUN_43794a44(&DAT_43e99208);
  uVar20 = DAT_43e9b590;
  if (iVar23 != 0) {
    uVar20 = DAT_43e9b9a0;
  }
  switch(uVar20) {
  case 0:
    DAT_43e9bb14 = 0;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    break;
  case 1:
    goto LAB_4379357a;
  case 2:
    DAT_43e9bb14 = 2;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    break;
  case 3:
    DAT_43e9bb14 = 4;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    break;
  default:
    FUN_4378eb78(5,0,1,&DAT_43c9b47c,s_SyncTask_cpp_43ca3a43,0x91e);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncTask_cpp_43ca3a43,0x91e);
LAB_4379357a:
    DAT_43e9bb14 = 1;
    DAT_43e9bcb4 = DAT_43e9b9b0;
  }
LAB_437937a2:
  FUN_4380f440(&DAT_43e99208,&DAT_43e994d0,&DAT_43e9baec,0);
  if (*(byte *)(iVar26 + 0xb3) != 0) {
    DAT_43e994d0 = (uint)*(byte *)(iVar26 + 0xb3);
  }
  FUN_4380e0cc(&DAT_43e99208,&DAT_43e994d0);
  FUN_4380e138(&DAT_43e99458);
  if ((uint)DAT_43f9a4a7 != (int)(char)DAT_43e9945d) {
    DAT_43f9a4a7 = DAT_43e9945d;
    FUN_43ae913c(auStack_68,&LAB_4378f364_1);
    FUN_439018b0(&DAT_43e992e0,auStack_68,&DAT_43e99458,0);
  }
  if ((1 < DAT_43e9bb18) && ((DAT_43e9bcd4 & 1) != DAT_43e9920c[3])) {
    if (DAT_43e9920c[3] == 0) {
      DAT_43e9bcd4 = 2;
    }
    else {
      DAT_43e9bcd4 = 1;
    }
    DAT_43e9bce4 = DAT_43e9bcd4;
    FUN_4378ea78(0);
  }
  if (DAT_43e9bcc0 == DAT_43e9bad8) {
    uVar39 = DAT_43e9920c[0xf];
    if (uVar39 == 0) {
      iVar23 = FUN_43b00cba(uVar19);
      if ((((iVar23 == 0) || (DAT_43e9b600 != 1)) || ((DAT_43e9bd0c & 1) == 0)) ||
         (DAT_43e9920c[3] != 0)) {
        iVar23 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
        if (iVar23 == 0) {
          if (bVar42) {
            FUN_4378ea78();
            DAT_43e9bcd4 = 0;
            DAT_43e9bce4 = 0;
          }
          else if ((DAT_43e9b548 == 0x121) || (DAT_43e9b548 == 300)) {
            FUN_4378ea78(0);
            DAT_43e9bcd4 = 0;
            DAT_43e9bce4 = 0;
          }
          else if (DAT_43e9bb18 < 2) {
            if (DAT_43e9920c[3] == 0) {
              uVar39 = 0;
LAB_43793978:
              FUN_4378ea78();
              DAT_43e9bcd4 = uVar39;
              DAT_43e9bce4 = uVar39;
            }
          }
          else {
            uVar39 = 1;
            if (DAT_43e9920c[3] == 1) goto LAB_43793978;
          }
        }
        else {
          FUN_4380c7f8(uVar3,auStack_40);
          if (((bVar42) && (uVar39 = bStack_3c & 0x20, (bStack_3c & 0x20) == 0)) &&
             (DAT_43e9bcd4 != 0)) {
            FUN_4378ea78(uVar39);
            DAT_43e9bcd4 = uVar39;
            DAT_43e9bce4 = uVar39;
          }
        }
      }
      else {
        FUN_4378ea78(0);
        DAT_43e9bd0c = DAT_43e9bd0c & 0xfe;
        DAT_43e9bcd4 = 0;
        DAT_43e9bce4 = 0;
      }
    }
    else {
      uVar40 = *(int *)(DAT_43e99210 + 0x1e8) + 1;
      if (uVar39 <= uVar40) {
        if (uVar39 == uVar40) {
          iVar23 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
          if (iVar23 == 0) {
            DAT_43e9bce4 = DAT_43e9bcd4;
            FUN_4378ea78();
          }
        }
        else {
          FUN_4378ea78(0);
          DAT_43e9bcd4 = DAT_43e9920c[0xf] - 1;
          DAT_43e9bce4 = DAT_43e9920c[0xf] - 1;
        }
      }
    }
  }
  uVar39 = DAT_43e9ba54;
  switch(*(undefined1 *)(iVar26 + 1)) {
  case 1:
    uVar39 = 0;
    break;
  case 2:
    uVar39 = 2;
    break;
  case 3:
    uVar39 = 1;
    break;
  case 4:
    uVar39 = 3;
  }
  if (((uint)DAT_43e9bca8 != (uVar39 & 3) >> 1) || ((uint)DAT_43e9bca9 != (uVar39 & 1))) {
    DAT_43e9bca9 = (byte)(uVar39 & 1);
    DAT_43e9bca8 = (byte)((uVar39 << 0x1e) >> 0x1f);
    FUN_4378ea78(0);
  }
  iVar26 = FUN_43ae8d4e();
  if ((iVar26 == 0) || (DAT_43f9a4b8 != '\0')) {
    FUN_4378ea78(1);
    DAT_43f9a4b8 = '\0';
  }
  uVar20 = DAT_44025f5c;
  iVar26 = FUN_43ae8cc8(DAT_44025f5c);
  if (iVar26 != 0) {
    DAT_43e9bce4 = DAT_43e9bcd4;
  }
  DAT_43e9bcd9 = '\x01' - (char)DAT_43e9bcd4;
  if (1 < DAT_43e9bcd4) {
    DAT_43e9bcd9 = '\0';
  }
  DAT_43e9bcd8 = 1 >= DAT_43e9bcd4;
  DAT_43e9bce8 = '\x01' - (char)DAT_43e9bce4;
  if (1 < DAT_43e9bce4) {
    DAT_43e9bce8 = '\0';
  }
  DAT_43e9d029 = FUN_43ae8ccc(uVar20);
  if ((DAT_43e9bd50 & 0x100000) == 0) {
    uStack_30 = *(undefined4 *)(DAT_43e99214 + 4);
  }
  else {
    uStack_30 = *(undefined4 *)(DAT_43e99214 + 0xc);
  }
  iVar26 = FUN_43b00cba(uVar19);
  if ((iVar26 != 0) && (*(int *)(DAT_43e99208 + 0xb8) == 1)) {
    FUN_43b00e4c(uVar19,&DAT_43e99208,&uStack_30);
  }
  DAT_43e9bb28 = FUN_4380e15c(&DAT_43e99208,uStack_30,&DAT_43e99320,
                              DAT_43e9bcd4 + DAT_43e9920c[3] & 1);
  iVar23 = FUN_437955ec();
  iVar26 = DAT_4402546c;
  if (iVar23 == 1) {
    DAT_43e9bcdc = DAT_43e9bb28;
    if (DAT_43e9bce8 != '\0') {
      DAT_43e9bce0 = DAT_43e9bce0 + '\x01';
    }
  }
  else if (iVar23 == 2) {
    if (((*(byte *)(DAT_4402546c + 0x22) & 1) == 0) &&
       (uVar39 = *(uint *)(DAT_43e99214 + 8), DAT_43e9bbb8 < 2)) {
      uVar40 = DAT_43e9bb18;
      if (DAT_43e9bcd9 != '\0') {
        uVar40 = DAT_43e9bb28;
      }
      if (uVar40 != 0) {
        if (uVar40 == 1) {
          uVar40 = 1;
        }
        else {
          uVar40 = 2;
        }
        if (uVar39 < uVar40) {
          uVar39 = uVar40;
        }
      }
      if ((1 < uVar39) &&
         (uVar39 = FUN_43acf19e(uVar39,2), (DAT_43e9bce4 + DAT_43e9920c[3] & 1) != 0)) {
        uVar39 = 1;
      }
    }
    else {
      DAT_43e9bcdc = DAT_43e9bb28;
      uVar39 = DAT_43e9bcdc;
    }
    DAT_43e9bcdc = uVar39;
    if (DAT_43e9bce8 != '\0') {
      DAT_43e9bce0 = DAT_43e9bce0 + '\x01';
    }
  }
  else if (iVar23 == 0) {
    DAT_43e9bcdc = DAT_43e9bb28;
  }
  if (DAT_43e9bb30 != 0x11) {
    uVar19 = DAT_43e9bcac;
    if (DAT_43e9bd48 != 0) {
      uVar19 = 10;
    }
    DAT_43e9bcb0 = FUN_43acc1a6(DAT_43e9bb30,uVar19);
  }
  if ((DAT_43e9bb30 == 0x12) || (DAT_43e9bb30 == 0x3f)) {
    DAT_43e9baec = 1;
  }
  else if (DAT_43e9bb30 == 8) {
    DAT_43e9baec = 2;
  }
  else {
    DAT_43e9baec = *(undefined4 *)(DAT_44020e90 + 0x40);
  }
  if (*(char *)(DAT_4401f1d0 + 0x43) == '\x01') {
    DAT_43e9bcb8 = 1;
  }
  else {
    DAT_43e9bcb8 = 0;
    if (DAT_43e9b624 != '\0') {
      DAT_43e9bcb8 = DAT_43e9d310 ^ 1;
    }
  }
  if (DAT_43e9d310 == 0) {
    DAT_43e9bcbc = *(undefined4 *)(DAT_43e99208 + 0xbc);
  }
  else {
    DAT_43e9bcbc = 1;
  }
  DAT_43e9bb2d = DAT_43e9bb1c;
  if (DAT_43e9bcd9 != '\0') {
    DAT_43e9bb2d = DAT_43e9bb1c + '\x01';
  }
  DAT_43e9bdb4 = FUN_43ae8d10(uVar20);
  DAT_43e9bdb8 = FUN_43ae8d14(uVar20);
  if (DAT_43e99320 != DAT_43e9939c) {
    FUN_43901a8c(4,0x203d);
    DAT_43e9939c = DAT_43e99320;
  }
  uVar41 = DAT_43e9bcd4;
  uVar40 = DAT_43e9bb28;
  uVar39 = DAT_43e9bb18;
  if ((*(byte *)(iVar26 + 3) & 1) != 0) {
    uVar36 = *DAT_43e9920c;
    uVar38 = DAT_43e9920c[3];
    uVar27 = FUN_437955ec();
    uVar5 = DAT_43e9bd58;
    uVar17 = DAT_43e9bce4;
    uVar16 = DAT_43e9bcdc;
    uVar22 = DAT_43e9bb20;
    uVar4 = DAT_43e9b548;
    uVar21 = DAT_43e994dc;
    uVar2 = DAT_43e994d0;
    uVar19 = DAT_43e9932c;
    iVar23 = DAT_43e99320;
    uVar33 = DAT_43e9920c[4];
    uVar34 = DAT_43e9920c[0xc];
    uVar28 = DAT_43e9920c[0xf];
    uVar29 = FUN_43ae8cd0(uVar20);
    uVar30 = FUN_43ae8cc8(uVar20);
    uVar31 = FUN_43ae8ccc(uVar20);
    FUN_4378eb78(3,9,1,&DAT_43ca3a50,uVar36,uVar38,uVar39,uVar40,uVar41,uVar27,uVar22,uVar16,uVar17,
                 uVar33,uVar34,uVar28,uVar4,uVar5,iVar23,uVar2,uVar19,uVar21,uVar29,uVar30,uVar31);
    uVar2 = DAT_43e9bcd4;
    uVar41 = DAT_43e9bb28;
    uVar40 = DAT_43e9bb18;
    uVar28 = *DAT_43e9920c;
    uVar36 = DAT_43e9920c[3];
    uVar27 = FUN_437955ec();
    uVar5 = DAT_43e9bd58;
    uVar17 = DAT_43e9bce4;
    uVar16 = DAT_43e9bcdc;
    uVar22 = DAT_43e9bb20;
    uVar4 = DAT_43e9b548;
    uVar21 = DAT_43e994dc;
    uVar39 = DAT_43e994d0;
    uVar19 = DAT_43e9932c;
    iVar23 = DAT_43e99320;
    uVar34 = DAT_43e9920c[4];
    uVar33 = DAT_43e9920c[0xc];
    uVar38 = DAT_43e9920c[0xf];
    uVar29 = FUN_43ae8cd0(uVar20);
    uVar30 = FUN_43ae8cc8(uVar20);
    uVar31 = FUN_43ae8ccc(uVar20);
    FUN_43902718(s_vfc_d__d__shut_d_>_d__d__zaf__d__43ca3a64,uVar28,uVar36,uVar40,uVar41,uVar2,
                 uVar27,uVar22,uVar16,uVar17,uVar34,uVar33,uVar38,uVar4,uVar5,iVar23,uVar39,uVar19,
                 uVar21,uVar29,uVar30,uVar31);
  }
  uVar19 = FUN_43b039fc(&DAT_43e9948c,&DAT_43e994d0);
  FUN_43780080(&DAT_43e99208,&DAT_43e9d3b4,uVar19);
  FUN_4380db04(&DAT_43e99208,&DAT_43e9d3b4);
  FUN_4378c4d0(&DAT_43e9baec);
  FUN_4378f7a0(0xb2a);
  iVar23 = FUN_43ae8cd0(uVar20);
  if (iVar23 == 0) {
    FUN_43ae8cda(uVar20);
  }
  FUN_4377e0e8(&DAT_43e99208);
  FUN_437217f8(DAT_43e9920c[6]);
  FUN_437b4db8(&DAT_43e99208,&DAT_43e9c7d8);
  FUN_437c194c(&DAT_43e99208,&DAT_43e9cc78);
  thunk_FUN_437d0e5c(&DAT_43e99208,&DAT_43e9ce1c);
  FUN_4378f754(&DAT_43e9b548,&DAT_43e9d024);
  FUN_43af6784(&DAT_43e9ced8,&DAT_43e99208);
  FUN_4378f7a0(0xb51);
  if (*DAT_43e9921c == '\0') {
    uVar19 = 0;
    if (*(char *)(iVar26 + 0xec) == '\0') {
      uVar19 = *(undefined4 *)(DAT_43e9921c + 4);
    }
  }
  else {
    uVar19 = 0;
  }
  uVar20 = FUN_43814138();
  iVar23 = FUN_43799a38(1,1,*DAT_43e9920c,0);
  if (iVar23 == 0) {
    iVar23 = FUN_43799a38(1,2,*DAT_43e9920c,0);
    bVar42 = iVar23 != 0;
  }
  else {
    bVar42 = true;
  }
  DAT_43e9bd34 = FUN_43b03c62(uVar20,uVar19,bVar42);
  if ((*(char *)(iVar26 + 0xed) == '\0') &&
     ((*(int *)(DAT_44020e90 + 0x44) == 3 || (*(int *)(DAT_44020e90 + 0x44) == 4)))) {
    if ((*(ushort *)(DAT_43e99210 + 0x264) & 0x1ff) >> 6 != 0) {
      uVar19 = FUN_438148f0();
      uVar20 = FUN_43799a38(1,10,*DAT_43e9920c,0);
      goto LAB_4379405e;
    }
    auStack_48[0] = DAT_43e9bd86;
    uStack_44 = DAT_43e9bb08;
    thunk_FUN_438aaab8(auStack_48,auStack_3a8);
    uVar19 = FUN_438148f0();
    uVar20 = FUN_43799a38(1,10,*DAT_43e9920c,0);
    puVar44 = auStack_348;
    puVar35 = auStack_3a8;
    puVar45 = auStack_2e0;
    puVar46 = auStack_280;
  }
  else {
    uVar19 = FUN_438148f0();
    uVar20 = FUN_43799a38(1,10,*DAT_43e9920c,0);
LAB_4379405e:
    puVar35 = (undefined1 *)0x0;
    uStack_2e8 = 0;
    puVar44 = (undefined1 *)0x0;
    uStack_2e4 = 0;
    puVar45 = (undefined1 *)0x0;
    uStack_220 = 0;
    puVar46 = (undefined1 *)0x0;
    uStack_21c = 0;
  }
  FUN_4381493c(&uStack_3b8,uVar19,puVar35,uStack_2e8,puVar44,uStack_2e4,puVar45,uStack_220,puVar46,
               uStack_21c,uVar20);
  DAT_43e9bd38 = uStack_3b8;
  DAT_43e9bd3c = uStack_3b4;
  DAT_43e9bd40 = uStack_3b0;
  DAT_43e9bd44 = uStack_3ac;
  FUN_43ae8faa(&DAT_43e99514,&DAT_43e9b548);
  FUN_43ae8eae(&DAT_43e99514,&DAT_43e993a4);
  if ((DAT_43e9bd4c & 4) == 0) {
    FUN_43560da8(0x11,4);
    FUN_43ae9148(auStack_7c,&LAB_43791454_1);
    FUN_437b4f2c(&DAT_43e993a4,auStack_7c,4);
  }
  if ((DAT_43e9bd4c & 2) == 0) {
    FUN_43560da8(0x11,2);
    FUN_43ae9148(auStack_90,&LAB_43ae8d46_1);
    FUN_437c297c(&DAT_43e993a4,auStack_90,2);
  }
  if ((DAT_43e9bd4c & 0x80) == 0) {
    FUN_43560da8(0x11,0x80);
    FUN_43ae9148(auStack_a4,&LAB_43ae8d46_1);
    FUN_437b66e0(&DAT_43e993a4,auStack_a4,0x80);
  }
  if ((DAT_43e9bd4c & 8) == 0) {
    FUN_43560da8(0x11,8);
    FUN_43ae9148(auStack_b8,&LAB_43ae8d46_1);
    FUN_4379fd58(&DAT_43e993a4,auStack_b8,8);
  }
  if ((DAT_43e9bd4c & 0x40) == 0) {
    FUN_43560da8(0x11,0x40);
    FUN_43ae9148(auStack_cc,&LAB_43ae8d46_1);
    FUN_437d9e00(&DAT_43e993a4,auStack_cc,0x40);
  }
  if ((DAT_43e9bd4c & 0x20) == 0) {
    FUN_43560da8(0x11,0x20);
    FUN_43ae9148(auStack_e0,&LAB_43ae8d46_1);
    FUN_437d0c90(&DAT_43e993a4,auStack_e0,0x20);
  }
  if ((DAT_43e9bd4c & 0x200) == 0) {
    FUN_43560da8(0x11,0x200);
    uVar19 = FUN_4378dd84();
    FUN_43ae9148(auStack_f4,&LAB_43ae8d46_1);
    FUN_437b82d8(&DAT_43e993a4,uVar19,auStack_f4,0x200);
  }
  bVar42 = (DAT_43e9bd54 & 0x40) != 0;
  if (bVar42) {
    uVar39 = DAT_43e9920c[4];
  }
  else {
    uVar39 = DAT_43e9920c[4];
  }
  thunk_FUN_43721e60(!bVar42,uVar39 == 3);
  if (DAT_43e9bb5c == 0) {
    if ((DAT_43e9bd54 & 0x40) != 0) {
      FUN_43795bf0();
      goto LAB_437944b8;
    }
    FUN_43ae93ce();
    uVar18 = 0;
  }
  else {
    if (uVar3 == 0x103) {
      if (DAT_43e9b548 == 0x14a) {
        FUN_43ae93dc();
        FUN_4378f3f8(1);
        DAT_43e9bd30 = 1;
      }
      goto LAB_437944be;
    }
    if (uVar3 < 0x104) {
      if (uVar3 < 0x100) goto LAB_437944be;
      if (uVar3 < 0x102) {
        if (1 < (ushort)(DAT_43e9b548 - 0x105)) goto LAB_437944be;
        FUN_43795c14();
        uVar18 = 0;
        goto LAB_437944ba;
      }
    }
    else {
      if (uVar3 == 0x10e) {
        if ((((DAT_43e9b548 == 0x102) || (DAT_43e9b548 == 0x107)) || (DAT_43e9b548 == 0x11a)) ||
           (((DAT_43e9b548 == 0x11b || (DAT_43e9b548 == 0x118)) ||
            ((DAT_43e9b548 == 0x119 || (DAT_43e9b548 == 0x132)))))) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
        }
        goto LAB_437944be;
      }
      if (uVar3 < 0x10f) {
        if (uVar3 != 0x107) goto LAB_437944be;
      }
      else if (uVar3 != 0x132) {
        if ((uVar3 == 0x14a) && ((ushort)(DAT_43e9b548 - 0x102) < 2)) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
          DAT_43e9bd30 = 0;
        }
        goto LAB_437944be;
      }
    }
    if (DAT_43e9b548 != 0x10e) goto LAB_437944be;
    FUN_43ae93dc();
LAB_437944b8:
    uVar18 = 1;
  }
LAB_437944ba:
  FUN_4378f3f8(uVar18);
LAB_437944be:
  if ((*(char *)(iVar26 + 0x70) == '\0') && (iVar23 = FUN_437999e4(1,0xe), iVar23 != 0)) {
    FUN_43b71948();
  }
  if ((*DAT_43e9920c & 0xfffff) == 0) {
    FUN_43728be0();
  }
  FUN_4378f7a0(0xc39);
  if (*(char *)(iVar26 + 0xbf) != '\0') {
    FUN_43ae9124(auStack_108,DAT_4401f7cc);
    FUN_439018b0(&DAT_43e99380,auStack_108,2,0);
  }
  FUN_43560da8(0x1a,0x40);
  FUN_43ae129a(4);
  if (param_1 != *DAT_43e9920c) {
    iVar23 = thunk_FUN_436cd00c();
    uVar39 = iVar23 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca3acb,param_1,*DAT_43e9920c,uVar39);
    FUN_43902718(s_VD_Pre__overflow__dV__>__dV__dus_43ca3adf,param_1,*DAT_43e9920c,uVar39);
    FUN_4378f988(4,0,uVar39);
    if ((*(byte *)(iVar26 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Pre_E_OF_43ca3b00);
    }
    if ((*(byte *)(iVar26 + 0x1b) & 2) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(byte *)(iVar26 + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Pre_E_43ca3b0c);
  }
  return;
}


/* ENTRY 4379155c */

void FUN_4379155c(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uStack_44;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  uint uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 auStack_24 [8];
  
  iVar1 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Seq_S_43ca34b3);
  }
  if (param_1 == *DAT_43e9920c) {
    iVar2 = FUN_43560de0(0x1a,0x40,0,auStack_24,4);
    if (iVar2 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,&DAT_43ca3507,*DAT_43e9920c,uStack_30);
      FUN_43902718(s_VD_Sequence__VD_Pre_wait_timeout_43ca351b,*DAT_43e9920c,uStack_30);
    }
    FUN_43560dc4(0x1a,0xffffffbf);
    FUN_43ae1292(1);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = '\x01';
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_43560dc4(0x1a,0xfffffeff);
    iVar2 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
    if (iVar2 == 0) {
      uVar6 = 0;
    }
    else if (DAT_43e99338 == 0) {
      if (DAT_43f9a4b8 == '\0') {
        if (DAT_43e9bcd9 == '\0') {
          uVar6 = 0;
        }
        else {
          uVar6 = 0x43e99324;
        }
      }
      else {
        uVar6 = 0;
      }
    }
    else {
      uVar6 = 0;
    }
    puVar3 = (undefined1 *)FUN_4379ce18();
    thunk_FUN_43af2858(DAT_43e99230,puVar3);
    *puVar3 = 0;
    uVar4 = FUN_43ae8cd0(DAT_44025f5c);
    DAT_43e9bd58 = FUN_43796954(uVar4,uVar6,&DAT_43e99208);
    iVar2 = FUN_437999e4(1,0xd);
    if (((iVar2 != 0) && (DAT_43e9bb18 != 0)) && ((DAT_43e9bbb8 == 1 || (DAT_43e9920c[3] == 0)))) {
      uStack_44 = FUN_43ae9332(DAT_43e9bb30);
      uStack_40 = 0;
      uStack_3f = 0;
      iVar2 = FUN_43795610(DAT_43e9bcd9);
      if (((iVar2 != 0) && (DAT_43f9a4b8 == '\0')) && (DAT_43e9bce8 != '\0')) {
        uStack_3f = 1;
      }
      uStack_3c = (uint)(*(int *)(DAT_43e99208 + 0x548) != 0);
      uStack_38 = *(undefined4 *)(DAT_43e99208 + 0x54c);
      iVar2 = FUN_437956c8(&DAT_43e9bba4,&uStack_44);
      if (iVar2 != 0) {
        FUN_4378eb78(3,9,1,&DAT_43ca3309,iVar2);
        FUN_43902718(s__DFE_SetParam_Error_0x_x_43ca331d,iVar2);
      }
    }
    FUN_43900380();
    FUN_439cdbc8();
    uStack_28 = 0;
    uStack_2c = 0;
    FUN_43728c18(0,&uStack_28,&uStack_2c);
    FUN_43b6d334(uStack_28,uStack_2c);
    FUN_43560da8(0x1a,0x100);
    FUN_43ae129a(1);
    if ((param_1 != *DAT_43e9920c) && (iVar2 = FUN_43ae8d4e(), iVar2 != 0)) {
      iVar2 = thunk_FUN_436cd00c();
      uVar5 = (uint)(iVar2 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca3546,param_1,*DAT_43e9920c,uVar5);
      FUN_43902718(s_VD_Sequence__overflow__dV__>__dV_43ca355a,param_1,*DAT_43e9920c,uVar5);
      FUN_4378f988(4,1,uVar5);
      if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Seq_E_OF_43ca3580);
      }
      if ((*(byte *)(iVar1 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43791528();
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Seq_E_43ca358c);
    }
  }
  else {
    iVar2 = FUN_43ae8d4e();
    if (iVar2 != 0) {
      iVar2 = thunk_FUN_436cd00c();
      uVar5 = (uint)(iVar2 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca34bc,param_1,*DAT_43e9920c,uVar5);
      FUN_43902718(s_VD_Sequence__start_delayed__dV___43ca34d0,param_1,*DAT_43e9920c,uVar5);
      FUN_4378f988(3,1,uVar5);
      if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Seq_S_OF_43ca34fb);
      }
      if ((*(byte *)(iVar1 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* ENTRY 4379210c */

void FUN_4379210c(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  byte bVar8;
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined1 auStack_2c [4];
  uint uStack_28;
  undefined1 auStack_24 [4];
  
  iVar2 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Post_S_43ca2f4b);
  }
  if (param_1 == *DAT_43e9920c) {
    FUN_43ae1292(4);
    iVar3 = FUN_43ae8d4e();
    if (iVar3 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_43728c70();
    FUN_4378f7a0(0xd35);
    DAT_43e9d394 = FUN_4377fdf8();
    FUN_43560e00(0x11,auStack_2c);
    iVar3 = FUN_4378e90c();
    if (iVar3 != 0) {
      uStack_28 = uStack_28 & 0xfffffffb | DAT_43e9bd4c & 4;
    }
    DAT_43e9bd4c = uStack_28;
    if (DAT_43f79b84 != 0) {
      DAT_43f79b82 = DAT_43f79b82 + 1;
      if (DAT_43f79b84 < DAT_43f79b82) {
        DAT_43f79b82 = 1;
        iVar3 = 0;
        do {
          *(undefined2 *)((int)&DAT_43f79b2e + iVar3) = 0;
          *(undefined2 *)((int)&DAT_43f79b48 + iVar3) = 0;
          *(undefined2 *)((int)&DAT_43f79b66 + iVar3) = 0;
          iVar3 = iVar3 + 2;
        } while (iVar3 != 0x1a);
      }
    }
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      if ((DAT_43e9bd4c & 4) == 0) {
        DAT_43e9d398 = FUN_437b4d64();
        FUN_43ae8e2c(&DAT_43e9b548,&DAT_43e99208);
        DAT_43f79b4c = 0;
      }
      else {
        DAT_43f79b6a = DAT_43f79b6a + 1;
        DAT_43f79b4c = DAT_43f79b4c + 1;
      }
    }
    if ((DAT_43e9bd4c & 8) == 0) {
      DAT_43e9d3a0 = FUN_4379fc20();
      FUN_43ae8e5c(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b4e = 0;
    }
    else {
      DAT_43f79b6c = DAT_43f79b6c + 1;
      DAT_43f79b4e = DAT_43f79b4e + 1;
    }
    if ((DAT_43e9bd4c & 0x20) == 0) {
      DAT_43e9d3a4 = FUN_437d0bc8();
      FUN_43ae8e74(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b52 = 0;
    }
    else {
      DAT_43f79b70 = DAT_43f79b70 + 1;
      DAT_43f79b52 = DAT_43f79b52 + 1;
    }
    if ((DAT_43e9bd4c & 0x40) == 0) {
      DAT_43e9d3a8 = FUN_437d9930();
      FUN_43ae8e84(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b54 = 0;
    }
    else {
      DAT_43f79b72 = DAT_43f79b72 + 1;
      DAT_43f79b54 = DAT_43f79b54 + 1;
    }
    if ((DAT_43e9bd4c & 0x80) == 0) {
      DAT_43e9d3ac = FUN_437b6614();
      FUN_43ae8e9a(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b56 = 0;
    }
    else {
      DAT_43f79b74 = DAT_43f79b74 + 1;
      DAT_43f79b56 = DAT_43f79b56 + 1;
    }
    if ((DAT_43e9bd4c & 0x200) == 0) {
      DAT_43e9d3b0 = FUN_437b8230();
      FUN_43ae8ea4(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b5a = 0;
    }
    else {
      DAT_43f79b78 = DAT_43f79b78 + 1;
      DAT_43f79b5a = DAT_43f79b5a + 1;
    }
    FUN_4378f7a0(0xd96);
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      FUN_4378f7a0(0xda0);
      FUN_437b4e28(&DAT_43e99208);
      FUN_4378f7a0(0xda2);
    }
    FUN_437c1bb4(&DAT_43e99208);
    thunk_FUN_43b7c7da(&DAT_43e99208);
    FUN_437b0244(&DAT_43e99208,&DAT_43e9d022);
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      FUN_4378f7a0(0xda9);
      FUN_43aef444(&DAT_43e99208,&DAT_43e9c7d8);
      FUN_4378f7a0(0xdad);
    }
    FUN_437c1b98(&DAT_43e99208,&DAT_43e9cc78);
    thunk_FUN_43b7c7dc(&DAT_43e99208,&DAT_43e9ce19);
    iVar3 = FUN_43560de0(0x1a,0x100,0,auStack_24,4);
    if (iVar3 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,&DAT_43ca3777,*DAT_43e9920c,uStack_30);
      FUN_43902718(s_VD_Post__VD_Sequence_wait_timeou_43ca378b,*DAT_43e9920c,uStack_30);
      FUN_43560da8(0x1a,0x100);
    }
    if (*(char *)(iVar2 + 0x70) == '\0') {
      iVar3 = FUN_437999e4(1,0xe);
      if (iVar3 != 0) {
        if ((DAT_43e9bb1f == '\0') || (DAT_43e9920c[3] != 0)) {
          FUN_439e21c0();
        }
        FUN_439e2184();
      }
      FUN_439fd76c();
    }
    FUN_4378f7a0(0xdd0);
    FUN_437967e8(&DAT_43e99208);
    FUN_4378f7a0(0xdd3);
    FUN_43ada220(auStack_48,0x4378f411);
    FUN_439018b0(&DAT_43e99380,auStack_48,param_1,0);
    bVar8 = *(byte *)(iVar2 + 0x1f) & 8;
    if (((*(byte *)(iVar2 + 0x1f) & 8) == 0) &&
       (iVar4 = FUN_436e8328(), iVar3 = DAT_4401f1d0, iVar4 != 0)) {
      iVar4 = DAT_43e9920c[9];
      iVar5 = DAT_43e9920c[2];
      uVar1 = *(undefined2 *)(DAT_4401f1d0 + 0x2e);
      FUN_43ae863c(auStack_5c,bVar8);
      FUN_436ccd9c(6,iVar4 + iVar5,uVar1,auStack_5c);
      iVar5 = DAT_43e9920c[9];
      iVar6 = DAT_43e9920c[2];
      iVar4 = FUN_43ada230();
      uVar1 = *(undefined2 *)(iVar3 + 0x2c);
      FUN_43ae863c(auStack_70,bVar8);
      FUN_436ccd9c(7,iVar5 + iVar6 + iVar4 * 2,uVar1,auStack_70);
    }
    FUN_43ae129a(4);
    if (param_1 != *DAT_43e9920c) {
      iVar3 = thunk_FUN_436cd00c();
      uVar7 = (uint)(iVar3 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca37b7,param_1,*DAT_43e9920c,uVar7);
      FUN_43902718(s_VD_Post__overflow__dV__>__dV__du_43ca37cb,param_1,*DAT_43e9920c,uVar7);
      FUN_4378f988(4,2,uVar7);
      if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Post_E_OF_43ca37ed);
      }
      if ((*(byte *)(iVar2 + 0x1b) & 8) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43901480(0);
    if ((*(byte *)(iVar2 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Post_E_43ca2f58);
    }
  }
  else {
    iVar3 = thunk_FUN_436cd00c();
    uVar7 = (uint)(iVar3 - DAT_43e9920c[2]) >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca372f,param_1,*DAT_43e9920c,uVar7);
    FUN_43902718(s_VD_Post__start_delayed__dV__>__d_43ca3743,param_1,*DAT_43e9920c,uVar7);
    FUN_4378f988(3,2,uVar7);
    if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Post_S_OF_43ca376a);
    }
    if ((*(byte *)(iVar2 + 0x1b) & 8) != 0) {
      FUN_4378ec60();
    }
  }
  return;
}


/* ENTRY 43791a7c */

void FUN_43791a7c(int param_1)

{
  undefined1 *puVar1;
  char *pcVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int *piVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  undefined4 uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined1 uStack_d8;
  undefined1 auStack_d4 [20];
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  undefined1 auStack_84 [20];
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  ushort uStack_2c;
  ushort uStack_2a;
  
  FUN_43795e7c();
  FUN_43796424();
  if (DAT_43f9a429 == '\0') {
    FUN_43ae863c(auStack_48,DAT_44025280);
    FUN_436ccee4(0x1e,1,auStack_48);
    FUN_43ae863c(auStack_5c,DAT_44023b9c);
    FUN_436ccee4(0x17,1,auStack_5c);
    DAT_43f9a429 = '\x01';
  }
  iVar13 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0xc) & 1) != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca35b6);
    FUN_43902718(&DAT_43ca35ca);
  }
  thunk_FUN_4386116c();
  thunk_FUN_436e06f4();
  piVar6 = DAT_44022438;
  puVar3 = DAT_440216d4;
  if ((*(byte *)(iVar13 + 4) & 1) != 0) {
    iVar14 = *DAT_44022438;
    uVar12 = *DAT_440216d4;
    uVar7 = FUN_43795d2c();
    puVar5 = DAT_44022084;
    puVar4 = DAT_44021cf8;
    FUN_4378eb78(3,9,1,&DAT_43ca35cf,iVar14,uVar12,uVar7,*DAT_44022084,*DAT_44021cf8);
    iVar14 = *piVar6;
    uVar12 = *puVar3;
    uVar7 = FUN_43795d2c();
    FUN_43902718(s_CamV__10d__CamOutV__10d__Blank___43ca35e3,iVar14,uVar12,uVar7,*puVar5,*puVar4);
    *piVar6 = param_1;
    *puVar3 = 0;
    *puVar5 = 0;
    *puVar4 = 0;
  }
  FUN_43904008();
  FUN_43901638(0);
  FUN_43901638(4);
  FUN_43901638(8);
  FUN_43901638(5);
  pcVar2 = DAT_440223fc;
  iVar14 = DAT_4401f1d0;
  if (((*(byte *)(DAT_4401f1d0 + 0x29) & 0xf) != 0xf) && (*DAT_440223fc != '\0')) {
    FUN_43901638(9);
    *pcVar2 = '\0';
  }
  pcVar2 = DAT_44020c34;
  if (((*(byte *)(iVar14 + 0x29) & 0xf0) != 0xf0) && (*DAT_44020c34 != '\0')) {
    FUN_43901638(10);
    *pcVar2 = '\0';
  }
  FUN_43901768();
  FUN_43901748();
  FUN_43903f18();
  DAT_43e9d026 = DAT_43e9bb2c;
  FUN_4378e1a4(param_1,DAT_43e9bb2c,&DAT_43e9baa8);
  iVar8 = FUN_437fe4f4();
  DAT_43e9bb1f = iVar8 != 0;
  if (DAT_43ff36bc != 7) {
    FUN_4378eb78(3,9,1,&DAT_43ca3626,param_1,DAT_43ff36bc);
    FUN_43902718(s_HS_jump__d__d_8V_43ca363a,param_1,DAT_43ff36bc);
  }
  DAT_43e9d027 = 0;
  DAT_43e9d028 = 0;
  DAT_43ff36bc = 0;
  DAT_43e9b544 = 1;
  iVar15 = *DAT_43e9920c;
  iVar8 = FUN_4379a898();
  DAT_43e9bb1e = *(undefined1 *)(iVar8 + 0x5c);
  DAT_43e9bb1d = DAT_43e9bcd9;
  if (DAT_43e9bcd9 != '\0') {
    DAT_43e9bb1c = DAT_43e9bb1c + '\x01';
    DAT_43e9bb18 = DAT_43e9bb28;
    DAT_43e9bcd4 = DAT_43e9bb28;
    FUN_43ae8cd4(DAT_44025f5c);
  }
  if (DAT_43e9bcd4 != 0) {
    DAT_43e9bcd4 = DAT_43e9bcd4 + -1;
  }
  DAT_43e9bb25 = DAT_43e9bce8;
  if (DAT_43e9bce8 != '\0') {
    DAT_43e9bb24 = DAT_43e9bce0;
    DAT_43e9bb20 = DAT_43e9bcdc;
    DAT_43e9bce4 = DAT_43e9bcdc;
  }
  if (DAT_43e9bce4 != 0) {
    DAT_43e9bce4 = DAT_43e9bce4 + -1;
  }
  if ((DAT_43e9946c == DAT_43ff36c8) && (DAT_43f9a4bc < 5)) {
    DAT_43f9a4bc = DAT_43f9a4bc + 1;
    uVar11 = (uint)DAT_43f9a4bc;
    uVar10 = (uint)DAT_43f79b62;
    FUN_4378eb78(3,9,1,&DAT_43ca364b,uVar10,uVar11);
    FUN_43902718(s_TaskHS_is_stopping_after__dLINE___43ca365f,DAT_43f79b62,DAT_43f9a4bc);
    if (DAT_43f9a4bc == 1) {
      FUN_43901a8c(3,1,DAT_43f79b62,0);
    }
    if (DAT_43f9a4bc == 5) {
      FUN_4378eb78(3,9,1,&DAT_43ca3682,uVar10,uVar11);
      FUN_43902718(s_TaskHS_is_stopping_log_end_43ca3696);
    }
  }
  DAT_43ff36c8 = DAT_43e9946c;
  if (DAT_43e99460 != (code *)0x0) {
    uStack_f0 = DAT_43ff36bc;
    iVar8 = FUN_4378f9b4();
    uStack_ec = *(undefined4 *)(*(int *)(iVar8 + 8) + 0x1e8);
    iVar8 = FUN_4378f9b4();
    uStack_e8 = *(undefined4 *)(*(int *)(iVar8 + 8) + 0x3c);
    iVar8 = FUN_4378f9b4();
    uStack_dc = *(undefined4 *)(*(int *)(iVar8 + 4) + 0x18);
    iVar8 = FUN_4378f9b4();
    uStack_e0 = *(undefined4 *)(*(int *)(iVar8 + 0xc) + 0x5c);
    uStack_d8 = FUN_43ae1252();
    (*DAT_43e99460)(&uStack_f0);
  }
  FUN_43ada220(auStack_70,0x43792a0d);
  FUN_439018b0(&DAT_43e9b528,auStack_70,iVar15,0);
  FUN_43ada220(auStack_84,0x4378fef5);
  FUN_439018b0(&DAT_43e9b528,auStack_84,iVar15 << 8,0);
  iVar8 = DAT_43e9920c[0xb];
  FUN_43ae863c(auStack_98,0x437927c5);
  FUN_436ccd9c(1,param_1 + iVar8,1,auStack_98);
  if ((*(byte *)(iVar13 + 0x1f) & 1) == 0) {
    FUN_4378d818(param_1,DAT_43e9920c[9]);
  }
  if ((*(byte *)(iVar13 + 0x1f) & 2) == 0) {
    FUN_4378db0c(param_1,DAT_43e9920c[9]);
  }
  DAT_43f9a426 = 0;
  iVar8 = FUN_436e8328();
  if (iVar8 == 1) {
    FUN_43ae72f6(&uStack_34);
    DAT_43e9936c = (uint)uStack_30;
    DAT_43e99370 = (uint)uStack_2e;
    if ((DAT_43e9920c[5] != 1) &&
       (DAT_43e9936c = (uint)uStack_2c, DAT_43e99370 = (uint)uStack_2a, DAT_43e9920c[5] != 2)) {
      DAT_43e9936c = (uint)uStack_34;
      DAT_43e99370 = (uint)uStack_32;
    }
    uVar16 = DAT_43e9936c << 1;
    DAT_43e99370 = DAT_43e99370 << 1;
    DAT_43e9936c = uVar16;
    uVar9 = FUN_43ae8c60();
    uVar11 = DAT_43e99370;
    uVar10 = DAT_43e9936c;
    if (((uVar16 < uVar9) || (iVar8 = FUN_43ae8c60(), uVar11 < iVar8 + uVar10)) ||
       ((uint)DAT_43e9920c[9] < DAT_43e99370)) {
      FUN_4378eb78(3,9,1,&DAT_43ca36b1,DAT_43e9936c,DAT_43e99370,DAT_43e9920c[9]);
      FUN_43902718(s_LM__GetSendTiming_value_error_1s_43ca36c5,DAT_43e9936c,DAT_43e99370,
                   DAT_43e9920c[9]);
      DAT_43e9936c = 0;
      DAT_43e99370 = 0;
    }
    else if ((*(byte *)(iVar13 + 0x1f) & 4) == 0) {
      iVar13 = param_1 + DAT_43e9936c;
      FUN_43ae863c(auStack_ac,&LAB_43792750_1);
      FUN_436ccd9c(5,iVar13,1,auStack_ac);
      DAT_43f9a426 = 1;
      iVar13 = FUN_4378e90c();
      if (iVar13 != 0) {
        uVar11 = (uint)*(byte *)(iVar14 + 0x28) * -200 + DAT_43e9936c;
        DAT_43e992b8 = uVar11;
        uVar10 = FUN_43ae8c60();
        if ((uVar11 < uVar10) || (DAT_43e9936c <= DAT_43e992b8)) {
          FUN_4378eb78(3,9,1,&DAT_43ca36f9,DAT_43e992b8,DAT_43e9920c[9]);
          FUN_43902718(s_EC_VD_Post_timing_error__d__vd___43ca370d,DAT_43e992b8,DAT_43e9920c[9]);
          DAT_43e992b8 = FUN_43ae8c60();
        }
        param_1 = param_1 + DAT_43e992b8;
        FUN_43ae863c(auStack_c0,&LAB_437926fc_1);
        puVar1 = &stack0x0000002c;
        goto LAB_43791fca;
      }
    }
  }
  else {
    DAT_43e9936c = 0;
    DAT_43e99370 = 0;
  }
  param_1 = FUN_4378e938();
  FUN_43ae863c(auStack_d4,&LAB_4379140c_1);
  puVar1 = &stack0x00000018;
LAB_43791fca:
  FUN_436ccd9c(0,param_1,1,puVar1 + -0xec);
  return;
}


/* ENTRY 437918ac */

void candidate_437918ac(int param_1)

{
  undefined *puVar1;
  undefined1 *puVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [20];
  undefined1 auStack_40 [20];
  undefined1 auStack_2c [24];
  
  puVar2 = auStack_90;
  iVar4 = DAT_43e9920c[1];
  if (iVar4 != *DAT_43e9920c) {
    DAT_43e99454 = DAT_43e99454 | 2;
  }
  if ((*(byte *)(DAT_4402546c + 0xc) & 4) != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca3595);
    FUN_43902718(s_DummyCamOutV_43ca35a9);
  }
  if (DAT_43e9bb18 == 0) {
    if (DAT_43e9baec == 1) {
      FUN_43560dc4(0x1a,0xffffff7f);
      iVar3 = DAT_43e9920c[10];
      FUN_43ae863c(auStack_54,&LAB_43ae8d3e_1);
      FUN_436ccd9c(4,param_1 + iVar3 * 2,1,auStack_54);
      FUN_43ada220(auStack_68,0x4379155d);
      puVar2 = auStack_68;
    }
    else {
      if (DAT_43e9baec == 2) {
        iVar3 = DAT_43e9920c[10];
        FUN_43ae863c(auStack_2c,&LAB_43791a10_1);
        FUN_436ccd9c(4,param_1 + iVar3,1,auStack_2c);
        FUN_43560da8(0x1a,0x80);
        FUN_43ada220(auStack_40,&LAB_43790b68_1);
        puVar2 = auStack_40;
        iVar4 = iVar4 << 8;
        puVar1 = &DAT_43e9b528;
        goto LAB_437919bc;
      }
      FUN_43560da8(0x1a,0x80);
      FUN_43ada220(auStack_7c,0x4379155d);
      puVar2 = auStack_7c;
    }
    puVar1 = &DAT_43e992fc;
  }
  else {
    FUN_43560da8(0x1a,0x80);
    FUN_43ada220(auStack_90,0x4379155d);
    puVar1 = &DAT_43e992fc;
  }
LAB_437919bc:
  FUN_439018b0(puVar1,puVar2,iVar4,0);
  return;
}


/* ENTRY 4379140c */

void candidate_4379140c(void)

{
  undefined4 uVar1;
  undefined1 auStack_1c [20];
  
  uVar1 = *DAT_43e9920c;
  FUN_43ae8c7a(uVar1,&DAT_43e9baa8);
  FUN_43ada220(auStack_1c,0x4379210d);
  FUN_439018b0(&DAT_43e9b528,auStack_1c,uVar1,0);
  return;
}


/* ENTRY 43791454 */

void candidate_43791454(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  FUN_43560dc4(0x11,~param_1,param_3,param_4,param_1);
  iVar1 = FUN_4378e90c();
  if (iVar1 != 0) {
    FUN_43ada220(&uStack_1c,0x4378f849);
    FUN_439018b0(&DAT_43e9b528,&uStack_1c,*DAT_43e9920c,0);
  }
  return;
}


/* ENTRY 437926fc */

void candidate_437926fc(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined1 auStack_38 [20];
  undefined1 auStack_24 [24];
  
  uVar2 = *DAT_43e9920c;
  uVar1 = FUN_4378e938();
  FUN_43ae863c(auStack_24,0x4379140d);
  FUN_436ccd9c(0,uVar1,1,auStack_24);
  FUN_43ada220(auStack_38,0x4378f849);
  FUN_439018b0(&DAT_43e9b528,auStack_38,uVar2,0);
  return;
}


/* ENTRY 43792750 */

void candidate_43792750(void)

{
  int iVar1;
  undefined1 auStack_1c [20];
  
  FUN_43901638(7);
  if (DAT_43e992dc == *DAT_43e9920c) {
    iVar1 = DAT_43e99370 + DAT_43e9920c[2];
    FUN_43ae863c(auStack_1c,&LAB_4378ea10_1);
    FUN_436ccd9c(5,iVar1,1,auStack_1c);
    thunk_FUN_436e82ec();
  }
  else {
    FUN_4378eb78(3,9,1,&DAT_43ca37fa);
    FUN_43902718(s_int_LM_Send1st_Handler__EC_VD_Po_43ca380e);
  }
  return;
}


/* ENTRY 4378ea10 */

void candidate_4378ea10(undefined4 param_1,uint param_2,undefined4 param_3)

{
  undefined4 uStack_10;
  uint uStack_c;
  undefined4 uStack_8;
  
  uStack_10 = param_1;
  uStack_c = param_2;
  uStack_8 = param_3;
  FUN_43560e00(0x11,&uStack_10);
  DAT_43e9bd4c = uStack_c & 2 | DAT_43e9bd4c & 0xfffffffd;
  if (DAT_43f79b84 != 0) {
    if ((uStack_c & 2) == 0) {
      DAT_43f79b4a = 0;
    }
    else {
      DAT_43f79b68 = DAT_43f79b68 + 1;
      DAT_43f79b4a = DAT_43f79b4a + 1;
    }
  }
  thunk_FUN_436e8300();
  return;
}


/* ENTRY 436cf954 */

void FUN_436cf954(uint param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  code *pcVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = DAT_44024944;
  uVar3 = param_1 & 0x3380000;
  uVar4 = param_1;
  if (uVar3 != 0) {
    if ((*(byte *)(DAT_44024944 + 0xf) & 1) != 0) {
      FUN_436cf6d4(0x165,1,1,&DAT_43c91f6e,uVar3,param_2,param_3);
      FUN_43902718(s_judgeComplexCallBack__x_43c91f79,uVar3);
    }
    if ((uVar3 & DAT_43e7ec4c) != 0) {
      param_2 = DAT_43e7ec4c;
      FUN_436cf6d4(0x165,1,1,&DAT_43c91f91,uVar3,DAT_43e7ec4c,param_3);
      FUN_43902718(s_DfeCoreErr_judgeComplexCallBack__43c91f9c,uVar3,DAT_43e7ec4c);
    }
    iVar5 = 0;
    DAT_43e7ec4c = uVar3 | DAT_43e7ec4c;
    do {
      if ((*(int *)((int)&DAT_43e7ec2c + iVar5) != 0) &&
         ((*(uint *)((int)&DAT_43e7ec28 + iVar5) & DAT_43e7ec4c) ==
          *(uint *)((int)&DAT_43e7ec28 + iVar5))) {
        if ((*(byte *)(iVar1 + 0xf) & 1) != 0) {
          FUN_436cf6d4(0x165,1,1,&DAT_43c91fd5,*(int *)((int)&DAT_43e7ec2c + iVar5),param_2,param_3)
          ;
          FUN_43902718(s_CallCallBack__x_43c91fe0,*(undefined4 *)((int)&DAT_43e7ec2c + iVar5));
        }
        FUN_436cf91c(*(undefined4 *)((int)&DAT_43e7ec28 + iVar5));
        pcVar2 = *(code **)((int)&DAT_43e7ec2c + iVar5);
        *(undefined4 *)((int)&DAT_43e7ec28 + iVar5) = 0;
        *(undefined4 *)((int)&DAT_43e7ec2c + iVar5) = 0;
        (*pcVar2)();
      }
      iVar5 = iVar5 + 8;
    } while (iVar5 != 0x20);
    uVar4 = param_1 & ~uVar3;
  }
  if (uVar4 == 0) {
    return;
  }
  FUN_436cf6d4(0x165,1,1,&DAT_43c91ff0,param_1,param_2,param_3);
  FUN_43902718(s_camIntHandler0__fact__x_43c91ffb,param_1);
  return;
}


/* ENTRY 436cf780 */

void candidate_436cf780(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int extraout_r1;
  uint uVar1;
  
  uVar1 = DAT_43e7ec48 + 1;
  DAT_43e7ec48 = uVar1;
  if ((9 < uVar1) &&
     (FUN_4355fd4c(uVar1,1000,param_3,&DAT_43e7ec48,param_1,param_2,param_3), extraout_r1 != 0)) {
    return;
  }
  FUN_436cf6d4(0x165,1,1,&DAT_43c91e75,param_1,uVar1);
  FUN_43902718(s_camIntHandler1__fact__x_num__d_43c91e80,param_1,DAT_43e7ec48);
  return;
}


/* ENTRY 436cf818 */

void FUN_436cf818(void)

{
  FUN_43ad690c(0xfc000000,1);
  FUN_436cf0c8(9,0x436cf955);
  FUN_436cf0c8(10,0x436cf781);
  return;
}


/* ENTRY 436cf0c8 */

undefined4 FUN_436cf0c8(uint param_1,undefined4 param_2)

{
  if (param_1 < 0xe) {
    if (*(int *)(&DAT_43e7ebf0 + param_1 * 4) == 0) {
      *(undefined4 *)(&DAT_43e7ebf0 + param_1 * 4) = param_2;
      switch(param_1) {
      case 1:
        FUN_43ad696c();
        break;
      case 2:
        FUN_43ad6980();
        break;
      case 3:
        FUN_43ad6994();
        break;
      case 4:
        FUN_43ad69a8();
        break;
      case 5:
        FUN_43ad69ba();
        break;
      case 6:
        FUN_43ad69cc();
        break;
      case 7:
        FUN_43ad69de();
        break;
      case 8:
        FUN_43ad69f0();
        break;
      case 9:
        FUN_43ad6a0c();
        break;
      case 10:
        FUN_43ad6a20();
        break;
      case 0xb:
        FUN_43ad6a34();
        break;
      case 0xc:
        FUN_43ad6a48();
        break;
      case 0xd:
        FUN_43ad6a5c();
        break;
      default:
        FUN_43ad695a();
      }
      return 0;
    }
    FUN_436cf01c(0x165,1,1,&DAT_43c916f8,param_1,param_2);
    FUN_43902718(s__Err__DFE_INT__already_set_int___43c91703,param_1);
  }
  else {
    FUN_436cf01c(0x165,1,1,&DAT_43c916d1,param_1,param_2);
    FUN_43902718(s__Err__DFE_INT__NOT_SUPPORT_43c916dc);
  }
  return 1;
}


/* ENTRY 436cf91c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf91c(uint param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = FUN_436cf7e8();
  if ((uVar1 & param_1) != param_1) {
    FUN_436cf6d4(0x165,0,3,s__DFECore____clearCamIntEnable0__a_43c91f38,uVar1,param_1,param_3);
  }
  _DAT_fc0a0018 = uVar1 & ~param_1;
  return;
}


/* ENTRY 436ccd9c */

undefined4 FUN_436ccd9c(uint param_1)

{
  if (param_1 < 10) {
    FUN_43ad6006(&DAT_43e7e934 + param_1 * 0x1c);
    return 0;
  }
  return 1;
}


/* ENTRY 43ad6006 */

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


/* ENTRY 437968b0 */

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


/* ENTRY 437967e8 */

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


/* ENTRY 43ad6034 */

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


/* ENTRY 43796954 */

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


/* ENTRY 4379bb90 */

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


/* ENTRY 43797afc */

void FUN_43797afc(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9de9c,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* ENTRY 43797b10 */

void FUN_43797b10(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9de64,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* ENTRY 43797b24 */

void FUN_43797b24(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9dee0,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* ENTRY 43797b38 */

void FUN_43797b38(undefined2 *param_1,undefined4 param_2)

{
  FUN_435a9928(&DAT_43e9df18,*(undefined4 *)(param_1 + 2),*param_1,param_2);
  return;
}


/* ENTRY 435a9928 */

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

