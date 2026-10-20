/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "439035e0" */

int FUN_439035e0(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined2 param_6)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined2 *puVar5;
  undefined1 auStack_80 [4];
  undefined2 uStack_7c;
  byte bStack_78;
  undefined4 auStack_70 [24];
  
  iVar2 = FUN_43902c2c(param_2,param_3,param_4,param_5,auStack_80,param_6);
  if (iVar2 == 0) {
    *(undefined4 *)(param_1 + 2) = param_2;
    *param_1 = uStack_7c;
    *(byte *)(param_1 + 1) = bStack_78;
    if (4 < bStack_78) {
      FUN_43902984(5,1,1,&DAT_43cceb4c,bStack_78,4);
      FUN_43902718(s_MemoryHandle__AllocRendezvous__E_43cceb57,*(undefined1 *)(param_1 + 1),4);
      *(undefined1 *)(param_1 + 1) = 4;
    }
    bVar1 = *(byte *)(param_1 + 1);
    puVar4 = auStack_70;
    puVar5 = param_1;
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
      *(undefined4 *)(puVar5 + 4) = *puVar4;
      *(undefined4 *)(puVar5 + 6) = puVar4[1];
      puVar5 = puVar5 + 4;
      puVar4 = puVar4 + 2;
    }
    *(undefined1 *)((int)param_1 + 3) = 1;
  }
  return iVar2;
}


/* query "43b2a2d0" */

undefined4
FUN_43b2a2d0(undefined2 *param_1,undefined4 param_2,undefined4 param_3,int param_4,
            undefined2 param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar2 = param_2;
  iVar1 = FUN_43ae9674();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    if (*(char *)((int)param_1 + 3) == '\0') {
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_43b0662c(param_1);
      if (iVar1 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 2;
      }
      uVar2 = FUN_43903118(*param_1,param_2,uVar3,param_3,param_5,uVar2);
    }
    if (param_4 == 0) {
      *(undefined1 *)((int)param_1 + 3) = 0;
    }
    else {
      FUN_43ae7542(param_1);
    }
  }
  return uVar2;
}


/* query "43903558" */

int FUN_43903558(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined2 param_5)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined2 *puVar5;
  undefined1 auStack_80 [4];
  undefined2 uStack_7c;
  byte bStack_78;
  undefined4 auStack_70 [24];
  
  iVar2 = FUN_43902a34(param_2,param_3,param_4,auStack_80,param_5);
  if (iVar2 == 0) {
    *(undefined4 *)(param_1 + 2) = param_2;
    *param_1 = uStack_7c;
    *(byte *)(param_1 + 1) = bStack_78;
    if (4 < bStack_78) {
      FUN_43902984(5,1,1,&DAT_43cceb07,bStack_78,4);
      FUN_43902718(s_MemoryHandle__AllocNew__ERR_EXTE_43cceb12,*(undefined1 *)(param_1 + 1),4);
      *(undefined1 *)(param_1 + 1) = 4;
    }
    bVar1 = *(byte *)(param_1 + 1);
    puVar4 = auStack_70;
    puVar5 = param_1;
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
      *(undefined4 *)(puVar5 + 4) = *puVar4;
      *(undefined4 *)(puVar5 + 6) = puVar4[1];
      puVar5 = puVar5 + 4;
      puVar4 = puVar4 + 2;
    }
    *(undefined1 *)((int)param_1 + 3) = 1;
  }
  return iVar2;
}


/* query "43903720" */

int FUN_43903720(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined1 auStack_88 [8];
  byte bStack_80;
  undefined4 auStack_78 [25];
  
  iVar2 = FUN_43ae9674();
  if (iVar2 == 0) {
    iVar2 = -6;
  }
  else {
    iVar2 = FUN_43b0662c(param_1);
    if (iVar2 == 0) {
      if (*(char *)((int)param_1 + 3) == '\0') {
        iVar2 = -7;
      }
      else {
        iVar2 = FUN_43903280(*param_1,param_2,param_3,auStack_88,param_4);
        if (iVar2 == 0) {
          *(byte *)(param_1 + 1) = bStack_80;
          if (4 < bStack_80) {
            FUN_43902984(5,1,1,&DAT_43ccec16,bStack_80,4);
            FUN_43902718(s_MemoryHandle__Open__ERR_EXTENT_S_43ccec21,*(undefined1 *)(param_1 + 1),4)
            ;
            *(undefined1 *)(param_1 + 1) = 4;
          }
          bVar1 = *(byte *)(param_1 + 1);
          puVar4 = auStack_78;
          for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
            *(undefined4 *)(param_1 + 4) = *puVar4;
            *(undefined4 *)(param_1 + 6) = puVar4[1];
            param_1 = param_1 + 4;
            puVar4 = puVar4 + 2;
          }
        }
      }
    }
    else {
      iVar2 = 0;
    }
  }
  return iVar2;
}


/* query "43b2a252" */

void FUN_43b2a252(undefined4 *param_1)

{
  FUN_43561604(*param_1);
  return;
}


/* query "43ae75dc" */

undefined4 FUN_43ae75dc(undefined4 *param_1)

{
  return *param_1;
}


/* query "4379a914" */

bool FUN_4379a914(int param_1)

{
  return param_1 == DAT_43e9f06c;
}


/* query "436519c0" */

int FUN_436519c0(undefined4 param_1,undefined2 *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 *puVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  undefined1 auStack_270 [272];
  short sStack_160;
  short sStack_15e;
  ushort uStack_15a;
  ushort uStack_158;
  undefined4 auStack_150 [24];
  undefined1 auStack_f0 [16];
  undefined4 auStack_e0 [24];
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined4 uStack_74;
  int iStack_70;
  ushort uStack_6c;
  undefined2 uStack_6a;
  undefined1 auStack_30 [4];
  ushort uStack_2c;
  undefined2 auStack_2a [3];
  
  FUN_435aa02c(auStack_30);
  FUN_435a92e0(auStack_270);
  FUN_439c5a04(&uStack_80,0,0x50);
  FUN_439c5a04(auStack_f0,0,0x70);
  FUN_439c5a04(&sStack_160,0,0x70);
  iVar1 = FUN_43a97568(param_1,*(undefined4 *)(param_2 + 2),auStack_2a);
  if (iVar1 == 0) {
    iVar1 = FUN_43651530(param_1,&uStack_2c);
    if (iVar1 == 0) {
      uStack_80 = 5;
      uStack_74 = 0xffffffff;
      uStack_7e = *param_2;
      uStack_6c = uStack_2c;
      uStack_6a = auStack_2a[0];
      iStack_70 = iVar1;
      iVar1 = FUN_43a49628(auStack_270,0x56015c);
      iVar2 = FUN_435a9304(auStack_270,&uStack_80,0x50);
      if (iVar1 == 0 && iVar2 == 0) {
        uVar4 = FUN_435aa068(auStack_30,0x61003c,auStack_270);
        if (uVar4 == 0) {
          iVar1 = FUN_43a9759a(param_1,auStack_270,&sStack_160);
          if (iVar1 == 0) {
            uVar4 = 0;
            puVar3 = auStack_150;
            puVar5 = auStack_e0;
            while( true ) {
              if (uStack_158 <= uVar4) break;
              uVar4 = uVar4 + 1;
              *puVar5 = *puVar3;
              puVar5[1] = puVar3[1];
              puVar3 = puVar3 + 2;
              puVar5 = puVar5 + 2;
            }
            if (sStack_160 == -0x7ffb) {
              if (uStack_2c == uStack_15a) {
                iVar2 = FUN_43651648(param_1,(int)sStack_15e);
                if (iVar2 == 0) {
                  param_3[2] = 0;
                  param_3[4] = 0;
                  param_3[6] = 0;
                  param_3[8] = 0;
                  param_3[10] = 0;
                  param_3[0xc] = 0;
                  param_3[0xe] = 0;
                  param_3[0x10] = 0;
                  *(char *)param_3 = (char)uStack_158;
                  uVar4 = 0;
                  puVar3 = auStack_e0;
                  while( true ) {
                    if (uStack_158 <= uVar4) break;
                    uVar4 = uVar4 + 1;
                    param_3[1] = *puVar3;
                    param_3[2] = puVar3[1];
                    param_3 = param_3 + 2;
                    puVar3 = puVar3 + 2;
                  }
                  goto LAB_43651d8c;
                }
                FUN_43651574(param_1,(int)sStack_15e);
                FUN_435ab880(s__SDF__DMM_UNIT_HANDLE_____x_43c7cad4,uStack_7e);
                FUN_435ab880(s__SDF__ERROR__DMM_UNIT_OPEN_Error_43c7cb16);
                FUN_43639190(0x40,0,0x8000,0x42,6,0x1000,0,0x507);
                FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x508);
                FUN_43639204(0x80,0,0x8000,0x8005,uStack_15a,0,0x509);
                uVar7 = 0x50a;
              }
              else {
                FUN_43639190(0x40,0,0x8000,0x41,6,0x1000,0,0x4fc);
                FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x4fd);
                FUN_43639204(0x80,0,0x8000,0x8005,uStack_15a,0,0x4fe);
                uVar7 = 0x4ff;
              }
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x40,6,0x1000,0,0x4f3);
              FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x4f4);
              FUN_43639204(0x80,0,0x8000,sStack_160,uStack_15a,0,0x4f5);
              uVar7 = 0x4f6;
            }
            FUN_43639204(0x80,0,0x8000,(int)sStack_15e,0,0,uVar7);
            iVar1 = 0x1000;
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x3f,6,iVar1,0,0x4e3);
          }
          goto LAB_43651d8c;
        }
        FUN_43639190(0x40,0,0x8000,0x3e,6,0x200,0,0x4dc);
        uVar7 = 0x4dd;
        uVar6 = 0;
      }
      else {
        FUN_43639190(0x40,0,0x8000,0x3d,6,0x200,0,0x4cf);
        FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x4d0);
        uVar4 = (uint)uStack_6c;
        uVar7 = 0x4d1;
        uVar6 = uStack_6a;
      }
      FUN_43639204(0x80,0,0x8000,uVar4,uVar6,0,uVar7);
      iVar1 = 0x200;
      goto LAB_43651d8c;
    }
    FUN_43639190(0x40,0,0x8000,0x3c,6,iVar1,0,0x4bf);
    uVar4 = (uint)uStack_2c;
    uVar7 = 0x4c0;
    auStack_2a[0] = 0;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x3b,6,iVar1,0,0x4b8);
    uVar7 = 0x4b9;
    uVar4 = *(uint *)(param_2 + 2);
  }
  FUN_43639204(0x80,0,0x8000,uVar4,auStack_2a[0],0,uVar7);
LAB_43651d8c:
  FUN_435a92c8(auStack_270);
  FUN_435aa014(auStack_30);
  return iVar1;
}


/* query "43651694" */

int FUN_43651694(undefined4 param_1,undefined2 *param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined1 auStack_1f0 [272];
  short sStack_e0;
  short sStack_de;
  ushort uStack_da;
  undefined2 uStack_70;
  undefined2 uStack_6e;
  int iStack_60;
  ushort uStack_5c;
  undefined1 auStack_20 [6];
  ushort uStack_1a;
  
  FUN_435aa02c(auStack_20);
  FUN_435a92e0(auStack_1f0);
  FUN_439c5a04(&uStack_70,0,0x50);
  FUN_439c5a04(&sStack_e0,0,0x70);
  iVar1 = FUN_43651530(param_1,&uStack_1a);
  if (iVar1 == 0) {
    uStack_6e = *param_2;
    uStack_70 = 6;
    uStack_5c = uStack_1a;
    iStack_60 = iVar1;
    iVar1 = FUN_43a49628(auStack_1f0,0x56015c);
    iVar2 = FUN_435a9304(auStack_1f0,&uStack_70,0x50);
    if (iVar1 == 0 && iVar2 == 0) {
      uVar3 = FUN_435aa068(auStack_20,0x61003c,auStack_1f0);
      if (uVar3 == 0) {
        iVar1 = FUN_43a9759a(param_1,auStack_1f0,&sStack_e0);
        if (iVar1 == 0) {
          if (sStack_e0 == -0x7ffa) {
            if (uStack_1a == uStack_da) {
              iVar2 = FUN_43651648(param_1,(int)sStack_de);
              if (iVar2 == 0) goto LAB_43651988;
              FUN_43651574(param_1,(int)sStack_de);
              FUN_435ab880(s__SDF__DMM_UNIT_HANDLE_____x_43c7cad4,uStack_6e);
              FUN_435ab880(s__SDF__ERROR__DMM_UNIT_CLOSE_Erro_43c7caf2);
              FUN_43639190(0x40,0,0x8000,0x50,6,0x1000,0,0x5d8);
              FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5d9);
              FUN_43639204(0x80,0,0x8000,0x8006,uStack_da,0,0x5da);
              uVar4 = 0x5db;
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x4f,6,0x1000,0,0x5cd);
              FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5ce);
              FUN_43639204(0x80,0,0x8000,0x8006,uStack_da,0,0x5cf);
              uVar4 = 0x5d0;
            }
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x4e,6,0x1000,0,0x5c4);
            FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5c5);
            FUN_43639204(0x80,0,0x8000,sStack_e0,uStack_da,0,0x5c6);
            uVar4 = 0x5c7;
          }
          FUN_43639204(0x80,0,0x8000,(int)sStack_de,0,0,uVar4);
          iVar1 = 0x1000;
        }
        else {
          FUN_43639190(0x40,0,0x8000,0x4d,6,iVar1,0,0x5b9);
        }
        goto LAB_43651988;
      }
      FUN_43639190(0x40,0,0x8000,0x4c,6,0x200,0,0x5b2);
      uVar4 = 0x5b3;
    }
    else {
      FUN_43639190(0x40,0,0x8000,0x4b,6,0x200,0,0x5a6);
      FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5a7);
      uVar3 = (uint)uStack_5c;
      uVar4 = 0x5a8;
    }
    FUN_43639204(0x80,0,0x8000,uVar3,0,0,uVar4);
    iVar1 = 0x200;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x4a,6,iVar1,0,0x598);
    FUN_43639204(0x80,0,0x8000,uStack_1a,0,0,0x599);
  }
LAB_43651988:
  FUN_435a92c8(auStack_1f0);
  FUN_435aa014(auStack_20);
  return iVar1;
}


/* query "43561604" */

void FUN_43561604(void)

{
  (**(code **)(*(int *)(DAT_440205c0 + 0x14) + 0x308))();
  return;
}


/* query "43ae7c48" */

undefined8 FUN_43ae7c48(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  FUN_43901a8c(4,0xb,param_1,param_2,param_1,param_2,param_3);
  uVar2 = 5;
  uVar1 = FUN_43902df8(param_1,param_2,param_3,param_4);
  FUN_43901a8c(4,0xc,param_1,param_2);
  return CONCAT44(uVar2,uVar1);
}


/* query "43815560" */

void FUN_43815560(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 auStack_208 [2];
  undefined2 uStack_200;
  undefined2 uStack_1fe;
  undefined4 uStack_1fc;
  uint uStack_1f8;
  undefined2 uStack_1f2;
  undefined2 uStack_1f0;
  undefined4 uStack_1ec;
  undefined1 uStack_1e8;
  undefined1 uStack_1e7;
  undefined4 uStack_1e4;
  undefined1 uStack_1e0;
  undefined4 uStack_1dc;
  undefined4 uStack_1d8;
  undefined1 uStack_1d4;
  undefined1 uStack_1d3;
  undefined4 uStack_1d0;
  undefined1 uStack_1cc;
  undefined2 uStack_168;
  undefined4 uStack_164;
  undefined4 uStack_160;
  undefined1 auStack_15c [4];
  ushort uStack_158;
  undefined1 auStack_ec [104];
  undefined4 auStack_84 [2];
  uint uStack_7c;
  undefined4 uStack_78;
  uint uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  uint uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined2 uStack_24;
  
  uStack_38 = 0x80;
  uStack_40 = 4;
  uStack_3c = 7;
  uStack_34 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  uStack_36 = 0;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),7,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3bdc,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_R_43cb3bf0,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),1,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3c19,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_R_43cb3c2d,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0xb,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3c56,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_R_43cb3c6a,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),3,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3c9a,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_W_43cb3cae,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),4,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3cd7,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_W_43cb3ceb,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0x11,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3d14,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_W_43cb3d28,iVar1);
  }
  uStack_36 = 0x7d;
  uStack_2c = 1;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),10,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3d58,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_R_43cb3d6c,iVar1);
  }
  uStack_36 = 0x56a;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0x10,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3d9a,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_W_43cb3dae,iVar1);
  }
  uStack_36 = 0x268;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),6,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3e83,iVar1);
    FUN_43902718(s_APL_ERR_0x_02x_apl_mov_set_aic_R_43cb3e97,iVar1);
  }
  auStack_208[0] = *(undefined4 *)(param_1 + 0xc6c);
  uStack_200 = *(undefined2 *)(param_1 + 0x19e);
  uStack_1fe = *(undefined2 *)(param_1 + 0x1a0);
  uStack_1fc = FUN_43814d24(*(undefined4 *)(param_1 + 0x1b4));
  uStack_1f8 = (uint)*(byte *)(param_1 + 0xc18);
  uStack_1f2 = *(undefined2 *)(param_1 + 0xc76);
  uStack_1f0 = *(undefined2 *)(param_1 + 0xc74);
  uStack_1d4 = *(undefined1 *)(param_1 + 0xc88);
  uStack_1d3 = *(undefined1 *)(param_1 + 0xc8a);
  uStack_1ec = FUN_43814d74(*(undefined4 *)(*(int *)(param_2 + 4) + 0x14));
  uStack_1e8 = FUN_43814e84(*(undefined4 *)(param_1 + 0xc7c));
  uStack_1e7 = *(char *)(param_1 + 0xc80) == '\x01';
  uStack_1e4 = *(undefined4 *)(param_1 + 0x1f0);
  uStack_1e0 = FUN_43b04042(*(undefined4 *)(param_1 + 0xc84));
  uStack_1dc = FUN_43814db4(*(undefined4 *)(param_1 + 0x1b0),0);
  uStack_1d8 = FUN_43814e04(*(undefined4 *)(param_1 + 0xc8c));
  uStack_1d0 = FUN_43814e44(*(undefined4 *)(param_1 + 0x1e8));
  uStack_1cc = 0;
  uStack_164 = *(undefined4 *)(param_1 + 0xc30);
  uStack_168 = *(undefined2 *)(param_1 + 0xc78);
  uStack_160 = *(undefined4 *)(param_1 + 0xc34);
  thunk_FUN_4387a1fc(auStack_208,auStack_ec,param_2);
  iVar1 = FUN_43902df8(0x172f5e,param_3,0,auStack_15c,5);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3ec5);
    FUN_43902718(&LAB_43cb3ed8_1);
  }
  uStack_7c = (uint)uStack_158;
  auStack_84[0] = 0;
  uStack_78 = 0;
  uStack_70 = (uint)*(ushort *)(param_1 + 0x15c);
  uStack_5c = 0;
  uStack_68 = 0;
  uStack_6c = *(undefined4 *)(param_1 + 0x160);
  uStack_60 = 0;
  uStack_4c = *(undefined4 *)(param_1 + 0xc4);
  uStack_54 = (uint)*(ushort *)(param_1 + 0x1c);
  uStack_50 = *(undefined4 *)(param_1 + 0xd10);
  uStack_44 = param_5;
  uStack_48 = param_4;
  iVar1 = FUN_436be554(*(undefined4 *)(param_1 + 0xc6c),auStack_84);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3ddc,iVar1);
    FUN_43902718(s_Sequence_HSRecGolfshot__APL_ERR__43cb3df0,iVar1);
    FUN_43902fbc(uStack_158,2,5);
  }
  uStack_28 = 0;
  uStack_24 = 0;
  iVar1 = FUN_436bdbfc(*(undefined4 *)(param_1 + 0xc6c),0,&uStack_28);
  *(undefined2 *)(param_1 + 0x1a6) = (undefined2)uStack_28;
  *(undefined2 *)(param_1 + 0x1aa) = uStack_28._2_2_;
  *(undefined2 *)(param_1 + 0x1a8) = uStack_24;
  *(undefined2 *)(param_1 + 0x1ac) = uStack_24;
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3e33,iVar1);
    FUN_43902718(s_Sequence_HSRecGolfshot__APL_ERR__43cb3e47,iVar1);
  }
  return;
}

