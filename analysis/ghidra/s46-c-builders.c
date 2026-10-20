/* S41: read-only exports. */

/* 437da078 */

void FUN_437da078(undefined4 *param_1,uint *param_2)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  ushort *puVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  code *pcVar8;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  int iVar9;
  undefined4 unaff_r6;
  undefined4 unaff_lr;
  
  bVar1 = *(byte *)(*(int *)(DAT_437da0b4 + 0x437da080 + DAT_437da0b8) + 1);
  if ((ushort)bVar1 != *(ushort *)(DAT_437da0bc + 0x437da08c)) {
    *(ushort *)((int)&DAT_437da0b4 + DAT_437da0c0) = (ushort)bVar1;
    FUN_437d9f9c();
  }
  iVar3 = DAT_437da0c8;
  puVar4 = (ushort *)(DAT_437da0c8 + 0x437da0ac);
  *(ushort *)(DAT_437da0c4 + 0x437da0aa) = (ushort)bVar1;
  iVar9 = DAT_437da354 + 0x437da2e8;
  if (((*(int *)(iVar3 + 0x437da308) != 0) && (iVar7 = *(int *)(iVar3 + 0x437da304), -1 < iVar7)) &&
     (iVar7 < *(int *)(iVar3 + 0x437da30c))) {
    pcVar8 = *(code **)(*(int *)(iVar3 + 0x437da308) + iVar7 * 4);
    *param_2 = (uint)*puVar4;
    param_2[1] = (uint)*(ushort *)(iVar3 + 0x437da0ae);
    param_2[2] = iVar3 + 0x437da0b0;
    param_2[4] = iVar3 + 0x437da1d8;
    iVar7 = (*pcVar8)(param_1,param_2,param_2,pcVar8,unaff_r4,unaff_r5,unaff_r6,unaff_lr);
    if (iVar7 == 0) {
      *(int *)(iVar3 + 0x437da304) = *(int *)(iVar3 + 0x437da304) + 1;
      return;
    }
    if (iVar7 == 2) {
      FUN_43af6860(puVar4);
      *(undefined4 *)(iVar3 + 0x437da1d4) = *(undefined4 *)(param_1[0x14] + 0xc);
      FUN_4378a048(iVar3 + 0x437da1d4);
      cVar2 = *(char *)(*(int *)(iVar9 + DAT_437da358) + 0x8d);
      if (cVar2 != '\0') {
        uVar5 = *param_1;
        uVar6 = FUN_437e0560(uVar5,0,0,cVar2,unaff_r4,unaff_lr);
        FUN_437e1d40(uVar5,uVar6);
        return;
      }
    }
  }
  return;
}


/* 43ae7564 */

void FUN_43ae7564(undefined4 param_1,int param_2)

{
  if (*(char *)(param_2 + 0x14) != '\0') {
    FUN_4377fe14(0);
  }
  if (*(char *)(param_2 + 0x16) != '\0') {
    FUN_4377fe14(1,param_2);
  }
  if ((*(uint *)(param_2 + 0x14) & 0xff00ff00) != 0) {
    FUN_4377fea4(param_2);
    return;
  }
  return;
}


/* 43780080 */

void FUN_43780080(undefined4 *param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 *puVar2;
  char *pcVar3;
  
  if ((((*(short *)*param_1 == 0x13c) && (*(char *)(param_1[2] + 0x1ed) != '\0')) &&
      (iVar1 = FUN_43ae8d02(*(undefined4 *)(DAT_43780154 + 0x43780092 + DAT_43780158)), iVar1 != 0))
     && (*(char *)(param_1[0xc] + 0xc) != '\0')) {
    if ((*(char *)(DAT_4378015c + 0x437800ba) == '\0') && (param_3 != 0)) {
      *(char *)(DAT_4378015c + 0x437800ba) = '\x01';
      puVar2 = (undefined1 *)(DAT_43780160 + 0x437800d0);
      *puVar2 = 1;
      FUN_4377fe14(2,param_2,1,puVar2,param_4);
      FUN_43ae75e0(*(undefined2 *)(param_2 + 0x1e));
      goto LAB_43780124;
    }
  }
  pcVar3 = (char *)(DAT_43780184 + 0x4378014c);
  if (*pcVar3 == '\0') {
    if ((*(short *)*param_1 != 0x13c) &&
       (pcVar3 = (char *)(DAT_43780168 + 0x437800fe), *pcVar3 != '\0')) {
      FUN_43782b20(*(undefined2 *)
                    ((uint)*(byte *)(DAT_4378016c + 0x4378010a) * 0x28 + DAT_43780170 + 0x43780120))
      ;
      iVar1 = DAT_43780174;
      *pcVar3 = '\0';
      *(undefined4 *)(iVar1 + 0x43780120) = 0;
      FUN_4377fea4(param_2);
    }
  }
  else {
    FUN_43782b08();
    *pcVar3 = '\0';
    *(undefined4 *)(DAT_43780164 + 0x437800ec) = 1;
  }
LAB_43780124:
  if ((*(int *)(DAT_43780178 + 0x4378012a) != 0) &&
     (*(char *)((uint)*(byte *)(DAT_4378017c + 0x43780136) * 0x28 + DAT_43780180 + 0x43780141) !=
      '\0')) {
    *(int *)(DAT_43780178 + 0x4378012a) = 2;
    return;
  }
  return;
}


/* 4380db04 */

void FUN_4380db04(int *param_1,int param_2)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  char cVar7;
  uint uVar8;
  int iVar9;
  bool bVar10;
  undefined1 auStack_78 [20];
  undefined1 auStack_64 [20];
  undefined1 auStack_50 [20];
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  uVar6 = *(uint *)param_1[0x14];
  uVar8 = ((uint *)param_1[0x14])[1];
  iVar9 = DAT_4380ddd0 + 0x4380db20;
  if ((*(short *)*param_1 != 0x104) && (*(short *)*param_1 != 0x141)) {
    *(undefined1 *)(DAT_4380de00 + 0x4380dd4e) = 0;
    goto LAB_4380dd4e;
  }
  if (*(char *)(DAT_4380ddd4 + 0x4380db34) != '\0') goto LAB_4380dd4e;
  *(char *)(DAT_4380ddd4 + 0x4380db34) = '\x01';
  iVar2 = FUN_43a12c64();
  if (iVar2 != 0) goto LAB_4380ddbc;
  if (uVar8 == 0x404) {
    if (uVar6 == 0x69) {
LAB_4380ddb8:
      cVar7 = '\x01';
      goto LAB_4380dc24;
    }
    if (uVar6 < 0x6a) {
      if (uVar6 != 0x4e) {
        if (uVar6 < 0x4f) {
          if (uVar6 != 0xe) {
            if (uVar6 != 0x46) {
              bVar10 = uVar6 == 8;
              goto LAB_4380dba6;
            }
            goto LAB_4380ddb8;
          }
        }
        else if (uVar6 != 0x55) {
          if (uVar6 < 0x56) {
            bVar10 = uVar6 == 0x4f;
          }
          else {
            if (uVar6 == 0x56) goto LAB_4380ddb8;
            bVar10 = uVar6 == 0x57;
          }
          if (!bVar10) goto LAB_4380dbcc;
        }
        cVar7 = '\x03';
        goto LAB_4380dc24;
      }
    }
    else if (uVar6 != 0xc2) {
      if (uVar6 < 0xc3) {
        if ((uVar6 != 0xb7) && (uVar6 != 0xba)) {
          bVar10 = uVar6 == 0xb5;
LAB_4380dba6:
          if (!bVar10) goto LAB_4380dbcc;
        }
        goto LAB_4380ddb8;
      }
      if (uVar6 == 0xc6) {
        cVar7 = '\x04';
        goto LAB_4380dc24;
      }
      if (uVar6 < 199) {
        bVar10 = uVar6 == 0xc4;
      }
      else {
        if (uVar6 == 0xd3) {
          cVar7 = '\x06';
          goto LAB_4380dc24;
        }
        bVar10 = uVar6 == 0xec;
      }
      if (!bVar10) goto LAB_4380dbcc;
    }
LAB_4380ddbc:
    cVar7 = '\x02';
LAB_4380dc24:
    bVar10 = false;
  }
  else {
    if ((uVar8 == 0x4c0) && (uVar6 == 3)) {
      cVar7 = '\b';
      goto LAB_4380dc24;
    }
LAB_4380dbcc:
    iVar2 = FUN_437fc65c();
    if (iVar2 == 0x21) goto LAB_4380ddbc;
    if (iVar2 < 0x22) {
      if (iVar2 - 0xcU < 3) {
        if (*(char *)(*param_1 + 0x40b) == '\0') {
          cVar7 = '\x01';
        }
        else {
          cVar7 = '\x05';
        }
      }
      else {
LAB_4380dc00:
        cVar7 = *(char *)(*(int *)(iVar9 + DAT_4380ddd8) + 2);
        if ((cVar7 != '\x03') && (cVar7 != '\x02')) {
          if (cVar7 == '\x04') {
            cVar7 = '\x04';
          }
          else {
            cVar7 = '\x01';
          }
        }
      }
      goto LAB_4380dc24;
    }
    if (iVar2 != 0x5e) {
      if ((iVar2 != 0x60) && (iVar2 != 0x51)) goto LAB_4380dc00;
      goto LAB_4380ddbc;
    }
    if (*(char *)(param_1[3] + 0x7e) == '\0') {
      cVar7 = '\a';
      goto LAB_4380dc24;
    }
    cVar7 = '\a';
    bVar10 = true;
  }
  if ((*(char *)(*(int *)(iVar9 + DAT_4380dddc) + 0x69) == '\0') && (bVar10)) goto LAB_4380dd4e;
  FUN_43afb43a(&uStack_3c,0);
  switch(cVar7) {
  case '\x03':
  case '\b':
    iVar2 = DAT_4380dde0 + 0x4380dc5e;
    break;
  case '\x04':
    iVar2 = DAT_4380dde4 + 0x4380dc66;
    break;
  case '\x05':
    iVar2 = *(int *)(iVar9 + DAT_4380dde8);
    break;
  case '\x06':
    FUN_43b0394a(param_1,param_2);
    iVar2 = DAT_4380ddec + 0x4380dc80;
    break;
  default:
    iVar2 = DAT_4380ddf0 + 0x4380dc88;
  }
  FUN_43afb452(&uStack_3c,iVar2);
  uVar3 = FUN_437e0014(cVar7,uStack_3c,uStack_38,uStack_34,uStack_30,uStack_2c);
  uVar4 = FUN_43804de8();
  if (uVar6 == 0x46) {
LAB_4380dcbe:
    uVar5 = 1;
  }
  else {
    if (uVar6 < 0x47) {
      bVar10 = uVar6 == 8;
    }
    else {
      if (uVar6 == 0x55) goto LAB_4380dcbe;
      bVar10 = uVar6 == 0xba;
    }
    if (bVar10) goto LAB_4380dcbe;
    uVar5 = 0;
  }
  if (*(short *)*param_1 == 0x141) {
    uVar5 = 1;
  }
  candidate_437dfd58(uVar3,uVar4,uVar5,0,0);
  iVar2 = candidate_437dfe4c(uVar3);
  *(undefined4 *)(iVar2 + 0xa4) = 0;
  *(undefined4 *)(iVar2 + 0x90) = 0;
  *(undefined4 *)(iVar2 + 0xa8) = 1;
  *(undefined4 *)(iVar2 + 0x94) = 1;
  uVar4 = FUN_437de2fc();
  FUN_43b00b1e(auStack_50,*(undefined4 *)(iVar9 + DAT_4380ddf4));
  FUN_439018b0(uVar4,auStack_50,1,0);
  FUN_43ada220(auStack_64,*(undefined4 *)(iVar9 + DAT_4380ddf8));
  FUN_439018b0(uVar4,auStack_64,uVar3,0);
  FUN_43ada220(auStack_78,*(undefined4 *)(iVar9 + DAT_4380ddfc));
  FUN_439018b0(uVar4,auStack_78,uVar3,0);
LAB_4380dd4e:
  if (((uVar6 == 0) && (*(short *)(DAT_4380de04 + 0x4380dd56) != -1)) &&
     (*(short *)(*param_1 + 0x10) == 0xa00)) {
    FUN_4380d894();
  }
  iVar9 = DAT_4380de08;
  uVar1 = *(undefined2 *)(DAT_4380de08 + 0x4380dd72);
  *(undefined4 *)(param_2 + 0x30) = *(undefined4 *)(DAT_4380de08 + 0x4380dd76);
  uVar3 = *(undefined4 *)(iVar9 + 0x4380dd7a);
  *(undefined2 *)(param_2 + 0x2e) = uVar1;
  *(undefined4 *)(param_2 + 0x34) = uVar3;
  *(undefined4 *)(param_2 + 0x38) = *(undefined4 *)(iVar9 + 0x4380dd7e);
  *(undefined4 *)(param_2 + 0x3c) = *(undefined4 *)(iVar9 + 0x4380dd82);
  *(undefined4 *)(param_2 + 0x40) = *(undefined4 *)(iVar9 + 0x4380dd86);
  uVar3 = *(undefined4 *)(iVar9 + 0x4380dd8e);
  *(undefined4 *)(param_2 + 0x44) = *(undefined4 *)(iVar9 + 0x4380dd8a);
  *(undefined4 *)(param_2 + 0x48) = uVar3;
  if (*(short *)*param_1 == 0x147) {
    if (*(char *)(DAT_4380de0c + 0x4380dda2) == '\0') {
      *(char *)(DAT_4380de0c + 0x4380dda2) = '\x01';
      FUN_437dfd28();
    }
  }
  else {
    *(undefined1 *)(DAT_4380de10 + 0x4380ddb6) = 0;
  }
  return;
}

