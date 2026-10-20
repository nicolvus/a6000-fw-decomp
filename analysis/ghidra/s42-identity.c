/* S41: read-only exports. */

/* 436d6320 */

undefined4 FUN_436d6320(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    iVar2 = DAT_436d6354 + 0x436d6332;
    FUN_436d6020(0xbc,0,1,DAT_436d6350 + 0x436d6330,iVar2,0);
    FUN_43902718(DAT_436d6358 + 0x436d633e,iVar2);
    uVar1 = 1;
  }
  else {
    uVar1 = (**(code **)(*(int *)*param_1 + 0x28))();
  }
  return uVar1;
}


/* 436d6f6c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d6f6c(int param_1,ushort *param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  undefined1 uVar4;
  byte bVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  ushort *puVar10;
  byte bVar11;
  int iVar12;
  short sVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  undefined4 in_stack_ffffffa0;
  undefined2 uVar20;
  
  iVar7 = _DAT_436d72a0;
  uVar20 = (undefined2)((uint)in_stack_ffffffa0 >> 0x10);
  iVar18 = _DAT_436d7298 + 0x436d6f84;
  if (*(int *)(param_1 + 0x170) == 0x11) {
    iVar7 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar7 != 0) {
      FUN_436d6738(0xbc,0,3,_DAT_436d729c + 0x436d6fa6,*(undefined4 *)(param_1 + 0x170));
    }
    return 2;
  }
  uVar1 = param_2[2];
  uVar17 = (uint)uVar1;
  uVar2 = *param_2;
  uVar16 = (uint)uVar2;
  uVar3 = param_2[3];
  uVar4 = *(undefined1 *)((int)param_2 + 9);
  *(uint *)(param_1 + 0x3a8) = uVar17;
  iVar8 = *(int *)(iVar18 + _DAT_436d72a4);
  iVar19 = *(int *)(iVar18 + _DAT_436d72a8);
  iVar12 = *(int *)(iVar18 + _DAT_436d72ac);
  iVar14 = *(int *)(iVar18 + _DAT_436d72b0);
  iVar15 = *(int *)(iVar18 + _DAT_436d72b4);
  *(char *)(*(int *)(iVar18 + iVar7) + 2) = (char)uVar1;
  bVar11 = (byte)(uVar1 >> 8) & 0xf;
  *(byte *)(iVar8 + 2) = *(byte *)(iVar8 + 2) & 0xf0 | bVar11;
  bVar5 = (byte)(uVar2 >> 8) & 0x3f;
  *(char *)(iVar19 + 2) = (char)uVar2;
  bVar6 = (byte)(uVar3 >> 8) & 0xf;
  *(byte *)(iVar12 + 2) = *(byte *)(iVar12 + 2) & 0xc0 | bVar5;
  *(char *)(iVar14 + 2) = (char)uVar3;
  *(byte *)(iVar15 + 2) = *(byte *)(iVar15 + 2) & 0xf0 | bVar6;
  if (*(char *)(*(int *)(iVar18 + _DAT_436d72b8) + 0x7f) != -1) {
    iVar15 = *(int *)(iVar18 + _DAT_436d72c0);
    iVar8 = *(int *)(iVar18 + _DAT_436d72c4);
    iVar7 = *(int *)(iVar18 + _DAT_436d72c8);
    iVar12 = *(int *)(iVar18 + _DAT_436d72cc);
    iVar14 = *(int *)(iVar18 + _DAT_436d72d0);
    *(char *)(*(int *)(iVar18 + _DAT_436d72bc) + 2) = (char)uVar1;
    *(byte *)(iVar15 + 2) = *(byte *)(iVar15 + 2) & 0xf0 | bVar11;
    *(char *)(iVar8 + 2) = (char)uVar2;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xc0 | bVar5;
    *(char *)(iVar12 + 2) = (char)uVar3;
    *(byte *)(iVar14 + 2) = *(byte *)(iVar14 + 2) & 0xf0 | bVar6;
  }
  iVar7 = FUN_436d8a74(param_1 + 0x18,*(undefined4 *)(param_1 + 0x170));
  if (iVar7 != 0) {
    *(ushort *)(param_1 + 0x10) = uVar1;
    *(ushort *)(param_1 + 0x12) = uVar2;
  }
  iVar7 = *(int *)(iVar18 + _DAT_436d72d4);
  switch(uVar4) {
  case 0:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xfb;
    bVar11 = *(byte *)(iVar7 + 2) & 0x7f;
    break;
  case 1:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xef;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
    iVar7 = FUN_436d6f34(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
    uVar9 = uVar16 * (*(uint *)(iVar7 + 4) >> 8);
    goto code_r0x436d719e;
  case 2:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x10;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xbf;
    *(char *)(*(int *)(iVar18 + _UNK_436d72d8) + 2) = (char)param_2[4];
    *(char *)(*(int *)(iVar18 + _UNK_436d72dc) + 2) = (char)param_2[10];
    iVar7 = FUN_436d6f34(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
    sVar13 = FUN_4355faf0(*(uint *)(iVar7 + 4) >> 8,1000);
    sVar13 = uVar2 * sVar13 + 1 + (short)(((byte)param_2[10] + 1) * 0x26aa >> 0x10);
    goto code_r0x436d71e0;
  case 3:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x10;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
    uVar9 = (uint)param_2[8];
code_r0x436d719e:
    sVar13 = FUN_4355faf0(uVar9,1000);
    *(short *)(param_1 + 0x3a0) = sVar13 + 1;
    goto code_r0x436d71e4;
  case 4:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xfb;
    bVar11 = *(byte *)(iVar7 + 2) | 0x80;
    break;
  default:
    return 1;
  }
  *(byte *)(iVar7 + 2) = bVar11;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xef;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
  puVar10 = (ushort *)
            func_0x436d6f50(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
  sVar13 = (*puVar10 >> 8) + 1;
code_r0x436d71e0:
  *(short *)(param_1 + 0x3a0) = sVar13;
code_r0x436d71e4:
  iVar18 = param_1 + 0xfc;
  FUN_43ad9a40(iVar18,uVar17,uVar16,uVar3,uVar4,0);
  FUN_43ad99d4(iVar18,*(undefined4 *)(param_1 + 0x14c),*(undefined4 *)(param_1 + 0x150),
               *(undefined4 *)(param_1 + 0x154),*(undefined4 *)(param_1 + 0x158),
               *(undefined4 *)(param_1 + 0x15c),
               CONCAT22(uVar20,(short)*(undefined4 *)(param_1 + 0x160)));
  iVar7 = FUN_436d9f70(iVar18,1);
  if (iVar7 != 0) {
    iVar7 = *(int *)(param_1 + 0x174);
    if ((iVar7 != *(int *)(param_1 + 0x170)) || (*(int *)(param_1 + 0x178) != iVar7)) {
      FUN_436d6738(0xbc,0,3,&UNK_436d7246 + _UNK_436d72e0,*(int *)(param_1 + 0x178),iVar7,
                   *(int *)(param_1 + 0x170),uVar17,uVar16,uVar3,uVar4);
    }
  }
  iVar7 = FUN_436d9f70(iVar18,8);
  if (iVar7 != 0) {
    FUN_436d6738(0xbc,0,3,&UNK_436d7284 + _UNK_436d72e4,*(undefined4 *)(param_1 + 0x178),
                 *(undefined4 *)(param_1 + 0x174),*(undefined4 *)(param_1 + 0x170),uVar17,uVar16,
                 uVar3,uVar4);
  }
  return 0;
}


/* 43842158 */

void FUN_43842158(int param_1,int param_2,int param_3,int param_4)

{
  char cVar1;
  ushort uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  
  uVar2 = *(ushort *)(param_3 + 0x4bc);
  iVar8 = DAT_43842340 + 0x43842170;
  if (((uVar2 & 0x60) == 0) && ((uVar2 & 0x80) == 0)) {
    if (*(int *)(param_3 + 0x41c) == 1) {
      uVar3 = 1;
      if (*(char *)(param_4 + 2) == '\0') {
        if (*(ushort *)(param_2 + 0x162) <= **(ushort **)(iVar8 + DAT_43842350)) {
          iVar5 = DAT_43842358 + 0x438421c4;
          goto LAB_438421e6;
        }
        iVar5 = DAT_43842354 + 0x438421be;
      }
      else if (*(char *)(param_4 + 2) == '\x01') {
        if (*(char *)(param_3 + 0x38c) != '\x01') {
          iVar5 = DAT_43842360 + 0x438421dc;
          goto LAB_438421e6;
        }
        iVar5 = DAT_4384235c + 0x438421d6;
        uVar3 = 1;
      }
      else {
        iVar5 = DAT_43842364 + 0x438421e2;
      }
    }
    else {
      iVar5 = DAT_43842368 + 0x438421e8;
LAB_438421e6:
      uVar3 = 3;
    }
  }
  else if (((uVar2 & 0x20) == 0) ||
          ((uVar2 = *(ushort *)(*(int *)(iVar8 + DAT_43842344) + 0xb0), uVar2 == 0 ||
           (*(ushort *)(param_2 + 0x162) <= uVar2)))) {
    uVar3 = 1;
    iVar5 = DAT_4384234c + 0x4384219e;
  }
  else {
    uVar3 = 5;
    iVar5 = DAT_43842348 + 0x43842196;
  }
  *(undefined4 *)(iVar5 + 0x60) = uVar3;
  iVar5 = *(int *)(iVar8 + DAT_4384236c);
  cVar1 = *(char *)(iVar5 + 0x7e);
  if (cVar1 != '\0') {
    if (cVar1 == '\x01') {
      uVar3 = 0;
      iVar6 = DAT_43842370 + 0x43842204;
    }
    else if (cVar1 == '\x02') {
      iVar6 = DAT_43842374 + 0x4384220e;
LAB_4384225a:
      uVar3 = 1;
    }
    else if (cVar1 == '\x03') {
      uVar3 = 2;
      iVar6 = DAT_43842378 + 0x4384221a;
    }
    else if (cVar1 == '\x04') {
      uVar3 = 3;
      iVar6 = DAT_4384237c + 0x43842226;
    }
    else if (cVar1 == '\x05') {
      uVar3 = 4;
      iVar6 = DAT_43842380 + 0x43842232;
    }
    else if (cVar1 == '\x06') {
      uVar3 = 5;
      iVar6 = DAT_43842384 + 0x4384223e;
    }
    else if (cVar1 == '\a') {
      uVar3 = 6;
      iVar6 = DAT_43842388 + 0x4384224a;
    }
    else {
      if (cVar1 != '\b') {
        iVar6 = DAT_43842390 + 0x4384225c;
        goto LAB_4384225a;
      }
      uVar3 = 7;
      iVar6 = DAT_4384238c + 0x43842256;
    }
    *(undefined4 *)(iVar6 + 0x60) = uVar3;
  }
  if ((*(char *)(param_4 + 2) != '\x01') || (uVar4 = 1, *(char *)(param_3 + 0x38c) != '\0')) {
    uVar4 = 0;
  }
  FUN_43841aac(uVar4);
  if (*(int *)(param_3 + 0x41c) == 1) {
    iVar6 = DAT_43842394 + 0x4384227e;
LAB_43842290:
    *(undefined1 *)(iVar6 + 100) = 1;
  }
  else {
    iVar6 = DAT_43842398 + 0x43842286;
    *(undefined1 *)(DAT_43842398 + 0x438422ea) = 0;
    if (*(char *)(iVar5 + 0x10f) == '\x01') goto LAB_43842290;
  }
  if (((*(char *)(iVar5 + 0xf9) != '\x01') ||
      (iVar6 = DAT_4384239c + 0x438422a2, *(int *)(DAT_4384239c + 0x43842302) != 3)) ||
     (uVar4 = 1, *(ushort *)(param_2 + 0x162) < *(ushort *)(iVar5 + 0xfc))) {
    uVar4 = 0;
    iVar6 = DAT_438423a0 + 0x438422ba;
  }
  *(undefined1 *)(iVar6 + 0x65) = uVar4;
  iVar5 = DAT_438423a4;
  if (*(char *)(param_1 + 0x36) == '\x01') {
    *(undefined1 *)(DAT_438423a4 + 0x43842331) = 0;
    *(undefined1 *)(iVar5 + 0x43842330) = 0;
    uVar7 = (uint)*(byte *)(param_1 + 0x37);
    if (uVar7 == 0) {
      *(undefined4 *)(iVar5 + 0x4384232c) = 1;
    }
    else {
      if (uVar7 == 1) {
        uVar7 = 3;
      }
      else if (uVar7 != 2) {
        if (uVar7 == 3) {
          *(undefined4 *)(iVar5 + 0x4384232c) = 0;
          goto LAB_43842306;
        }
        if (((uVar7 != 4) && (uVar7 != 5)) && (uVar7 != 6)) {
          if (uVar7 == 7) {
            uVar7 = 7;
          }
          else {
            uVar7 = 1;
          }
        }
      }
      *(uint *)(iVar5 + 0x4384232c) = uVar7;
    }
  }
LAB_43842306:
  iVar5 = DAT_438423a8;
  uVar4 = *(undefined1 *)((int)&DAT_4384236c + DAT_438423a8 + 2);
  *(undefined1 *)(*(int *)(iVar8 + DAT_438423ac) + 0x9b4) = uVar4;
  **(undefined1 **)(iVar8 + DAT_438423b0) = uVar4;
  **(undefined1 **)(iVar8 + DAT_438423b4) = (char)*(undefined4 *)(param_3 + 0x41c);
  uVar4 = *(undefined1 *)((int)&DAT_43842370 + iVar5 + 3);
  **(undefined1 **)(iVar8 + DAT_438423b8) = *(undefined1 *)((int)&DAT_43842370 + iVar5 + 2);
  **(undefined1 **)(iVar8 + DAT_438423bc) = uVar4;
  return;
}


/* 438c828c */

undefined4 FUN_438c828c(int param_1)

{
  undefined2 uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  bool bVar9;
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [24];
  
  FUN_43ae769a(param_1,0xe);
  uVar2 = FUN_437f8a50(param_1);
  iVar6 = DAT_438c8460 + 0x438c82a6;
  iVar3 = FUN_43a12c64();
  if ((iVar3 == 2) || (iVar3 = FUN_43a12c64(), iVar3 == 3)) {
    *(undefined1 *)(param_1 + 0x655) = 0;
    *(undefined2 *)(param_1 + 0x650) = 0;
    *(undefined4 *)(param_1 + 0x64c) = 2;
    *(undefined2 *)(param_1 + 0x652) = 0;
    *(undefined1 *)(param_1 + 0x654) = 0;
  }
  if (*(int *)(param_1 + 0x4b9c) == 0) {
    FUN_43b1e520(param_1);
    uVar1 = *(undefined2 *)(param_1 + 0x650);
    if (*(int *)(param_1 + 0x504) == 1) {
      *(undefined2 *)(param_1 + 0x650) = 0;
    }
    *(undefined2 *)(param_1 + 0x6b8) = *(undefined2 *)(param_1 + 0x12f8);
    uVar4 = FUN_436d6118();
    FUN_436d6320(uVar4,param_1 + 0x64c,*(undefined2 *)(param_1 + 0x4b9c));
    uVar4 = FUN_436d6118();
    FUN_436d6398(uVar4,param_1 + 0x6bc,*(undefined2 *)(param_1 + 0x4b9c));
    FUN_436d6118();
    FUN_43ad9116();
    uVar4 = FUN_436d6118();
    FUN_43ad911c(uVar4,1);
    *(undefined2 *)(param_1 + 0x650) = uVar1;
  }
  else {
    uVar4 = FUN_436d6118();
    FUN_43ad911c(uVar4,0);
  }
  uVar4 = *(undefined4 *)(param_1 + 0x570);
  if (*(int *)(param_1 + 0x740) == 0) {
    iVar3 = FUN_43a12c64();
    if (iVar3 != 3) {
      iVar7 = *(int *)(param_1 + 0x56c);
      FUN_436d6118();
      iVar3 = FUN_43ad90b6();
      FUN_436c2270();
      uVar5 = FUN_436c28d0();
      iVar3 = DAT_438c845c * (iVar3 + 1);
      uVar5 = FUN_4355faf0(iVar7 * 1000,uVar5);
      uVar5 = FUN_4355faf0(iVar3,uVar5);
      *(undefined4 *)(param_1 + 0x570) = uVar5;
    }
  }
  else if (*(char *)(param_1 + 0x60c) == '\0') {
    *(uint *)(param_1 + 0x570) = uVar2 & 0xffff;
  }
  FUN_43901a8c(2,0x107,(uint)*(ushort *)(param_1 + 0x4b64) | *(int *)(param_1 + 0x1d8) << 0x10,
               *(uint *)(param_1 + 0x56c) | *(int *)(param_1 + 0x570) << 0x10);
  if (((*(int *)(param_1 + 0x740) == 0) &&
      (*(undefined2 *)(param_1 + 0x650) = 0, *(char *)(param_1 + 0x4b84) == '\0')) &&
     (*(char *)(param_1 + 0x74f) != '\0')) {
    if (*(char *)(*(int *)(iVar6 + DAT_438c8464) + 0x60) == '\0') {
      uVar5 = 4;
    }
    else {
      uVar5 = 3;
    }
  }
  else {
    uVar5 = 3;
  }
  if (*(int *)(param_1 + 0x4b9c) == 0) {
    FUN_436d6118();
    FUN_43ad9132();
  }
  iVar3 = DAT_438c846c;
  if (*(int *)(param_1 + 0x740) == 0) {
    iVar3 = DAT_438c8468;
  }
  uVar8 = *(undefined4 *)(iVar6 + iVar3);
  if (*(int *)(param_1 + 0x504) == 1) {
    bVar9 = *(int *)(param_1 + 0x4b9c) != 0;
  }
  else {
    bVar9 = false;
  }
  FUN_43acac1a(auStack_34,*(undefined4 *)(iVar6 + DAT_438c8470));
  FUN_43acac1a(auStack_48,uVar8);
  FUN_43795dec(uVar5,param_1 + 0x548,bVar9,auStack_34,auStack_48);
  *(undefined4 *)(param_1 + 0x570) = uVar4;
  return 1;
}


/* 4380f440 */

void FUN_4380f440(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  iVar1 = DAT_4380f4fc;
  puVar2 = (uint *)(DAT_4380f4f0 + 0x4380f452);
  if ((*puVar2 & 1) == 0) {
    FUN_43afb46a(&uStack_3c,*(undefined4 *)(DAT_4380f4f4 + 0x4380f45a + DAT_4380f4f8));
    FUN_43b03a2e(&uStack_50);
    FUN_43afb43a(&uStack_64,0);
    FUN_439c5a04(iVar1 + 0x4380f47e,0,0x44);
    *(undefined4 *)(iVar1 + 0x4380f482) = uStack_3c;
    *(undefined4 *)(iVar1 + 0x4380f486) = uStack_38;
    *(undefined4 *)(iVar1 + 0x4380f48a) = uStack_34;
    *(undefined4 *)(iVar1 + 0x4380f48e) = uStack_30;
    *(undefined4 *)(iVar1 + 0x4380f492) = uStack_2c;
    *(undefined4 *)(iVar1 + 0x4380f49a) = uStack_50;
    *(undefined4 *)(iVar1 + 0x4380f49e) = uStack_4c;
    *(undefined4 *)(iVar1 + 0x4380f4a2) = uStack_48;
    *(undefined4 *)(iVar1 + 0x4380f4a6) = uStack_44;
    *(undefined4 *)(iVar1 + 0x4380f4aa) = uStack_40;
    *(undefined4 *)(iVar1 + 0x4380f4ae) = uStack_64;
    *(undefined4 *)(iVar1 + 0x4380f4b2) = uStack_60;
    *(undefined4 *)(iVar1 + 0x4380f4b6) = uStack_5c;
    *(undefined4 *)(iVar1 + 0x4380f4ba) = uStack_58;
    *(undefined4 *)(iVar1 + 0x4380f4be) = uStack_54;
    *puVar2 = 1;
  }
  iVar1 = FUN_437c1d38(*(undefined2 *)(*param_1 + 4));
  if ((iVar1 == 0) || (*(int *)(DAT_4380f500 + 0x4380f4d2) == 0)) {
    FUN_4380e43c(param_1,param_3,param_4);
  }
  FUN_439c5320(param_2,DAT_4380f504 + 0x4380f4e8,0x44);
  return;
}


/* 4380e43c */

void FUN_4380e43c(int *param_1,int param_2,int param_3)

{
  char cVar1;
  undefined1 *puVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  int *piVar9;
  undefined4 *puVar10;
  bool bVar11;
  short *psVar12;
  int iVar13;
  int iVar14;
  bool bVar15;
  undefined4 auStack_348 [5];
  undefined4 uStack_334;
  undefined4 uStack_330;
  undefined4 uStack_32c;
  undefined4 uStack_328;
  undefined4 uStack_324;
  undefined4 auStack_320 [5];
  undefined4 uStack_30c;
  undefined4 uStack_308;
  undefined4 uStack_304;
  undefined4 uStack_300;
  undefined4 uStack_2fc;
  undefined4 auStack_2f8 [5];
  undefined4 uStack_2e4;
  undefined4 uStack_2e0;
  undefined4 uStack_2dc;
  undefined4 uStack_2d8;
  undefined4 uStack_2d4;
  undefined4 auStack_2d0 [5];
  undefined4 uStack_2bc;
  undefined4 uStack_2b8;
  undefined4 uStack_2b4;
  undefined4 uStack_2b0;
  undefined4 uStack_2ac;
  undefined4 auStack_2a8 [5];
  undefined4 uStack_294;
  undefined4 uStack_290;
  undefined4 uStack_28c;
  undefined4 uStack_288;
  undefined4 uStack_284;
  undefined4 auStack_280 [5];
  undefined4 uStack_26c;
  undefined4 uStack_268;
  undefined4 uStack_264;
  undefined4 uStack_260;
  undefined4 uStack_25c;
  undefined4 auStack_258 [5];
  undefined4 uStack_244;
  undefined4 uStack_240;
  undefined4 uStack_23c;
  undefined4 uStack_238;
  undefined4 uStack_234;
  undefined4 auStack_230 [10];
  undefined4 auStack_208 [5];
  undefined4 auStack_1f4 [5];
  undefined4 auStack_1e0 [5];
  undefined4 auStack_1cc [5];
  undefined4 auStack_1b8 [10];
  undefined4 auStack_190 [5];
  undefined4 auStack_17c [5];
  undefined4 auStack_168 [5];
  undefined4 auStack_154 [5];
  undefined4 auStack_140 [5];
  undefined4 auStack_12c [5];
  undefined4 auStack_118 [4];
  undefined4 uStack_108;
  undefined4 uStack_104;
  undefined4 uStack_100;
  undefined4 uStack_fc;
  undefined4 uStack_f8;
  undefined4 uStack_f4;
  undefined4 auStack_f0 [4];
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined4 auStack_c8 [4];
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined4 uStack_b0;
  undefined4 uStack_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined4 auStack_a0 [4];
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 auStack_78 [4];
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 auStack_50 [4];
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  psVar12 = (short *)(DAT_4380ef3c + 0x4380e452);
  iVar8 = DAT_4380ef40 + 0x4380e45c;
  if ((*(short *)*param_1 != *psVar12) &&
     ((*(byte *)(*(int *)(iVar8 + DAT_4380ef44) + 0x2a) & 1) != 0)) {
    uVar3 = FUN_43ae0c38();
    *(undefined1 *)(DAT_4380ef48 + 0x4380e47e) = uVar3;
    *psVar12 = *(short *)*param_1;
  }
  iVar13 = *param_1;
  uVar4 = FUN_43b039e6(param_1);
  uVar4 = FUN_4380df30(iVar13,uVar4,0);
  iVar13 = param_1[2];
  iVar5 = *param_1;
  *(undefined4 *)(param_2 + 0x218) = uVar4;
  iVar13 = FUN_437c1be4(*(undefined4 *)(iVar5 + 0x2c4),*(undefined4 *)(iVar5 + 0x398),
                        *(undefined4 *)(iVar5 + 0x394),(*(byte *)(iVar13 + 0x268) & 0xf) >> 3,
                        (*(uint *)(iVar13 + 0x264) & 0xfffff) >> 0xf == 7);
  bVar11 = iVar13 == 1 || iVar13 == 3;
  bVar15 = *(int *)(*param_1 + 0x354) == 2;
  if (param_3 == 0) {
    uVar4 = FUN_437fe4f4();
    **(undefined4 **)(iVar8 + DAT_4380ef4c) = uVar4;
    uVar3 = FUN_43728564();
    *(undefined1 *)(DAT_4380ef50 + 0x4380e512) = uVar3;
  }
  iVar6 = param_1[2];
  iVar5 = *(int *)(iVar6 + 0x20c);
  switch((*(uint *)(iVar6 + 0x264) & 0xfffff) >> 0xf) {
  case 0:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_43794a44(param_1);
    if (iVar13 == 0) {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380ef58 + 0x4380e598));
      *(undefined4 *)(DAT_4380ef5c + 0x4380e5a4) = uVar4;
    }
    else {
      *(undefined4 *)(DAT_4380ef54 + 0x4380e58a) = 0xf;
    }
    piVar9 = (int *)(DAT_4380ef60 + 0x4380e5ae);
    iVar13 = FUN_4380de20(param_3,*piVar9);
    *piVar9 = iVar13;
    iVar13 = FUN_43794a44(param_1);
    if (iVar13 != 0) {
      puVar7 = auStack_348;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380ef64));
      FUN_4380e2a8(&uStack_334);
      goto LAB_4380f390;
    }
    goto LAB_4380ea46;
  case 1:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    piVar9 = (int *)(DAT_4380ef6c + 0x4380e620);
    uVar3 = *(undefined1 *)(DAT_4380ef68 + 0x4380e61e);
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_4380de60(param_1,bVar11,uVar3);
    *piVar9 = iVar13;
    FUN_4380dfe4(piVar9);
    iVar13 = FUN_4380de20(param_3,*piVar9);
    goto LAB_4380e772;
  case 2:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = *param_1;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_4386be30(*(undefined4 *)(iVar13 + 0x2c4),*(undefined4 *)(iVar13 + 0x398),
                          *(undefined4 *)(iVar13 + 0x394),0,1);
    if ((iVar13 == 1) || (*(char *)(param_1[0x14] + 0x2c) != '\0')) {
      puVar7 = (undefined4 *)(DAT_4380ef70 + 0x4380e690);
LAB_4380e6f4:
      uVar4 = 1;
LAB_4380e6c0:
      *puVar7 = uVar4;
    }
    else {
      if (iVar13 == 2) {
        if (*(char *)(param_1[0xe] + 0x84) != '\0') {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x44);
          if (iVar13 != 0) {
            uVar4 = 0x44;
            puVar7 = (undefined4 *)(DAT_4380f424 + 0x4380f344);
            goto LAB_4380e6c0;
          }
        }
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,3);
        if (iVar13 == 0) {
          if ((*(int *)(DAT_4380ef78 + 0x4380e6cc) != 1) &&
             (*(int *)(DAT_4380ef78 + 0x4380e6cc) != 0x30)) {
            FUN_4380e020(3,9,1,DAT_4380ef7c + 0x4380e6e2);
            FUN_43902718(DAT_4380ef80 + 0x4380e6ec);
          }
          puVar7 = (undefined4 *)(DAT_4380ef84 + 0x4380e6f6);
          goto LAB_4380e6f4;
        }
        puVar7 = (undefined4 *)(DAT_4380ef74 + 0x4380e6c0);
LAB_4380e6be:
        uVar4 = 3;
        goto LAB_4380e6c0;
      }
      if (iVar13 - 3U < 2) {
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x39);
        if (iVar13 != 0) {
          uVar4 = 0x39;
          puVar7 = (undefined4 *)(DAT_4380ef88 + 0x4380e714);
          goto LAB_4380e6c0;
        }
        *(undefined4 *)(DAT_4380ef8c + 0x4380e71c) = 1;
      }
      else {
        if ((*(int *)(*(int *)(iVar8 + DAT_4380ef90) + 0x3c) == 0) &&
           (*(int *)(*param_1 + 0x2c4) != 0)) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,3);
          if (iVar13 != 0) {
            puVar7 = (undefined4 *)(DAT_4380f428 + 0x4380f34c);
            goto LAB_4380e6be;
          }
        }
        uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380ef94 + 0x4380e74e));
        *(undefined4 *)(DAT_4380ef98 + 0x4380e75a) = uVar4;
      }
    }
    piVar9 = (int *)(DAT_4380ef9c + 0x4380e764);
    uVar4 = FUN_4380de20(param_3,*piVar9);
    iVar13 = FUN_43b03958(iVar5 != 0,uVar4);
LAB_4380e772:
    *piVar9 = iVar13;
LAB_4380ea46:
    iVar13 = *param_1;
    goto LAB_4380eace;
  case 3:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = DAT_4380ef90;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(*(int *)(iVar8 + iVar13) + 0x3c) == 0) {
      uVar4 = FUN_436d6118();
      iVar5 = FUN_43ad909c(uVar4,3);
      iVar13 = DAT_4380efa8;
      if ((iVar5 == 0) || (*(char *)(*(int *)(iVar8 + DAT_4380efa0) + 0x88) == '\x01')) {
        uVar4 = 1;
        puVar7 = (undefined4 *)(DAT_4380f42c + 0x4380f356);
      }
      else {
        uVar4 = 3;
        puVar7 = (undefined4 *)(DAT_4380efa4 + 0x4380e7cc);
      }
      *puVar7 = uVar4;
      puVar7 = (undefined4 *)(iVar13 + 0x4380e7d4);
      FUN_4380dfe4(puVar7);
      uVar4 = FUN_4380de20(param_3,*puVar7);
      *puVar7 = uVar4;
    }
    else {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380efac + 0x4380e7f4));
      *(undefined4 *)(DAT_4380efb0 + 0x4380e800) = uVar4;
    }
    iVar13 = *param_1;
    piVar9 = (int *)(DAT_4380efb4 + 0x4380e810);
    goto LAB_4380eace;
  case 4:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = DAT_4380ef90;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(*(int *)(iVar8 + iVar13) + 0x3c) == 0) {
      puVar7 = (undefined4 *)(DAT_4380efb8 + 0x4380e844);
      *puVar7 = 1;
      FUN_4380dfe4(puVar7);
      uVar4 = FUN_4380de20(param_3,*puVar7);
      *puVar7 = uVar4;
    }
    else {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380efbc + 0x4380e868));
      *(undefined4 *)(DAT_4380efc0 + 0x4380e874) = uVar4;
    }
    iVar13 = *param_1;
    piVar9 = (int *)(DAT_4380efc4 + 0x4380e884);
    goto LAB_4380eace;
  case 5:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    iVar14 = *(int *)(iVar8 + DAT_4380ef44);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(iVar14 + 0x44));
    iVar13 = *param_1;
    iVar6 = param_1[3];
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_4386be30(*(undefined4 *)(iVar13 + 0x2c4),*(undefined4 *)(iVar13 + 0x398),
                          *(undefined4 *)(iVar13 + 0x394),*(undefined4 *)(iVar6 + 0xc),0);
    if (iVar13 == 1) {
      iVar13 = FUN_4380dfb4(param_1[3],*(undefined1 *)(DAT_4380efc8 + 0x4380e8d2),param_3);
      if (iVar13 != 0) {
        uVar4 = FUN_4380df00();
        puVar7 = (undefined4 *)(DAT_4380efcc + 0x4380e8e4);
        goto LAB_4380e9b8;
      }
      *(undefined4 *)(DAT_4380efd0 + 0x4380e8ec) = 1;
    }
    else {
      if (iVar13 == 2) {
        if (*(char *)(param_1[0xe] + 0x84) == '\0') {
LAB_4380e90c:
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,3);
          if (iVar13 == 0) {
            if ((*(int *)(DAT_4380efd8 + 0x4380e92c) != 1) &&
               (*(int *)(DAT_4380efd8 + 0x4380e92c) != 0x30)) {
              FUN_4380e020(3,9,1,DAT_4380efdc + 0x4380e942);
              FUN_43902718(DAT_4380efe0 + 0x4380e94c);
            }
            puVar7 = (undefined4 *)(DAT_4380efe4 + 0x4380e956);
            goto LAB_4380e99c;
          }
          uVar4 = 3;
          puVar7 = (undefined4 *)(DAT_4380efd4 + 0x4380e922);
        }
        else {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x44);
          if (iVar13 == 0) goto LAB_4380e90c;
          uVar4 = 0x44;
          puVar7 = (undefined4 *)(DAT_4380f430 + 0x4380f360);
        }
      }
      else {
        if (1 < iVar13 - 3U) {
          uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380eff8 + 0x4380e9ae));
          puVar7 = (undefined4 *)(DAT_4380effc + 0x4380e9ba);
LAB_4380e9b8:
          *puVar7 = uVar4;
          goto LAB_4380e9ba;
        }
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x39);
        if (iVar13 != 0) {
          uVar4 = 0x39;
          puVar7 = (undefined4 *)(DAT_4380efe8 + 0x4380e976);
          goto LAB_4380f35e;
        }
        iVar13 = FUN_4380dfb4(param_1[3],*(undefined1 *)(DAT_4380efec + 0x4380e984),param_3);
        if (iVar13 != 0) {
          uVar4 = FUN_4380df00();
          puVar7 = (undefined4 *)(DAT_4380eff0 + 0x4380e996);
          goto LAB_4380e9b8;
        }
        puVar7 = (undefined4 *)(DAT_4380eff4 + 0x4380e99e);
LAB_4380e99c:
        uVar4 = 1;
      }
LAB_4380f35e:
      *puVar7 = uVar4;
    }
LAB_4380e9ba:
    piVar9 = (int *)(DAT_4380f000 + 0x4380e9c4);
    uVar4 = FUN_4380de20(param_3,*piVar9);
    iVar13 = FUN_43b03958(iVar5 != 0,uVar4);
    *piVar9 = iVar13;
    if (((iVar13 != 8) && (iVar13 != 0x12)) && (iVar13 != 0x3f)) goto LAB_4380ea46;
    iVar5 = *(int *)(*param_1 + 100);
    iVar13 = FUN_437d2424();
    if (((iVar13 == 0) || (*(int *)(param_2 + 0x218) != 0)) ||
       ((iVar5 - 0x1fU < 2 || ((*(char *)(iVar14 + 0x45) != '\0' || (bVar15)))))) {
      puVar7 = auStack_2f8;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f434));
      FUN_4380e2a8(&uStack_2e4);
      piVar9 = (int *)(DAT_4380f438 + 0x4380f390);
      uStack_334 = uStack_2e4;
      uStack_330 = uStack_2e0;
      uStack_32c = uStack_2dc;
      uStack_328 = uStack_2d8;
      uStack_324 = uStack_2d4;
    }
    else {
      puVar7 = auStack_320;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f004));
      FUN_4380e2a8(&uStack_30c);
      piVar9 = (int *)(DAT_4380f008 + 0x4380ea44);
      uStack_334 = uStack_30c;
      uStack_330 = uStack_308;
      uStack_32c = uStack_304;
      uStack_328 = uStack_300;
      uStack_324 = uStack_2fc;
    }
    goto LAB_4380f390;
  case 6:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = DAT_4380ef90;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(*(int *)(iVar8 + iVar13) + 0x3c) == 0) {
      if (*(char *)(param_1[3] + 0x16) == '\x01') {
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x44);
        if (iVar13 == 0) goto LAB_4380ea92;
        uVar4 = 0x44;
        puVar7 = (undefined4 *)(DAT_4380f43c + 0x4380f39c);
      }
      else {
LAB_4380ea92:
        uVar4 = 1;
        puVar7 = (undefined4 *)(DAT_4380f00c + 0x4380ea9c);
      }
      iVar13 = DAT_4380f010;
      *puVar7 = uVar4;
      FUN_4380dfe4(iVar13 + 0x4380eaa4);
    }
    else {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380f014 + 0x4380eab4));
      *(undefined4 *)(DAT_4380f018 + 0x4380eac0) = uVar4;
    }
    iVar13 = *param_1;
    piVar9 = (int *)(DAT_4380f01c + 0x4380ead0);
LAB_4380eace:
    FUN_4380e358(iVar13,bVar15,param_2 + 0x218,piVar9);
    goto LAB_4380f270;
  case 7:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(iVar6 + 0x1d4) == 3) {
        if (*(int *)(*param_1 + 0x34) == 1) {
          uVar4 = 0x22;
          puVar7 = (undefined4 *)(DAT_4380f020 + 0x4380eaf6);
        }
        else {
          uVar4 = 0x41;
          puVar7 = (undefined4 *)(DAT_4380f024 + 0x4380eb00);
        }
      }
      else if (*(int *)(*param_1 + 0x34) == 1) {
        uVar4 = 0x20;
        puVar7 = (undefined4 *)(DAT_4380f028 + 0x4380eb12);
      }
      else {
        iVar13 = *(int *)(iVar6 + 0x208);
        if (iVar13 == 1) {
          uVar4 = 0x43;
          puVar7 = (undefined4 *)(DAT_4380f02c + 0x4380eb2c);
        }
        else if (iVar13 == 2) {
          uVar4 = 0x42;
          puVar7 = (undefined4 *)(DAT_4380f030 + 0x4380eb36);
        }
        else {
          if (iVar13 == 0) {
            puVar7 = (undefined4 *)(DAT_4380f034 + 0x4380eb3e);
          }
          else {
            FUN_4380e020(3,9,1,DAT_4380f038 + 0x4380eb4e,iVar13);
            FUN_43902718(DAT_4380f03c + 0x4380eb5e,*(undefined4 *)(param_1[2] + 0x208));
            puVar7 = (undefined4 *)(DAT_4380f040 + 0x4380eb68);
          }
          uVar4 = 0x40;
        }
      }
      goto LAB_4380eafe;
    }
    if ((*(char *)(iVar6 + 0x1cc) != '\0') && ((*(byte *)(iVar6 + 0x26a) & 1) != 0)) {
      uVar4 = 0x16;
      puVar7 = (undefined4 *)(DAT_4380f044 + 0x4380eb84);
      goto LAB_4380eafe;
    }
    switch(*(undefined4 *)(iVar6 + 0x1d4)) {
    case 2:
      if (*(int *)(*param_1 + 0x548) == 1) {
        puVar7 = (undefined4 *)(DAT_4380f04c + 0x4380ec0e);
LAB_4380ecc2:
        uVar4 = 0x20;
        break;
      }
      cVar1 = *(char *)(param_1[0xb] + 0xb1);
      if (*(int *)(iVar6 + 0x1c) == 4) {
        uVar4 = 0x13;
      }
      else if (iVar5 == 0) {
        if (iVar13 == 1) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3d);
          if (iVar13 != 0) {
            uVar4 = 0x3d;
            goto LAB_4380ec9c;
          }
        }
        else if (iVar13 == 3) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3e);
          if (iVar13 != 0) {
            uVar4 = 0x3e;
            goto LAB_4380ec9c;
          }
        }
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x10);
        if (iVar13 == 0) {
          if (cVar1 == '\0') {
            uVar4 = FUN_436d6118();
            iVar13 = FUN_43ad909c(uVar4,0x18);
            if (iVar13 != 0) {
              uVar4 = 0x18;
              goto LAB_4380ec9c;
            }
          }
          uVar4 = 5;
        }
        else {
          if (cVar1 == '\0') {
            uVar4 = FUN_436d6118();
            iVar13 = FUN_43ad909c(uVar4,0x1a);
            if (iVar13 != 0) {
              uVar4 = 0x1a;
              goto LAB_4380ec9c;
            }
          }
          uVar4 = 0x10;
        }
      }
      else {
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x34);
        if (iVar13 == 0) {
          uVar4 = 0x32;
        }
        else {
          uVar4 = 0x34;
        }
      }
LAB_4380ec9c:
      *(undefined4 *)(DAT_4380f050 + 0x4380eca2) = uVar4;
      goto LAB_4380ecf0;
    case 3:
      cVar1 = *(char *)(param_1[0xb] + 0xb1);
      if (*(int *)(iVar6 + 0x1c) == 4) {
        uVar4 = 0x1f;
      }
      else if (iVar5 == 0) {
        if (iVar13 == 1) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3b);
          if (iVar13 != 0) {
            uVar4 = 0x3b;
            goto LAB_4380ebf4;
          }
        }
        else if (iVar13 == 3) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3c);
          if (iVar13 != 0) {
            uVar4 = 0x3c;
            goto LAB_4380ebf4;
          }
        }
        if (cVar1 == '\0') {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x19);
          if (iVar13 != 0) {
            uVar4 = 0x19;
            goto LAB_4380ebf4;
          }
        }
        uVar4 = 7;
      }
      else {
        uVar4 = 0x33;
      }
LAB_4380ebf4:
      puVar7 = (undefined4 *)(DAT_4380f048 + 0x4380ebfc);
      goto LAB_4380ecee;
    case 4:
      uVar4 = 0x12;
      puVar7 = (undefined4 *)(DAT_4380f054 + 0x4380ecac);
      break;
    case 5:
      uVar4 = 8;
      puVar7 = (undefined4 *)(DAT_4380f058 + 0x4380ecb4);
      break;
    default:
      if (*(int *)(*param_1 + 0x548) == 1) {
        puVar7 = (undefined4 *)(DAT_4380f05c + 0x4380ecc4);
        goto LAB_4380ecc2;
      }
      if (iVar5 == 0) {
        if (*(char *)(param_1[0xb] + 0xb1) == '\0') {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x18);
          if (iVar13 != 0) {
            uVar4 = 0x18;
            goto LAB_4380ecea;
          }
        }
        uVar4 = 5;
      }
      else {
        uVar4 = 0x32;
      }
LAB_4380ecea:
      puVar7 = (undefined4 *)(DAT_4380f060 + 0x4380ecf0);
LAB_4380ecee:
      *puVar7 = uVar4;
      goto LAB_4380ecf0;
    }
LAB_4380eafe:
    *puVar7 = uVar4;
LAB_4380ecf0:
    if (*(int *)(param_1[2] + 0x1d4) - 4U < 2) {
      puVar7 = auStack_2d0;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f064));
      FUN_4380e2a8(&uStack_2bc);
      piVar9 = (int *)(DAT_4380f068 + 0x4380ed28);
      uStack_334 = uStack_2bc;
      uStack_330 = uStack_2b8;
      uStack_32c = uStack_2b4;
      uStack_328 = uStack_2b0;
      uStack_324 = uStack_2ac;
    }
    else {
      iVar13 = FUN_43794a78(param_1);
      if (iVar13 == 0) {
        puVar7 = auStack_2a8;
        FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380ef64));
        FUN_4380e2a8(&uStack_294);
        piVar9 = (int *)(DAT_4380f06c + 0x4380ed5c);
        uStack_334 = uStack_294;
        uStack_330 = uStack_290;
        uStack_32c = uStack_28c;
        uStack_328 = uStack_288;
        uStack_324 = uStack_284;
      }
      else {
        puVar7 = auStack_280;
        FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f070));
        FUN_4380e2a8(&uStack_26c);
        piVar9 = (int *)(DAT_4380f074 + 0x4380ed88);
        uStack_334 = uStack_26c;
        uStack_330 = uStack_268;
        uStack_32c = uStack_264;
        uStack_328 = uStack_260;
        uStack_324 = uStack_25c;
      }
    }
    goto LAB_4380f390;
  case 8:
    if (iVar5 == 1) {
      uVar4 = 0x32;
      puVar7 = (undefined4 *)(DAT_4380f078 + 0x4380ed94);
    }
    else {
      uVar4 = 5;
      puVar7 = (undefined4 *)(DAT_4380f07c + 0x4380ed9c);
    }
    *puVar7 = uVar4;
    puVar7 = auStack_258;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380ef64));
    FUN_4380e2a8(&uStack_244);
    piVar9 = (int *)(DAT_4380f080 + 0x4380edc8);
    uStack_334 = uStack_244;
    uStack_330 = uStack_240;
    uStack_32c = uStack_23c;
    uStack_328 = uStack_238;
    uStack_324 = uStack_234;
    goto LAB_4380f390;
  case 9:
    puVar7 = auStack_208;
    puVar10 = auStack_1f4;
    piVar9 = (int *)(DAT_4380f08c + 0x4380edf0);
    *piVar9 = 8;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f090));
    break;
  case 10:
    puVar7 = auStack_1e0;
    puVar10 = auStack_1cc;
    piVar9 = (int *)(DAT_4380f094 + 0x4380ee0a);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f098));
    break;
  case 0xb:
    puVar7 = auStack_230;
    puVar2 = &stack0x00000130;
    piVar9 = (int *)(DAT_4380f084 + 0x4380edd6);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f088));
    goto LAB_4380ee2e;
  case 0xc:
    puVar7 = auStack_190;
    puVar10 = auStack_17c;
    piVar9 = (int *)(DAT_4380f0a4 + 0x4380ee44);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0a8));
    break;
  case 0xd:
    puVar7 = auStack_1b8;
    puVar2 = &stack0x000001a8;
    piVar9 = (int *)(DAT_4380f09c + 0x4380ee24);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0a0));
LAB_4380ee2e:
    puVar10 = (undefined4 *)(puVar2 + -0x34c);
    FUN_43b03a2e(puVar10);
    goto LAB_4380ee88;
  case 0xe:
    puVar7 = auStack_168;
    puVar10 = auStack_154;
    piVar9 = (int *)(DAT_4380f0ac + 0x4380ee5e);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0b0));
    break;
  case 0xf:
    puVar7 = auStack_140;
    puVar10 = auStack_12c;
    piVar9 = (int *)(DAT_4380f0b4 + 0x4380ee78);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0b8));
    break;
  case 0x10:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(*param_1 + 0x34) == 1) {
        if (*(int *)(iVar6 + 0x208) == 1) {
          uVar4 = 0x21;
          puVar7 = (undefined4 *)(DAT_4380f0bc + 0x4380eec2);
          goto LAB_4380f10c;
        }
        FUN_4380e020(3,9,1,DAT_4380f0c0 + 0x4380eece,*(int *)(iVar6 + 0x208));
        FUN_43902718(DAT_4380f0c4 + 0x4380eedc,*(undefined4 *)(param_1[2] + 0x208));
        puVar7 = (undefined4 *)(DAT_4380f0c8 + 0x4380eee4);
      }
      else {
        FUN_4380e020(3,9,1,DAT_4380f0cc + 0x4380eef2,*(int *)(*param_1 + 0x34));
        FUN_43902718(DAT_4380f0d0 + 0x4380eefe,*(undefined4 *)(*param_1 + 0x34));
        puVar7 = (undefined4 *)(DAT_4380f0d4 + 0x4380ef06);
      }
      uVar4 = 0x21;
      goto LAB_4380f10c;
    }
    switch(*(undefined4 *)(iVar6 + 0x208)) {
    case 1:
      puVar7 = (undefined4 *)(DAT_4380f0d8 + 0x4380ef22);
      goto LAB_4380f10a;
    case 2:
      uVar4 = 0x25;
      puVar7 = (undefined4 *)(DAT_4380f0dc + 0x4380ef2a);
      break;
    case 3:
      uVar4 = 0x2b;
      puVar7 = (undefined4 *)(DAT_4380f0e0 + 0x4380ef32);
      break;
    case 4:
      uVar4 = 0x2c;
      puVar7 = (undefined4 *)(&UNK_4380ef3a + DAT_4380f0e4);
      break;
    default:
      FUN_4380e020(3,9,1,DAT_4380f3b8 + 0x4380f0f6,*(undefined4 *)(iVar6 + 0x208));
      FUN_43902718(DAT_4380f3bc + 0x4380f104,*(undefined4 *)(param_1[2] + 0x208));
      puVar7 = (undefined4 *)(DAT_4380f3c0 + 0x4380f10c);
LAB_4380f10a:
      uVar4 = 0x26;
    }
LAB_4380f10c:
    *puVar7 = uVar4;
    puVar7 = auStack_118;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f3c4));
    FUN_4380e2a8(&uStack_104);
    piVar9 = (int *)(DAT_4380f3c8 + 0x4380f13a);
    uStack_90 = uStack_108;
    uStack_8c = uStack_104;
    uStack_88 = uStack_100;
    uStack_84 = uStack_fc;
    uStack_80 = uStack_f8;
    uStack_7c = uStack_f4;
    goto LAB_4380f266;
  case 0x11:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(*param_1 + 0x34) == 1) {
        puVar7 = (undefined4 *)(DAT_4380f3cc + 0x4380f152);
      }
      else {
        FUN_4380e020(3,9,1,DAT_4380f3d0 + 0x4380f160,*(int *)(*param_1 + 0x34));
        FUN_43902718(DAT_4380f3d4 + 0x4380f16c,*(undefined4 *)(*param_1 + 0x34));
        puVar7 = (undefined4 *)(DAT_4380f3d8 + 0x4380f174);
      }
      uVar4 = 0x28;
      goto LAB_4380f1c2;
    }
    switch(*(undefined4 *)(iVar6 + 0x208)) {
    case 1:
    case 2:
      puVar7 = (undefined4 *)(DAT_4380f3dc + 0x4380f18e);
      goto LAB_4380f1c0;
    case 3:
      uVar4 = 0x2d;
      puVar7 = (undefined4 *)(DAT_4380f3e0 + 0x4380f196);
      break;
    case 4:
      uVar4 = 0x2e;
      puVar7 = (undefined4 *)(DAT_4380f3e4 + 0x4380f19e);
      break;
    default:
      FUN_4380e020(3,9,1,DAT_4380f3e8 + 0x4380f1ac,*(undefined4 *)(iVar6 + 0x208));
      FUN_43902718(DAT_4380f3ec + 0x4380f1ba,*(undefined4 *)(param_1[2] + 0x208));
      puVar7 = (undefined4 *)(DAT_4380f3f0 + 0x4380f1c2);
LAB_4380f1c0:
      uVar4 = 0x2a;
    }
LAB_4380f1c2:
    *puVar7 = uVar4;
    puVar7 = auStack_f0;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f3c4));
    FUN_4380e2a8(&uStack_dc);
    piVar9 = (int *)(DAT_4380f3f4 + 0x4380f1f0);
    uStack_90 = uStack_e0;
    uStack_8c = uStack_dc;
    uStack_88 = uStack_d8;
    uStack_84 = uStack_d4;
    uStack_80 = uStack_d0;
    uStack_7c = uStack_cc;
    goto LAB_4380f266;
  case 0x12:
    puVar7 = auStack_c8;
    piVar9 = (int *)(DAT_4380f3f8 + 0x4380f202);
    *piVar9 = 1;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f3fc));
    FUN_4380e2a8(&uStack_b4);
    uStack_90 = uStack_b8;
    uStack_8c = uStack_b4;
    uStack_88 = uStack_b0;
    uStack_84 = uStack_ac;
    uStack_80 = uStack_a8;
    uStack_7c = uStack_a4;
    goto LAB_4380f266;
  default:
    puVar7 = auStack_a0;
    piVar9 = (int *)(DAT_4380f400 + 0x4380f23c);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f404));
    FUN_43b03a2e(&uStack_8c);
    goto LAB_4380f266;
  }
  FUN_4380e2a8(puVar10);
LAB_4380ee88:
  uStack_334 = *puVar10;
  uStack_330 = puVar10[1];
  uStack_32c = puVar10[2];
  uStack_328 = puVar10[3];
  uStack_324 = puVar10[4];
LAB_4380f390:
  uStack_90 = puVar7[4];
  uStack_8c = uStack_334;
  uStack_88 = uStack_330;
  uStack_84 = uStack_32c;
  uStack_80 = uStack_328;
  uStack_7c = uStack_324;
LAB_4380f266:
  FUN_4380e2e8(*puVar7,puVar7[1],puVar7[2],puVar7[3],uStack_90,uStack_8c,uStack_88,uStack_84,
               uStack_80,uStack_7c,piVar9);
LAB_4380f270:
  if ((*(char *)(*(int *)(iVar8 + DAT_4380f408) + 3) == '\0') &&
     (*(char *)(param_1[3] + 0x10) == '\0')) {
    if (*(char *)(param_1[0x14] + 0x2d) == '\0') goto LAB_4380f302;
    puVar7 = auStack_50;
    puVar10 = (undefined4 *)(DAT_4380f414 + 0x4380f2ce);
    *puVar10 = 5;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f410));
    FUN_4380e2a8(&uStack_3c);
    uStack_68 = uStack_40;
    uStack_64 = uStack_3c;
    uStack_60 = uStack_38;
    uStack_5c = uStack_34;
    uStack_58 = uStack_30;
    uStack_54 = uStack_2c;
  }
  else {
    puVar7 = auStack_78;
    puVar10 = (undefined4 *)(DAT_4380f40c + 0x4380f28c);
    *puVar10 = 9;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f410));
    FUN_4380e2a8(&uStack_64);
  }
  FUN_4380e2e8(*puVar7,puVar7[1],puVar7[2],puVar7[3],uStack_68,uStack_64,uStack_60,uStack_5c,
               uStack_58,uStack_54,puVar10);
LAB_4380f302:
  iVar13 = *(int *)(DAT_4380f418 + 0x4380f308);
  if (((iVar13 == 0x12) || (iVar13 == 0x3f)) || (iVar13 == 8)) {
    uVar4 = 1;
  }
  else {
    uVar4 = 0;
  }
  *(undefined4 *)(DAT_4380f41c + 0x4380f338) = uVar4;
  if ((*(int *)(*param_1 + 0x80) == 1) && (iVar13 == 3)) {
    **(undefined4 **)(iVar8 + DAT_4380f420) = 1;
  }
  else {
    **(undefined4 **)(iVar8 + DAT_4380f420) = 0;
  }
  return;
}


/* 43795a60 */

void FUN_43795a60(undefined4 param_1,byte param_2,byte param_3,undefined4 *param_4)

{
  byte bVar1;
  byte bVar2;
  undefined1 uVar3;
  
  bVar1 = *(byte *)(DAT_43795a88 + 0x43795aa6);
  bVar2 = *(byte *)(DAT_43795a88 + 0x43795aa7);
  *param_4 = param_1;
  uVar3 = FUN_437959b8();
  *(byte *)((int)param_4 + 6) = param_2 ^ bVar1;
  *(byte *)((int)param_4 + 5) = param_3 ^ bVar2;
  *(undefined1 *)(param_4 + 1) = uVar3;
  return;
}

