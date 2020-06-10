#include "Sample_LIB.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int Get_value_of_arr(int a[SiZE])
{
    a[0] = 9999;
    a[1] = 2222;
    a[2] = 3333;

    int b = 99;
    return b;
}

int Get_value_of_struct(TFL_PointXYZ str[SiZE])
{
    str[0].x = 1;
    str[0].y = 2;
    str[0].z = 3;

    str[1].x = 11;
    str[1].y = 22;
    str[1].z = 33;

    str[2].x = 111;
    str[2].y = 222;
    str[2].z = 333;

    int a = 7890;
    return a;
}