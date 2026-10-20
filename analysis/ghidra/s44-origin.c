/* S41: read-only exports. */

/* 437b5b14 */

void FUN_437b5b14(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  
  FUN_43859710(0x10);
  iVar8 = DAT_437b5ce0;
  FUN_4383b520(0x20,0);
  iVar8 = iVar8 + 0x437b5b34;
  uVar10 = *(undefined4 *)(iVar8 + DAT_437b5ce4);
  iVar9 = *(int *)(iVar8 + DAT_437b5ce8);
  uVar11 = *(undefined4 *)(iVar8 + DAT_437b5cec);
  uVar12 = *(undefined4 *)(iVar8 + DAT_437b5cf0);
  uVar13 = *(undefined4 *)(iVar8 + DAT_437b5cf4);
  uVar15 = *(undefined4 *)(iVar8 + DAT_437b5cf8);
  uVar16 = *(undefined4 *)(iVar8 + DAT_437b5cfc);
  uVar1 = *(undefined4 *)(iVar8 + DAT_437b5d00);
  uVar2 = *(undefined4 *)(iVar8 + DAT_437b5d04);
  uVar3 = *(undefined4 *)(iVar8 + DAT_437b5d08);
  uVar4 = *(undefined4 *)(iVar8 + DAT_437b5d0c);
  FUN_43844e80(param_1,*(undefined4 *)(iVar8 + DAT_437b5d10),*(undefined4 *)(iVar8 + DAT_437b5d14),
               *(int *)(iVar8 + DAT_437b5d18) + 0x290,uVar10,iVar9,uVar11,uVar12,uVar13,uVar15,
               uVar16,uVar1,uVar2,uVar3,uVar4);
  FUN_4383b520(0x20,1);
  FUN_4383b520(0x21,0);
  FUN_43859ae0(iVar9);
  FUN_4383b520(0x21,1);
  FUN_4383b520(0x22,0);
  uVar5 = *(undefined4 *)(iVar8 + DAT_437b5d1c);
  FUN_4382dd78(param_1,iVar9,uVar5);
  FUN_4383b520(0x22,1);
  uVar14 = *(undefined4 *)(iVar8 + DAT_437b5d20);
  uVar6 = *(undefined4 *)(iVar8 + DAT_437b5d24);
  uVar7 = *(undefined4 *)(iVar8 + DAT_437b5d28);
  if (*(int *)(iVar9 + 0x24c) == 0) {
    FUN_4383b520(0x23);
    FUN_43859b34(iVar9,uVar7,uVar11,uVar12,uVar2,uVar13,uVar15,uVar1,uVar14,uVar5,uVar3,uVar16,uVar4
                 ,uVar10,uVar6);
    FUN_4383b520(0x23,1);
  }
  FUN_4383b520(0x35,0);
  FUN_4384b268(uVar7,uVar11,uVar12,uVar13,uVar2,uVar5,uVar3,uVar16,uVar14,uVar1,uVar4,uVar6,uVar10,
               iVar9,uVar15,*(undefined4 *)(iVar8 + DAT_437b5d2c),param_2);
  FUN_4383b520(0x35,1);
  FUN_4383b520(0x36,0);
  FUN_43b08648();
  FUN_4385b234(iVar9);
  FUN_4383a974();
  FUN_43859710(0x20);
  FUN_43859a24();
  FUN_4383b520(0x36,1);
  return;
}


/* 43ad8e54 */

void FUN_43ad8e54(int *param_1)

{
  byte *pbVar1;
  int iVar2;
  char *pcVar3;
  
  iVar2 = *param_1;
  pbVar1 = *(byte **)(iVar2 + 0x10);
  if (pbVar1 != (byte *)(iVar2 + 0x28)) {
    if (*(char *)(iVar2 + 0x20) == '\0') {
      *pbVar1 = *pbVar1 & 0xf;
      *(byte **)(iVar2 + 0x10) = pbVar1 + 1;
      *(undefined1 *)(*param_1 + 0x20) = 1;
    }
    pcVar3 = *(char **)(*param_1 + 0x1c);
    *pcVar3 = ((char)*(undefined4 *)(*param_1 + 0x10) + -1) - (char)pcVar3;
  }
  return;
}


/* 43ad8eb0 */

void FUN_43ad8eb0(int *param_1,uint param_2)

{
  char *pcVar1;
  undefined1 *puVar2;
  uint uVar3;
  undefined1 *puVar4;
  byte *pbVar5;
  
  puVar2 = *(undefined1 **)(*param_1 + 0x10);
  *puVar2 = 0x81;
  pbVar5 = puVar2 + 2;
  pcVar1 = (char *)*param_1;
  *(undefined1 **)(pcVar1 + 0x1c) = puVar2 + 1;
  if (*pcVar1 == '\0') {
    puVar2[2] = pcVar1[3];
    puVar4 = puVar2 + 3;
    if (8 < *(byte *)(*param_1 + 1)) {
      puVar4 = puVar2 + 4;
      puVar2[3] = (char)(param_2 >> 8);
    }
    pbVar5 = puVar4 + 1;
    *puVar4 = (char)param_2;
  }
  else {
    uVar3 = 0;
    while( true ) {
      if ((int)(uint)(*(byte *)(*param_1 + 1) >> 2) <= (int)uVar3) break;
      if ((uVar3 & 1) == 0) {
        *pbVar5 = (byte)param_2 & 0xf;
      }
      else {
        *pbVar5 = *pbVar5 | (byte)(param_2 << 4);
        pbVar5 = pbVar5 + 1;
      }
      param_2 = param_2 >> 4;
      uVar3 = uVar3 + 1;
    }
    if ((*(byte *)(*param_1 + 1) & 7) != 0) {
      FUN_43ad8e9c(param_1);
    }
  }
  *(byte **)(*param_1 + 0x10) = pbVar5;
  return;
}


/* 43ad8f20 */

void FUN_43ad8f20(int *param_1,uint param_2)

{
  char *pcVar1;
  uint uVar2;
  byte *pbVar3;
  byte *pbVar4;
  
  pcVar1 = (char *)*param_1;
  pbVar3 = *(byte **)(pcVar1 + 0x10);
  if (*pcVar1 == '\0') {
    *pbVar3 = (byte)param_2;
    pbVar3 = pbVar3 + 1;
  }
  else {
    uVar2 = 0;
    if (pcVar1[0x20] == '\0') {
      for (; (int)uVar2 < (int)(uint)(*(byte *)(*param_1 + 2) >> 2); uVar2 = uVar2 + 1) {
        if ((uVar2 == 0) || ((uVar2 & 1) == 0)) {
          pbVar4 = pbVar3 + 1;
          *pbVar3 = *pbVar3 | (byte)(param_2 << 4);
        }
        else {
          *pbVar3 = (byte)param_2 & 0xf;
          pbVar4 = pbVar3;
        }
        param_2 = param_2 >> 4;
        pbVar3 = pbVar4;
      }
    }
    else {
      for (uVar2 = 0; (int)uVar2 < (int)(uint)(*(byte *)(*param_1 + 2) >> 2); uVar2 = uVar2 + 1) {
        if ((uVar2 & 1) == 0) {
          *pbVar3 = (byte)param_2 & 0xf;
        }
        else {
          *pbVar3 = *pbVar3 | (byte)(param_2 << 4);
          pbVar3 = pbVar3 + 1;
        }
        param_2 = param_2 >> 4;
      }
    }
    if ((*(byte *)(*param_1 + 2) & 7) != 0) {
      FUN_43ad8e9c(param_1);
    }
  }
  *(byte **)(*param_1 + 0x10) = pbVar3;
  return;
}


/* 43ad8e88 */

void FUN_43ad8e88(int *param_1,uint param_2)

{
  *(uint *)(*param_1 + 0x18) = param_2 & ~(-1 << *(sbyte *)(*param_1 + 1));
  return;
}

