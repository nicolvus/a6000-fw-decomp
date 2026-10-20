/* S41: read-only exports. */

/* 437fee08 */

void candidate_437fee08(undefined4 param_1,undefined4 param_2,undefined4 param_3,char *param_4)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  char *pcStack_14;
  
  pcStack_14 = param_4;
  do {
    while (iVar3 = FUN_43561260(DAT_437feedc,&pcStack_14,0xffffffff), pcVar2 = pcStack_14,
          iVar3 != 0) {
      iVar3 = DAT_437feee4 + 0x437fee28;
      FUN_437fed58(5,0,1,DAT_437feee0 + 0x437fee26,iVar3,0x44,param_3);
      FUN_43902718(DAT_437feee8 + 0x437fee3a,iVar3,0x44);
    }
    uVar6 = *(undefined4 *)(pcStack_14 + -4);
    FUN_437876dc();
    iVar3 = FUN_43b00cb4();
    if (iVar3 == 1) {
      if (*pcVar2 == '\0') {
        uVar4 = FUN_437876dc();
        iVar3 = FUN_43805854(uVar4,*(undefined2 *)(pcVar2 + 2));
        if (iVar3 != 0) {
          uVar4 = FUN_437876dc();
          FUN_4380577c(uVar4,0xffffffff);
        }
      }
      if ((*pcVar2 == '\0') || (*pcVar2 == '\x02')) {
        uVar4 = FUN_437876dc();
        uVar5 = FUN_43561340(pcStack_14);
        FUN_43805930(uVar4,pcVar2,uVar5);
      }
    }
    FUN_43560d38(0x17,0xffffffff);
    cVar1 = *pcVar2;
    if (cVar1 == '\x02') {
LAB_437feea6:
      FUN_43809148(pcVar2,uVar6);
    }
    else if (cVar1 == '\x05') {
      candidate_438052d8(pcVar2,uVar6);
    }
    else if (cVar1 == '\0') goto LAB_437feea6;
    if (*pcVar2 == '\0') {
      FUN_437fea60(*(undefined2 *)(pcVar2 + 2),uVar6);
    }
    FUN_43560d1c(0x17);
    FUN_435612ec(DAT_437feedc,pcStack_14);
  } while( true );
}

