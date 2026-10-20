/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43814ea0" */

void FUN_43814ea0(int param_1,undefined4 param_2,int param_3,int param_4,undefined4 param_5,
                 undefined4 param_6,undefined4 param_7)

{
  undefined1 *puVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  undefined1 *puVar6;
  uint uVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined4 *puVar10;
  int iVar11;
  undefined4 auStack_188 [2];
  ushort uStack_180;
  ushort uStack_17e;
  undefined4 uStack_17c;
  uint uStack_178;
  undefined2 uStack_172;
  undefined2 uStack_170;
  undefined4 uStack_16c;
  undefined1 uStack_168;
  undefined1 uStack_167;
  undefined4 uStack_164;
  undefined1 uStack_160;
  undefined4 uStack_15c;
  undefined4 uStack_158;
  undefined1 uStack_154;
  undefined1 uStack_153;
  undefined4 uStack_150;
  undefined1 uStack_14c;
  undefined2 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined1 auStack_dc [4];
  undefined2 uStack_d8;
  byte bStack_d6;
  undefined2 uStack_d4;
  byte bStack_d2;
  undefined2 uStack_d0;
  byte bStack_ce;
  undefined2 uStack_cc;
  byte bStack_ca;
  undefined2 uStack_c8;
  byte bStack_c6;
  undefined2 uStack_c4;
  byte bStack_c2;
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  char cStack_84;
  char cStack_83;
  undefined4 uStack_80;
  undefined1 uStack_7c;
  undefined1 uStack_7b;
  undefined1 uStack_7a;
  undefined2 uStack_78;
  undefined1 uStack_76;
  undefined1 uStack_75;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_68;
  uint uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  uint uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined2 uStack_2c;
  
  uStack_17e = *(ushort *)(param_1 + 0x1a0);
  uStack_180 = *(ushort *)(param_1 + 0x19e);
  auStack_188[0] = param_2;
  uStack_17c = FUN_43814d24(*(undefined4 *)(param_1 + 0x1b4));
  uStack_178 = (uint)*(byte *)(param_1 + 0xc18);
  iVar11 = 0;
  uStack_172 = *(undefined2 *)(param_1 + 0xc76);
  uStack_170 = *(undefined2 *)(param_1 + 0xc74);
  uStack_154 = *(undefined1 *)(param_1 + 0xc88);
  uStack_153 = *(undefined1 *)(param_1 + 0xc8a);
  uStack_16c = FUN_43814d74(*(undefined4 *)(*(int *)(param_3 + 4) + 0x14));
  uStack_168 = FUN_43814e84(*(undefined4 *)(param_1 + 0xc7c));
  uStack_167 = *(char *)(param_1 + 0xc80) == '\x01';
  uStack_164 = *(undefined4 *)(param_1 + 0x1f0);
  uStack_160 = FUN_43b04042(*(undefined4 *)(param_1 + 0xc84));
  uStack_15c = FUN_43814db4(*(undefined4 *)(param_1 + 0x1b0),*(undefined1 *)(param_1 + 0x191));
  uStack_158 = FUN_43814e04(*(undefined4 *)(param_1 + 0xc8c));
  uStack_150 = FUN_43814e44(*(undefined4 *)(param_1 + 0x1e8));
  iVar4 = FUN_439fd844();
  uStack_14c = (undefined1)*(undefined4 *)(iVar4 + 0x1c);
  uVar7 = (uint)uStack_180;
  iVar5 = *(int *)(iVar4 + 0x1c);
  uVar8 = (uint)uStack_17e;
  puVar10 = auStack_188;
  while( true ) {
    if (iVar11 == iVar5) break;
    uVar2 = *(ushort *)(iVar4 + 0x28);
    iVar11 = iVar11 + 1;
    uVar3 = FUN_4355faf0(uVar7 * ((uint)*(ushort *)(iVar4 + 0x24) + (uint)(uVar2 >> 1)),0x280);
    *(undefined2 *)(puVar10 + 0x10) = uVar3;
    uVar3 = FUN_4355faf0(uVar8 * ((uint)*(ushort *)(iVar4 + 0x26) +
                                 (uint)(*(ushort *)(iVar4 + 0x2a) >> 1)),0x1e0);
    *(undefined2 *)((int)puVar10 + 0x42) = uVar3;
    uVar3 = FUN_4355faf0(uVar7 * uVar2,0x280);
    puVar10[0x12] = *(undefined4 *)(iVar4 + 0x20);
    *(undefined2 *)(puVar10 + 0x11) = uVar3;
    iVar4 = iVar4 + 0x54;
    puVar10 = puVar10 + 3;
  }
  uStack_e4 = *(undefined4 *)(param_1 + 0xc30);
  uStack_e8 = *(undefined2 *)(param_1 + 0xc78);
  uStack_e0 = *(undefined4 *)(param_1 + 0xc34);
  thunk_FUN_4387a1fc(auStack_188,auStack_dc,param_3);
  iVar4 = DAT_4402546c;
  uStack_74 = 3;
  uStack_70 = param_5;
  if (*(char *)(DAT_4402546c + 0xef) == '\0') {
    uVar2 = *(ushort *)(param_1 + 0x15c);
    uStack_5c = *(undefined4 *)(param_1 + 0x160);
  }
  else {
    uVar2 = *(ushort *)(param_1 + 0x1c);
    uStack_5c = *(undefined4 *)(param_1 + 0x20);
  }
  uStack_68 = 0;
  uStack_60 = (uint)uVar2;
  uStack_4c = 0;
  uStack_58 = 0;
  uStack_50 = 0;
  uStack_3c = *(undefined4 *)(param_1 + 0xc4);
  uStack_44 = (uint)*(ushort *)(param_1 + 0x1c);
  uStack_40 = *(undefined4 *)(param_1 + 0x24);
  uStack_38 = param_6;
  uStack_34 = param_7;
  iVar5 = FUN_436be554(param_2,&uStack_74);
  if (iVar5 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3b28,iVar5);
    FUN_43902718(s_Sequence_Movie__APL_ERR_0x_02x_a_43cb3b3c,iVar5);
  }
  uStack_30 = 0;
  uStack_2c = 0;
  iVar5 = FUN_436bdbfc(param_2,0,&uStack_30);
  *(undefined2 *)(param_1 + 0x1a6) = (undefined2)uStack_30;
  *(undefined2 *)(param_1 + 0x1aa) = uStack_30._2_2_;
  *(undefined2 *)(param_1 + 0x1a8) = uStack_2c;
  *(undefined2 *)(param_1 + 0x1ac) = uStack_2c;
  if (iVar5 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3b77,iVar5);
    FUN_43902718(s_Sequence_Movie__APL_ERR_0x_02x_a_43cb3b8b,iVar5);
  }
  if ((*(byte *)(iVar4 + 0xc) & 8) != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3bbf);
    FUN_43902718(s_Apl_Kick_43cb3bd3);
  }
  *(undefined1 *)(param_4 + 100) = 1;
  puVar6 = auStack_dc;
  iVar5 = 0;
  *(undefined4 *)(param_4 + 0x68) = *(undefined4 *)(param_1 + 0x1f0);
  iVar4 = param_4;
  do {
    iVar5 = iVar5 + 1;
    *(undefined1 *)(iVar4 + 0x6c) = puVar6[0x1c];
    *(undefined1 *)(iVar4 + 0x80) = puVar6[0x30];
    puVar1 = puVar6 + 0x44;
    puVar6 = puVar6 + 1;
    *(undefined1 *)(iVar4 + 0x94) = *puVar1;
    iVar4 = iVar4 + 1;
  } while (iVar5 != 0x14);
  if (cStack_84 == '\0') {
    *(undefined1 *)(param_4 + 0xa8) = 0;
  }
  else {
    *(undefined1 *)(param_4 + 0xa8) = 1;
    *(undefined4 *)(param_4 + 0xac) = uStack_80;
    *(undefined2 *)(param_4 + 0xb4) = uStack_d4;
    *(undefined2 *)(param_4 + 0xb0) = uStack_d8;
    *(undefined2 *)(param_4 + 0xbc) = uStack_cc;
    *(ushort *)(param_4 + 0xb2) = (ushort)bStack_d6;
    *(undefined2 *)(param_4 + 0xc4) = uStack_c4;
    *(ushort *)(param_4 + 0xb6) = (ushort)bStack_d2;
    *(undefined2 *)(param_4 + 0xb8) = uStack_d0;
    *(ushort *)(param_4 + 0xba) = (ushort)bStack_ce;
    *(ushort *)(param_4 + 0xbe) = (ushort)bStack_ca;
    *(undefined2 *)(param_4 + 0xc0) = uStack_c8;
    *(ushort *)(param_4 + 0xc2) = (ushort)bStack_c6;
    *(ushort *)(param_4 + 0xc6) = (ushort)bStack_c2;
  }
  if (cStack_83 == '\0') {
    *(undefined1 *)(param_4 + 200) = 0;
  }
  else {
    *(undefined1 *)(param_4 + 200) = 1;
    uVar9 = *(undefined4 *)(param_1 + 0x1f0);
    *(int *)(param_4 + 0xd4) = param_1 + 0xbc;
    *(undefined4 *)(param_4 + 0xcc) = uVar9;
    *(undefined1 *)(param_4 + 0xd0) = auStack_dc[0];
  }
  *(undefined1 *)(param_4 + 0xd8) = uStack_7c;
  *(undefined1 *)(param_4 + 0xd9) = uStack_7b;
  *(undefined1 *)(param_4 + 0xda) = uStack_7a;
  *(undefined2 *)(param_4 + 0xdc) = uStack_78;
  *(undefined1 *)(param_4 + 0xde) = uStack_76;
  *(undefined1 *)(param_4 + 0xdf) = uStack_75;
  *(undefined2 *)(param_4 + 0xe0) = uStack_172;
  return;
}

