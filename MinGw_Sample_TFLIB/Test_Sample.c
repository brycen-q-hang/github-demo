#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "Sample_LIB.h"
#include <stdbool.h>
#include <time.h>

int main()
{
    // int a[SiZE];
    // int b = Get_value_of_arr(a);
    // printf("Value of b is: %d \n", b);
    // printf("Adress b is: %x \n", &b);
    // for(int i = 0; i < 3; i++)
    // {
    //     printf("Phan tu thu %d la: %d \n", i, a[i]);
    //     printf("Adress a is: %x \n", a[i]);
    // }

    TFL_PointXYZ str[SIZE];
    int _b = Get_value_of_struct(str);
    
    for(int i = 0; i < SiZE; i++)
    {
        printf("Value of array is: %f %f %f \n", str[i].x, str[i].y, str[i].z);
    }
    return 0;  
}