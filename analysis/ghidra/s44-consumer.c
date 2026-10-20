/* S41: read-only exports. */

/* 436cf0c8 */

undefined4 FUN_436cf0c8(uint param_1,undefined4 param_2)

{
  if (param_1 < 0xe) {
    if (*(int *)(DAT_436cf190 + 0x436cf0f0 + param_1 * 4) == 0) {
      *(undefined4 *)(DAT_436cf190 + 0x436cf0f0 + param_1 * 4) = param_2;
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
    FUN_436cf01c(0x165,1,1,DAT_436cf194 + 0x436cf104,param_1,param_2);
    FUN_43902718(DAT_436cf198 + 0x436cf10e,param_1);
  }
  else {
    FUN_436cf01c(0x165,1,1,DAT_436cf188 + 0x436cf0de,param_1,param_2);
    FUN_43902718(DAT_436cf18c + 0x436cf0e6);
  }
  return 1;
}

