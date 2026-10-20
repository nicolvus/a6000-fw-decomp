/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43e7ef80" */

/* query "43e7ee00" */

/* query "43e7ee44" */

/* query "43e7eed4" */

/* query "44023400" */

/* query "44024d10" */

/* query "44021914" */

/* query "4402603c" */

/* query "43ad828c" */

void FUN_43ad828c(int param_1)

{
  if (*(char *)(param_1 + 0x14) != '\0') {
    (**(code **)(**(int **)(param_1 + 0x10) + 8))();
    (**(code **)(**(int **)(param_1 + 0xc) + 8))();
  }
  return;
}


/* query "43ad79ae" */

void FUN_43ad79ae(int param_1)

{
  FUN_43ad7ea6(param_1 + 0x14);
  (**(code **)(**(int **)(param_1 + 0x10) + 8))();
  (**(code **)(**(int **)(param_1 + 0xc) + 8))();
  return;
}

