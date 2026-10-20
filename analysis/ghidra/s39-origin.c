/* S39: existing functions; no project modifications. */

/* 436bec28 */

undefined4 FUN_436bec28(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 != 1) {
    return 1;
  }
  iVar2 = FUN_436bd274(0,iVar1);
  if (iVar2 == param_1) {
    if (*param_2 != *(int *)(DAT_436bec70 + 0x436bec56 + iVar1 * 4)) {
      *(int *)(DAT_436bec70 + 0x436bec56 + iVar1 * 4) = *param_2;
      return 0;
    }
    return 1;
  }
  return 1;
}


/* 436bef2c */

undefined4 FUN_436bef2c(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 == 1) {
    iVar3 = FUN_436bd274(0,iVar1);
    iVar2 = DAT_436befc8;
    if (iVar3 == param_1) {
      if (*(int *)(DAT_436befc8 + 0x436bef58 + iVar1 * 4) != param_2) {
        *(int *)(DAT_436befc8 + 0x436bef58 + iVar1 * 4) = param_2;
        iVar3 = DAT_436befcc;
        if (iVar1 == 0) {
          FUN_436bd3f4(0);
          FUN_436bd7d8(0);
          if (*(char *)(iVar3 + 0x436bef73) == '\0') {
            return 0;
          }
          FUN_436bd3f4(1);
          FUN_436bd7d8(1);
          *(undefined4 *)(iVar2 + 0x436bef5c) = 0;
          *(undefined1 *)(iVar3 + 0x436bef73) = 0;
          return 0;
        }
        if (param_2 != 0x11) {
          *(undefined1 *)(DAT_436befd4 + 0x436befad) = 0;
          FUN_436bd3f4(1);
          FUN_436bd7d8(1);
          return 0;
        }
        FUN_436bf230(iVar1);
        *(undefined1 *)(DAT_436befd0 + 0x436befa1) = 1;
      }
      uVar4 = 0;
    }
    else {
      uVar4 = 4;
    }
  }
  else {
    uVar4 = 2;
  }
  return uVar4;
}


/* 4378c4d0 */

void FUN_4378c4d0(int param_1)

{
  int iVar1;
  int iVar2;
  char cVar3;
  undefined1 *puVar4;
  
  iVar1 = DAT_4378c518;
  puVar4 = (undefined1 *)(DAT_4378c518 + 0x4378c4dc);
  iVar2 = FUN_435611b8(*(undefined4 *)(DAT_4378c518 + 0x4378c4e8),1);
  *(undefined1 *)(param_1 + 0x1ff) = *puVar4;
  *(undefined1 *)(param_1 + 0x200) = *(undefined1 *)(iVar1 + 0x4378c4f4);
  *(undefined1 *)(param_1 + 0x1fe) = *(undefined1 *)(iVar1 + 0x4378c4ed);
  *(undefined1 *)(param_1 + 0x201) = *(undefined1 *)(iVar1 + 0x4378c4f5);
  cVar3 = *(char *)(iVar1 + 0x4378c4dd);
  if (cVar3 == -1) {
    cVar3 = '\0';
  }
  *(char *)(param_1 + 0x1fd) = cVar3;
  if (iVar2 == 0) {
    FUN_435611d4(*(undefined4 *)((int)&DAT_4378c518 + DAT_4378c51c));
    return;
  }
  return;
}


/* 4378e938 */

int FUN_4378e938(void)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = *(int *)(DAT_4378e9bc + 0x4378e946);
  iVar4 = *(int *)(iVar5 + 0x28) * (*(byte *)(DAT_4378e9c0 + 0x43790424) - 1) + *(int *)(iVar5 + 8);
  iVar3 = *(int *)(DAT_4378e9c4 + 0x4378e94e + DAT_4378e9c8);
  if (*(char *)(DAT_4378e9c0 + 0x4378ef1d) == '\0') {
    if ((*(byte *)(*(int *)(DAT_4378e9bc + 0x4378e94a) + 0x264) & 8) == 0) {
      if (*(int *)(DAT_4378e9c0 + 0x4378ef16) == 0) {
        uVar2 = (uint)*(byte *)(iVar3 + 0x1a);
      }
      else {
        uVar2 = (uint)*(byte *)(iVar3 + 0x19);
      }
    }
    else {
      if (*(int *)(DAT_4378e9c0 + 0x4378ef16) == 0) {
        return (uint)*(byte *)(iVar3 + 0x18) * -200 + iVar4;
      }
      if (*(int *)(iVar5 + 0xc) != 1) {
        return (uint)*(byte *)(iVar3 + 0x15) * -200 + iVar4;
      }
      uVar2 = (uint)*(byte *)(iVar3 + 0x14);
    }
  }
  else {
    if (*(int *)(iVar5 + 0xc) == 1) {
      bVar1 = *(byte *)(iVar3 + 0x16);
    }
    else {
      bVar1 = *(byte *)(iVar3 + 0x17);
    }
    uVar2 = (uint)bVar1;
  }
  return uVar2 * -200 + iVar4;
}


/* 4378ea78 */

void FUN_4378ea78(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  int iStack_28;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined4 uStack_14;
  
  iVar1 = DAT_4378eb60;
  puVar4 = (undefined4 *)(DAT_4378eb58 + 0x4378ea88);
  FUN_439c5320(puVar4,DAT_4378eb5c + 0x4378ea8e,0x44);
  iVar2 = DAT_4378eb64;
  uVar3 = *puVar4;
  *(undefined1 *)(DAT_4378eb64 + 0x4378f07e) = 4;
  *(undefined4 *)(iVar2 + 0x4378f082) = uVar3;
  FUN_437957ec(uVar3,*(undefined1 *)(iVar2 + 0x4378f1fa),*(undefined1 *)(iVar2 + 0x4378f1fb),
               iVar2 + 0x4378f0f6,iVar2 + 0x4378f2de);
  FUN_4378e334(*(undefined4 *)(iVar1 + 0x4378ea9c + DAT_4378eb68),DAT_4378eb6c + 0x4378eac8,param_1)
  ;
  iStack_28 = FUN_437955ec();
  iVar1 = DAT_4378eb70;
  if (((iStack_28 != 1) && (iStack_28 != 2)) && (iStack_28 != 0)) {
    iStack_28 = 0;
  }
  uStack_24 = *(undefined2 *)(DAT_4378eb70 + 0x4378f32e);
  uStack_22 = *(undefined2 *)(DAT_4378eb70 + 0x4378f332);
  uStack_20 = *(undefined2 *)((int)&DAT_4378f350 + DAT_4378eb70 + 2);
  uStack_1e = *(undefined2 *)(DAT_4378eb70 + 0x4378f1f6);
  uStack_1c = *(undefined2 *)(DAT_4378eb70 + 0x4378f1f8);
  uStack_1a = *(undefined2 *)(DAT_4378eb70 + 0x4378f1fa);
  uStack_18 = *(undefined2 *)(DAT_4378eb70 + 0x4378f240);
  uStack_16 = *(undefined2 *)(DAT_4378eb70 + 0x4378f242);
  thunk_FUN_43ae6916(&iStack_28,&uStack_14);
  FUN_43795d38(uStack_14);
  if ((*(ushort *)(*(int *)(DAT_4378eb74 + 0x4378eb40) + 0x264) & 0x1c0) == 0) {
    uVar3 = FUN_43794a78();
    *(undefined4 *)(&LAB_4378f2ea + iVar1) = uVar3;
  }
  else {
    *(undefined4 *)(&LAB_4378f2ea + iVar1) = 0;
  }
  return;
}


/* 4378f9b4 */

undefined * FUN_4378f9b4(void)

{
  return &UNK_4378f9ba + DAT_4378f9bc;
}


/* 4378f9c0 */

int FUN_4378f9c0(void)

{
  return DAT_4378f9cc + 0x4378ff6a;
}


/* 4378fa70 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void candidate_4378fa70(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  undefined2 *puVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  undefined1 auStack_134 [68];
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined4 uStack_30;
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  
  iVar1 = _DAT_4378fd64;
  iVar8 = _DAT_4378fd5c + 0x4378fa84;
  iVar6 = *(int *)(iVar8 + _DAT_4378fd60);
  puVar5 = (undefined2 *)(_DAT_4378fd64 + 0x4378fa90);
  *(undefined4 *)(_DAT_4378fd64 + 0x43790050) = 0;
  uVar4 = *(undefined4 *)(iVar6 + 0x40);
  *(undefined4 *)(iVar1 + 0x4379005c) = 0;
  *(undefined1 *)(iVar1 + 0x43790058) = 0;
  *(undefined4 *)(iVar1 + 0x43790034) = uVar4;
  *(int *)(iVar1 + 0x43790d1c) = _DAT_4378fd68 + 0x4378fab0;
  *(undefined4 *)(_DAT_4378fd6c + 0x4378fab6) = param_2;
  *(undefined4 *)(iVar1 + 0x43790054) = 2;
  uStack_30 = 0xb;
  uStack_2c = FUN_4378de7c();
  uStack_2a = 0;
  uStack_2b = 0;
  uVar4 = FUN_436d6118();
  FUN_436d61a4(uVar4,&uStack_30,auStack_134);
  *(undefined4 *)(iVar1 + 0x43790060) = 1;
  *(undefined4 *)(iVar1 + 0x4379003c) = uStack_cc;
  *(undefined1 *)(iVar1 + 0x43791570) = 1;
  *(undefined4 *)(iVar1 + 0x43790070) = 1;
  *(undefined4 *)(iVar1 + 0x43790038) = uStack_d0;
  *(undefined4 *)(iVar1 + 0x4379021c) = 0;
  *(undefined1 *)(iVar1 + 0x43790065) = 1;
  *(undefined4 *)(iVar1 + 0x43790040) = uStack_c8;
  *(undefined1 *)(iVar1 + 0x43790220) = 1;
  *(undefined1 *)(iVar1 + 0x43790221) = 1;
  *(undefined4 *)(iVar1 + 0x43790048) = uStack_ec;
  *(undefined1 *)(iVar1 + 0x43790064) = 0;
  *(undefined1 *)(iVar1 + 0x43790075) = 0;
  *(undefined4 *)(iVar1 + 0x43790044) = uStack_f0;
  *(undefined2 *)(iVar1 + 0x43791572) = 0;
  *(undefined2 *)(iVar1 + 0x43791574) = 0;
  *(undefined4 *)(iVar1 + 0x4379004c) = uStack_e8;
  *(undefined4 *)(iVar1 + 0x43790068) = 1;
  *(undefined1 *)(iVar1 + 0x4379156e) = 4;
  *(undefined1 *)(iVar1 + 0x43790074) = 4;
  *(undefined4 *)(iVar1 + 0x43790224) = 1;
  *(undefined4 *)(iVar1 + 0x4379022c) = 0;
  *(undefined1 *)(iVar1 + 0x4379006d) = 1;
  *(undefined1 *)(iVar1 + 0x43790230) = 1;
  *(undefined1 *)(iVar1 + 0x4379006c) = 0;
  *(undefined1 *)(iVar1 + 0x43790228) = 0;
  *(undefined2 *)(iVar1 + 0x43791576) = 0;
  *(undefined2 *)(iVar1 + 0x43791578) = 0;
  *(undefined4 *)(iVar1 + 0x43790078) = 0x11;
  *(undefined1 *)(iVar1 + 0x437901f0) = 0;
  *(undefined1 *)(iVar1 + 0x437901f1) = 0;
  FUN_439c5320(iVar1 + 0x4379007c,param_1,0x70);
  iVar2 = _DAT_4378fd70;
  *(undefined4 *)(iVar1 + 0x43790208) = *(undefined4 *)(iVar6 + 0x50);
  uVar4 = FUN_43ae8c50();
  *(undefined1 *)(iVar1 + 0x43790210) = 0;
  *(undefined4 *)(iVar1 + 0x43790214) = 0;
  *(undefined4 *)(iVar1 + 0x43790218) = 1;
  *(undefined1 *)(iVar1 + 0x43790066) = 0;
  *(undefined4 *)(iVar1 + 0x4379023c) = 0;
  *(undefined1 *)(iVar1 + 0x437902c4) = 0;
  *(undefined2 *)(iVar1 + 0x437902c6) = 0;
  *(undefined2 *)(iVar1 + 0x437902c8) = 0;
  *(undefined2 *)(iVar1 + 0x437902ca) = 0;
  *(undefined2 *)(iVar1 + 0x437902cc) = 0;
  *(undefined4 *)(iVar1 + 0x4379027c) = 0;
  *(undefined4 *)(iVar1 + 0x43790240) = 0;
  *(undefined4 *)(iVar1 + 0x43790244) = 0;
  *(undefined4 *)(iVar1 + 0x4379020c) = uVar4;
  uVar3 = FUN_437fc54c(0);
  *puVar5 = uVar3;
  uVar3 = FUN_437fc54c(0);
  *(undefined1 *)(iVar1 + 0x43790278) = 0;
  *(undefined1 *)(iVar1 + 0x43791a5c) = 1;
  *(undefined1 *)(iVar1 + 0x43790279) = 0;
  *(undefined1 *)(iVar1 + 0x43791949) = 0;
  *(undefined4 *)(iVar1 + 0x43790290) = 0;
  *(undefined1 *)(iVar1 + 0x43791958) = 1;
  *(undefined1 *)(iVar1 + 0x437902ce) = 0;
  *(undefined4 *)(iVar1 + 0x437902a4) = 1;
  *(undefined4 *)(iVar1 + 0x437902a8) = 1;
  *(undefined2 *)(iVar1 + 0x437902ac) = 0;
  *(undefined2 *)(iVar1 + 0x437902ae) = 0;
  *(undefined2 *)(iVar1 + 0x437902b0) = 0;
  *(undefined2 *)(iVar1 + 0x437902b2) = 0;
  *(undefined2 *)(iVar1 + 0x437902b4) = 0;
  *(undefined2 *)(iVar1 + 0x437902b6) = 0;
  *(undefined2 *)(iVar1 + 0x437902b8) = 0;
  *(undefined2 *)(iVar1 + 0x437902ba) = 0;
  *(undefined2 *)(iVar1 + 0x437902bc) = 0;
  *(undefined2 *)(iVar1 + 0x437902be) = 0;
  *(undefined2 *)(iVar1 + 0x437902c0) = 0;
  *(undefined2 *)(iVar1 + 0x437902c2) = 0;
  *(undefined2 *)(iVar1 + 0x437902a0) = uVar3;
  *(undefined2 *)(iVar1 + 0x43790258) = uVar3;
  *(undefined2 *)(iVar1 + 0x43790274) = uVar3;
  uVar4 = FUN_4377fdf8();
  *(undefined4 *)(iVar1 + 0x437918dc) = uVar4;
  uVar4 = FUN_437b4d64();
  *(undefined4 *)(iVar1 + 0x437918e0) = uVar4;
  uVar4 = FUN_437c1440();
  *(undefined4 *)(iVar1 + 0x437918e4) = uVar4;
  uVar4 = FUN_4379fc20();
  *(undefined4 *)(iVar1 + 0x437918e8) = uVar4;
  uVar4 = FUN_437d0bc8();
  *(undefined4 *)(iVar1 + 0x437918ec) = uVar4;
  uVar4 = FUN_437d9930();
  *(undefined4 *)(&LAB_437918f0 + iVar1) = uVar4;
  uVar4 = FUN_437b6614();
  *(undefined4 *)(iVar1 + 0x437918f4) = uVar4;
  uVar4 = FUN_437b8230();
  *(undefined4 *)(iVar1 + 0x437918f8) = uVar4;
  iVar6 = _DAT_4378fd74;
  FUN_43ae8eae(puVar5,iVar2 + 0x4378fb8e);
  puVar7 = (undefined4 *)(iVar6 + 0x4378fc90);
  candidate_4380e3f4(puVar7);
  FUN_439c5320(_DAT_4378fd78 + 0x4378fca2,puVar7,0x44);
  FUN_439c5320(_DAT_4378fd7c + 0x4378fcb6,puVar7,0x44);
  uVar4 = *puVar7;
  *(undefined1 *)(iVar1 + 0x43790074) = 4;
  *(undefined4 *)(iVar1 + 0x43790078) = uVar4;
  FUN_437957ec(uVar4,*(undefined1 *)(iVar1 + 0x437901f0),*(undefined1 *)(iVar1 + 0x437901f1),
               iVar1 + 0x437900ec,iVar1 + 0x437902d4);
  FUN_4378e334(*(undefined4 *)(iVar8 + _DAT_4378fd80),iVar2 + 0x4378fb8e,1);
  *(undefined1 *)(iVar1 + 0x43791571) = 0;
  *(undefined4 *)(iVar1 + 0x437901f4) = 0;
  *(undefined4 *)(iVar1 + 0x437901f8) = 0;
  *(undefined4 *)(iVar1 + 0x437902d0) = 1;
  FUN_43560da8(0x1a,_DAT_4378fd58);
  FUN_43560dc4(0x11,0);
  func_0x43901788();
  func_0x437fe208();
  FUN_4378c4d0(iVar1 + 0x43790034);
  FUN_43b2a162(_DAT_4378fd84 + 0x4378fd26);
  FUN_43b2a162(_DAT_4378fd88 + 0x4378fd2e);
  FUN_43b2a162(_DAT_4378fd8c + 0x4378fd36);
  FUN_43b2a162(_DAT_4378fd90 + 0x4378fd3e);
  FUN_43b2a162(_DAT_4378fd94 + 0x4378fd46);
  FUN_43b2a162(_DAT_4378fd98 + 0x4378fd4e);
  return;
}


/* 4378fef4 */

void candidate_4378fef4(uint param_1)

{
  byte bVar1;
  char cVar2;
  ushort uVar3;
  byte bVar4;
  undefined1 uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  short sVar9;
  short sVar10;
  uint uVar11;
  undefined1 *puVar12;
  int iVar13;
  uint uVar14;
  short *psVar15;
  int iVar16;
  undefined1 auStack_50 [20];
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 auStack_30 [4];
  uint uStack_2c;
  undefined1 auStack_28 [4];
  int aiStack_24 [2];
  
  iVar16 = DAT_437908e8 + 0x4378ff08;
  iVar13 = *(int *)(iVar16 + DAT_437908ec);
  if (((*(byte *)(iVar13 + 0x12) & 1) != 0) &&
     (uVar11 = (uint)*(byte *)((int)&DAT_437919f8 + DAT_437908f0 + 1), uVar11 < 4)) {
                    /* WARNING: Could not recover jumptable at 0x4378ff22. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_4378ff22::switchdataD_4378ff26 +
              (uint)(&switchD_4378ff22::switchdataD_4378ff26)[uVar11] * 2))();
    return;
  }
  uVar11 = param_1 >> 8;
  param_1 = param_1 & 0xff;
  if ((uVar11 != **(uint **)(DAT_43790904 + 0x4378ff60)) ||
     (param_1 != *(byte *)(DAT_43790908 + 0x43791a49))) {
    iVar6 = thunk_FUN_436cd00c();
    iVar7 = DAT_43790910;
    iVar16 = DAT_4379090c;
    uVar14 = (uint)(iVar6 - (*(undefined4 **)(DAT_4379090c + 0x4378ff88))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43790914 + 0x4378ffa6,uVar11,param_1,
                 **(undefined4 **)(DAT_4379090c + 0x4378ff88),
                 *(undefined1 *)(DAT_43790910 + 0x43791a67),uVar14);
    FUN_43902718(DAT_43790918 + 0x4378ffc4,uVar11,param_1,**(undefined4 **)(iVar16 + 0x4378ff88),
                 *(undefined1 *)(iVar7 + 0x43791a67),uVar14);
    if (param_1 < 4) {
      uVar8 = *(undefined4 *)(DAT_4379091c + 0x4378ffd6 + param_1 * 4);
    }
    else {
      uVar8 = 7;
    }
    FUN_4378f988(3,uVar8,uVar14);
    if ((*(byte *)(iVar13 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43790920 + 0x4378fff4);
    }
    if ((*(byte *)(iVar13 + 0x1b) & 0x20) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  if (*(char *)(DAT_43790908 + 0x43791a4a) != '\0') {
    FUN_43acad44();
  }
  FUN_43ae1292(4);
  iVar7 = FUN_43ae8d4e();
  if (iVar7 == 0) {
    FUN_43901778();
    if (*(char *)(DAT_43790924 + 0x4379002c) != '\0') {
      *(undefined1 *)(DAT_43790928 + 0x43790038) = 1;
    }
    uVar5 = 0;
    puVar12 = (undefined1 *)(DAT_4379092c + 0x43790042);
  }
  else {
    uVar5 = 1;
    puVar12 = (undefined1 *)(DAT_43790930 + 0x4379004c);
  }
  iVar7 = DAT_43790934;
  *puVar12 = uVar5;
  FUN_4378f7a0(0xf7c);
  if (*(char *)(iVar7 + 0x43791b38) != '\0') {
    FUN_43560e00(0x11,auStack_30);
    if ((uStack_2c & 2) == 0) {
      uVar8 = FUN_437c1440();
      iVar6 = DAT_43790938 + 0x43790086;
      *(undefined4 *)(iVar7 + 0x43791eac) = uVar8;
      FUN_43ae8e44(iVar7 + 0x43790058,iVar6);
    }
    if (*(char *)(DAT_4379093c + 0x43790094) == '\0') {
      *(uint *)(DAT_43790940 + 0x437908a4) =
           uStack_2c & 2 | *(uint *)(DAT_43790940 + 0x437908a4) & 0xfffffffd;
      if (*(short *)(DAT_43790944 + 0x437900ba) != 0) {
        if ((uStack_2c & 2) == 0) {
          iVar7 = DAT_43790948 + 0x437900ca;
          sVar9 = 0;
        }
        else {
          *(short *)(DAT_4379094c + 0x437900d4) = *(short *)(DAT_4379094c + 0x437900d4) + 1;
          iVar7 = DAT_43790950 + 0x437900de;
          sVar9 = *(short *)(DAT_43790950 + 0x437900e0) + 1;
        }
        *(short *)(iVar7 + 2) = sVar9;
      }
    }
    sVar9 = *(short *)(DAT_43790954 + 0x437900ea);
    if ((sVar9 != 0) || (*(char *)(iVar13 + 0xe) != '\0')) {
      if (*(short *)(DAT_43790958 + 0x437900fc) != sVar9) {
        iVar7 = 0;
        do {
          *(undefined2 *)(DAT_4379095c + 0x4379010c + iVar7) = 0;
          *(undefined2 *)(DAT_43790960 + 0x43790114 + iVar7) = 0;
          *(undefined2 *)(DAT_43790964 + 0x4379011c + iVar7) = 0;
          iVar7 = iVar7 + 2;
        } while (iVar7 != 0x1a);
        *(short *)(DAT_43790968 + 0x4379012a) = sVar9;
      }
      iVar7 = DAT_43790970;
      if ((sVar9 != 0) && (*(short *)(DAT_4379096c + 0x43790136) == sVar9)) {
        if ((*(byte *)(iVar13 + 0xe) & 1) != 0) {
          FUN_4378eb78(3,9,1,DAT_43790974 + 0x43790174,sVar9,
                       *(undefined2 *)(DAT_43790970 + 0x4379015e),
                       *(undefined2 *)(DAT_43790970 + 0x43790154),
                       *(undefined2 *)(DAT_43790970 + 0x43790152),
                       *(undefined2 *)(DAT_43790970 + 0x43790156),
                       *(undefined2 *)(DAT_43790970 + 0x4379015c),
                       *(undefined2 *)(DAT_43790970 + 0x4379015a),
                       *(undefined2 *)(DAT_43790970 + 0x43790162));
          FUN_43902718(DAT_4379097c + 0x4379019e,*(undefined2 *)(DAT_43790978 + 0x43790180),
                       *(undefined2 *)(iVar7 + 0x4379015e),*(undefined2 *)(iVar7 + 0x43790154),
                       *(undefined2 *)(iVar7 + 0x43790152),*(undefined2 *)(iVar7 + 0x43790156),
                       *(undefined2 *)(iVar7 + 0x4379015c),*(undefined2 *)(iVar7 + 0x4379015a),
                       *(undefined2 *)(iVar7 + 0x43790162));
        }
        iVar7 = DAT_43790980;
        FUN_43900368(0,(uint)*(ushort *)(DAT_43790980 + 0x437901ae) * 0x10000 +
                       (uint)*(ushort *)(DAT_43790980 + 0x437901ac));
        FUN_43900368(1,(uint)*(ushort *)(iVar7 + 0x437901b0) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x437901b6));
        FUN_43900368(2,(uint)*(ushort *)(iVar7 + 0x437901b4) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x437901bc));
        FUN_43900368(3,(uint)*(ushort *)(iVar7 + 0x437901b8) << 0x10);
      }
      iVar7 = 0;
      do {
        uVar3 = *(ushort *)(DAT_43790984 + 0x437901e4 + iVar7);
        if (*(ushort *)(DAT_43790988 + 0x437901ec + iVar7) < uVar3) {
          *(ushort *)(DAT_43790988 + 0x437901ec + iVar7) = uVar3;
        }
        iVar6 = DAT_43790994;
        iVar7 = iVar7 + 2;
      } while (iVar7 != 0x1a);
      psVar15 = (short *)(DAT_4379098c + 0x43790200);
      sVar9 = *psVar15;
      if ((sVar9 != 0) && (*(short *)(DAT_43790990 + 0x4379020c) == sVar9)) {
        if ((*(byte *)(iVar13 + 0xe) & 2) != 0) {
          FUN_4378eb78(3,9,1,DAT_43790998 + 0x4379024a,*(short *)(DAT_43790990 + 0x4379020c),
                       *(undefined2 *)(DAT_43790994 + 0x43790234),
                       *(undefined2 *)(DAT_43790994 + 0x4379022a),
                       *(undefined2 *)(DAT_43790994 + 0x43790228),
                       *(undefined2 *)(DAT_43790994 + 0x4379022c),
                       *(undefined2 *)(DAT_43790994 + 0x43790232),
                       *(undefined2 *)(DAT_43790994 + 0x43790230),
                       *(undefined2 *)(DAT_43790994 + 0x43790238));
          FUN_43902718(DAT_4379099c + 0x4379026e,*psVar15,*(undefined2 *)(iVar6 + 0x43790234),
                       *(undefined2 *)(iVar6 + 0x4379022a),*(undefined2 *)(iVar6 + 0x43790228),
                       *(undefined2 *)(iVar6 + 0x4379022c),*(undefined2 *)(iVar6 + 0x43790232),
                       *(undefined2 *)(iVar6 + 0x43790230),*(undefined2 *)(iVar6 + 0x43790238));
        }
        iVar7 = DAT_437909a0;
        FUN_43900368(4,(uint)*(ushort *)(DAT_437909a0 + 0x4379027e) * 0x10000 +
                       (uint)*(ushort *)(DAT_437909a0 + 0x4379027c));
        FUN_43900368(5,(uint)*(ushort *)(iVar7 + 0x43790280) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x43790286));
        FUN_43900368(6,(uint)*(ushort *)(iVar7 + 0x43790284) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x4379028c));
        FUN_43900368(7,(uint)*(ushort *)(iVar7 + 0x43790288) << 0x10);
      }
      iVar7 = DAT_437909a4;
      if ((((*(byte *)(iVar13 + 0xe) & 4) != 0) &&
          (uVar14 = *(uint *)((int)&DAT_43790abc + DAT_437909a4 + 2), uVar14 != 0)) &&
         ((uVar14 & 0x6e) != 0)) {
        FUN_4378eb78(3,9,1,DAT_437909a8 + 0x437902d4,uVar14);
        FUN_43902718(DAT_437909ac + 0x437902e2,*(undefined4 *)((int)&DAT_43790abc + iVar7 + 2));
      }
    }
    FUN_439c5320(DAT_437909b0 + 0x437902f2,DAT_437909b4 + 0x437902f4,0x44);
  }
  uVar5 = FUN_43ae8ccc(*(undefined4 *)(iVar16 + DAT_437909b8));
  iVar16 = DAT_437909bc;
  bVar4 = *(byte *)(DAT_437909bc + 0x437908de);
  sVar9 = *(short *)(DAT_437909bc + 0x43791dec);
  sVar10 = (ushort)bVar4 * 0x100;
  *(short *)(DAT_437909bc + 0x43791dec) = sVar10;
  *(undefined1 *)(iVar16 + 0x43791deb) = uVar5;
  iVar7 = *(int *)(DAT_437909c0 + 0x4379032a);
  if (*(int *)(iVar7 + 0x2c) == 0) {
    bVar1 = *(byte *)(iVar16 + 0x43791de9);
    if (*(int *)(iVar16 + 0x437908ae) == 1) {
      bVar1 = bVar1 >> 1;
    }
    *(ushort *)(iVar16 + 0x43791dec) = sVar10 + (ushort)bVar1;
  }
  if ((*(char *)(iVar7 + 0x1ed) == '\0') ||
     (*(char *)(*(int *)(DAT_437909c4 + 0x4379036c) + 2) == '\0')) {
    if (*(int *)(iVar7 + 0x2c) == 0) {
      iVar16 = DAT_437909cc + 0x43791e2e;
      if (*(int *)((int)&DAT_43790910 + DAT_437909cc + 2) == 1) {
        sVar10 = sVar10 + (short)(*(byte *)(DAT_437909cc + 0x43791e4d) + 1 >> 1);
      }
      else {
        sVar10 = sVar10 + *(byte *)(DAT_437909cc + 0x43791e4d) + 1;
      }
    }
    else {
      iVar16 = DAT_437909d0 + 0x43791e52;
    }
    *(short *)(iVar16 + 0x24) = sVar10;
  }
  else {
    *(ushort *)(DAT_437909c8 + 0x43791e3e) = (bVar4 + 1) * 0x100;
  }
  iVar6 = FUN_437955ec();
  iVar7 = DAT_437909d8;
  iVar16 = DAT_437909d4;
  if (iVar6 == 0) {
    sVar10 = (ushort)*(byte *)((int)&DAT_43790980 + DAT_437909d4) << 8;
    *(short *)(DAT_437909d4 + 0x43791e8a) = sVar10;
    *(short *)(iVar16 + 0x43791e8c) = sVar10;
  }
  else {
    iVar16 = *(int *)((int)&DAT_43790990 + DAT_437909d8 + 2);
    sVar10 = (ushort)*(byte *)((int)&DAT_43790994 + DAT_437909d8 + 2) * 0x100;
    *(short *)(DAT_437909d8 + 0x43791ea0) = sVar10;
    if (iVar16 == 0) {
      bVar4 = *(byte *)(iVar7 + 0x43791e99);
      if (*(int *)((int)&DAT_4379095c + iVar7 + 2) == 1) {
        bVar4 = bVar4 >> 1;
      }
      *(ushort *)(iVar7 + 0x43791ea0) = sVar10 + (ushort)bVar4;
    }
    if ((*(char *)(DAT_437909dc + 0x43790b84) == '\0') ||
       (*(char *)(DAT_437909dc + 0x43791ec4) == '\0')) {
      iVar16 = DAT_437909e0 + 0x43791ec2;
      if (*(int *)((int)&DAT_437909d8 + DAT_437909e0 + 2) != 0) {
        bVar4 = *(byte *)((int)&DAT_437909dc + DAT_437909e0 + 2);
        goto LAB_43790430;
      }
      bVar4 = *(byte *)((int)&DAT_437909dc + DAT_437909e0 + 2);
      if (*(int *)((int)&DAT_437909a4 + DAT_437909e0 + 2) == 1) {
        sVar10 = (ushort)bVar4 * 0x100 + (short)(*(byte *)(DAT_437909e0 + 0x43791ee1) + 1 >> 1);
      }
      else {
        sVar10 = *(byte *)(DAT_437909e0 + 0x43791ee1) + 1 + (ushort)bVar4 * 0x100;
      }
    }
    else {
      iVar16 = DAT_437909dc + 0x43791ea4;
      bVar4 = *(byte *)(DAT_437909dc + 0x43790b7c);
LAB_43790430:
      sVar10 = (ushort)bVar4 << 8;
    }
    *(short *)(iVar16 + 0x28) = sVar10;
  }
  iVar16 = DAT_437909e4;
  sVar10 = *(short *)(DAT_437909e4 + 0x43791f1e);
  if ((sVar9 != sVar10) && (*(char *)(iVar13 + 0x70) == '\0')) {
    FUN_439c5a04(&uStack_3c,0,0xc);
    uStack_38 = **(undefined4 **)(DAT_437909e8 + 0x4379046e);
    uStack_3c._0_3_ = CONCAT12(1,sVar10);
    uStack_34 = *(undefined4 *)((int)&DAT_43790a0c + iVar16);
    FUN_43b71696(uStack_3c,uStack_38,uStack_34);
  }
  iVar16 = DAT_437909ec;
  FUN_437999e4(1,0xd);
  FUN_437957a0();
  FUN_4378f7a0(0x105e);
  iVar7 = DAT_437909f0;
  if (*(char *)(*(int *)(iVar16 + 0x437904b2) + 2) != '\0') {
    if (((*(byte *)(DAT_437909f0 + 0x43790cba) & 1) != 0) &&
       (iVar6 = FUN_43560de0(0x1a,2,0,auStack_28,1), iVar6 != 0)) {
      FUN_43560e00(0x1a,auStack_30);
      FUN_4378eb78(3,9,1,DAT_437909f4 + 0x437904f2,**(undefined4 **)(iVar16 + 0x43790496),
                   *(undefined1 *)(iVar7 + 0x43791f8b),uStack_2c);
      FUN_43902718(DAT_437909f8 + 0x43790502,**(undefined4 **)(iVar16 + 0x43790496),
                   *(undefined1 *)(iVar7 + 0x43791f8b),uStack_2c);
      FUN_43560da8(0x1a,3);
    }
    if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
      FUN_43561540(DAT_437909fc + 0x4379051e);
    }
    thunk_FUN_43ae74ca(DAT_43790a04 + 0x4379052e,DAT_43790a00 + 0x4379226c);
  }
  if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
    FUN_43561540(DAT_43790a08 + 0x43790544);
  }
  FUN_437d99a4(DAT_43790a10 + 0x43790558,DAT_43790a0c + 0x4379238e);
  FUN_4378f7a0(0x1073);
  if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
    FUN_43561540(DAT_43790a14 + 0x43790574);
  }
  iVar7 = DAT_43790a1c;
  iVar16 = DAT_43790a18;
  FUN_437b4e88(DAT_43790a1c + 0x43790584,DAT_43790a18 + 0x4379206e);
  FUN_4378f7a0(0x1078);
  iVar6 = thunk_FUN_43adaaf6();
  if (((iVar6 != 0) && ((*(byte *)(iVar16 + 0x43790d8e) & 0x40) == 0)) &&
     (iVar6 = FUN_43560de0(0x1a,1,0,auStack_28,1), iVar6 != 0)) {
    FUN_43560e00(0x1a,auStack_30);
    FUN_4378eb78(3,9,1,DAT_43790a20 + 0x437905e0,**(undefined4 **)(iVar7 + 0x43790588),
                 *(undefined1 *)((int)&DAT_43792060 + iVar16 + 1),uStack_2c);
    FUN_43902718(DAT_43790a24 + 0x437905f2,**(undefined4 **)(iVar7 + 0x43790588),
                 *(undefined1 *)((int)&DAT_43792060 + iVar16 + 1),uStack_2c);
    FUN_43560da8(0x1a,3);
  }
  if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
    FUN_43561540(DAT_43790a28 + 0x4379060e);
  }
  iVar16 = DAT_43790a30;
  aiStack_24[0] = DAT_43790a34 + 0x4379062a;
  FUN_437c1fcc(DAT_43790a30 + 0x43790624,DAT_43790a2c + 0x437921ee,aiStack_24);
  if (*(char *)(*(int *)(iVar16 + 0x43790644) + 2) != '\0') {
    if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
      FUN_43561540(DAT_43790a38 + 0x4379064a);
    }
    iVar16 = DAT_43790a3c;
    FUN_43721840();
    if (((*(uint *)(iVar16 + 0x43790e64) & DAT_437908e4) == 0) &&
       (iVar6 = FUN_43560de0(0x1a,2,0,auStack_28,1), iVar7 = DAT_43790a40, iVar6 != 0)) {
      FUN_43560e00(0x1a,auStack_30);
      FUN_4378eb78(3,9,1,DAT_43790a44 + 0x4379069e,**(undefined4 **)(iVar7 + 0x43790686),
                   *(undefined1 *)(iVar16 + 0x43792137),uStack_2c);
      FUN_43902718(DAT_43790a48 + 0x437906ac,**(undefined4 **)(iVar7 + 0x43790686),
                   *(undefined1 *)(iVar16 + 0x43792137),uStack_2c);
      FUN_43560da8(0x1a,3);
    }
    if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
      FUN_43561540(DAT_43790a4c + 0x437906c6);
    }
    thunk_FUN_4377f210(DAT_43790a54 + 0x437906d2,DAT_43790a50 + 0x43792410);
  }
  iVar7 = DAT_43790a5c;
  iVar16 = DAT_43790a58;
  if (*(char *)(*(int *)(DAT_43790a58 + 0x437906fe) + 2) != '\0') {
    FUN_437fc56c(0,*(undefined2 *)(*(int *)(DAT_43790a58 + 0x437906e6) + 0x26c));
    FUN_437fc56c(2,**(undefined2 **)(iVar16 + 0x437906ea));
    FUN_437fc56c(1,*(undefined2 *)(*(int *)(iVar16 + 0x43790716) + 0x14));
    FUN_437fc56c(3,**(undefined2 **)(iVar16 + 0x4379071a));
    FUN_437fc56c(4,**(undefined2 **)(iVar16 + 0x4379070a));
    FUN_437fc56c(6,*(undefined2 *)(*(int *)(iVar16 + 0x437906f2) + 0x2c));
    FUN_437fc56c(8,**(undefined2 **)(iVar16 + 0x437906fa));
    FUN_437fc56c(10,*(undefined2 *)(iVar7 + 0x437921cc));
    FUN_437fc56c(9,**(undefined2 **)(iVar16 + 0x4379072a));
    uVar8 = FUN_4377e500();
    FUN_437fc56c(0xb,uVar8);
    FUN_437fc56c(5,*(undefined2 *)(iVar7 + 0x437906fc));
    FUN_437fc56c(0xc,*(undefined2 *)(iVar7 + 0x437921ce));
    FUN_43b007ae();
    FUN_437fc580();
    FUN_43ae9130(auStack_50,DAT_43790a60 + 0x43790776);
    FUN_439018b0(DAT_43790a64 + 0x43790782,auStack_50,0,0);
  }
  if (*(char *)(DAT_43790a68 + 0x4379226b) == '\x01') {
    uVar8 = FUN_437876dc();
    iVar16 = FUN_43b00cba();
    if (iVar16 != 0) {
      FUN_43b00ed8(uVar8,DAT_43790a6c + 0x437907a8);
    }
  }
  FUN_43ae129a(4);
  if ((uVar11 != **(uint **)(DAT_43790a70 + 0x437907ba)) ||
     (param_1 != *(byte *)(DAT_43790a74 + 0x437922a1))) {
    iVar6 = thunk_FUN_436cd00c();
    iVar7 = DAT_43790a7c;
    iVar16 = DAT_43790a78;
    uVar14 = (uint)(iVar6 - (*(undefined4 **)(DAT_43790a78 + 0x437907de))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43790a80 + 0x437907fa,uVar11,param_1,
                 **(undefined4 **)(DAT_43790a78 + 0x437907de),
                 *(undefined1 *)(DAT_43790a7c + 0x437922bd),uVar14);
    FUN_43902718(DAT_43790a84 + 0x43790816,uVar11,param_1,**(undefined4 **)(iVar16 + 0x437907de),
                 *(undefined1 *)(iVar7 + 0x437922bd),uVar14);
    if (param_1 < 4) {
      uVar8 = *(undefined4 *)(DAT_43790a88 + 0x43790826 + param_1 * 4);
    }
    else {
      uVar8 = 7;
    }
    FUN_4378f988(4,uVar8,uVar14);
    if ((*(byte *)(iVar13 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43790a8c + 0x43790842);
    }
    if ((*(byte *)(iVar13 + 0x1b) & 0x20) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(char *)(DAT_43790a90 + 0x43792336) == '\0') ||
     (*(int *)(*(int *)(DAT_43790a94 + 0x43790866) + 0x14) != 0)) {
    FUN_4378d3b4();
  }
  cVar2 = *(char *)(DAT_43790a98 + 0x4379234f);
  if (cVar2 == '\x01') {
    if (*(int *)(DAT_43790a98 + 0x43790e40) == 0) goto LAB_437908b0;
    uVar8 = 2;
  }
  else if (cVar2 == '\0') {
    if ((*(int *)(DAT_43790a98 + 0x43790e40) == 0) && (*(int *)(DAT_43790a98 + 0x43790e14) != 1))
    goto LAB_437908b0;
    uVar8 = 1;
  }
  else {
    if ((cVar2 != '\x02') ||
       ((*(int *)(DAT_43790a98 + 0x43790e40) == 0 && (*(int *)(DAT_43790a98 + 0x43790e14) != 1))))
    goto LAB_437908b0;
    uVar8 = 3;
  }
  FUN_43901480(uVar8);
LAB_437908b0:
  if (((*(byte *)(iVar13 + 0x12) & 1) != 0) && (*(byte *)(DAT_43790a9c + 0x4379239f) < 4)) {
                    /* WARNING: Could not recover jumptable at 0x437908ca. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_437908ca::switchdataD_437908ce +
              (uint)(&switchD_437908ca::switchdataD_437908ce)[*(byte *)(DAT_43790a9c + 0x4379239f)]
              * 2))();
    return;
  }
  return;
}


/* 4379155c */

void FUN_4379155c(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  undefined1 *puVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
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
  
  iVar9 = DAT_43791830 + 0x4379156c;
  iVar8 = *(int *)(iVar9 + DAT_43791834);
  if ((*(byte *)(iVar8 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43791838 + 0x4379157a);
  }
  iVar3 = DAT_4379183c;
  if (param_1 == **(int **)(DAT_4379183c + 0x43791586)) {
    iVar2 = FUN_43560de0(0x1a,0x40,0,auStack_24,4);
    if (iVar2 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,DAT_4379184c + 0x4379161e,**(undefined4 **)(iVar3 + 0x43791586),uStack_30);
      FUN_43902718(DAT_43791850 + 0x4379162a,**(undefined4 **)(iVar3 + 0x43791586),uStack_30);
    }
    FUN_43560dc4(0x1a,0xffffffbf);
    FUN_43ae1292(1);
    iVar3 = FUN_43ae8d4e();
    if (iVar3 == 0) {
      FUN_43901778();
      if (*(char *)(DAT_43791854 + 0x4379164e) != '\0') {
        *(undefined1 *)(DAT_43791858 + 0x43791658) = 1;
      }
      uVar5 = 0;
      puVar6 = (undefined1 *)(DAT_4379185c + 0x43791660);
    }
    else {
      uVar5 = 1;
      puVar6 = (undefined1 *)(DAT_43791860 + 0x43791668);
    }
    *puVar6 = uVar5;
    iVar3 = DAT_43791864;
    FUN_43560dc4(0x1a,0xfffffeff);
    iVar2 = FUN_43b039fc(iVar3 + 0x4379167a,DAT_43791868 + 0x4379167e);
    if (iVar2 == 0) {
      iVar3 = 0;
    }
    else if (*(int *)(iVar3 + 0x43791692) == 0) {
      if (*(char *)(DAT_4379186c + 0x4379168c) == '\0') {
        if (*(char *)(DAT_43791870 + 0x43791e25) == '\0') {
          iVar3 = 0;
        }
        else {
          iVar3 = iVar3 + 0x4379167e;
        }
      }
      else {
        iVar3 = 0;
      }
    }
    else {
      iVar3 = 0;
    }
    puVar6 = (undefined1 *)FUN_4379ce18();
    iVar2 = DAT_43791874;
    iVar7 = DAT_43791874 + 0x437916b8;
    thunk_FUN_43af2858(*(undefined4 *)(DAT_43791874 + 0x437916e0),puVar6);
    *puVar6 = 0;
    uVar4 = FUN_43ae8cd0(*(undefined4 *)(iVar9 + DAT_43791878));
    iVar9 = DAT_4379187c;
    uVar1 = FUN_43796954(uVar4,iVar3,iVar7);
    *(undefined2 *)(iVar9 + 0x43791eee) = uVar1;
    iVar7 = FUN_437999e4(1,0xd);
    iVar3 = DAT_43791880;
    if (((iVar7 != 0) && (*(int *)(iVar9 + 0x43791cae) != 0)) &&
       ((*(short *)(iVar9 + 0x43791d4e) == 1 || (*(int *)(*(int *)(iVar2 + 0x437916bc) + 0xc) == 0))
       )) {
      uStack_44 = FUN_43ae9332(*(undefined4 *)(DAT_43791880 + 0x43791cf0));
      uStack_40 = 0;
      uStack_3f = 0;
      iVar9 = FUN_43795610(*(undefined1 *)(iVar3 + 0x43791e99));
      if (((iVar9 != 0) && (*(char *)(DAT_43791884 + 0x4379172a) == '\0')) &&
         (*(char *)(iVar3 + 0x43791ea8) != '\0')) {
        uStack_3f = 1;
      }
      uStack_3c = (uint)(*(int *)(*(int *)(DAT_43791888 + 0x4379173e) + 0x548) != 0);
      uStack_38 = *(undefined4 *)(*(int *)(DAT_43791888 + 0x4379173e) + 0x54c);
      iVar9 = FUN_437956c8(DAT_4379188c + 0x43791dae,&uStack_44);
      if (iVar9 != 0) {
        FUN_4378eb78(3,9,1,DAT_43791890 + 0x43791770,iVar9);
        FUN_43902718(DAT_43791894 + 0x4379177a,iVar9);
      }
    }
    FUN_43900380();
    iVar9 = DAT_43791898;
    FUN_439cdbc8();
    uStack_28 = 0;
    uStack_2c = 0;
    FUN_43728c18(0,&uStack_28,&uStack_2c);
    FUN_43b6d334(uStack_28,uStack_2c);
    FUN_43560da8(0x1a,0x100);
    FUN_43ae129a(1);
    if ((param_1 != **(int **)(iVar9 + 0x43791796)) && (iVar3 = FUN_43ae8d4e(), iVar3 != 0)) {
      iVar3 = thunk_FUN_436cd00c();
      uVar10 = (uint)(iVar3 - (*(undefined4 **)(iVar9 + 0x43791796))[2]) >> 1;
      FUN_4378eb78(3,9,1,DAT_4379189c + 0x437917d4,param_1,**(undefined4 **)(iVar9 + 0x43791796),
                   uVar10);
      FUN_43902718(DAT_437918a0 + 0x437917ea,param_1,**(undefined4 **)(iVar9 + 0x43791796),uVar10);
      FUN_4378f988(4,1,uVar10);
      if ((*(byte *)(iVar8 + 0x12) & 4) != 0) {
        FUN_43561540(DAT_437918a4 + 0x43791806);
      }
      if ((*(byte *)(iVar8 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43791528();
    if ((*(byte *)(iVar8 + 0x12) & 1) != 0) {
      FUN_43561540(DAT_437918a8 + 0x43791826);
    }
  }
  else {
    iVar9 = FUN_43ae8d4e();
    if (iVar9 != 0) {
      iVar9 = thunk_FUN_436cd00c();
      uVar10 = (uint)(iVar9 - (*(undefined4 **)(iVar3 + 0x43791586))[2]) >> 1;
      FUN_4378eb78(3,9,1,DAT_43791840 + 0x437915aa,param_1,**(undefined4 **)(iVar3 + 0x43791586),
                   uVar10);
      FUN_43902718(DAT_43791844 + 0x437915c0,param_1,**(undefined4 **)(iVar3 + 0x43791586),uVar10);
      FUN_4378f988(3,1,uVar10);
      if ((*(byte *)(iVar8 + 0x12) & 4) != 0) {
        FUN_43561540(DAT_43791848 + 0x437915dc);
      }
      if ((*(byte *)(iVar8 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* 43791a7c */

void FUN_43791a7c(int param_1)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  byte *pbVar11;
  uint *puVar12;
  undefined4 uVar13;
  undefined4 *puVar14;
  char *pcVar15;
  ushort *puVar16;
  uint *puVar17;
  int iVar18;
  undefined4 *puVar19;
  int iVar20;
  int *piVar21;
  undefined4 *puVar22;
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
  
  iVar10 = DAT_43791fe4;
  iVar7 = DAT_43791fe0;
  FUN_43795e7c();
  FUN_43796424();
  iVar10 = iVar10 + 0x43791a9a;
  if (*(char *)(iVar7 + 0x43791a94) == '\0') {
    FUN_43ae863c(auStack_48,*(undefined4 *)(iVar10 + DAT_43791fe8));
    FUN_436ccee4(0x1e,1,auStack_48);
    FUN_43ae863c(auStack_5c,*(undefined4 *)(iVar10 + DAT_43791fec));
    FUN_436ccee4(0x17,1,auStack_5c);
    *(char *)(iVar7 + 0x43791a94) = '\x01';
  }
  iVar7 = *(int *)(iVar10 + DAT_43791ff0);
  if ((*(byte *)(iVar7 + 0xc) & 1) != 0) {
    FUN_4378eb78(3,9,1,DAT_43791ff4 + 0x43791aea);
    FUN_43902718(DAT_43791ff8 + 0x43791af4);
  }
  thunk_FUN_4386116c();
  thunk_FUN_436e06f4();
  if ((*(byte *)(iVar7 + 4) & 1) != 0) {
    piVar21 = *(int **)(iVar10 + DAT_43791ffc);
    iVar18 = *piVar21;
    puVar22 = *(undefined4 **)(iVar10 + DAT_43792000);
    uVar13 = *puVar22;
    uVar3 = FUN_43795d2c();
    puVar19 = *(undefined4 **)(iVar10 + DAT_43792004);
    puVar14 = *(undefined4 **)(iVar10 + DAT_43792008);
    FUN_4378eb78(3,9,1,DAT_4379200c + 0x43791b4c,iVar18,uVar13,uVar3,*puVar19,*puVar14);
    iVar18 = *piVar21;
    uVar13 = *puVar22;
    uVar3 = FUN_43795d2c();
    FUN_43902718(DAT_43792010 + 0x43791b72,iVar18,uVar13,uVar3,*puVar19,*puVar14);
    *piVar21 = param_1;
    *puVar22 = 0;
    *puVar19 = 0;
    *puVar14 = 0;
  }
  FUN_43904008();
  FUN_43901638(0);
  FUN_43901638(4);
  FUN_43901638(8);
  FUN_43901638(5);
  iVar18 = *(int *)(iVar10 + DAT_43792014);
  if (((*(byte *)(iVar18 + 0x29) & 0xf) != 0xf) &&
     (pcVar15 = *(char **)(iVar10 + DAT_43792018), *pcVar15 != '\0')) {
    FUN_43901638(9);
    *pcVar15 = '\0';
  }
  if (((*(byte *)(iVar18 + 0x29) & 0xf0) != 0xf0) &&
     (pcVar15 = *(char **)(iVar10 + DAT_4379201c), *pcVar15 != '\0')) {
    FUN_43901638(10);
    *pcVar15 = '\0';
  }
  iVar8 = DAT_43792020;
  FUN_43901768();
  FUN_43901748();
  FUN_43903f18();
  uVar1 = *(undefined1 *)(iVar8 + 0x437921da);
  *(undefined1 *)((int)&DAT_437936d4 + iVar8) = uVar1;
  FUN_4378e1a4(param_1,uVar1,iVar8 + 0x43792156);
  iVar4 = FUN_437fe4f4();
  *(bool *)(iVar8 + 0x437921cd) = iVar4 != 0;
  piVar21 = (int *)(DAT_43792024 + 0x43791c22);
  iVar8 = *piVar21;
  if (iVar8 != 7) {
    FUN_4378eb78(3,9,1,DAT_43792028 + 0x43791c36,param_1,iVar8);
    FUN_43902718(DAT_4379202c + 0x43791c42,param_1,*piVar21);
  }
  iVar8 = DAT_43792030;
  *(undefined1 *)((int)&DAT_43793728 + DAT_43792030 + 3) = 0;
  *(undefined1 *)((int)&DAT_4379372c + iVar8) = 0;
  *(undefined4 *)(DAT_43792034 + 0x43791c5c) = 0;
  *(undefined4 *)(DAT_43792038 + 0x43791c64) = 1;
  iVar20 = **(int **)(DAT_4379203c + 0x43791c6e);
  iVar4 = FUN_4379a898();
  *(undefined1 *)(iVar8 + 0x43792222) = *(undefined1 *)(iVar4 + 0x5c);
  *(char *)(iVar8 + 0x43792221) = *(char *)(iVar8 + 0x437923dd);
  if (*(char *)(iVar8 + 0x437923dd) != '\0') {
    *(char *)(iVar8 + 0x43792220) = *(char *)(iVar8 + 0x43792220) + '\x01';
    *(undefined4 *)(iVar8 + 0x4379221c) = *(undefined4 *)(iVar8 + 0x4379222c);
    *(undefined4 *)(iVar8 + 0x437923d8) = *(undefined4 *)(iVar8 + 0x4379222c);
    FUN_43ae8cd4(*(undefined4 *)(iVar10 + DAT_43792040));
  }
  if (*(int *)(DAT_43792044 + 0x43792432) != 0) {
    *(int *)(DAT_43792044 + 0x43792432) = *(int *)(DAT_43792044 + 0x43792432) + -1;
  }
  iVar10 = DAT_43792048;
  pcVar15 = (char *)(DAT_43792048 + 0x43792456);
  *(char *)(DAT_43792048 + 0x43792293) = *pcVar15;
  if (*pcVar15 != '\0') {
    *(undefined1 *)(iVar10 + 0x43792292) = *(undefined1 *)(iVar10 + 0x4379244e);
    *(undefined4 *)(iVar10 + 0x4379228e) = *(undefined4 *)(iVar10 + 0x4379244a);
    *(undefined4 *)(iVar10 + 0x43792452) = *(undefined4 *)(iVar10 + 0x4379244a);
  }
  if (*(int *)(DAT_4379204c + 0x43792474) != 0) {
    *(int *)(DAT_4379204c + 0x43792474) = *(int *)(DAT_4379204c + 0x43792474) + -1;
  }
  if (*(int *)(DAT_43792050 + 0x43791cea) == *(int *)(DAT_43792054 + 0x43791cee)) {
    pbVar11 = (byte *)(DAT_43792058 + 0x43791cf8);
    if (*pbVar11 < 5) {
      bVar6 = *pbVar11 + 1;
      puVar16 = (ushort *)(DAT_4379205c + 0x43791d08);
      uVar9 = (uint)bVar6;
      *pbVar11 = bVar6;
      uVar5 = (uint)*puVar16;
      FUN_4378eb78(3,9,1,DAT_43792060 + 0x43791d18,uVar5,uVar9);
      FUN_43902718(DAT_43792064 + 0x43791d22,*puVar16,*pbVar11);
      if (*pbVar11 == 1) {
        FUN_43901a8c(3,1,*puVar16,0);
      }
      if (*(char *)(DAT_43792068 + 0x43791d3c) == '\x05') {
        FUN_4378eb78(3,9,1,DAT_4379206c + 0x43791d4c,uVar5,uVar9);
        FUN_43902718(DAT_43792070 + 0x43791d54);
      }
    }
  }
  piVar21 = (int *)(DAT_43792078 + 0x43791d62);
  *(undefined4 *)(DAT_43792074 + 0x43791d5e) = *(undefined4 *)(DAT_4379207c + 0x43791d64);
  if (*piVar21 != 0) {
    uStack_f0 = *(undefined4 *)(DAT_43792080 + 0x43791d70);
    iVar10 = FUN_4378f9b4();
    uStack_ec = *(undefined4 *)(*(int *)(iVar10 + 8) + 0x1e8);
    iVar10 = FUN_4378f9b4();
    uStack_e8 = *(undefined4 *)(*(int *)(iVar10 + 8) + 0x3c);
    iVar10 = FUN_4378f9b4();
    uStack_dc = *(undefined4 *)(*(int *)(iVar10 + 4) + 0x18);
    iVar10 = FUN_4378f9b4();
    uStack_e0 = *(undefined4 *)(*(int *)(iVar10 + 0xc) + 0x5c);
    uStack_d8 = FUN_43ae1252();
    (*(code *)*piVar21)(&uStack_f0);
  }
  iVar8 = DAT_43792088 + 0x43791db6;
  FUN_43ada220(auStack_70,DAT_43792084 + 0x43791db4);
  FUN_439018b0(iVar8,auStack_70,iVar20,0);
  FUN_43ada220(auStack_84,DAT_4379208c + 0x43791dcc);
  iVar10 = DAT_43792090;
  FUN_439018b0(iVar8,auStack_84,iVar20 << 8,0);
  iVar8 = *(int *)(*(int *)(iVar10 + 0x43791de0) + 0x2c);
  FUN_43ae863c(auStack_98,DAT_43792094 + 0x43791de8);
  FUN_436ccd9c(1,param_1 + iVar8,1,auStack_98);
  if ((*(byte *)(iVar7 + 0x1f) & 1) == 0) {
    FUN_4378d818(param_1,*(undefined4 *)(*(int *)(iVar10 + 0x43791de0) + 0x24));
  }
  if ((*(byte *)(iVar7 + 0x1f) & 2) == 0) {
    FUN_4378db0c(param_1,*(undefined4 *)(*(int *)(DAT_43792098 + 0x43791e24) + 0x24));
  }
  *(undefined1 *)(DAT_4379209c + 0x43791e2e) = 0;
  iVar10 = FUN_436e8328();
  if (iVar10 == 1) {
    FUN_43ae72f6(&uStack_34);
    iVar10 = *(int *)(*(int *)(DAT_437920a8 + 0x43791e58) + 0x14);
    if (iVar10 == 1) {
      *(uint *)(DAT_437920b4 + 0x43791e86) = (uint)uStack_30;
      *(uint *)(DAT_437920b8 + 0x43791e8c) = (uint)uStack_2e;
    }
    else if (iVar10 == 2) {
      *(uint *)(DAT_437920bc + 0x43791e94) = (uint)uStack_2c;
      *(uint *)(DAT_437920c0 + 0x43791e9a) = (uint)uStack_2a;
    }
    else {
      *(uint *)(DAT_437920ac + 0x43791e78) = (uint)uStack_34;
      *(uint *)(DAT_437920b0 + 0x43791e7e) = (uint)uStack_32;
    }
    puVar12 = (uint *)(DAT_437920c4 + 0x43791ea2);
    puVar17 = (uint *)(DAT_437920c8 + 0x43791ea4);
    uVar9 = *puVar12;
    uVar5 = *puVar17;
    *puVar12 = uVar9 << 1;
    *puVar17 = uVar5 << 1;
    uVar5 = FUN_43ae8c60();
    if (((uVar9 << 1 < uVar5) ||
        (uVar5 = *puVar17, uVar9 = *puVar12, iVar10 = FUN_43ae8c60(), uVar5 < iVar10 + uVar9)) ||
       (*(uint *)(*(int *)(DAT_437920cc + 0x43791ed2) + 0x24) < *puVar17)) {
      iVar7 = DAT_437920d8;
      puVar19 = (undefined4 *)(DAT_437920d0 + 0x43791ee0);
      puVar14 = (undefined4 *)(DAT_437920d4 + 0x43791ee4);
      FUN_4378eb78(3,9,1,DAT_437920dc + 0x43791efa,*puVar19,*puVar14,
                   *(undefined4 *)(*(int *)(DAT_437920d8 + 0x43791eee) + 0x24));
      FUN_43902718(DAT_437920e0 + 0x43791f08,*puVar19,*puVar14,
                   *(undefined4 *)(*(int *)(iVar7 + 0x43791eee) + 0x24));
      *puVar19 = 0;
      *puVar14 = 0;
    }
    else if ((*(byte *)(iVar7 + 0x1f) & 4) == 0) {
      uVar5 = *puVar12;
      FUN_43ae863c(auStack_ac,DAT_437920e4 + 0x43791f20);
      FUN_436ccd9c(5,param_1 + uVar5,1,auStack_ac);
      *(undefined1 *)(DAT_437920e8 + 0x43791f36) = 1;
      iVar7 = FUN_4378e90c();
      if (iVar7 != 0) {
        uVar9 = (uint)*(byte *)(iVar18 + 0x28) * -200 + *puVar12;
        puVar17 = (uint *)(DAT_437920ec + 0x43791f52);
        *puVar17 = uVar9;
        uVar5 = FUN_43ae8c60();
        iVar7 = DAT_437920f4;
        if ((uVar9 < uVar5) || (*puVar12 <= *puVar17)) {
          puVar14 = (undefined4 *)(DAT_437920f0 + 0x43791f6e);
          FUN_4378eb78(3,9,1,DAT_437920f8 + 0x43791f80,*puVar14,
                       *(undefined4 *)(*(int *)(DAT_437920f4 + 0x43791f76) + 0x24));
          FUN_43902718(DAT_437920fc + 0x43791f8c,*puVar14,
                       *(undefined4 *)(*(int *)(iVar7 + 0x43791f76) + 0x24));
          uVar3 = FUN_43ae8c60();
          *puVar14 = uVar3;
        }
        param_1 = param_1 + *(int *)(DAT_43792100 + 0x43791fa0);
        FUN_43ae863c(auStack_c0,DAT_43792104 + 0x43791fa6);
        puVar2 = &stack0x0000002c;
        goto LAB_43791fca;
      }
    }
  }
  else {
    *(undefined4 *)(DAT_437920a0 + 0x43791e3c) = 0;
    *(undefined4 *)(DAT_437920a4 + 0x43791e42) = 0;
  }
  param_1 = FUN_4378e938();
  FUN_43ae863c(auStack_d4,DAT_43792108 + 0x43791fbc);
  puVar2 = &stack0x00000018;
LAB_43791fca:
  FUN_436ccd9c(0,param_1,1,puVar2 + -0xec);
  return;
}


/* 4379210c */

void FUN_4379210c(int param_1)

{
  ushort uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  undefined1 uVar8;
  undefined4 *puVar9;
  undefined1 *puVar10;
  ushort *puVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  byte bVar16;
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined1 auStack_2c [4];
  uint uStack_28;
  undefined1 auStack_24 [4];
  
  iVar13 = DAT_437925f8 + 0x43792120;
  iVar12 = *(int *)(iVar13 + DAT_437925fc);
  if ((*(byte *)(iVar12 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43792600 + 0x43792130);
  }
  iVar4 = DAT_43792604;
  if (param_1 == **(int **)(DAT_43792604 + 0x4379213e)) {
    FUN_43ae1292(4);
    iVar4 = FUN_43ae8d4e();
    if (iVar4 == 0) {
      FUN_43901778();
      if (*(char *)(DAT_43792614 + 0x437921ba) != '\0') {
        *(undefined1 *)(DAT_43792618 + 0x437921c6) = 1;
      }
      uVar8 = 0;
      puVar10 = (undefined1 *)(DAT_4379261c + 0x437921d0);
    }
    else {
      uVar8 = 1;
      puVar10 = (undefined1 *)(DAT_43792620 + 0x437921da);
    }
    *puVar10 = uVar8;
    FUN_43728c70();
    FUN_4378f7a0(0xd35);
    iVar4 = DAT_43792624;
    uVar5 = FUN_4377fdf8();
    *(undefined4 *)(iVar4 + 0x43794040) = uVar5;
    FUN_43560e00(0x11,auStack_2c);
    iVar6 = FUN_4378e90c();
    if (iVar6 != 0) {
      uStack_28 = uStack_28 & 0xfffffffb | *(uint *)(iVar4 + 0x437929f8) & 4;
    }
    *(uint *)(iVar4 + 0x437929f8) = uStack_28;
    uVar1 = *(ushort *)(DAT_43792628 + 0x43792220);
    if (uVar1 != 0) {
      puVar11 = (ushort *)(DAT_4379262c + 0x4379222a);
      uVar2 = *puVar11;
      *puVar11 = uVar2 + 1;
      if (uVar1 < (ushort)(uVar2 + 1)) {
        *puVar11 = 1;
        iVar4 = 0;
        do {
          *(undefined2 *)(DAT_43792630 + 0x43792242 + iVar4) = 0;
          *(undefined2 *)(DAT_43792634 + 0x43792248 + iVar4) = 0;
          *(undefined2 *)(DAT_43792638 + 0x4379224e + iVar4) = 0;
          iVar4 = iVar4 + 2;
        } while (iVar4 != 0x1a);
      }
    }
    iVar6 = FUN_4378e90c();
    iVar4 = DAT_4379263c;
    if (iVar6 == 0) {
      iVar6 = DAT_4379263c + 0x43792262;
      if ((*(uint *)(DAT_4379263c + 0x43792a66) & 4) == 0) {
        uVar5 = FUN_437b4d64();
        iVar7 = DAT_43792640 + 0x43792278;
        *(undefined4 *)(iVar4 + 0x437940b2) = uVar5;
        FUN_43ae8e2c(iVar6,iVar7);
        *(undefined2 *)(DAT_43792644 + 0x43792288) = 0;
      }
      else {
        *(short *)(DAT_43792648 + 0x43792290) = *(short *)(DAT_43792648 + 0x43792290) + 1;
        *(short *)(DAT_4379264c + 0x4379229a) = *(short *)(DAT_4379264c + 0x4379229a) + 1;
      }
    }
    iVar4 = DAT_43792650;
    iVar6 = DAT_43792650 + 0x437922a2;
    if ((*(uint *)(DAT_43792650 + 0x43792aa6) & 8) == 0) {
      uVar5 = FUN_4379fc20();
      iVar7 = DAT_43792654 + 0x437922b8;
      *(undefined4 *)(iVar4 + 0x437940fa) = uVar5;
      FUN_43ae8e5c(iVar6,iVar7);
      *(undefined2 *)(DAT_43792658 + 0x437922ca) = 0;
    }
    else {
      *(short *)(DAT_4379265c + 0x437922d2) = *(short *)(DAT_4379265c + 0x437922d2) + 1;
      *(short *)(DAT_43792660 + 0x437922dc) = *(short *)(DAT_43792660 + 0x437922dc) + 1;
    }
    iVar4 = DAT_43792664;
    iVar6 = DAT_43792664 + 0x437922e2;
    if ((*(uint *)(DAT_43792664 + 0x43792ae6) & 0x20) == 0) {
      uVar5 = FUN_437d0bc8();
      iVar7 = DAT_43792668 + 0x437922f8;
      *(undefined4 *)(iVar4 + 0x4379413e) = uVar5;
      FUN_43ae8e74(iVar6,iVar7);
      *(undefined2 *)(DAT_4379266c + 0x4379230e) = 0;
    }
    else {
      *(short *)(DAT_43792670 + 0x43792316) = *(short *)(DAT_43792670 + 0x43792316) + 1;
      *(short *)(DAT_43792674 + 0x43792320) = *(short *)(DAT_43792674 + 0x43792320) + 1;
    }
    iVar4 = DAT_43792678;
    iVar6 = DAT_43792678 + 0x43792322;
    if ((*(uint *)(DAT_43792678 + 0x43792b26) & 0x40) == 0) {
      uVar5 = FUN_437d9930();
      iVar7 = DAT_4379267c + 0x43792338;
      *(undefined4 *)(iVar4 + 0x43794182) = uVar5;
      FUN_43ae8e84(iVar6,iVar7);
      *(undefined2 *)(DAT_43792680 + 0x43792350) = 0;
    }
    else {
      *(short *)(DAT_43792684 + 0x43792358) = *(short *)(DAT_43792684 + 0x43792358) + 1;
      *(short *)(DAT_43792688 + 0x43792362) = *(short *)(DAT_43792688 + 0x43792362) + 1;
    }
    iVar4 = DAT_4379268c;
    iVar6 = DAT_4379268c + 0x43792362;
    if ((*(uint *)(DAT_4379268c + 0x43792b66) & 0x80) == 0) {
      uVar5 = FUN_437b6614();
      iVar7 = DAT_43792690 + 0x43792378;
      *(undefined4 *)(iVar4 + 0x437941c6) = uVar5;
      FUN_43ae8e9a(iVar6,iVar7);
      *(undefined2 *)(DAT_43792694 + 0x43792392) = 0;
    }
    else {
      *(short *)(DAT_43792698 + 0x4379239a) = *(short *)(DAT_43792698 + 0x4379239a) + 1;
      *(short *)(DAT_4379269c + 0x437923a4) = *(short *)(DAT_4379269c + 0x437923a4) + 1;
    }
    iVar4 = DAT_437926a0;
    iVar6 = DAT_437926a0 + 0x437923a2;
    if ((*(uint *)(DAT_437926a0 + 0x43792ba6) & 0x200) == 0) {
      uVar5 = FUN_437b8230();
      iVar7 = DAT_437926a4 + 0x437923b8;
      *(undefined4 *)(iVar4 + 0x4379420a) = uVar5;
      FUN_43ae8ea4(iVar6,iVar7);
      *(undefined2 *)(DAT_437926a8 + 0x437923d6) = 0;
    }
    else {
      *(short *)(DAT_437926ac + 0x437923de) = *(short *)(DAT_437926ac + 0x437923de) + 1;
      *(short *)(DAT_437926b0 + 0x437923e8) = *(short *)(DAT_437926b0 + 0x437923e8) + 1;
    }
    FUN_4378f7a0(0xd96);
    iVar4 = FUN_4378e90c();
    if (iVar4 == 0) {
      FUN_4378f7a0(0xda0);
      FUN_437b4e28(DAT_437926b4 + 0x437923f6);
      FUN_4378f7a0(0xda2);
    }
    iVar4 = DAT_437926bc;
    iVar7 = DAT_437926b8 + 0x4379240a;
    FUN_437c1bb4(iVar7);
    thunk_FUN_43b7c7da(iVar7);
    FUN_437b0244(iVar7,iVar4 + 0x43793ee8);
    iVar6 = FUN_4378e90c();
    if (iVar6 == 0) {
      FUN_4378f7a0(0xda9);
      FUN_43aef444(iVar7,iVar4 + 0x4379369e);
      FUN_4378f7a0(0xdad);
    }
    iVar6 = DAT_437926c4;
    iVar4 = DAT_437926c0;
    iVar7 = DAT_437926c4 + 0x43792450;
    FUN_437c1b98(iVar7,DAT_437926c0 + 0x43793b7e);
    thunk_FUN_43b7c7dc(iVar7,iVar4 + 0x43793d1f);
    iVar4 = FUN_43560de0(0x1a,0x100,0,auStack_24,4);
    if (iVar4 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,DAT_437926c8 + 0x43792498,**(undefined4 **)(iVar6 + 0x43792454),uStack_30);
      FUN_43902718(DAT_437926cc + 0x437924a4,**(undefined4 **)(iVar6 + 0x43792454),uStack_30);
      FUN_43560da8(0x1a,0x100);
    }
    if (*(char *)(iVar12 + 0x70) == '\0') {
      iVar4 = FUN_437999e4(1,0xe);
      if (iVar4 != 0) {
        if ((*(char *)(DAT_437926d0 + 0x43792a9f) == '\0') ||
           (*(int *)(*(int *)(DAT_437926d4 + 0x437924d6) + 0xc) != 0)) {
          FUN_439e21c0();
        }
        FUN_439e2184();
      }
      FUN_439fd76c();
    }
    iVar4 = DAT_437926d8;
    FUN_4378f7a0(0xdd0);
    FUN_437967e8(iVar4 + 0x437924f0);
    FUN_4378f7a0(0xdd3);
    FUN_43ada220(auStack_48,DAT_437926dc + 0x43792504);
    FUN_439018b0(DAT_437926e0 + 0x43792510,auStack_48,param_1,0);
    bVar16 = *(byte *)(iVar12 + 0x1f) & 8;
    if (((*(byte *)(iVar12 + 0x1f) & 8) == 0) && (iVar6 = FUN_436e8328(), iVar6 != 0)) {
      iVar6 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 0x24);
      iVar7 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 8);
      iVar15 = *(int *)(iVar13 + DAT_437926e4);
      uVar3 = *(undefined2 *)(iVar15 + 0x2e);
      FUN_43ae863c(auStack_5c,bVar16);
      FUN_436ccd9c(6,iVar6 + iVar7,uVar3,auStack_5c);
      iVar6 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 0x24);
      iVar4 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 8);
      iVar13 = FUN_43ada230();
      uVar3 = *(undefined2 *)(iVar15 + 0x2c);
      FUN_43ae863c(auStack_70,bVar16);
      FUN_436ccd9c(7,iVar6 + iVar4 + iVar13 * 2,uVar3,auStack_70);
    }
    iVar13 = DAT_437926e8;
    FUN_43ae129a(4);
    if (param_1 != **(int **)(iVar13 + 0x43792582)) {
      iVar4 = thunk_FUN_436cd00c();
      uVar14 = (uint)(iVar4 - (*(undefined4 **)(iVar13 + 0x43792582))[2]) >> 1;
      FUN_4378eb78(3,9,1,DAT_437926ec + 0x4379259c,param_1,**(undefined4 **)(iVar13 + 0x43792582),
                   uVar14);
      FUN_43902718(DAT_437926f0 + 0x437925b2,param_1,**(undefined4 **)(iVar13 + 0x43792582),uVar14);
      FUN_4378f988(4,2,uVar14);
      if ((*(byte *)(iVar12 + 0x12) & 4) != 0) {
        FUN_43561540(DAT_437926f4 + 0x437925ce);
      }
      if ((*(byte *)(iVar12 + 0x1b) & 8) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43901480(0);
    if ((*(byte *)(iVar12 + 0x12) & 1) != 0) {
      FUN_43561540(DAT_437926f8 + 0x437925f0);
    }
  }
  else {
    iVar13 = thunk_FUN_436cd00c();
    puVar9 = *(undefined4 **)(iVar4 + 0x4379213e);
    uVar14 = (uint)(iVar13 - puVar9[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43792608 + 0x4379215a,param_1,*puVar9,uVar14);
    FUN_43902718(DAT_4379260c + 0x43792172,param_1,**(undefined4 **)(iVar4 + 0x4379213e),uVar14);
    FUN_4378f988(3,2,uVar14);
    if ((*(byte *)(iVar12 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43792610 + 0x43792190);
    }
    if ((*(byte *)(iVar12 + 0x1b) & 8) != 0) {
      FUN_4378ec60();
    }
  }
  return;
}


/* 437927c4 */

void FUN_437927c4(int param_1)

{
  char cVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  byte bVar4;
  uint uVar5;
  int *piVar6;
  uint *puVar7;
  uint *puVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined4 uStack_a0;
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
  
  iVar11 = DAT_43792974 + 0x437927da;
  uVar5 = *(uint *)(DAT_43792970 + 0x437927ce) + 1;
  *(uint *)(DAT_43792970 + 0x437927ce) = uVar5;
  if ((uVar5 & 1) != 0) goto LAB_43792826;
  cVar1 = *(char *)((int)&DAT_437942c4 + DAT_43792978 + 3);
  if (cVar1 == '\x01') {
    uVar3 = 2;
LAB_43792802:
    FUN_43901638(uVar3);
  }
  else {
    if (cVar1 == '\0') {
      uVar3 = 1;
      goto LAB_43792802;
    }
    if (cVar1 == '\x02') {
      uVar3 = 3;
      goto LAB_43792802;
    }
  }
  iVar9 = DAT_4379297c;
  bVar4 = *(char *)((int)&DAT_437942e8 + DAT_4379297c + 3) + 1;
  *(byte *)((int)&DAT_437942e8 + DAT_4379297c + 3) = bVar4;
  if ((uint)*(byte *)((int)&DAT_437942e8 + iVar9 + 2) <= bVar4 + 1) {
    *(undefined1 *)((int)&DAT_437942ec + iVar9) = 1;
  }
LAB_43792826:
  iVar9 = DAT_437929a0;
  puVar8 = (uint *)(DAT_43792984 + 0x43792832);
  piVar6 = *(int **)(DAT_43792980 + 0x43792832);
  puVar7 = (uint *)(DAT_43792988 + 0x43792836);
  iVar10 = *piVar6;
  bVar4 = *(byte *)((int)&DAT_43794318 + DAT_4379298c + 3);
  uVar5 = *puVar8;
  if (uVar5 == *puVar7) {
    if (uVar5 < 7) {
      *puVar7 = uVar5 + 1;
      iVar11 = piVar6[0xb];
      FUN_43ae863c(auStack_48,iVar9 + 0x43792898);
      FUN_436ccd9c(1,iVar11 + param_1,1,auStack_48);
    }
    piVar6 = (int *)(DAT_437929a4 + 0x437928ae);
    if (*piVar6 != 0) {
      uStack_a0 = *(undefined4 *)(DAT_437929a8 + 0x437928b6);
      iVar11 = FUN_4378f9b4();
      uStack_9c = *(undefined4 *)(*(int *)(iVar11 + 8) + 0x1e8);
      iVar11 = FUN_4378f9b4();
      uStack_98 = *(undefined4 *)(*(int *)(iVar11 + 8) + 0x3c);
      iVar11 = FUN_4378f9b4();
      uStack_8c = *(undefined4 *)(*(int *)(iVar11 + 4) + 0x18);
      iVar11 = FUN_4378f9b4();
      uStack_90 = *(undefined4 *)(*(int *)(iVar11 + 0xc) + 0x5c);
      uStack_88 = FUN_43ae1252();
      (*(code *)*piVar6)(&uStack_a0);
    }
    if ((*(uint *)(DAT_437929ac + 0x437928f6) & 1) == 0) {
      iVar9 = (uint)bVar4 + iVar10 * 0x100;
      iVar11 = DAT_437929b4 + 0x4379290c;
      FUN_43ada220(auStack_5c,DAT_437929b0 + 0x43792908);
      FUN_439018b0(iVar11,auStack_5c,iVar9,0);
      if (*(int *)(DAT_437929b8 + 0x43792ef0) == 0) {
        if (*(int *)(DAT_437929b8 + 0x43792ec4) != 1) {
          return;
        }
        if ((*(byte *)((int)&DAT_437943fc + DAT_437929b8 + 3) & 1) == 0) {
          return;
        }
        FUN_43ada220(auStack_84,DAT_437929c0 + 0x4379295c);
        puVar2 = &stack0x00000008;
      }
      else {
        if (*(char *)((int)&DAT_43794400 + DAT_437929b8) == '\0') {
          return;
        }
        FUN_43ada220(auStack_70,DAT_437929bc + 0x43792934);
        puVar2 = &stack0x0000001c;
      }
      FUN_439018b0(iVar11,puVar2 + -0x8c,iVar9,0);
    }
  }
  else {
    FUN_43ae9130(auStack_34,*(undefined4 *)(iVar11 + DAT_43792990));
    FUN_439018b0(DAT_43792994 + 0x43792860,auStack_34,0,0);
    FUN_4378eb78(3,9,1,DAT_43792998 + 0x43792876,*puVar7,*puVar8);
    FUN_43902718(DAT_4379299c + 0x43792880,*puVar7,*puVar8);
  }
  return;
}


/* 43792a0c */

void FUN_43792a0c(int param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  undefined4 uVar17;
  int iVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  undefined4 uVar21;
  undefined4 uVar22;
  undefined4 uVar23;
  undefined4 uVar24;
  short sVar25;
  int extraout_r1;
  undefined4 uVar26;
  undefined4 uVar27;
  undefined4 uVar28;
  undefined4 uVar29;
  undefined4 uVar30;
  undefined4 uVar31;
  undefined1 uVar32;
  char cVar33;
  byte bVar34;
  undefined1 *puVar35;
  undefined4 uVar36;
  undefined4 *puVar37;
  short *psVar38;
  int iVar39;
  int iVar40;
  undefined4 uVar41;
  char *pcVar42;
  int iVar43;
  int iVar44;
  undefined2 *puVar45;
  int iVar46;
  ushort *puVar47;
  uint uVar48;
  int iVar49;
  int *piVar50;
  uint *puVar51;
  int *piVar52;
  uint uVar53;
  undefined4 *puVar54;
  undefined4 uVar55;
  bool bVar56;
  bool bVar57;
  undefined1 *puVar58;
  undefined1 *puVar59;
  undefined1 *puVar60;
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
  
  iVar43 = DAT_43792c44 + 0x43792a1e;
  iVar44 = *(int *)(iVar43 + DAT_43792c48);
  if ((*(byte *)(iVar44 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43792c4c + 0x43792a2e);
  }
  uVar13 = FUN_437876dc();
  if (*(char *)(iVar44 + 0xaa) != '\0') {
    *(int *)(DAT_43792c50 + 0x43792a42) = *(int *)(DAT_43792c50 + 0x43792a42) + 1;
    FUN_4355fd4c();
    if (extraout_r1 == 0) {
      uVar14 = FUN_43728564();
      uVar15 = FUN_437284b4();
      uVar16 = FUN_43ae0c38();
      FUN_4378eb78(5,2,1,DAT_43792c54 + 0x43792a68,uVar14,uVar15,uVar16);
      uVar14 = FUN_43728564();
      uVar15 = FUN_437284b4();
      uVar16 = FUN_43ae0c38();
      FUN_43902718(DAT_43792c58 + 0x43792a8c,uVar14,uVar15,uVar16);
    }
  }
  cVar33 = *(char *)(iVar44 + 0x1b);
  if (cVar33 != '\0') {
    puVar35 = (undefined1 *)(DAT_43792c5c + 0x43792a97);
    puVar37 = DAT_43792c38;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != DAT_43792c3c);
    puVar35 = (undefined1 *)(DAT_43792c60 + 0x43792aad);
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != DAT_43792c40);
    if (cVar33 == '\x01') {
      FUN_4378ec60();
      *(undefined1 *)(iVar44 + 0x1b) = 0;
    }
  }
  if (*(byte *)(iVar44 + 0x11) != 0) {
    uVar53 = (uint)*(byte *)(iVar44 + 0x11) * 100;
    iVar46 = *(int *)(*(int *)(DAT_43792c64 + 0x43792adc) + 8);
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c68)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c6c + 0x43792af8,uVar48);
      FUN_43902718(DAT_43792c70 + 0x43792b04,uVar48);
      FUN_43561540(DAT_43792c74 + 0x43792b0c);
    }
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c78)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c7c + 0x43792b28,uVar48);
      FUN_43902718(DAT_43792c80 + 0x43792b34,uVar48);
      FUN_43561540(DAT_43792c84 + 0x43792b3c);
    }
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c88)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c8c + 0x43792b58,uVar48);
      FUN_43902718(DAT_43792c90 + 0x43792b64,uVar48);
      FUN_43561540(DAT_43792c94 + 0x43792b6c);
    }
  }
  iVar46 = DAT_43792c98;
  if (param_1 != **(int **)(DAT_43792c98 + 0x43792b7a)) {
    iVar43 = thunk_FUN_436cd00c();
    puVar37 = *(undefined4 **)(iVar46 + 0x43792b7a);
    uVar48 = (uint)(iVar43 - puVar37[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43792c9c + 0x43792b96,param_1,*puVar37,uVar48);
    FUN_43902718(DAT_43792ca0 + 0x43792bac,param_1,**(undefined4 **)(iVar46 + 0x43792b7a),uVar48);
    FUN_4378f988(3,0,uVar48);
    if ((*(byte *)(iVar44 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43792ca4 + 0x43792bc8);
    }
    if ((*(byte *)(iVar44 + 0x1b) & 2) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  FUN_43ae1292(4);
  iVar46 = FUN_43ae8d4e();
  if (iVar46 == 0) {
    FUN_43901778();
    if (*(char *)(DAT_43792ca8 + 0x43792bf2) != '\0') {
      *(undefined1 *)(DAT_43792cac + 0x43792bfc) = 1;
    }
    uVar32 = 0;
    puVar35 = (undefined1 *)(DAT_43792cb0 + 0x43792c04);
  }
  else {
    uVar32 = 1;
    puVar35 = (undefined1 *)(DAT_43792cb4 + 0x43792c0c);
  }
  *puVar35 = uVar32;
  if (*(byte *)(iVar44 + 0x20) == 0) {
    psVar38 = (short *)(DAT_437935f4 + 0x43792ccc);
    sVar25 = 0;
  }
  else {
    uVar48 = *(int *)(*(int *)(DAT_43792cb8 + 0x43792c1e) + 0x14) - 1;
    if (uVar48 < 2) {
      sVar25 = *(short *)(DAT_43792cbc + 0x43792c28 + uVar48 * 2);
    }
    else {
      sVar25 = 0x3c;
    }
    sVar25 = sVar25 * (ushort)*(byte *)(iVar44 + 0x20);
    psVar38 = (short *)(&UNK_43792c36 + DAT_43792cc0);
  }
  *psVar38 = sVar25;
  *(int *)(DAT_437935f8 + 0x43792cd8) = *(int *)(DAT_437935f8 + 0x43792cd8) + 1;
  *(undefined1 *)(DAT_437935fc + 0x43792ce6) = 0;
  FUN_4378f7a0(0x708);
  iVar46 = FUN_437999e4(1,1);
  if (((iVar46 != 0) || (iVar46 = FUN_437999e4(1,2), iVar46 != 0)) &&
     ((iVar46 = DAT_43793608, *(ushort *)(DAT_43793600 + 0x43793376) < 2 ||
      (*(int *)(*(int *)(DAT_43793604 + 0x43792d18) + 0xc) != 0)))) {
    iVar49 = DAT_4379360c + 0x43792d26;
    FUN_43aef52c(iVar49,DAT_43793608 + 0x43793fb4);
    FUN_437d9a04((int)&DAT_437946b4 + iVar46,iVar49);
    if (((*(byte *)(iVar44 + 0x16) & 5) == 4) && (*(int *)(iVar46 + 0x43793598) != 0)) {
      FUN_43ad53b8(iVar46 + 0x4379359c,*(int *)(iVar46 + 0x43793598),0);
    }
  }
  iVar46 = DAT_43793610;
  FUN_43a0cb54();
  FUN_43b2a04a();
  puVar47 = (ushort *)(iVar46 + 0x43792d68);
  FUN_437fdf5c();
  uVar12 = *(undefined2 *)(iVar46 + 0x43792d7a);
  uVar1 = *puVar47;
  uVar2 = *(undefined2 *)(iVar46 + 0x43792d6c);
  uVar3 = *(undefined2 *)(iVar46 + 0x43792d78);
  uVar4 = *(undefined2 *)(iVar46 + 0x43792d74);
  uVar8 = *(undefined2 *)(iVar46 + 0x43792d76);
  uVar5 = *(undefined2 *)(iVar46 + 0x43792d7c);
  uVar6 = *(undefined2 *)(iVar46 + 0x43792d6a);
  uVar9 = *(undefined2 *)(iVar46 + 0x43792d70);
  uVar7 = *(undefined2 *)(iVar46 + 0x43792d7e);
  uVar10 = *(undefined2 *)(iVar46 + 0x43792d6e);
  uVar11 = *(undefined2 *)(iVar46 + 0x43792d72);
  FUN_43804c5c(puVar47);
  *(undefined2 *)(iVar46 + 0x43792d6a) = uVar6;
  *(undefined2 *)(iVar46 + 0x43792d6c) = uVar2;
  *(undefined2 *)(iVar46 + 0x43792d74) = uVar4;
  *(undefined2 *)(iVar46 + 0x43792d7e) = uVar7;
  iVar49 = DAT_43793614;
  *(undefined2 *)(iVar46 + 0x43792d76) = uVar8;
  *(undefined2 *)(iVar46 + 0x43792d7a) = uVar12;
  piVar50 = (int *)(iVar49 + 0x43792dca);
  *(undefined2 *)(iVar46 + 0x43792d78) = uVar3;
  *(undefined2 *)(iVar46 + 0x43792d7c) = uVar5;
  *puVar47 = uVar1;
  *(undefined2 *)(iVar46 + 0x43792d70) = uVar9;
  *(undefined2 *)(iVar46 + 0x43792d6e) = uVar10;
  *(undefined2 *)(iVar46 + 0x43792d72) = uVar11;
  FUN_43ae8fa2();
  FUN_43ae8f98();
  FUN_437fc404(piVar50);
  FUN_437fc54c(1);
  FUN_4375dd04();
  iVar46 = FUN_437fc54c(0);
  FUN_4380c7f8(iVar46,auStack_38);
  bVar56 = false;
  if ((bStack_34 & 0x20) != 0) {
    iVar49 = *(int *)(iVar49 + 0x43792dd6);
    if (*(uint *)(iVar49 + 0xc) < 2) {
      bVar56 = false;
      if (*(char *)(iVar49 + 0x11) != '\0') {
        bVar56 = *(int *)(*piVar50 + 0x2c4) != 0;
      }
    }
    else {
      bVar56 = false;
    }
  }
  iVar49 = FUN_43b00cb4(uVar13);
  if ((((iVar49 == 1) && (iVar46 == 0x110)) &&
      (sVar25 = *(short *)(*(int *)(DAT_43793618 + 0x43792e4a) + 0x240), sVar25 != 0x110)) &&
     (sVar25 != 0x101)) {
    bVar57 = sVar25 != 0x100;
  }
  else {
    bVar57 = false;
  }
  if ((((*(int *)(*(int *)(DAT_4379361c + 0x43792e6c) + 0xc) == 1) ||
       (*(uint *)(DAT_43793620 + 0x43793446) < 2)) || (bVar56)) && (!bVar57)) {
    uVar12 = FUN_437fc54c();
    iVar46 = DAT_43793624;
    *(undefined2 *)(DAT_43793624 + 0x43792e90) = uVar12;
    uVar12 = FUN_437fc54c(2);
    *(undefined2 *)(iVar46 + 0x43792e92) = uVar12;
    uVar12 = FUN_437fc54c(1);
    *(undefined2 *)(iVar46 + 0x43792e94) = uVar12;
    uVar12 = FUN_437fc54c(3);
    *(undefined2 *)(iVar46 + 0x43792e96) = uVar12;
    uVar12 = FUN_437fc54c(5);
    *(undefined2 *)(iVar46 + 0x43792e9a) = uVar12;
    uVar12 = FUN_437fc54c(4);
    *(undefined2 *)(iVar46 + 0x43792e98) = uVar12;
    uVar12 = FUN_437fc54c(6);
    *(undefined2 *)(iVar46 + 0x43792e9c) = uVar12;
    uVar12 = FUN_437fc54c(8);
    *(undefined2 *)(iVar46 + 0x43792e9e) = uVar12;
    uVar12 = FUN_437fc54c(10);
    *(undefined2 *)(iVar46 + 0x43792ea2) = uVar12;
    uVar12 = FUN_437fc54c(9);
    *(undefined2 *)(iVar46 + 0x43792ea0) = uVar12;
    uVar12 = FUN_437fc54c(0xc);
    iVar49 = *(int *)(*(int *)(DAT_43793628 + 0x43792eea) + 0x14);
    iVar39 = *(int *)(*(int *)(DAT_43793628 + 0x43792eea) + 0x34);
    *(undefined2 *)(iVar46 + 0x43792ea6) = uVar12;
    if (iVar49 == iVar39) {
      uVar12 = FUN_437fc54c(0xb);
      *(undefined2 *)(iVar46 + 0x43792ea4) = uVar12;
    }
    FUN_4380c7f8(*(undefined2 *)(DAT_4379362c + 0x43792f00),(int)&DAT_43793708 + DAT_4379362c);
  }
  iVar49 = DAT_43793638;
  iVar46 = DAT_43793634;
  iVar39 = *(int *)(DAT_43793630 + 0x43792f1a);
  if (*(int *)(*(int *)(DAT_43793630 + 0x43792f12) + 0xb4) == 1) {
    puVar35 = (undefined1 *)(DAT_43793634 + 0x43792f2a);
    *(undefined1 *)(DAT_43793638 + 0x43792f2c) = *puVar35;
    *(undefined1 *)(iVar49 + 0x43792f2d) = *(undefined1 *)(iVar46 + 0x43792f2b);
    FUN_43796044(puVar35);
    iVar40 = 0;
    if (*(char *)(iVar46 + 0x43792f2b) != '\0') {
      if (*(char *)(iVar49 + 0x43792f2d) != '\0') goto LAB_43792f54;
      iVar46 = FUN_4378f9b4();
      iVar40 = **(int **)(iVar46 + 4) + 5;
    }
    *(int *)(iVar39 + 0x204) = iVar40;
  }
LAB_43792f54:
  iVar49 = FUN_43b00cba(uVar13);
  iVar46 = DAT_4379363c;
  if (iVar49 != 0) {
    FUN_43b00dd4(uVar13);
    FUN_43805b04(uVar13,iVar46 + 0x43792f6e,DAT_43793640 + 0x43792f72,DAT_43793640 + 0x43793516);
    FUN_43b00e40(uVar13,iVar46 + 0x43792f6e);
  }
  iVar46 = DAT_43793648;
  piVar50 = (int *)(DAT_43793648 + 0x43792f96);
  iVar49 = (int)&DAT_43794dfc + DAT_43793644;
  FUN_437da078(piVar50,iVar49);
  FUN_43ae7564(piVar50,iVar49);
  iVar49 = *piVar50;
  if (*(int *)(iVar49 + 0xb4) == 2) {
    iVar46 = *(int *)(iVar46 + 0x43792f9e);
    *(undefined4 *)(iVar46 + 0x204) = *(undefined4 *)(iVar46 + 0x238);
    *(undefined1 *)(iVar46 + 0x202) = *(undefined1 *)(iVar46 + 0x234);
  }
  bVar34 = *(byte *)(DAT_4379364c + 0x437937d9) & 0x40;
  if (((*(byte *)(DAT_4379364c + 0x437937d9) & 0x40) != 0) &&
     (bVar34 = 1, *(int *)(iVar49 + 0x30) != 1)) {
    bVar34 = 0;
  }
  *(byte *)(DAT_4379364c + 0x4379378c) = bVar34;
  if ((*(char *)(DAT_43793654 + 0x43792fee) != *(char *)(DAT_43793650 + 0x437937ac)) ||
     (*(int *)(DAT_43793658 + 0x43793000) != *(int *)(iVar49 + 0x34))) {
    FUN_43901a8c(4,0x203e,*(char *)(DAT_43793650 + 0x437937ac),*(undefined4 *)(iVar49 + 0x34));
    *(undefined1 *)(DAT_43793660 + 0x4379301e) = *(undefined1 *)(DAT_4379365c + 0x437937dc);
    *(undefined4 *)(DAT_43793668 + 0x43793032) =
         *(undefined4 *)(*(int *)(DAT_43793664 + 0x4379302e) + 0x34);
  }
  iVar49 = DAT_4379368c;
  iVar46 = DAT_43793688;
  if ((*(byte *)(*(int *)(DAT_4379366c + 0x43793044) + 0x266) & 0x20) == 0) {
    *(undefined4 *)(DAT_43793690 + 0x437938aa) = 0;
  }
  else {
    psVar38 = (short *)(DAT_43793670 + 0x43793052);
    if ((ushort)(*psVar38 - 0x148U) < 2) {
      if (*(int *)(DAT_43793670 + 0x43793116) - 8U < 4) {
                    /* WARNING: Could not recover jumptable at 0x43793066. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)(&switchD_43793066::switchdataD_4379306a +
                  (uint)*(byte *)(*(int *)(DAT_43793670 + 0x43793116) + 0x43793062) * 2))();
        return;
      }
    }
    else {
      if ((*(char *)(DAT_43793670 + 0x43793812) == '\0') ||
         (*(int *)(*(int *)(DAT_4379366c + 0x4379303c) + 0x34) != 0)) {
        uVar14 = 0;
        psVar38 = (short *)(DAT_43793684 + 0x437930c6);
      }
      else if (*(int *)(DAT_43793670 + 0x43793116) == 8) {
        uVar14 = 1;
      }
      else {
        uVar14 = 0;
        if (*(int *)(DAT_43793670 + 0x43793116) == 9) {
          uVar14 = 2;
        }
      }
      *(undefined4 *)(psVar38 + 0x3d6) = uVar14;
      iVar39 = *(int *)(iVar46 + 0x4379387c);
      if (*(int *)(iVar49 + 0x437930d6) != iVar39) {
        FUN_43901a8c(4,0x203f,iVar39,0);
        *(int *)(iVar49 + 0x437930d6) = *(int *)(iVar46 + 0x4379387c);
      }
    }
  }
  iVar49 = DAT_437936a0;
  iVar46 = DAT_4379369c;
  if (((*(uint *)(DAT_43793694 + 0x43793910) & 0xf8000) == 0x38000) &&
     (*(int *)(*(int *)(DAT_43793698 + 0x4379311c) + 0x474) == 2)) {
    uVar32 = 1;
  }
  else {
    uVar32 = 0;
  }
  *(undefined1 *)(DAT_43793694 + 0x437938f1) = uVar32;
  cVar33 = *(char *)(iVar46 + 0x4379391f);
  if (*(char *)(iVar49 + 0x4379313c) != cVar33) {
    FUN_43901a8c(4,0x2043,cVar33,0);
    *(char *)(iVar49 + 0x4379313c) = *(char *)(iVar46 + 0x4379391f);
  }
  iVar46 = DAT_437936a8;
  uVar48 = *(byte *)(DAT_437936a4 + 0x4379396a) & 7;
  if (uVar48 - 1 < 6) {
                    /* WARNING: Could not recover jumptable at 0x43793170. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_43793170::switchdataD_43793174 + (uint)*(byte *)(uVar48 + 0x43793173) * 2))
              ();
    return;
  }
  *(undefined4 *)(DAT_437936a8 + 0x43793908) = 0;
  *(undefined4 *)(iVar46 + 0x437938fc) = *(undefined4 *)(*(int *)(DAT_437936ac + 0x43793192) + 0x30)
  ;
  *(undefined4 *)(iVar46 + 0x4379390c) = 1;
  iVar49 = DAT_437936e4;
  iVar46 = DAT_437936e0;
  piVar50 = (int *)(DAT_437936e4 + 0x437932b4);
  iVar39 = FUN_43ae8c50(*(undefined4 *)(DAT_437936e0 + 0x43793a2a));
  iVar49 = *(int *)(*(int *)(iVar49 + 0x437932b8) + 0x14);
  *(int *)(iVar46 + 0x43793a2e) = iVar39;
  *(bool *)(iVar46 + 0x43793a32) = iVar39 != iVar49;
  iVar49 = FUN_436e9234();
  iVar40 = *piVar50;
  iVar39 = *(int *)(iVar40 + 0x178);
  uVar14 = *(undefined4 *)(DAT_437936e8 + 0x437932e2 + (iVar49 * 3 + *(int *)(iVar40 + 0x174)) * 4);
  *(int *)(iVar46 + 0x43793a62) = iVar39;
  *(undefined4 *)(iVar46 + 0x43793a66) = uVar14;
  bVar34 = *(byte *)(iVar40 + 0x17c);
  iVar49 = *(int *)(DAT_437936ec + 0x43793300);
  *(uint *)(iVar46 + 0x43793a6a) = (uint)bVar34;
  iVar46 = DAT_437936f4;
  if ((iVar49 != iVar39) || (*(uint *)(DAT_437936f0 + 0x4379330e) != (uint)bVar34)) {
    FUN_439d88c4();
    FUN_43901a8c(4,0x2030,*(undefined4 *)(iVar46 + 0x43793ad2),0xff);
    uVar15 = *(undefined4 *)(*(int *)(DAT_437936f8 + 0x43793330) + 0x174);
    uVar14 = FUN_436e9234();
    FUN_43901a8c(4,0x2031,uVar15,uVar14);
    FUN_43901a8c(4,0x203c,*(undefined4 *)(iVar46 + 0x43793386),*(undefined4 *)(iVar46 + 0x43793ada))
    ;
    *(undefined4 *)(DAT_437936fc + 0x43793360) = *(undefined4 *)(iVar46 + 0x43793ad2);
    *(undefined4 *)(DAT_43793700 + 0x4379336a) = *(undefined4 *)(iVar46 + 0x43793ada);
  }
  if ((*(char *)(DAT_43793704 + 0x43793370) == '\0') &&
     ((((sVar25 = *(short *)(DAT_43793708 + 0x4379337a), sVar25 == 0x11a || (sVar25 == 0x118)) ||
       (sVar25 == 0x102)) || (((sVar25 == 0x11b || (sVar25 == 0x119)) || (sVar25 == 0x107)))))) {
    if (*(int *)(*(int *)(DAT_4379370c + 0x437933a6) + 0x174) == 1) {
      FUN_439c5a04(auStack_54,0,9);
      uStack_52 = 0x40d4;
      uStack_4c = (undefined1)*(undefined4 *)(DAT_43793710 + 0x43793b7e);
      auStack_54[0] = 5;
      FUN_435aa02c(auStack_2c);
      FUN_435a92e0(auStack_218);
      iVar46 = FUN_43a49628(auStack_218,DAT_437935f0);
      if (iVar46 == 0) {
        iVar46 = FUN_435a9304(auStack_218,auStack_54,9);
        if (iVar46 != 0) {
          FUN_4378eb78(3,9,1,DAT_4379371c + 0x43793428,iVar46);
          iVar49 = DAT_43793720 + 0x43793430;
          goto LAB_43793456;
        }
        iVar46 = FUN_435aa20c(auStack_2c,DAT_437935f0,auStack_218);
        if (iVar46 != 0) {
          FUN_4378eb78(3,9,1,DAT_43793724 + 0x43793450,iVar46);
          iVar49 = DAT_43793728 + 0x43793458;
          goto LAB_43793456;
        }
      }
      else {
        FUN_4378eb78(3,9,1,DAT_43793714 + 0x43793400,iVar46);
        iVar49 = DAT_43793718 + 0x43793408;
LAB_43793456:
        FUN_43902718(iVar49,iVar46);
      }
      FUN_435a92c8(auStack_218);
      FUN_435aa014(auStack_2c);
    }
    *(undefined1 *)(DAT_4379372c + 0x43793474) = 1;
  }
  iVar49 = DAT_43793734;
  iVar46 = DAT_43793730;
  piVar50 = (int *)(DAT_43793734 + 0x43793480);
  FUN_437c1740(piVar50,DAT_43793730 + 0x43794bae);
  uVar48 = (*(byte *)(iVar46 + 0x43793c86) & 0x3f) >> 4;
  if (uVar48 == 1) {
    *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar46 + 0x4379349a);
    *(undefined4 *)(iVar46 + 0x43793bea) = *(undefined4 *)(iVar46 + 0x437938e6);
    *(undefined4 *)(iVar46 + 0x43793a42) = *(undefined4 *)(iVar46 + 0x437934a6);
    *(undefined1 *)(iVar46 + 0x43793a46) = 0;
    *(undefined4 *)(iVar46 + 0x43793a4a) = 0;
    *(undefined4 *)(iVar46 + 0x437934c6) = 0;
    iVar49 = FUN_43794a44(piVar50);
    if (iVar49 != 0) {
      if (*(uint *)(iVar46 + 0x437938d6) < 4) {
                    /* WARNING: Could not recover jumptable at 0x437935c4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)(&switchD_437935c4::switchdataD_437935c8 +
                  (uint)(&switchD_437935c4::switchdataD_437935c8)[*(uint *)(iVar46 + 0x437938d6)] *
                  2))();
        return;
      }
      iVar46 = DAT_437942c0 + 0x43793788;
      FUN_4378eb78(5,0,1,DAT_437942bc + 0x43793786,iVar46,0x93c);
      FUN_43902718(DAT_437942c4 + 0x437937a0,iVar46,0x93c);
    }
    goto LAB_437937a2;
  }
  if (uVar48 == 2) {
    iVar39 = *piVar50;
    if (*(int *)(*(int *)(iVar49 + 0x43793484) + 0x10) == *(int *)(iVar39 + 0x20)) {
      uVar14 = *(undefined4 *)(iVar39 + 0x24);
      *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar39 + 0x1c);
      iVar49 = *(int *)(iVar39 + 0x28);
      *(undefined4 *)(iVar46 + 0x43793a4a) = uVar14;
      *(int *)(iVar46 + 0x43793a42) = iVar49;
      if ((*(ushort *)(iVar46 + 0x43793c86) & 0x1c0) == 0) {
        *(byte *)(iVar46 + 0x43793a46) =
             (byte)(((uint)*(ushort *)(iVar46 + 0x43793c86) << 0x17) >> 0x1d);
        if (((iVar49 == 1) &&
            ((*(int *)(iVar39 + 0x538) != 1 || (*(int *)(iVar46 + 0x43793bf6) != 0)))) &&
           (*(char *)(DAT_43793738 + 0x43793ccf) == '\0')) {
          *(undefined1 *)(DAT_43793738 + 0x43793aae) = 1;
        }
      }
      else {
        *(undefined1 *)(iVar46 + 0x43793a46) = 0;
      }
    }
    iVar46 = DAT_4379373c + 0x437934fe;
    uVar14 = *(undefined4 *)(DAT_4379373c + 0x4379396e);
    goto LAB_43793588;
  }
  *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar46 + 0x4379349a);
  *(undefined4 *)(iVar46 + 0x43793a42) = *(undefined4 *)(iVar46 + 0x437934a6);
  *(undefined1 *)(iVar46 + 0x43793a46) = 0;
  iVar49 = FUN_43794a44(piVar50);
  if (iVar49 == 0) {
    uVar14 = *(undefined4 *)(iVar46 + 0x437934c6);
  }
  else {
    uVar14 = *(undefined4 *)(iVar46 + 0x437938d6);
  }
  switch(uVar14) {
  case 0:
    uVar14 = 0;
    iVar46 = DAT_43793740 + 0x43793538;
    break;
  case 1:
    iVar46 = DAT_43793748 + 0x43793546;
    goto LAB_4379357a;
  case 2:
    uVar14 = 2;
    iVar46 = DAT_43793744 + 0x43793540;
    break;
  case 3:
    uVar14 = 4;
    iVar46 = DAT_4379374c + 0x4379354e;
    break;
  default:
    iVar46 = DAT_43793754 + 0x4379355e;
    FUN_4378eb78(5,0,1,DAT_43793750 + 0x4379355a,iVar46,0x91e);
    FUN_43902718(DAT_43793758 + 0x43793574,iVar46,0x91e);
    iVar46 = DAT_4379375c + 0x4379357c;
LAB_4379357a:
    uVar14 = 1;
  }
  *(undefined4 *)(iVar46 + 0x5cc) = uVar14;
  iVar46 = DAT_43793760 + 0x43793586;
  uVar14 = *(undefined4 *)(DAT_43793760 + 0x437939ee);
LAB_43793588:
  *(undefined4 *)(iVar46 + 0x76c) = uVar14;
LAB_437937a2:
  puVar51 = (uint *)(DAT_437942cc + 0x437937b6);
  FUN_4380f440(DAT_437942d0 + 0x437937bc,puVar51,DAT_437942c8 + 0x43793d54,0);
  if (*(byte *)(iVar44 + 0xb3) != 0) {
    *puVar51 = (uint)*(byte *)(iVar44 + 0xb3);
  }
  iVar46 = DAT_437942dc;
  iVar39 = DAT_437942dc + 0x437937de;
  FUN_4380e0cc(DAT_437942d4 + 0x437937da,DAT_437942d8 + 0x437937dc);
  FUN_4380e138(iVar39);
  iVar49 = DAT_437942e4;
  if ((uint)*(byte *)(DAT_437942e0 + 0x437937f0) != (int)(char)*(byte *)(iVar46 + 0x437937e3)) {
    *(byte *)(DAT_437942e0 + 0x437937f0) = *(byte *)(iVar46 + 0x437937e3);
    FUN_43ae913c(auStack_68,iVar49 + 0x43793804);
    FUN_439018b0(DAT_437942e8 + 0x43793814,auStack_68,iVar39,0);
  }
  iVar46 = DAT_437942ec;
  if ((1 < *(uint *)(DAT_437942ec + 0x43793df0)) &&
     (uVar48 = *(uint *)(*(int *)(DAT_437942f0 + 0x43793836) + 0xc),
     (*(uint *)(DAT_437942ec + 0x43793fac) & 1) != uVar48)) {
    if (uVar48 == 0) {
      uVar14 = 2;
    }
    else {
      uVar14 = 1;
    }
    *(undefined4 *)(DAT_437942ec + 0x43793fac) = uVar14;
    *(undefined4 *)(iVar46 + 0x43793fbc) = uVar14;
    FUN_4378ea78(0);
  }
  iVar49 = DAT_437942f8;
  iVar46 = DAT_437942f4;
  if (*(int *)(DAT_437942f4 + 0x43793fd2) == *(int *)(DAT_437942f4 + 0x43793dea)) {
    uVar48 = *(uint *)(*(int *)(DAT_437942f8 + 0x43793872) + 0x3c);
    if (uVar48 == 0) {
      iVar39 = FUN_43b00cba(uVar13);
      if ((((iVar39 == 0) || (*(int *)(iVar46 + 0x43793912) != 1)) ||
          ((*(byte *)(iVar46 + 0x4379401e) & 1) == 0)) ||
         (*(int *)(*(int *)(iVar49 + 0x43793872) + 0xc) != 0)) {
        iVar49 = FUN_43b039fc(DAT_43794624 + 0x437945c4,DAT_43794628 + 0x437945c6);
        iVar46 = DAT_43794308;
        if (iVar49 == 0) {
          if (bVar56) {
            FUN_4378ea78();
            iVar46 = DAT_43794304;
            *(undefined4 *)(DAT_43794304 + 0x437940aa) = 0;
            *(undefined4 *)(iVar46 + 0x437940ba) = 0;
          }
          else if ((*(short *)(DAT_43794308 + 0x43793932) == 0x121) ||
                  (*(short *)(DAT_43794308 + 0x43793932) == 300)) {
            FUN_4378ea78(0);
            iVar46 = DAT_4379430c;
            *(undefined4 *)(DAT_4379430c + 0x437940d8) = 0;
            *(undefined4 *)(iVar46 + 0x437940e8) = 0;
          }
          else if (*(uint *)(DAT_43794308 + 0x43793f02) < 2) {
            if (*(int *)(*(int *)(DAT_43794310 + 0x43793968) + 0xc) == 0) {
              uVar14 = 0;
LAB_43793978:
              FUN_4378ea78();
              *(undefined4 *)(iVar46 + 0x437940be) = uVar14;
              *(undefined4 *)(iVar46 + 0x437940ce) = uVar14;
            }
          }
          else {
            uVar14 = 1;
            if (*(int *)(*(int *)(DAT_43794314 + 0x43793976) + 0xc) == 1) goto LAB_43793978;
          }
        }
        else {
          FUN_4380c7f8(uVar1,auStack_40);
          iVar46 = DAT_43794318;
          if (((bVar56) && (uVar48 = bStack_3c & 0x20, (bStack_3c & 0x20) == 0)) &&
             (*(int *)(DAT_43794318 + 0x43794132) != 0)) {
            FUN_4378ea78(uVar48);
            *(uint *)(iVar46 + 0x43794132) = uVar48;
            *(uint *)(iVar46 + 0x43794142) = uVar48;
          }
        }
      }
      else {
        FUN_4378ea78(0);
        *(undefined4 *)(iVar46 + 0x43793fe6) = 0;
        *(undefined4 *)(iVar46 + 0x43793ff6) = 0;
        *(byte *)(iVar46 + 0x4379401e) = *(byte *)(iVar46 + 0x4379401e) & 0xfe;
      }
    }
    else {
      uVar53 = *(int *)(*(int *)(DAT_437942f8 + 0x43793876) + 0x1e8) + 1;
      if (uVar48 <= uVar53) {
        if (uVar48 == uVar53) {
          iVar49 = FUN_43b039fc(DAT_437942fc + 0x43793892,DAT_43794300 + 0x43793894);
          if (iVar49 == 0) {
            *(undefined4 *)(iVar46 + 0x43793ff6) = *(undefined4 *)(iVar46 + 0x43793fe6);
            FUN_4378ea78();
          }
        }
        else {
          FUN_4378ea78(0);
          iVar49 = *(int *)(*(int *)(iVar49 + 0x43793872) + 0x3c) + -1;
          *(int *)(iVar46 + 0x43793fe6) = iVar49;
          *(int *)(iVar46 + 0x43793ff6) = iVar49;
        }
      }
    }
  }
  iVar46 = DAT_43794324;
  uVar48 = *(uint *)(DAT_4379431c + 0x43793ece);
  if (*(byte *)(iVar44 + 1) - 1 < 4) {
                    /* WARNING: Could not recover jumptable at 0x437939ca. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_437939ca::switchdataD_437939ce +
              (uint)*(byte *)(*(byte *)(iVar44 + 1) + 0x437939cd) * 2))();
    return;
  }
  if (((uint)*(byte *)(DAT_43794320 + 0x43794150) != (uVar48 & 3) >> 1) ||
     ((uint)*(byte *)(DAT_43794320 + 0x43794151) != (uVar48 & 1))) {
    *(byte *)(DAT_43794324 + 0x4379416a) = (byte)((uVar48 << 0x1e) >> 0x1f);
    *(char *)(iVar46 + 0x4379416b) = (char)(uVar48 & 1);
    FUN_4378ea78(0);
  }
  iVar44 = FUN_43ae8d4e();
  if ((iVar44 == 0) || (*(char *)(DAT_43794328 + 0x43793a22) != '\0')) {
    FUN_4378ea78(1);
    *(undefined1 *)(DAT_4379432c + 0x43793a34) = 0;
  }
  uVar14 = *(undefined4 *)(iVar43 + DAT_43794330);
  iVar44 = FUN_43ae8cc8(uVar14);
  if (iVar44 != 0) {
    *(undefined4 *)(DAT_43794334 + 0x437941e6) = *(undefined4 *)(DAT_43794334 + 0x437941d6);
  }
  iVar44 = DAT_43794338;
  uVar48 = *(uint *)(DAT_43794338 + 0x437941e6);
  cVar33 = '\x01' - (char)uVar48;
  if (1 < uVar48) {
    cVar33 = '\0';
  }
  *(bool *)(DAT_43794338 + 0x437941ea) = 1 >= uVar48;
  *(char *)(iVar44 + 0x437941eb) = cVar33;
  cVar33 = '\x01' - (char)*(uint *)(iVar44 + 0x437941f6);
  if (1 < *(uint *)(iVar44 + 0x437941f6)) {
    cVar33 = '\0';
  }
  *(char *)(iVar44 + 0x437941fa) = cVar33;
  uVar32 = FUN_43ae8ccc(uVar14);
  *(undefined1 *)(iVar44 + 0x4379553b) = uVar32;
  if ((*(byte *)(iVar44 + 0x43794264) & 0x10) == 0) {
    uStack_30 = *(undefined4 *)(*(int *)(DAT_43794340 + 0x43793abc) + 4);
  }
  else {
    uStack_30 = *(undefined4 *)(*(int *)(DAT_4379433c + 0x43793ab0) + 0xc);
  }
  iVar44 = FUN_43b00cba(uVar13);
  if ((iVar44 != 0) && (*(int *)(*(int *)(DAT_43794344 + 0x43793ac6) + 0xb8) == 1)) {
    FUN_43b00e4c(uVar13,(int *)(DAT_43794344 + 0x43793ac6),&uStack_30);
  }
  iVar46 = DAT_4379434c;
  iVar44 = DAT_43794348;
  uVar13 = FUN_4380e15c(DAT_43794348 + 0x43793ae4,uStack_30,DAT_43794350 + 0x43793b00,
                        *(int *)(DAT_4379434c + 0x43794276) +
                        *(int *)(*(int *)(DAT_43794348 + 0x43793ae8) + 0xc) & 1);
  *(undefined4 *)(iVar46 + 0x437940ca) = uVar13;
  iVar49 = FUN_437955ec();
  iVar39 = *(int *)(iVar43 + DAT_43794354);
  if (iVar49 == 1) {
    *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
    if (*(char *)(iVar46 + 0x4379428a) != '\0') {
      *(char *)(iVar46 + 0x43794282) = *(char *)(iVar46 + 0x43794282) + '\x01';
    }
  }
  else if (iVar49 == 2) {
    if (((*(byte *)(iVar39 + 0x22) & 1) == 0) &&
       (uVar48 = *(uint *)(*(int *)(iVar44 + 0x43793af0) + 8), *(ushort *)(iVar46 + 0x4379415a) < 2)
       ) {
      if (*(char *)(iVar46 + 0x4379427b) == '\0') {
        iVar44 = *(int *)(iVar46 + 0x437940ba);
      }
      else {
        iVar44 = *(int *)(iVar46 + 0x437940ca);
      }
      if (iVar44 != 0) {
        if (iVar44 == 1) {
          uVar53 = 1;
        }
        else {
          uVar53 = 2;
        }
        if (uVar48 < uVar53) {
          uVar48 = uVar53;
        }
      }
      if ((1 < uVar48) &&
         (uVar48 = FUN_43acf19e(uVar48,2),
         (*(int *)((int)&DAT_43794338 + DAT_4379435c) +
          *(int *)(*(int *)(DAT_43794358 + 0x43793b9e) + 0xc) & 1U) != 0)) {
        uVar48 = 1;
      }
      *(uint *)((int)&DAT_43794348 + DAT_43794360 + 2) = uVar48;
    }
    else {
      *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
    }
    if (*(char *)((int)&DAT_43794360 + DAT_43794364) != '\0') {
      *(char *)((int)&DAT_43794358 + DAT_43794364) =
           *(char *)((int)&DAT_43794358 + DAT_43794364) + '\x01';
    }
  }
  else if (iVar49 == 0) {
    *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
  }
  iVar44 = DAT_43794368;
  if (*(int *)(DAT_43794368 + 0x437941be) != 0x11) {
    uVar13 = *(undefined4 *)((int)&DAT_43794338 + DAT_43794368 + 2);
    if (*(int *)((int)&DAT_437943d4 + DAT_43794368 + 2) != 0) {
      uVar13 = 10;
    }
    uVar13 = FUN_43acc1a6(*(int *)(DAT_43794368 + 0x437941be),uVar13);
    *(undefined4 *)((int)&DAT_4379433c + iVar44 + 2) = uVar13;
  }
  iVar46 = DAT_4379436c + 0x43793bfc;
  iVar44 = *(int *)(DAT_4379436c + 0x437941e4);
  if ((iVar44 == 0x12) || (iVar44 == 0x3f)) {
    uVar13 = 1;
    iVar46 = DAT_43794370 + 0x43793c18;
  }
  else if (iVar44 == 8) {
    uVar13 = 2;
  }
  else {
    uVar13 = *(undefined4 *)(*(int *)(iVar43 + DAT_43794374) + 0x40);
  }
  *(undefined4 *)(iVar46 + 0x5a4) = uVar13;
  if (*(char *)(*(int *)(iVar43 + DAT_43794378) + 0x43) == '\x01') {
    iVar44 = DAT_4379437c + 0x43793c3a;
    bVar34 = 1;
  }
  else {
    bVar34 = 0;
    if (*(char *)(DAT_43794380 + 0x43793d1e) != '\0') {
      bVar34 = (byte)FUN_43795a08[DAT_43794380 + 2] ^ 1;
    }
    iVar44 = DAT_43794384 + 0x43793c58;
  }
  *(byte *)(iVar44 + 0x770) = bVar34;
  if (*(char *)(DAT_43794388 + 0x43795a2a) == '\0') {
    uVar13 = *(undefined4 *)(*(int *)(DAT_4379438c + 0x43793c74) + 0xbc);
  }
  else {
    uVar13 = 1;
  }
  *(undefined4 *)((int)&DAT_437943d4 + DAT_43794388 + 2) = uVar13;
  cVar33 = *(char *)(DAT_43794390 + 0x43794258);
  if (*(char *)((int)&DAT_43794414 + DAT_43794390 + 1) != '\0') {
    cVar33 = cVar33 + '\x01';
  }
  *(char *)(DAT_43794390 + 0x43794269) = cVar33;
  uVar13 = FUN_43ae8d10(uVar14);
  iVar44 = DAT_43794394;
  piVar52 = (int *)(DAT_43794398 + 0x43793ca6);
  *(undefined4 *)(DAT_43794394 + 0x43794510) = uVar13;
  uVar13 = FUN_43ae8d14(uVar14);
  iVar46 = *piVar52;
  *(undefined4 *)(iVar44 + 0x43794514) = uVar13;
  piVar50 = (int *)(DAT_4379439c + 0x43793cbc);
  if (*piVar50 != iVar46) {
    FUN_43901a8c(4,0x203d);
    *piVar52 = *piVar50;
  }
  iVar40 = DAT_437943ac;
  iVar49 = DAT_437943a8;
  iVar46 = DAT_437943a4;
  iVar44 = DAT_437943a0;
  if ((*(byte *)(iVar39 + 3) & 1) != 0) {
    puVar45 = (undefined2 *)(DAT_437943a4 + 0x43793cec);
    puVar37 = (undefined4 *)(DAT_437943a8 + 0x43793cf4);
    uVar26 = *(undefined4 *)(DAT_437943a4 + 0x43794478);
    puVar54 = (undefined4 *)(DAT_437943ac + 0x43793cfa);
    uVar13 = *(undefined4 *)((int)&DAT_437942cc + DAT_437943a4);
    uVar36 = **(undefined4 **)(DAT_437943a0 + 0x43793cea);
    uVar41 = (*(undefined4 **)(DAT_437943a0 + 0x43793cea))[3];
    uVar55 = *(undefined4 *)((int)&DAT_437942bc + DAT_437943a4);
    uVar15 = FUN_437955ec();
    uVar27 = *(undefined4 *)(iVar46 + 0x43794480);
    uVar16 = *(undefined4 *)((int)&DAT_437942c4 + iVar46);
    uVar17 = *(undefined4 *)(iVar46 + 0x43794488);
    iVar18 = *(int *)(iVar44 + 0x43793cea);
    uVar28 = *(undefined4 *)(iVar18 + 0x10);
    uVar29 = *(undefined4 *)(iVar18 + 0x30);
    uVar19 = *(undefined4 *)(iVar18 + 0x3c);
    uVar12 = *puVar45;
    uVar2 = *(undefined2 *)(iVar46 + 0x437944fc);
    uVar20 = *puVar37;
    uVar30 = *puVar54;
    uVar21 = *(undefined4 *)(iVar49 + 0x43793d00);
    uVar31 = *(undefined4 *)(iVar40 + 0x43793d06);
    uVar22 = FUN_43ae8cd0(uVar14);
    uVar23 = FUN_43ae8cc8(uVar14);
    uVar24 = FUN_43ae8ccc(uVar14);
    FUN_4378eb78(3,9,1,DAT_437943b0 + 0x43793dcc,uVar36,uVar41,uVar55,uVar13,uVar26,uVar15,uVar16,
                 uVar27,uVar17,uVar28,uVar29,uVar19,uVar12,uVar2,uVar20,uVar30,uVar21,uVar31,uVar22,
                 uVar23,uVar24);
    uVar22 = *(undefined4 *)((int)&DAT_437942bc + iVar46);
    uVar26 = *(undefined4 *)((int)&DAT_437942cc + iVar46);
    uVar13 = **(undefined4 **)(iVar44 + 0x43793cea);
    uVar28 = (*(undefined4 **)(iVar44 + 0x43793cea))[3];
    uVar29 = *(undefined4 *)(iVar46 + 0x43794478);
    uVar15 = FUN_437955ec();
    iVar44 = *(int *)(iVar44 + 0x43793cea);
    uVar23 = *(undefined4 *)(iVar46 + 0x43794480);
    uVar27 = *(undefined4 *)(iVar46 + 0x43794488);
    uVar55 = *puVar54;
    uVar24 = *(undefined4 *)(iVar44 + 0x10);
    uVar12 = *puVar45;
    uVar41 = *(undefined4 *)(iVar40 + 0x43793d06);
    uVar2 = *(undefined2 *)(iVar46 + 0x437944fc);
    uVar16 = *(undefined4 *)((int)&DAT_437942c4 + iVar46);
    uVar17 = *(undefined4 *)(iVar44 + 0x30);
    uVar30 = *(undefined4 *)(iVar44 + 0x3c);
    uVar31 = *puVar37;
    uVar36 = *(undefined4 *)(iVar49 + 0x43793d00);
    uVar19 = FUN_43ae8cd0(uVar14);
    uVar20 = FUN_43ae8cc8(uVar14);
    uVar21 = FUN_43ae8ccc(uVar14);
    FUN_43902718(DAT_437943b4 + 0x43793e92,uVar13,uVar28,uVar22,uVar26,uVar29,uVar15,uVar16,uVar23,
                 uVar27,uVar24,uVar17,uVar30,uVar12,uVar2,uVar31,uVar55,uVar36,uVar41,uVar19,uVar20,
                 uVar21);
  }
  iVar46 = DAT_437943c4;
  iVar44 = DAT_437943c0;
  uVar13 = FUN_43b039fc(DAT_437943b8 + 0x43793ea0,DAT_437943bc + 0x43793ea6);
  iVar49 = iVar44 + 0x43795d1c;
  FUN_43780080(iVar46 + 0x43793eb6,iVar49,uVar13);
  FUN_4380db04(iVar46 + 0x43793eb6,iVar49);
  FUN_4378c4d0(iVar44 + 0x43794454);
  FUN_4378f7a0(0xb2a);
  iVar44 = FUN_43ae8cd0(uVar14);
  if (iVar44 == 0) {
    FUN_43ae8cda(uVar14);
  }
  iVar46 = DAT_437943cc;
  iVar44 = DAT_437943c8;
  iVar49 = DAT_437943c8 + 0x43793ef4;
  iVar40 = DAT_437943cc + 0x43793ef8;
  FUN_4377e0e8(iVar49);
  FUN_437217f8(*(undefined4 *)(*(int *)(iVar44 + 0x43793ef8) + 0x18));
  FUN_437b4db8(iVar49,iVar46 + 0x43795188);
  FUN_437c194c(iVar49,iVar46 + 0x43795628);
  thunk_FUN_437d0e5c(iVar49,(int)&DAT_437957cc + iVar46);
  FUN_4378f754(iVar40,iVar46 + 0x437959d4);
  FUN_43af6784((int)&DAT_43795888 + iVar46,iVar49);
  FUN_4378f7a0(0xb51);
  pcVar42 = *(char **)(iVar44 + 0x43793f08);
  if (*pcVar42 == '\0') {
    uVar13 = 0;
    if (*(char *)(iVar39 + 0xec) == '\0') {
      uVar13 = *(undefined4 *)(pcVar42 + 4);
    }
  }
  else {
    uVar13 = 0;
  }
  uVar14 = FUN_43814138();
  iVar44 = DAT_437943d0;
  iVar46 = FUN_43799a38(1,1,**(undefined4 **)(DAT_437943d0 + 0x43793f68),0);
  if (iVar46 == 0) {
    iVar44 = FUN_43799a38(1,2,**(undefined4 **)(iVar44 + 0x43793f68),0);
    bVar56 = iVar44 != 0;
  }
  else {
    bVar56 = true;
  }
  uVar13 = FUN_43b03c62(uVar14,uVar13,bVar56);
  *(undefined4 *)(FUN_43794784 + DAT_437943d4 + 4) = uVar13;
  iVar44 = DAT_437943d8;
  if ((*(char *)(iVar39 + 0xed) == '\0') &&
     ((iVar46 = *(int *)(*(int *)(iVar43 + DAT_43794374) + 0x44), iVar46 == 3 || (iVar46 == 4)))) {
    if ((*(ushort *)(*(int *)(DAT_437943d8 + 0x43793fc8) + 0x264) & 0x1ff) >> 6 != 0) {
      uVar13 = FUN_438148f0();
      iVar46 = DAT_437943e0 + 0x43794058;
      uVar14 = FUN_43799a38(1,10,**(undefined4 **)(iVar44 + 0x43793fc4),0);
      goto LAB_4379405e;
    }
    iVar46 = DAT_437943dc + 0x43793fdc;
    auStack_48[0] = *(undefined1 *)(DAT_437943dc + 0x4379481a);
    uStack_44 = *(undefined4 *)(&UNK_4379459c + DAT_437943dc);
    thunk_FUN_438aaab8(auStack_48,auStack_3a8);
    uVar13 = FUN_438148f0();
    uVar14 = FUN_43799a38(1,10,**(undefined4 **)(iVar44 + 0x43793fc4),0);
    puVar58 = auStack_348;
    puVar35 = auStack_3a8;
    puVar59 = auStack_2e0;
    puVar60 = auStack_280;
  }
  else {
    uVar13 = FUN_438148f0();
    iVar46 = DAT_43794630 + 0x437945e4;
    uVar14 = FUN_43799a38(1,10,**(undefined4 **)(DAT_4379462c + 0x437945e6),0);
LAB_4379405e:
    puVar35 = (undefined1 *)0x0;
    uStack_2e8 = 0;
    puVar58 = (undefined1 *)0x0;
    uStack_2e4 = 0;
    puVar59 = (undefined1 *)0x0;
    uStack_220 = 0;
    puVar60 = (undefined1 *)0x0;
    uStack_21c = 0;
  }
  FUN_4381493c(&uStack_3b8,uVar13,puVar35,uStack_2e8,puVar58,uStack_2e4,puVar59,uStack_220,puVar60,
               uStack_21c,uVar14);
  iVar44 = DAT_437943e8;
  iVar49 = DAT_437943e4 + 0x4379408a;
  *(undefined4 *)(iVar46 + 0x7f0) = uStack_3b8;
  *(undefined4 *)(iVar46 + 0x7f4) = uStack_3b4;
  *(undefined4 *)(iVar46 + 0x7f8) = uStack_3b0;
  *(undefined4 *)(iVar46 + 0x7fc) = uStack_3ac;
  iVar46 = DAT_437943ec;
  FUN_43ae8faa(iVar49,DAT_437943ec + 0x43794096);
  FUN_43ae8eae(iVar49,iVar44 + 0x43794090);
  if ((*(uint *)(iVar46 + 0x4379489a) & 4) == 0) {
    FUN_43560da8(0x11,4);
    FUN_43ae9148(auStack_7c,DAT_437943f0 + 0x437940bc);
    FUN_437b4f2c(iVar44 + 0x43794090,auStack_7c,4);
  }
  if ((*(uint *)(DAT_437943f4 + 0x437948d2) & 2) == 0) {
    FUN_43560da8(0x11,2);
    FUN_43ae9148(auStack_90,DAT_437943f8 + 0x437940e6);
    FUN_437c297c(DAT_437943fc + 0x437940f2,auStack_90,2);
  }
  if ((*(uint *)(DAT_43794400 + 0x437948fe) & 0x80) == 0) {
    FUN_43560da8(0x11,0x80);
    FUN_43ae9148(auStack_a4,DAT_43794404 + 0x43794112);
    FUN_437b66e0(DAT_43794408 + 0x4379411e,auStack_a4,0x80);
  }
  if ((*(uint *)(DAT_4379440c + 0x4379492a) & 8) == 0) {
    FUN_43560da8(0x11,8);
    FUN_43ae9148(auStack_b8,DAT_43794410 + 0x4379413e);
    FUN_4379fd58(DAT_43794414 + 0x4379414a,auStack_b8,8);
  }
  if ((*(uint *)(DAT_43794418 + 0x43794956) & 0x40) == 0) {
    FUN_43560da8(0x11,0x40);
    FUN_43ae9148(auStack_cc,DAT_4379441c + 0x4379416a);
    FUN_437d9e00(DAT_43794420 + 0x43794176,auStack_cc,0x40);
  }
  if ((*(uint *)(DAT_43794424 + 0x43794982) & 0x20) == 0) {
    FUN_43560da8(0x11,0x20);
    FUN_43ae9148(auStack_e0,DAT_43794428 + 0x43794196);
    FUN_437d0c90(DAT_4379442c + 0x437941a2,auStack_e0,0x20);
  }
  if ((*(uint *)((int)&DAT_437949ac + DAT_43794430 + 2) & 0x200) == 0) {
    FUN_43560da8(0x11,0x200);
    uVar13 = FUN_4378dd84();
    FUN_43ae9148(auStack_f4,DAT_43794434 + 0x437941c6);
    FUN_437b82d8(DAT_43794438 + 0x437941d6,uVar13,auStack_f4,0x200);
  }
  iVar44 = DAT_43794448;
  bVar56 = (*(byte *)((int)&DAT_437949ec + DAT_4379443c + 2) & 0x40) != 0;
  if (bVar56) {
    iVar46 = *(int *)(*(int *)(DAT_43794444 + 0x43794204) + 0x10);
  }
  else {
    iVar46 = *(int *)(*(int *)(DAT_43794440 + 0x437941f8) + 0x10);
  }
  psVar38 = (short *)(DAT_43794448 + 0x4379420e);
  thunk_FUN_43721e60(!bVar56,iVar46 == 3);
  if (*(int *)(iVar44 + 0x43794822) == 0) {
    if ((*(byte *)(iVar44 + 0x43794a1a) & 0x40) != 0) {
      FUN_43795bf0();
      goto LAB_437944b8;
    }
    FUN_43ae93ce();
    uVar32 = 0;
  }
  else {
    if (uVar1 == 0x103) {
      if (*psVar38 != 0x14a) goto LAB_437944be;
      FUN_43ae93dc();
      FUN_4378f3f8(1);
      uVar32 = 1;
LAB_437944a2:
      *(undefined1 *)((int)&DAT_437949f4 + iVar44 + 2) = uVar32;
      goto LAB_437944be;
    }
    if (uVar1 < 0x104) {
      if (uVar1 < 0x100) goto LAB_437944be;
      if (uVar1 < 0x102) {
        if (1 < (ushort)(*psVar38 - 0x105U)) goto LAB_437944be;
        FUN_43795c14();
        uVar32 = 0;
        goto LAB_437944ba;
      }
    }
    else {
      if (uVar1 == 0x10e) {
        sVar25 = *psVar38;
        if (((((sVar25 == 0x102) || (sVar25 == 0x107)) || (sVar25 == 0x11a)) ||
            ((sVar25 == 0x11b || (sVar25 == 0x118)))) || ((sVar25 == 0x119 || (sVar25 == 0x132)))) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
        }
        goto LAB_437944be;
      }
      if (uVar1 < 0x10f) {
        if (uVar1 != 0x107) goto LAB_437944be;
      }
      else if (uVar1 != 0x132) {
        if ((uVar1 != 0x14a) || (1 < (ushort)(*psVar38 - 0x102U))) goto LAB_437944be;
        FUN_43ae93ea();
        FUN_4378f3f8(0);
        FUN_436d6118();
        FUN_43ad913e();
        uVar32 = 0;
        goto LAB_437944a2;
      }
    }
    if (*(short *)(DAT_437945fc + 0x437944ae) != 0x10e) goto LAB_437944be;
    FUN_43ae93dc();
LAB_437944b8:
    uVar32 = 1;
  }
LAB_437944ba:
  FUN_4378f3f8(uVar32);
LAB_437944be:
  if ((*(char *)(iVar39 + 0x70) == '\0') && (iVar44 = FUN_437999e4(1,0xe), iVar44 != 0)) {
    FUN_43b71948();
  }
  if ((**(uint **)(DAT_43794600 + 0x437944dc) & 0xfffff) == 0) {
    FUN_43728be0();
  }
  FUN_4378f7a0(0xc39);
  if (*(char *)(iVar39 + 0xbf) != '\0') {
    FUN_43ae9124(auStack_108,*(undefined4 *)(iVar43 + DAT_43794604));
    FUN_439018b0(DAT_43794608 + 0x4379450a,auStack_108,2,0);
  }
  iVar43 = DAT_4379460c;
  FUN_43560da8(0x1a,0x40);
  FUN_43ae129a(4);
  if (param_1 != **(int **)(iVar43 + 0x4379451c)) {
    iVar44 = thunk_FUN_436cd00c();
    uVar48 = (uint)(iVar44 - (*(undefined4 **)(iVar43 + 0x4379451c))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43794610 + 0x4379454c,param_1,**(undefined4 **)(iVar43 + 0x4379451c),
                 uVar48);
    FUN_43902718(DAT_43794614 + 0x4379455a,param_1,**(undefined4 **)(iVar43 + 0x4379451c),uVar48);
    FUN_4378f988(4,0,uVar48);
    if ((*(byte *)(iVar39 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43794618 + 0x43794578);
    }
    if ((*(byte *)(iVar39 + 0x1b) & 2) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(byte *)(iVar39 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_4379461c + 0x43794598);
  }
  return;
}


/* 4387a6c4 */

void FUN_4387a6c4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_c;
  undefined4 uStack_8;
  
  uStack_8 = param_3;
  if (*(uint *)(DAT_4387a6f4 + 0x4387a6cc) < 4) {
                    /* WARNING: Could not recover jumptable at 0x4387a6d0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uStack_c = param_2;
    (*(code *)(&switchD_4387a6d0::switchdataD_4387a6d4 +
              (uint)(&switchD_4387a6d0::switchdataD_4387a6d4)[*(uint *)(DAT_4387a6f4 + 0x4387a6cc)]
              * 2))();
    return;
  }
  uStack_c = 6;
  FUN_436bec28(param_1,&uStack_c,param_3,6,param_1);
  return;
}


/* 4387a758 */

void FUN_4387a758(undefined4 *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  ushort uVar2;
  char cVar3;
  int iVar4;
  undefined1 uVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  undefined1 *puVar8;
  undefined4 *puVar9;
  undefined1 *puVar10;
  undefined4 *puVar11;
  undefined4 uVar12;
  undefined1 *puVar13;
  int *piVar14;
  int iVar15;
  int iVar16;
  undefined4 uVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  
  iVar20 = 0;
  puVar9 = (undefined4 *)(DAT_4387b110 + 0x4387a770);
  uVar6 = *(undefined2 *)(param_1 + 2);
  iVar16 = DAT_4387b118 + 0x4387a77c;
  *(undefined4 *)(DAT_4387b114 + 0x4387a774) = *puVar9;
  puVar11 = (undefined4 *)(DAT_4387b11c + 0x4387a788);
  *(undefined4 *)(DAT_4387b120 + 0x4387a78a) = *puVar11;
  uVar17 = *param_1;
  *(undefined4 *)(DAT_4387b124 + 0x4387a796) = uVar17;
  iVar15 = DAT_4387b128;
  *(undefined2 *)(DAT_4387b128 + 0x4387a79e) = uVar6;
  *(undefined2 *)(iVar15 + 0x4387a7a0) = *(undefined2 *)((int)param_1 + 10);
  uVar5 = *(undefined1 *)(param_1 + 8);
  *puVar9 = param_1[3];
  *(undefined4 *)(DAT_4387b12c + 0x4387a7b4) = param_1[4];
  *(undefined2 *)(DAT_4387b130 + 0x4387a7be) = *(undefined2 *)((int)param_1 + 0x16);
  uVar6 = *(undefined2 *)(param_1 + 6);
  *(undefined2 *)(DAT_4387b134 + 0x4387a7c8) = uVar6;
  *(undefined1 *)(DAT_4387b138 + 0x4387a7d0) = uVar5;
  *(undefined1 *)(DAT_4387b13c + 0x4387a7dc) = *(undefined1 *)((int)param_1 + 0x21);
  iVar18 = param_1[0xb];
  *puVar11 = param_1[9];
  *(undefined1 *)(DAT_4387b140 + 0x4387a7ee) = *(undefined1 *)(param_1 + 10);
  uVar7 = param_1[0xc];
  uVar5 = *(undefined1 *)(param_1 + 0xd);
  *(int *)(DAT_4387b144 + 0x4387a7f8) = iVar18;
  *(undefined4 *)(DAT_4387b148 + 0x4387a804) = uVar7;
  *(undefined1 *)(DAT_4387b14c + 0x4387a80c) = uVar5;
  *(undefined1 *)(DAT_4387b150 + 0x4387a81a) = *(undefined1 *)((int)param_1 + 0x35);
  *(undefined4 *)(DAT_4387b154 + 0x4387a824) = param_1[0xe];
  iVar15 = DAT_4387b158;
  *(undefined2 *)(DAT_4387b158 + 0x4387a82c) = uVar6;
  *(undefined1 *)(iVar15 + 0x4387a82e) = *(undefined1 *)(param_1 + 0xf);
  do {
    iVar4 = DAT_4387b15c;
    iVar15 = iVar20 + 0x40;
    uVar7 = *(undefined4 *)((int)param_1 + iVar20 + 0x44);
    uVar12 = *(undefined4 *)((int)param_1 + iVar20 + 0x48);
    iVar19 = DAT_4387b15c + iVar20;
    iVar20 = iVar20 + 0xc;
    *(undefined4 *)(iVar19 + 0x4387a844) = *(undefined4 *)((int)param_1 + iVar15);
    *(undefined4 *)(iVar19 + 0x4387a848) = uVar7;
    *(undefined4 *)(iVar19 + 0x4387a84c) = uVar12;
  } while (iVar20 != 0x60);
  uVar6 = *(undefined2 *)(param_1 + 0x28);
  *(undefined1 *)(iVar4 + 0x4387a8b0) = uVar5;
  *(undefined2 *)(iVar4 + 0x4387a8a4) = uVar6;
  uVar7 = param_1[0x2a];
  *(undefined4 *)(iVar4 + 0x4387a8a8) = param_1[0x29];
  *(undefined4 *)(iVar4 + 0x4387a8ac) = uVar7;
  bVar1 = **(byte **)(iVar16 + DAT_4387b160);
  if ((bVar1 & 2) != 0) {
    *(ushort *)(DAT_4387b16c + 0x4387a896) =
         (ushort)**(byte **)(iVar16 + DAT_4387b164) * 0x100 +
         (ushort)**(byte **)(iVar16 + DAT_4387b168);
  }
  if ((bVar1 & 1) != 0) {
    *(ushort *)(DAT_4387b178 + 0x4387a8b8) =
         (ushort)**(byte **)(iVar16 + DAT_4387b170) * 0x100 +
         (ushort)**(byte **)(iVar16 + DAT_4387b174);
  }
  if ((bVar1 & 0x10) != 0) {
    *(byte *)(DAT_4387b17c + 0x4387a8d4) = (byte)(((uint)bVar1 << 0x1a) >> 0x1f);
  }
  if ((bVar1 & 0x40) != 0) {
    *(byte *)(DAT_4387b180 + 0x4387a8e6) = bVar1 >> 7;
  }
  if ((bVar1 & 4) != 0) {
    *(byte *)(DAT_4387b184 + 0x4387a8fa) = (byte)(((uint)bVar1 << 0x1c) >> 0x1f);
  }
  if ((**(byte **)(iVar16 + DAT_4387b188) & 8) != 0) {
    *(undefined1 *)(DAT_4387b18c + 0x4387a914) = 0;
    *(undefined4 *)(DAT_4387b190 + 0x4387a91e) = 1;
  }
  iVar15 = DAT_4387b1a0;
  puVar8 = (undefined1 *)(DAT_4387b194 + 0x4387a932);
  puVar10 = (undefined1 *)(DAT_4387b198 + 0x4387a938);
  puVar13 = (undefined1 *)(DAT_4387b19c + 0x4387a93a);
  *puVar8 = 0;
  *puVar10 = 0;
  *puVar13 = 0;
  *(undefined1 *)(iVar15 + 0x4387a940) = 0;
  iVar20 = DAT_4387b1a8;
  if (iVar18 == 0) {
    *puVar8 = 1;
    piVar14 = (int *)(DAT_4387b1a4 + 0x4387a958);
LAB_4387a984:
    *piVar14 = iVar18;
  }
  else {
    if (iVar18 == 1) {
      *puVar10 = 1;
      piVar14 = (int *)(iVar20 + 0x4387a966);
      goto LAB_4387a984;
    }
    if (iVar18 == 2) {
      *puVar13 = 1;
      piVar14 = (int *)(DAT_4387b1ac + 0x4387a976);
      goto LAB_4387a984;
    }
    if (iVar18 == 3) {
      *(undefined1 *)(iVar15 + 0x4387a940) = 1;
      piVar14 = (int *)(DAT_4387b1b0 + 0x4387a986);
      goto LAB_4387a984;
    }
  }
  uVar7 = FUN_4387a4f4();
  piVar14 = (int *)(DAT_4387b1b4 + 0x4387a996);
  FUN_43acb946(uVar17,uVar7,DAT_4387b1b8 + 0x4387a99a,piVar14,param_4);
  iVar15 = *piVar14;
  if ((iVar15 == 0) || (iVar15 == 0x11)) {
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b1bc + 0x4387a9b2);
  }
  else {
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b1c0 + 0x4387a9bc);
  }
  *puVar8 = uVar5;
  if ((((((iVar15 == 1) || (iVar15 == 9)) || (iVar15 == 2)) || ((iVar15 == 3 || (iVar15 == 6)))) ||
      (iVar15 == 7)) ||
     (((iVar15 == 8 || (iVar15 == 10)) ||
      ((iVar15 == 0xb || (((iVar15 == 0xc || (iVar15 == 0xd)) || (iVar15 == 0xe)))))))) {
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b1c4 + 0x4387a9f6);
  }
  else {
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b1c8 + 0x4387aa00);
  }
  *puVar8 = uVar5;
  if (((iVar15 - 4U < 2) || (iVar15 == 0xf)) || (iVar15 == 0x10)) {
    puVar8 = (undefined1 *)(DAT_4387b1cc + 0x4387aa16);
LAB_4387aa2e:
    uVar5 = 1;
  }
  else {
    if ((iVar15 == 1) || (iVar15 == 9)) {
      if (*(int *)(param_2[2] + 0x1c) - 2U < 2) {
        puVar8 = (undefined1 *)(DAT_4387b1d0 + 0x4387aa30);
        goto LAB_4387aa2e;
      }
      puVar8 = (undefined1 *)(DAT_4387b1d4 + 0x4387aa3a);
    }
    else {
      puVar8 = (undefined1 *)(DAT_4387b1d8 + 0x4387aa42);
    }
    uVar5 = 0;
  }
  *puVar8 = uVar5;
  if (iVar15 - 0xcU < 3) {
    *(undefined1 *)(DAT_4387b1dc + 0x4387aa56) = 1;
LAB_4387aa6a:
    if (((iVar15 == 2) || (iVar15 == 3)) || (iVar15 == 0xb)) goto LAB_4387aa76;
    *(undefined1 *)(DAT_4387b1e8 + 0x4387aa90) = 0;
LAB_4387aa9c:
    *(undefined1 *)(DAT_4387b1f0 + 0x4387aaa8) = 0;
    if (iVar15 != 0xd) goto LAB_4387aab6;
    *(undefined1 *)(DAT_4387b1f4 + 0x4387aab4) = 1;
LAB_4387aada:
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b200 + 0x4387aae4);
  }
  else {
    *(undefined1 *)(DAT_4387b1e0 + 0x4387aa64) = 0;
    if ((iVar15 != 1) && (iVar15 != 9)) goto LAB_4387aa6a;
LAB_4387aa76:
    *(undefined1 *)(DAT_4387b1e4 + 0x4387aa82) = 1;
    if (iVar15 != 2) goto LAB_4387aa9c;
    *(undefined1 *)(DAT_4387b1ec + 0x4387aa9a) = 1;
LAB_4387aab6:
    *(undefined1 *)(DAT_4387b1f8 + 0x4387aac2) = 0;
    if (((iVar15 != 9) && (iVar15 != 1)) && ((iVar15 != 7 && (iVar15 != 8)))) goto LAB_4387aada;
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b1fc + 0x4387aada);
  }
  *puVar8 = uVar5;
  if (iVar15 == 0xc) {
    *(undefined1 *)(DAT_4387b204 + 0x4387aaf2) = 1;
LAB_4387ab0c:
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b210 + 0x4387ab16);
  }
  else {
    *(undefined1 *)(DAT_4387b208 + 0x4387ab00) = 0;
    if (iVar15 != 6) goto LAB_4387ab0c;
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b20c + 0x4387ab0c);
  }
  *puVar8 = uVar5;
  if ((*(char *)(DAT_4387b214 + 0x4387ab1e) == '\0') &&
     ((*(char *)(DAT_4387b218 + 0x4387ab28) == '\0' ||
      (*(char *)(DAT_4387b21c + 0x4387ab32) == '\0')))) {
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b224 + 0x4387ab48);
  }
  else {
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b220 + 0x4387ab3e);
  }
  *puVar8 = uVar5;
  iVar15 = *(int *)(DAT_4387b228 + 0x4387ab50);
  if (iVar15 == 1) {
    *(undefined1 *)(DAT_4387b22c + 0x4387ab5c) = 1;
LAB_4387ab76:
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b238 + 0x4387ab80);
  }
  else {
    *(undefined1 *)(DAT_4387b230 + 0x4387ab6a) = 0;
    if (iVar15 != 2) goto LAB_4387ab76;
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b234 + 0x4387ab76);
  }
  *puVar8 = uVar5;
  if ((*(int *)(DAT_4387b23c + 0x4387ab88) == 1) && (*(char *)(DAT_4387b240 + 0x4387ab94) == '\0'))
  {
    *(undefined1 *)(DAT_4387b244 + 0x4387ab9e) = 1;
  }
  else {
    *(undefined1 *)(DAT_4387b248 + 0x4387abaa) = 0;
  }
  uVar7 = FUN_4387a468(param_2);
  iVar20 = param_2[2];
  uVar17 = *(undefined4 *)(param_2[1] + 0x10);
  iVar18 = *param_2;
  cVar3 = *(char *)(iVar20 + 0x29a);
  *(undefined4 *)(DAT_4387b24c + 0x4387abbe) = uVar17;
  *(char *)(DAT_4387b250 + 0x4387abcc) = cVar3;
  iVar15 = DAT_4387b3dc;
  uVar2 = *(ushort *)(iVar18 + 0xc);
  if (uVar2 == 0x708) {
    uVar7 = 2;
    puVar9 = (undefined4 *)(DAT_4387b260 + 0x4387ac2a);
    goto LAB_4387b06a;
  }
  if (0x708 < uVar2) {
    if (uVar2 == 0x714) goto LAB_4387abfa;
    if (uVar2 != 0x715) goto LAB_4387b064;
    if (*(int *)(iVar18 + 0x450) - 1U < 2) {
      uVar7 = 0;
      puVar9 = (undefined4 *)(DAT_4387b258 + 0x4387ac16);
      goto LAB_4387b06a;
    }
    puVar9 = (undefined4 *)(DAT_4387b25c + 0x4387ac1e);
LAB_4387ac1c:
    uVar7 = 1;
    goto LAB_4387b06a;
  }
  if (uVar2 == 0x702) {
LAB_4387abfa:
    puVar9 = (undefined4 *)(DAT_4387b254 + 0x4387ac02);
    goto LAB_4387ac1c;
  }
  if (uVar2 != 0x707) {
LAB_4387b064:
    uVar7 = 0x56;
    puVar9 = (undefined4 *)(DAT_4387b3d8 + 0x4387b06c);
    goto LAB_4387b06a;
  }
  switch(*(undefined4 *)(iVar20 + 0x1c)) {
  case 0:
    if (*(char *)(iVar20 + 0x24) == '\0') {
      switch(uVar17) {
      case 0:
      case 1:
        if (cVar3 == '\0') {
          switch(uVar7) {
          case 0:
            uVar7 = 0x24;
            puVar9 = (undefined4 *)(DAT_4387b31c + 0x4387ae9a);
            break;
          case 1:
            uVar7 = 0x25;
            puVar9 = (undefined4 *)(DAT_4387b320 + 0x4387aea4);
            break;
          case 2:
            uVar7 = 0x26;
            puVar9 = (undefined4 *)(DAT_4387b324 + 0x4387aeae);
            break;
          case 3:
            uVar7 = 0x27;
            puVar9 = (undefined4 *)(DAT_4387b328 + 0x4387aeb8);
            break;
          case 4:
            uVar7 = 0x28;
            puVar9 = (undefined4 *)(DAT_4387b32c + 0x4387aec2);
            break;
          case 5:
            uVar7 = 0x29;
            puVar9 = (undefined4 *)(DAT_4387b330 + 0x4387aecc);
            break;
          case 6:
            uVar7 = 0x2a;
            puVar9 = (undefined4 *)(DAT_4387b334 + 0x4387aed6);
            break;
          case 7:
            puVar9 = (undefined4 *)(DAT_4387b338 + 0x4387aede);
            goto LAB_4387aee4;
          default:
            puVar9 = (undefined4 *)(DAT_4387b33c + 0x4387aee6);
LAB_4387aee4:
            uVar7 = 0x2b;
          }
          goto LAB_4387b06a;
        }
        switch(uVar7) {
        case 0:
          uVar7 = 0x2c;
          puVar9 = (undefined4 *)(DAT_4387b2f8 + 0x4387ae32);
          break;
        case 1:
          uVar7 = 0x2d;
          puVar9 = (undefined4 *)(DAT_4387b2fc + 0x4387ae3c);
          break;
        case 2:
          uVar7 = 0x2e;
          puVar9 = (undefined4 *)(DAT_4387b300 + 0x4387ae46);
          break;
        case 3:
          uVar7 = 0x2f;
          puVar9 = (undefined4 *)(DAT_4387b304 + 0x4387ae50);
          break;
        case 4:
          uVar7 = 0x30;
          puVar9 = (undefined4 *)(DAT_4387b308 + 0x4387ae5a);
          break;
        case 5:
          uVar7 = 0x31;
          puVar9 = (undefined4 *)(DAT_4387b30c + 0x4387ae64);
          break;
        case 6:
          uVar7 = 0x32;
          puVar9 = (undefined4 *)(DAT_4387b310 + 0x4387ae6e);
          break;
        case 7:
          puVar9 = (undefined4 *)(DAT_4387b314 + 0x4387ae76);
          goto LAB_4387ae7c;
        default:
          puVar9 = (undefined4 *)(DAT_4387b318 + 0x4387ae7e);
LAB_4387ae7c:
          uVar7 = 0x33;
        }
        goto LAB_4387b06a;
      case 2:
      case 3:
        goto switchD_4387aeec_switchD;
      default:
        uVar7 = 0x3c;
        puVar9 = (undefined4 *)(DAT_4387b364 + 0x4387af5a);
        goto LAB_4387b06a;
      }
    }
    switch(uVar17) {
    case 0:
    case 1:
      if (cVar3 == '\0') {
        switch(uVar7) {
        case 0:
          uVar7 = 0xb;
          puVar9 = (undefined4 *)(DAT_4387b2ac + 0x4387ad46);
          break;
        case 1:
          uVar7 = 0xc;
          puVar9 = (undefined4 *)(DAT_4387b2b0 + 0x4387ad50);
          break;
        case 2:
          uVar7 = 0xd;
          puVar9 = (undefined4 *)(DAT_4387b2b4 + 0x4387ad5a);
          break;
        case 3:
          uVar7 = 0xe;
          puVar9 = (undefined4 *)(DAT_4387b2b8 + 0x4387ad64);
          break;
        case 4:
          uVar7 = 0xf;
          puVar9 = (undefined4 *)(DAT_4387b2bc + 0x4387ad6e);
          break;
        case 5:
          uVar7 = 0x10;
          puVar9 = (undefined4 *)(DAT_4387b2c0 + 0x4387ad78);
          break;
        case 6:
          uVar7 = 0x11;
          puVar9 = (undefined4 *)(DAT_4387b2c4 + 0x4387ad82);
          break;
        case 7:
          puVar9 = (undefined4 *)(DAT_4387b2c8 + 0x4387ad8a);
          goto LAB_4387ad90;
        default:
          puVar9 = (undefined4 *)(DAT_4387b2cc + 0x4387ad92);
LAB_4387ad90:
          uVar7 = 0x12;
        }
        goto LAB_4387b06a;
      }
      switch(uVar7) {
      case 0:
        uVar7 = 0x13;
        puVar9 = (undefined4 *)(DAT_4387b288 + 0x4387acde);
        break;
      case 1:
        uVar7 = 0x14;
        puVar9 = (undefined4 *)(DAT_4387b28c + 0x4387ace8);
        break;
      case 2:
        uVar7 = 0x15;
        puVar9 = (undefined4 *)(DAT_4387b290 + 0x4387acf2);
        break;
      case 3:
        uVar7 = 0x16;
        puVar9 = (undefined4 *)(DAT_4387b294 + 0x4387acfc);
        break;
      case 4:
        uVar7 = 0x17;
        puVar9 = (undefined4 *)(DAT_4387b298 + 0x4387ad06);
        break;
      case 5:
        uVar7 = 0x18;
        puVar9 = (undefined4 *)(DAT_4387b29c + 0x4387ad10);
        break;
      case 6:
        uVar7 = 0x19;
        puVar9 = (undefined4 *)(DAT_4387b2a0 + 0x4387ad1a);
        break;
      case 7:
        puVar9 = (undefined4 *)(DAT_4387b2a4 + 0x4387ad22);
        goto LAB_4387ad28;
      default:
        puVar9 = (undefined4 *)(DAT_4387b2a8 + 0x4387ad2a);
LAB_4387ad28:
        uVar7 = 0x1a;
      }
      goto LAB_4387b06a;
    case 2:
    case 3:
      goto switchD_4387ad98_switchD;
    default:
      uVar7 = 0x23;
      puVar9 = (undefined4 *)(DAT_4387b2f4 + 0x4387ae06);
      goto LAB_4387b06a;
    }
  case 1:
    goto switchD_4387af5e_switchD;
  case 2:
    switch(uVar7) {
    case 0:
      uVar7 = 0x4d;
      puVar9 = (undefined4 *)(DAT_4387b38c + 0x4387afc8);
      break;
    case 1:
      uVar7 = 0x4e;
      puVar9 = (undefined4 *)(DAT_4387b390 + 0x4387afd0);
      break;
    case 2:
      uVar7 = 0x4f;
      puVar9 = (undefined4 *)(DAT_4387b394 + 0x4387afd8);
      break;
    case 3:
      uVar7 = 0x50;
      puVar9 = (undefined4 *)(DAT_4387b398 + 0x4387afe0);
      break;
    case 4:
      uVar7 = 0x51;
      puVar9 = (undefined4 *)(DAT_4387b39c + 0x4387afe8);
      break;
    case 5:
      uVar7 = 0x52;
      puVar9 = (undefined4 *)(DAT_4387b3a0 + 0x4387aff0);
      break;
    case 6:
      uVar7 = 0x53;
      puVar9 = (undefined4 *)(DAT_4387b3a4 + 0x4387aff8);
      break;
    case 7:
      puVar9 = (undefined4 *)(DAT_4387b3a8 + 0x4387affe);
      goto LAB_4387b002;
    default:
      puVar9 = (undefined4 *)(DAT_4387b3ac + 0x4387b004);
LAB_4387b002:
      uVar7 = 0x54;
    }
    goto LAB_4387b06a;
  case 3:
    switch(uVar7) {
    case 0:
      uVar7 = 0x45;
      puVar9 = (undefined4 *)(DAT_4387b3b0 + 0x4387b01e);
      break;
    case 1:
      uVar7 = 0x46;
      puVar9 = (undefined4 *)(DAT_4387b3b4 + 0x4387b026);
      break;
    case 2:
      uVar7 = 0x47;
      puVar9 = (undefined4 *)(DAT_4387b3b8 + 0x4387b02e);
      break;
    case 3:
      uVar7 = 0x48;
      puVar9 = (undefined4 *)(DAT_4387b3bc + 0x4387b036);
      break;
    case 4:
      uVar7 = 0x49;
      puVar9 = (undefined4 *)(DAT_4387b3c0 + 0x4387b03e);
      break;
    case 5:
      uVar7 = 0x4a;
      puVar9 = (undefined4 *)(DAT_4387b3c4 + 0x4387b046);
      break;
    case 6:
      uVar7 = 0x4b;
      puVar9 = (undefined4 *)(DAT_4387b3c8 + 0x4387b04e);
      break;
    case 7:
      puVar9 = (undefined4 *)(DAT_4387b3cc + 0x4387b054);
      goto LAB_4387b058;
    default:
      puVar9 = (undefined4 *)(DAT_4387b3d0 + 0x4387b05a);
LAB_4387b058:
      uVar7 = 0x4c;
    }
    goto LAB_4387b06a;
  case 4:
    switch(uVar7) {
    case 0:
      uVar7 = 3;
      puVar9 = (undefined4 *)(DAT_4387b264 + 0x4387ac5a);
      break;
    case 1:
      uVar7 = 4;
      puVar9 = (undefined4 *)(DAT_4387b268 + 0x4387ac64);
      break;
    case 2:
      uVar7 = 5;
      puVar9 = (undefined4 *)(DAT_4387b26c + 0x4387ac6e);
      break;
    case 3:
      uVar7 = 6;
      puVar9 = (undefined4 *)(DAT_4387b270 + 0x4387ac78);
      break;
    case 4:
      uVar7 = 7;
      puVar9 = (undefined4 *)(DAT_4387b274 + 0x4387ac82);
      break;
    case 5:
      uVar7 = 8;
      puVar9 = (undefined4 *)(DAT_4387b278 + 0x4387ac8c);
      break;
    case 6:
      uVar7 = 9;
      puVar9 = (undefined4 *)(DAT_4387b27c + 0x4387ac96);
      break;
    case 7:
      puVar9 = (undefined4 *)(DAT_4387b280 + 0x4387ac9e);
      goto LAB_4387aca4;
    default:
      puVar9 = (undefined4 *)(DAT_4387b284 + 0x4387aca6);
LAB_4387aca4:
      uVar7 = 10;
    }
    goto LAB_4387b06a;
  default:
    uVar7 = 0x55;
    puVar9 = (undefined4 *)(DAT_4387b3d4 + 0x4387b064);
    goto LAB_4387b06a;
  }
switchD_4387aeec_switchD:
  switch(uVar7) {
  case 0:
    uVar7 = 0x34;
    puVar9 = (undefined4 *)(DAT_4387b340 + 0x4387af02);
    break;
  case 1:
    uVar7 = 0x35;
    puVar9 = (undefined4 *)(DAT_4387b344 + 0x4387af0c);
    break;
  case 2:
    uVar7 = 0x36;
    puVar9 = (undefined4 *)(DAT_4387b348 + 0x4387af16);
    break;
  case 3:
    uVar7 = 0x37;
    puVar9 = (undefined4 *)(DAT_4387b34c + 0x4387af20);
    break;
  case 4:
    uVar7 = 0x38;
    puVar9 = (undefined4 *)(DAT_4387b350 + 0x4387af2a);
    break;
  case 5:
    uVar7 = 0x39;
    puVar9 = (undefined4 *)(DAT_4387b354 + 0x4387af34);
    break;
  case 6:
    uVar7 = 0x3a;
    puVar9 = (undefined4 *)(DAT_4387b358 + 0x4387af3e);
    break;
  case 7:
    puVar9 = (undefined4 *)(DAT_4387b35c + 0x4387af46);
    goto LAB_4387af4c;
  default:
    puVar9 = (undefined4 *)(DAT_4387b360 + 0x4387af4e);
LAB_4387af4c:
    uVar7 = 0x3b;
  }
  goto LAB_4387b06a;
switchD_4387ad98_switchD:
  switch(uVar7) {
  case 0:
    uVar7 = 0x1b;
    puVar9 = (undefined4 *)(DAT_4387b2d0 + 0x4387adae);
    break;
  case 1:
    uVar7 = 0x1c;
    puVar9 = (undefined4 *)(DAT_4387b2d4 + 0x4387adb8);
    break;
  case 2:
    uVar7 = 0x1d;
    puVar9 = (undefined4 *)(DAT_4387b2d8 + 0x4387adc2);
    break;
  case 3:
    uVar7 = 0x1e;
    puVar9 = (undefined4 *)(DAT_4387b2dc + 0x4387adcc);
    break;
  case 4:
    uVar7 = 0x1f;
    puVar9 = (undefined4 *)(DAT_4387b2e0 + 0x4387add6);
    break;
  case 5:
    uVar7 = 0x20;
    puVar9 = (undefined4 *)(DAT_4387b2e4 + 0x4387ade0);
    break;
  case 6:
    uVar7 = 0x21;
    puVar9 = (undefined4 *)(DAT_4387b2e8 + 0x4387adea);
    break;
  case 7:
    puVar9 = (undefined4 *)(DAT_4387b2ec + 0x4387adf2);
    goto LAB_4387adf8;
  default:
    puVar9 = (undefined4 *)(DAT_4387b2f0 + 0x4387adfa);
LAB_4387adf8:
    uVar7 = 0x22;
  }
  goto LAB_4387b06a;
switchD_4387af5e_switchD:
  switch(uVar7) {
  case 0:
    uVar7 = 0x3d;
    puVar9 = (undefined4 *)(DAT_4387b368 + 0x4387af72);
    break;
  case 1:
    uVar7 = 0x3e;
    puVar9 = (undefined4 *)(DAT_4387b36c + 0x4387af7a);
    break;
  case 2:
    uVar7 = 0x3f;
    puVar9 = (undefined4 *)(DAT_4387b370 + 0x4387af82);
    break;
  case 3:
    uVar7 = 0x40;
    puVar9 = (undefined4 *)(DAT_4387b374 + 0x4387af8a);
    break;
  case 4:
    uVar7 = 0x41;
    puVar9 = (undefined4 *)(DAT_4387b378 + 0x4387af92);
    break;
  case 5:
    uVar7 = 0x42;
    puVar9 = (undefined4 *)(DAT_4387b37c + 0x4387af9a);
    break;
  case 6:
    uVar7 = 0x43;
    puVar9 = (undefined4 *)(DAT_4387b380 + 0x4387afa2);
    break;
  case 7:
    puVar9 = (undefined4 *)(DAT_4387b384 + 0x4387afa8);
    goto LAB_4387afac;
  default:
    puVar9 = (undefined4 *)(DAT_4387b388 + 0x4387afae);
LAB_4387afac:
    uVar7 = 0x44;
  }
LAB_4387b06a:
  *puVar9 = uVar7;
  if (0x56 < *(int *)(iVar15 + 0x4387b072)) {
    FUN_4387a3c4(3,7,1,DAT_4387b3e0 + 0x4387b082);
    FUN_43902718(DAT_4387b3e4 + 0x4387b08a);
    *(int *)(iVar15 + 0x4387b072) = 0x56;
  }
  uVar5 = FUN_4387a4e8();
  iVar15 = *(int *)(iVar16 + DAT_4387b3e8);
  *(undefined1 *)(iVar15 + 0xca) = uVar5;
  uVar5 = FUN_4387a710();
  *(undefined1 *)(iVar15 + 0xcb) = uVar5;
  uVar5 = FUN_4387a6a0();
  *(undefined1 *)(iVar15 + 0xcc) = uVar5;
  uVar5 = FUN_4387a6ac();
  *(undefined1 *)(iVar15 + 0xcd) = uVar5;
  uVar5 = FUN_4387a6b8();
  *(undefined1 *)(iVar15 + 0xce) = uVar5;
  uVar5 = FUN_4387a6f8();
  *(undefined1 *)(iVar15 + 0xcf) = uVar5;
  uVar5 = FUN_4387a704();
  *(undefined1 *)(iVar15 + 0xd0) = uVar5;
  uVar5 = FUN_4387a71c();
  *(undefined1 *)(iVar15 + 0xd1) = uVar5;
  uVar5 = FUN_4387a528();
  *(undefined1 *)(iVar15 + 0xd2) = uVar5;
  uVar6 = FUN_4387a638();
  *(undefined2 *)(iVar15 + 0xd6) = uVar6;
  uVar6 = FUN_4387a644();
  *(undefined2 *)(iVar15 + 0xd8) = uVar6;
  uVar5 = FUN_4387a728();
  *(undefined1 *)(iVar15 + 0xda) = uVar5;
  uVar5 = FUN_4387a734();
  *(undefined1 *)(iVar15 + 0xdb) = uVar5;
  uVar5 = FUN_4387a740();
  *(undefined1 *)(iVar15 + 0xdc) = uVar5;
  uVar5 = FUN_4387a74c();
  *(undefined1 *)(iVar15 + 0xdd) = uVar5;
  return;
}


/* 43acb7be */

undefined4 FUN_43acb7be(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,uVar1);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,uVar1);
  if (iVar2 == param_1) {
    FUN_436bd3f4(uVar1);
    FUN_436bd7d8(uVar1);
    return 0;
  }
  return 4;
}


/* 43acb946 */

bool FUN_43acb946(undefined4 param_1,short *param_2,int *param_3,undefined4 *param_4)

{
  short sVar1;
  int iVar2;
  undefined4 uVar3;
  bool bVar4;
  
  sVar1 = *param_2;
  if (sVar1 == 0x5a0) {
    sVar1 = param_2[1];
    if (sVar1 == 0x438) {
      uVar3 = 9;
    }
    else if (sVar1 == 0x398) {
      uVar3 = 8;
    }
    else {
      if (sVar1 != 0x32c) {
        uVar3 = 0xc;
        bVar4 = sVar1 != 0x21c;
        goto LAB_43acba42;
      }
      uVar3 = 7;
    }
LAB_43acba40:
    bVar4 = false;
  }
  else {
    if (sVar1 == 0x780) {
      if (param_2[1] == 0x438) {
        uVar3 = 2;
        goto LAB_43acba40;
      }
      bVar4 = param_2[1] == 0x21c;
      if (bVar4) {
        uVar3 = 0xd;
      }
      else {
        uVar3 = 0xc;
      }
    }
    else if (sVar1 == 0x300) {
      bVar4 = param_2[1] == 0x1e0;
      if (bVar4) {
        uVar3 = 5;
      }
      else {
        uVar3 = 0xc;
      }
    }
    else if (sVar1 == 0x280) {
      bVar4 = param_2[1] == 0x1e0;
      if (bVar4) {
        uVar3 = 4;
      }
      else {
        uVar3 = 0xc;
      }
    }
    else {
      if (sVar1 != 0x500) {
        if (sVar1 == 0x2d0) {
          if (param_2[1] != 0xf0) {
            bVar4 = param_2[1] == 0x120;
            if (bVar4) {
              uVar3 = 0x10;
            }
            else {
              uVar3 = 0xc;
            }
            goto LAB_43acb9de;
          }
          uVar3 = 0xf;
        }
        else if (sVar1 == 0x3c0) {
          if (param_2[1] == 0x438) {
            uVar3 = 3;
          }
          else {
            if (param_2[1] != 0x21c) goto LAB_43acba38;
            if (*param_3 == 1) {
              uVar3 = 0xe;
            }
            else {
              uVar3 = 10;
            }
          }
        }
        else {
          if ((sVar1 != 0xf00) || (param_2[1] != 0x870)) {
LAB_43acba38:
            uVar3 = 0xc;
            bVar4 = true;
            goto LAB_43acba42;
          }
          iVar2 = FUN_43acb0a0();
          if (iVar2 == 0) {
            uVar3 = 0;
            bVar4 = false;
            goto LAB_43acba42;
          }
          uVar3 = 0x11;
        }
        goto LAB_43acba40;
      }
      bVar4 = param_2[1] == 0x2d0;
      if (bVar4) {
        uVar3 = 6;
      }
      else {
        uVar3 = 0xc;
      }
    }
LAB_43acb9de:
    bVar4 = !bVar4;
  }
LAB_43acba42:
  *param_4 = uVar3;
  return bVar4;
}

