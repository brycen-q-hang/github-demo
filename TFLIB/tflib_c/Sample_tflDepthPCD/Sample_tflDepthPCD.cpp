// Sample_tflDepthPCD.cpp : This file contains the 'main' function. Program execution begins and ends there.
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
using namespace TFL;

int random(int minN, int maxN);

int main()
{
	printf("-- START -- \n");

	uint16_t depthBuf[TFL_FRAME_SIZE]; // 2byte 
	TFL_PointXYZ pcdFullBuff[TFL_FRAME_SIZE];

	unsigned char buffer[614400]; /// 1byte 
	int length = 0;

	FILE* ptr;
	ptr = fopen("Undistort_depth.bin", "rb");  // r for read, b for binary    
	if (!ptr) {
		printf("File not found \n");
	}
	fread(buffer, sizeof(buffer), 1, ptr);
	fclose(ptr);

	FILE* pt;
	pt = fopen("PCL_PointXYZ.ply", "w+");  //  Write ply file
	fprintf(pt, "ply\nformat ascii 1.0\nelement vertex 307200\nproperty float x\nproperty float y\nproperty float z\nend_header\n");
	if (!pt) {
		printf("File not found \n");
	}

	for (int i = 0; i < 614400; i = i + 2) //byte --> ushort ( 2byte)
	{
		int count_fake = i / 2;
		depthBuf[count_fake] = buffer[i + 1];
		depthBuf[count_fake] = depthBuf[count_fake] << 8;

		int seed = 0;
		if (i % 31 == 0)
		{
			seed = random(1, 100);
		}
		depthBuf[count_fake] |= buffer[i] + (unsigned short)seed;
	}
	length = sizeof(depthBuf) / sizeof(depthBuf[0]);

	//Start CreateMesh 	RESULT
	TFL_RESULT RESULT = DepthToPCD(depthBuf, pcdFullBuff);
	
	if (RESULT != TFL_RESULT::TFL_OK)
	{
		printf("Error code is : %d \n", RESULT);
	}
	for (int i = 0; i < length; i++)
	{
		fprintf(pt, "%f %f %f\n", pcdFullBuff[i].x, pcdFullBuff[i].y, pcdFullBuff[i].z);
	}

	fclose(pt);
	
	//End CreateMesh
	printf("-- FINISHED -- \n");
	system("pause");
}

int random(int minN, int maxN)
{
	return minN + rand() % (maxN + 1 - minN);
}