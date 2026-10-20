/* S41: read-only exports. */

/* 43ae8f98 */

void FUN_43ae8f98(void)

{
  FUN_43560dc4(0x1a,0xffffffef);
  return;
}


/* 43ae8fa2 */

void FUN_43ae8fa2(void)

{
  FUN_43560da8(0x1a,0x10);
  return;
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


/* 43ae8ef4 */

int FUN_43ae8ef4(int param_1)

{
  FUN_43ad44a6(param_1 + 0x2d4);
  FUN_43ae0e36(param_1 + 0x870);
  FUN_43ad892c(param_1 + 0xb78);
  FUN_43ae119e(param_1 + 0xc78);
  return param_1;
}

