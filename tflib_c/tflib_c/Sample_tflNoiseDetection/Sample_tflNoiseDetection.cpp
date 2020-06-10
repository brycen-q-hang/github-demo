// Sample_tflNoiseDetection.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <stdio.h>
#include <string.h> 
#include <stdlib.h>
#include <time.h> 
#include <stdbool.h>
#include <math.h> 
#include <float.h> 
#include <limits.h> 
#include <stdint.h> 

#include "tflib_c.h"
using namespace TFL_Common;

int main()
{
    printf("START \n");

    TFL_PointXYZ pcdFullBuf[TFL_FRAME_SIZE];
    FILE* File_input;
    File_input = fopen("data.ply", "r");   

    char str[1024];
    if (File_input == NULL)
    {
        printf("ERR: Read file");
        exit(EXIT_FAILURE);
        return 0;
    }
    int Count_array = 0;

    while (fgets(str, 1024, File_input) != NULL)
    {

        int XYZ = 0;
        char* p = strtok(str, " ");

        while (p != NULL)
        {
            if (XYZ == 0)
            {
                pcdFullBuf[Count_array].x = strtod(p, NULL);
            }

            if (XYZ == 1)
            {
                pcdFullBuf[Count_array].y = strtod(p, NULL);
            }

            if (XYZ == 2)
            {
                pcdFullBuf[Count_array].z = strtod(p, NULL);
            }

            XYZ++;
            p = strtok(NULL, " ");
        }

        Count_array++;
        if (Count_array == TFL_FRAME_SIZE)
        {
            break;
        }
    }
    fclose(File_input);

    uint16_t sensitiveFactor = 19;

    FILE* File_output;
    File_output = fopen("PCL_Noise.ply", "w");

    bool noiseFlags[TFL_FRAME_SIZE];
    uint16_t countNoise = 0;
    TFL_RESULT TFL_RESULT = MarkPCDNoise(pcdFullBuf, sensitiveFactor, noiseFlags, countNoise);
    printf("numNoise is: %d \n", countNoise);
    printf("Return is: %d \n", TFL_RESULT);

    fprintf(File_output, "ply\nformat ascii 1.0\nelement vertex 307200\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n");
    for (int i = 0; i < TFL_FRAME_SIZE; i++)
    {
        if (noiseFlags[i] == false) //Non Noise
        {
            //numdata ++;
            fprintf(File_output, "%0.2f %0.2f %0.1f 255 255 255 \n", pcdFullBuf[i].x, pcdFullBuf[i].y, pcdFullBuf[i].z);
        }
        else //Noise
        {
            fprintf(File_output, "%0.2f %0.2f %0.1f 255 0 0 \n", pcdFullBuf[i].x, pcdFullBuf[i].y, pcdFullBuf[i].z);
        }
    }
    fclose(File_output);

    printf("-- FINISH -- \n");

    return 0;
}
