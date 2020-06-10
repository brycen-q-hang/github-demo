// Sample4_tflUndistort.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include <string.h> 
#include <stdlib.h>
#include <time.h> 
#include <stdbool.h>
#include <math.h> 
#include <float.h> 
#include <limits.h> 
#include <stdint.h> 
#include <iostream> 

#include "tflib_c.h"

#define MeasureTime 1	// 0- No   1- Yes
#define SaveUndistort 1
#define WriteToBinary 1
using namespace TFL;

 
int main()
{
	printf("Start Undistort \n");
	uint16_t depthBuf[TFL_FRAME_SIZE]; // 2byte 
	uint16_t depthBufUnDistorted[TFL_FRAME_SIZE];

	unsigned char buffer[614400];   
	int length = 0;
	FILE* ptr;
	ptr = fopen("depth.bin", "rb");  // r for read, b for binary 
	if (!ptr) {
		printf("File not found \n");
	}
	fread(buffer, sizeof(buffer), 1, ptr);
	fclose(ptr);


#if WriteToBinary 
	FILE* pt_b;
	pt_b = fopen("Output_Undistort.bin", "wb");  // r for read, b for binary 
	if (!pt_b)
	{
		printf("File not found \n");
	} 
#endif


#if SaveUndistort

	FILE* Upt;
	Upt = fopen("Data_Undistort.csv", "w+");  //  Write Data Undistort
	//fprintf (pt, "end_header\n");
	if (!Upt) {
		printf("File not found \n");
	}

#endif
#if MeasureTime
	FILE* pt;
	pt = fopen("Time_Processing_Undistort.csv", "w+");  //  Write ply file
	//fprintf (pt, "end_header\n");
	if (!pt) {
		printf("File not found \n");
	}
	fprintf(pt,"Time by Milliseconds (ms)\n");
	int a = 0;
	while (a < 100)
	{
		a++;
#endif  
		//	Using code to convert ushort to byte
		/*
		clock_t time_undistort = clock();
		for (int i = 0; i < 614400; i = i + 2) //byte --> ushort ( 2byte)
		{
			int count_fake = i / 2;
			depthBuf[count_fake] = buffer[i + 1] << 8 | buffer[i];
		}
		float total_time = (float)(clock() - time_undistort) / (CLOCKS_PER_SEC / 1000);
		*/ 
		//	Using memcpy function to convert ushort to byte 
		memcpy(depthBuf, buffer, 614400);

#if MeasureTime 
		clock_t time_undistortaa = clock();
#endif

		TFL_RESULT TFL_RESULT = Undistort(depthBuf, depthBufUnDistorted);
		if (TFL_RESULT != TFL_RESULT::TFL_OK)     // Stop program if RESULT other TFL_OK
		{
			printf("Error code is : %d \n", TFL_RESULT);
			return 0;
		}


#if MeasureTime

		float total_time_dv = (float)(clock() - time_undistortaa) / (CLOCKS_PER_SEC / 1000);
		fprintf(pt, "Time UndistortLens     %f\n", total_time_dv);
		printf("Time UndistortLens,NO[%d] = %f \n",a, total_time_dv);
	} 
	fclose(pt); 
#endif
#if SaveUndistort
	for (int i = 0; i < TFL_FRAME_SIZE; i++)
	{
		fprintf(Upt, "NO[%d]     =    %hi\n",i, depthBufUnDistorted[i]);
	}
	fclose(Upt);
#endif
	
#if WriteToBinary 
	fwrite(depthBufUnDistorted, sizeof(depthBufUnDistorted), 1, pt_b); 
	fclose(pt_b);
#endif

	 
	printf("FINISHED\n");
}




//void depthRawToImage(uint16_t depthBufUnDistorted[TFL_FRAME_SIZE], cv::String outputimage)
//{
//	cv::Mat imageOutput(480, 640, CV_16U, depthBufUnDistorted);
//	double min;
//	double max;
//	cv::minMaxIdx(imageOutput, &min, &max);
//	imageOutput.convertTo(imageOutput, CV_8UC1, 255 / (max - min), -min);
//	equalizeHist(imageOutput, imageOutput);
//	cv::imwrite(outputimage, imageOutput);
//	cv::imshow(outputimage, imageOutput);
//	cv::waitKey();
//}