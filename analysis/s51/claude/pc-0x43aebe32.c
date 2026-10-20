
void FUN_43aebe32(uint param_1,uint param_2,ushort *param_3)

{
  if (param_1 < *param_3) {
    *param_3 = (ushort)param_1;
    return;
  }
  if (*param_3 < param_2) {
    *param_3 = (ushort)param_2;
  }
  return;
}

