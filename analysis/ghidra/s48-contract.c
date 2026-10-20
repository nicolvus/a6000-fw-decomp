/* S41: read-only exports. */

/* 435a9e4c */

void FUN_435a9e4c(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = FUN_435612b4();
  uVar2 = FUN_435a9df0();
  FUN_435aa628(DAT_435a9e70,0x14e,uVar2);
  FUN_435a9df0(uVar1);
  return;
}


/* 435625dc */

void FUN_435625dc(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_4356260c;
  *(undefined4 *)(param_1 + 4) = 2;
  iVar2 = DAT_43562610;
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  iVar3 = DAT_43562614;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  FUN_435612b4(DAT_43562608,*(undefined4 *)(iVar1 + 0x435625ee + iVar2),
               *(undefined4 *)(iVar1 + 0x435625ee + iVar3));
  return;
}


/* 435637b8 */

void FUN_435637b8(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_435612b4(DAT_435637dc,param_1 + 4,
                       *(undefined4 *)(DAT_435637e4 + 0x435637c2 + DAT_435637e8),0);
  if (iVar1 != 0) {
    FUN_43a3aeda(DAT_435637e0);
    return;
  }
  return;
}


/* 436e5658 */

void FUN_436e5658(void)

{
  int iVar1;
  
  iVar1 = DAT_436e569c + 0x436e5662;
  if (*(char *)(*(int *)(iVar1 + DAT_436e56a0) + 0x39) == '\x01') {
    FUN_435612b4(DAT_436e5694,*(undefined4 *)(iVar1 + DAT_436e56a4),
                 *(undefined4 *)(iVar1 + DAT_436e56a8),0);
    FUN_435612b4(DAT_436e5698,*(undefined4 *)(iVar1 + DAT_436e56ac),
                 *(undefined4 *)(iVar1 + DAT_436e56b0),0);
  }
  FUN_435612b4(DAT_436fe968,*(undefined4 *)(DAT_436fe96c + 0x436fe95c + DAT_436fe970),
               DAT_436fe974 + 0x436fe966,0);
  return;
}


/* 436fe388 */

void FUN_436fe388(void)

{
  int iVar1;
  
  iVar1 = DAT_436fe3c0 + 0x436fe392;
  FUN_435612b4(DAT_436fe3b8,*(undefined4 *)(iVar1 + DAT_436fe3c4),
               *(undefined4 *)(iVar1 + DAT_436fe3c8),0);
  FUN_435612b4(DAT_436fe3bc,*(undefined4 *)(iVar1 + DAT_436fe3cc),
               *(undefined4 *)(iVar1 + DAT_436fe3d0),0);
  FUN_435612b4(DAT_436fe968,*(undefined4 *)(DAT_436fe96c + 0x436fe95c + DAT_436fe970),
               DAT_436fe974 + 0x436fe966,0);
  return;
}


/* 437c1468 */

void FUN_437c1468(void)

{
  undefined2 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined2 *apuStack_14 [2];
  
  FUN_4375e2d0();
  iVar3 = DAT_437c15ec;
  FUN_43777158();
  uVar2 = FUN_437772a8();
  iVar3 = iVar3 + 0x437c1480;
  **(undefined4 **)(iVar3 + DAT_437c15f0) = uVar2;
  uVar2 = FUN_437672d4();
  **(undefined4 **)(iVar3 + DAT_437c15f4) = uVar2;
  uVar2 = FUN_43a3a9b4(*(undefined4 *)(iVar3 + DAT_437c15f8),0x12,3);
  **(undefined4 **)(iVar3 + DAT_437c15fc) = uVar2;
  FUN_43758944();
  FUN_43763dec();
  FUN_43547c28();
  FUN_43af2852();
  FUN_43758a8c();
  FUN_43b718f4(*(undefined1 *)(*(int *)(iVar3 + DAT_437c1600) + 8));
  FUN_43adaa0a();
  FUN_4373d0e8();
  FUN_4378a3a8(4,*(undefined4 *)(iVar3 + DAT_437c1604),0x100);
  FUN_43ae6738();
  FUN_436eec64();
  FUN_435612b4(DAT_437c15d4,DAT_437c1608 + 0x437c14e4,DAT_437c160c + 0x437c14e8,0);
  FUN_437ca7f0();
  FUN_4376cce0();
  FUN_439d6d00(DAT_437c1610 + 0x437c14f8);
  FUN_435612b4(DAT_437c15d8,DAT_437c1618 + 0x437c1506,*(undefined4 *)(iVar3 + DAT_437c1614),0);
  FUN_435612b4(DAT_437c15dc,DAT_437c1620 + 0x437c1516,*(undefined4 *)(iVar3 + DAT_437c161c),0);
  FUN_43778734();
  iVar3 = FUN_43ae6872();
  thunk_FUN_436e5188(iVar3 != 0);
  FUN_43a0ca14();
  FUN_436eecdc();
  apuStack_14[0] = (undefined2 *)0x0;
  iVar3 = FUN_435612d0(DAT_437c15e0,apuStack_14,0x34,1);
  puVar1 = apuStack_14[0];
  if (iVar3 == 0) {
    iVar3 = DAT_437c1624 + 0x437c1558;
    *apuStack_14[0] = 9;
    FUN_439c1c2c(apuStack_14[0] + 1,0x32,iVar3,3,DAT_437c1628 + 0x437c1560,DAT_437c162c + 0x437c1566
                );
    *(undefined1 *)((int)puVar1 + 0x33) = 0;
    FUN_43561228(DAT_437c15e0,apuStack_14[0]);
    FUN_435612ec(DAT_437c15e0,apuStack_14[0]);
  }
  apuStack_14[0] = (undefined2 *)((uint)apuStack_14[0] & 0xffffff00);
  FUN_435613b0(DAT_437c15e4,apuStack_14);
  FUN_43762f98((uint)apuStack_14[0] & 0xff);
  FUN_436eec70();
  iVar3 = FUN_435612d0(DAT_437c15e8,apuStack_14,0x14,1);
  if (iVar3 == 0) {
    apuStack_14[0][2] = 0;
    *apuStack_14[0] = 3;
    apuStack_14[0][4] = 0;
    apuStack_14[0][1] = 6;
    uVar2 = DAT_437c15e8;
    apuStack_14[0][3] = 0x22;
    FUN_4356120c(uVar2);
  }
  FUN_437c7704();
  FUN_43b2a162(DAT_437c1630 + 0x437c15cc);
  return;
}


/* 437ce788 */

void FUN_437ce788(int param_1)

{
  *(char *)(DAT_437ce7c0 + 0x437ce790) = (char)param_1;
  if (param_1 != 0) {
    FUN_435612b4(DAT_437ce7b8,DAT_437ce7c4 + 0x437ce79c,DAT_437ce7c8 + 0x437ce7a0,0);
    FUN_435612b4(DAT_437ce7bc,DAT_437ce7cc + 0x437ce7ae,DAT_437ce7d0 + 0x437ce7b0,0);
    return;
  }
  return;
}


/* 438e5bc0 */

void FUN_438e5bc0(void)

{
  int iVar1;
  
  iVar1 = DAT_438e5bfc + 0x438e5bca;
  if (**(char **)(iVar1 + DAT_438e5c00) != '\0') {
    FUN_435612b4(DAT_438e5bf4,*(undefined4 *)(iVar1 + DAT_438e5c04),
                 *(undefined4 *)(iVar1 + DAT_438e5c08),0);
    FUN_435612b4(DAT_438e5bf8,*(undefined4 *)(iVar1 + DAT_438e5c0c),
                 *(undefined4 *)(iVar1 + DAT_438e5c10),0);
    return;
  }
  return;
}


/* 438fb4e4 */

void FUN_438fb4e4(void)

{
  int iVar1;
  
  iVar1 = DAT_438fb518;
  FUN_435612b4(DAT_438fb50c,DAT_438fb510 + 0x438fb4f4,DAT_438fb514 + 0x438fb4f0,0);
  iVar1 = *(int *)(iVar1 + 0x438fb4fe + DAT_438fb51c);
  *(byte *)(iVar1 + 0x76) = *(byte *)(iVar1 + 0x76) | 2;
  return;
}


/* 438ffd6c */

void FUN_438ffd6c(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_435612b4(DAT_438ffd98,DAT_438ffd9c + 0x438ffd7c,DAT_438ffda0 + 0x438ffd78,0);
  iVar2 = *(int *)(DAT_438ffda4 + 0x438ffd88 + DAT_438ffda8);
  *(undefined1 *)(iVar2 + 0x77) = 0;
  if (iVar1 != 0) {
    *(undefined1 *)(iVar2 + 0x77) = 1;
  }
  return;
}


/* 4398e7c0 */

/* WARNING: Removing unreachable block (ram,0x4398e876) */

void FUN_4398e7c0(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iStack_18;
  undefined4 uStack_14;
  
  iStack_18 = param_3;
  uStack_14 = param_4;
  FUN_4398e16c();
  FUN_439c5a04(DAT_4398e8f0 + 0x4398e7d0,0xff,0x30);
  iVar2 = FUN_4356119c(DAT_4398e8d4,&iStack_18);
  if ((iVar2 == 0) && (iStack_18 == 1)) {
    FUN_435611d4(DAT_4398e8d4);
  }
  iVar2 = FUN_4356119c(DAT_4398e8d8,&iStack_18);
  if ((iVar2 == 0) && (iStack_18 == 1)) {
    FUN_435611d4(DAT_4398e8d8);
  }
  iVar2 = FUN_435612b4(DAT_4398e8dc,DAT_4398e8f4 + 0x4398e80a,DAT_4398e8f8 + 0x4398e80c,0);
  if (iVar2 != 0) {
    FUN_4398e4cc(0xbe,0xadc,1,DAT_4398e8fc + 0x4398e820,iVar2);
    param_1 = iVar2;
  }
  iVar2 = FUN_435612b4(DAT_4398e8e0,DAT_4398e900 + 0x4398e82e,DAT_4398e904 + 0x4398e830,0);
  if (iVar2 != 0) {
    FUN_4398e4cc(0xbe,0xadc,1,DAT_4398e908 + 0x4398e844,iVar2);
    param_1 = iVar2;
  }
  cVar1 = FUN_435613b0(DAT_4398e8e4,&stack0xfffffff7);
  if (cVar1 != '\x01') {
    FUN_4398e4cc(0xbe,0xadc,1,DAT_4398e90c + 0x4398e868,param_1);
  }
  *(undefined4 *)(DAT_4398e910 + 0x4398e876) = 0;
  iVar2 = FUN_435613b0(DAT_4398e8e8,&stack0xfffffff6);
  if (iVar2 == 1) {
    *(undefined4 *)(DAT_4398e918 + 0x4398e8a2) = 3;
  }
  iVar2 = FUN_435613b0(DAT_4398e8ec,&stack0xfffffff5);
  if (iVar2 == 1) {
    *(undefined4 *)(DAT_4398e91c + 0x4398e8ba) = 0xff;
  }
  *(undefined4 *)(DAT_4398e920 + 0x4398e8c4) = 0;
  *(undefined4 *)(DAT_4398e924 + 0x4398e8ca) = 1;
  FUN_4398e3f4();
  return;
}


/* 4398ee68 */

void FUN_4398ee68(void)

{
  FUN_435612b4(DAT_4398ee78,DAT_4398ee7c + 0x4398ee74,DAT_4398ee80 + 0x4398ee76,0);
  return;
}


/* 439905a0 */

void FUN_439905a0(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int aiStack_24 [4];
  
  iVar2 = DAT_439905f0 + 0x439905aa;
  iVar4 = DAT_439905f0 + 0x4399060e;
  iVar3 = iVar2;
  do {
    uVar5 = *(undefined4 *)(iVar3 + 8);
    FUN_4356119c(uVar5,aiStack_24);
    if (aiStack_24[0] == 1) {
      thunk_FUN_435611d4(uVar5);
    }
    iVar3 = iVar3 + 0x14;
  } while (iVar3 != iVar4);
  do {
    puVar1 = (undefined4 *)(iVar2 + 8);
    iVar2 = iVar2 + 0x14;
    FUN_43b5e516(*puVar1);
  } while (iVar2 != iVar4);
  FUN_435612b4(DAT_439905ec,DAT_439905f4 + 0x439905e0,DAT_439905f8 + 0x439905e4,0);
  return;
}


/* 436fecbc */

void FUN_436fecbc(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  undefined1 *puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  iVar7 = DAT_436fee00 + 0x436fecca;
  if (*(char *)(DAT_436fedfc + 0x436fecc4) == '\0') {
    *(int *)(DAT_436fee04 + 0x436fecd6) = DAT_436fee08 + 0x436fecd8;
    iVar9 = *(int *)(iVar7 + DAT_436fee0c);
    iVar8 = 0;
    do {
      iVar6 = iVar9 + iVar8;
      bVar4 = *(byte *)(iVar6 + 2);
      puVar5 = (undefined1 *)(iVar6 + 3);
      if ((bVar4 & 0x80) == 0) {
        switch(*(undefined1 *)(iVar9 + iVar8)) {
        case 1:
          iVar2 = DAT_436fee10;
          break;
        case 2:
          iVar2 = DAT_436fee14;
          break;
        case 3:
          iVar2 = DAT_436fee18;
          break;
        case 4:
          iVar2 = DAT_436fee1c;
          break;
        case 5:
          iVar2 = DAT_436fee24;
          break;
        case 6:
          iVar2 = DAT_436fee28;
          break;
        case 7:
          iVar2 = DAT_436fee20;
          break;
        default:
          goto switchD_436fecfa_caseD_8;
        case 0xe:
          iVar2 = DAT_436fee2c;
        }
        if (*(short *)(*(int *)(iVar7 + iVar2) + (uint)*(byte *)(iVar6 + 1) * 2) == -0x5433) {
          iVar6 = *(byte *)(iVar6 + 1) + 1;
          uVar1 = *(undefined2 *)(*(int *)(iVar7 + iVar2) + iVar6 * 2);
          goto LAB_436fed3e;
        }
      }
      else {
        uVar1 = *(undefined2 *)(iVar9 + iVar8);
        bVar4 = bVar4 ^ 0x80;
LAB_436fed3e:
        FUN_436fead8(uVar1,bVar4,*puVar5,iVar6,param_1,param_2,param_3);
      }
switchD_436fecfa_caseD_8:
      iVar8 = iVar8 + 4;
    } while (iVar8 != 0x100);
    FUN_43716f18(*(undefined4 *)(DAT_436fee30 + 0x436fed50));
    uVar3 = FUN_4370fff8();
    iVar8 = DAT_436fee38 + 0x436fed62;
    *(undefined4 *)(DAT_436fee34 + 0x436fed60) = uVar3;
    iVar8 = FUN_435612b4(DAT_436fedf0,iVar8,*(undefined4 *)(iVar7 + DAT_436fee3c),0);
    if (iVar8 != 0) {
      FUN_436febc4(0xf,4,1,DAT_436fee40 + 0x436fed7e,iVar8);
    }
    iVar7 = FUN_435612b4(DAT_436fedf4,DAT_436fee48 + 0x436fed8c,
                         *(undefined4 *)(iVar7 + DAT_436fee44),0);
    if (iVar7 != 0) {
      FUN_436febc4(0xf,4,1,DAT_436fee4c + 0x436feda0,iVar7);
    }
    FUN_4390406c(DAT_436fedf8,DAT_436fee50 + 0x436fedac,0x10);
    puVar5 = (undefined1 *)(DAT_436fee58 + 0x436fedba);
    *(undefined2 *)(DAT_436fee54 + 0x436fedb8) = 0;
    *(undefined2 *)(DAT_436fee5c + 0x436fedc0) = 0;
    *(undefined1 *)(DAT_436fee60 + 0x436fedc6) = 0;
    *(undefined1 *)(DAT_436fee64 + 0x436fedcc) = 0;
    *puVar5 = 1;
    *(undefined1 *)(DAT_436fee68 + 0x436fedd6) = 0;
    *(undefined4 *)(DAT_436fee6c + 0x436feddc) = 1;
    *(undefined4 *)(DAT_436fee70 + 0x436fede2) = 1;
    *(undefined4 *)(DAT_436fee74 + 0x436fede8) = 1;
    *(undefined1 *)(DAT_436fee78 + 0x436fedee) = 0;
  }
  return;
}


/* 436fe388 */

void FUN_436fe388(void)

{
  int iVar1;
  
  iVar1 = DAT_436fe3c0 + 0x436fe392;
  FUN_435612b4(DAT_436fe3b8,*(undefined4 *)(iVar1 + DAT_436fe3c4),
               *(undefined4 *)(iVar1 + DAT_436fe3c8),0);
  FUN_435612b4(DAT_436fe3bc,*(undefined4 *)(iVar1 + DAT_436fe3cc),
               *(undefined4 *)(iVar1 + DAT_436fe3d0),0);
  FUN_435612b4(DAT_436fe968,*(undefined4 *)(DAT_436fe96c + 0x436fe95c + DAT_436fe970),
               DAT_436fe974 + 0x436fe966,0);
  return;
}


/* 437ca7f0 */

void FUN_437ca7f0(void)

{
  int iVar1;
  
  iVar1 = FUN_43ae6750();
  if (iVar1 == 0) {
    FUN_437cd5c4(0xffff,0);
  }
  FUN_43b28d52();
  FUN_435612b4(DAT_437ca81c,DAT_437ca820 + 0x437ca812,DAT_437ca824 + 0x437ca814,0);
  return;
}


/* 438f64cc */

void FUN_438f64cc(void)

{
  FUN_435612b4(DAT_438f64e0,DAT_438f64ec + 0x438f64dc,
               *(undefined4 *)(DAT_438f64e4 + 0x438f64d4 + DAT_438f64e8),0);
  return;
}


/* 4370662c */

void FUN_4370662c(void)

{
  FUN_435612b4(DAT_4370663c,DAT_43706640 + 0x43706638,DAT_43706644 + 0x4370663a,0);
  return;
}


/* 43789fdc */

void FUN_43789fdc(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = FUN_43561298(DAT_4378a030,*(undefined4 *)(DAT_4378a034 + 0x43789fe4));
  uVar2 = FUN_43561324(0x52,0,*(undefined4 *)(DAT_4378a038 + 0x43789ff2));
  FUN_43788fd0(1,1,0xff,0xff);
  FUN_43788c2c(uVar1);
  FUN_43788c2c(uVar2);
  FUN_43788fd0(*(undefined1 *)(DAT_4378a03c + 0x4378a01e),*(undefined1 *)(DAT_4378a040 + 0x4378a020)
               ,*(undefined1 *)(DAT_4378a044 + 0x4378a022),uVar1 & 0xff);
  return;
}

