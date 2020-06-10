/* (C) 2020 by Brycen Group
 * This library developed by Brycen ToF team
 */

#pragma once
#include <stdbool.h>
#define EXPORT __declspec(dllexport)

// Define the Vec3 structure
// The Vec3 will be used throughout this lib, for holding 3 float value
typedef struct struct_vec Vec3;
struct struct_vec
{
	float x;
	float y;
	float z;
};

/*-----------------------------------------------------------------------------------------------------------------------------
* HEADER for file tflNoise.cpp

Integration pipeline:

Step 1: call initNoiseHandler() once before using markNoise
Step 2: call markNoise(...) each time you want to detect noise from the input X Y Z array
Step 3: call releaseNoiseHandler() once, after you done using the depthZToXYZ in your program
-----------------------------------------------------------------------------------------------------------------------------*/

// This initNoiseHandler() method need to be call once before using markNoise()
extern "C" EXPORT void initNoiseHandler();

// This MarkNoise function can be call each time user want to detect outliner point (or noise) for the input organized-point-cloud
//
// INPUT:
// * param 1: Vector3 *data array represent for input point clouds. Each item of the array holding x y z of the points
// * param 2: threshold ranging from 19..100. The smaller the threshold, the more sensitive to the noise detection
// * param 3: sensor_w number of sensor pixel in width
// * param 4: sensor_h number of sensor pixel in heigh
// 
// OUTPUT:
// * param 5: out_countNoise is the number of points recognized as a outlier/noise
// * return bool array represent for noise of the input Vec3 *data. Each item of the array will hold bool value, 'true' for outlier/noise and 'false' for non-noise
extern "C" EXPORT bool* markNoise(Vec3 *data, float threshold, int sensor_w, int sensor_h, unsigned int &out_countNoise);

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
extern "C" EXPORT void releaseNoiseHandler();

/*-----------------------------------------------------------------------------------------------------------------------------
* HEADER for file tflDepthToRGB.cpp

Integration pipeline:

Step 1: call initRGBHandler() once before using markNoise
Step 2: call depthToRainbow(...) or depthToGrayscale(...) each time you want to generate the RGB color for the input depth data
Step 3: call releaseRGBHandler() once, after you done using the depthToRainbow or depthToGrayscale in your program
-----------------------------------------------------------------------------------------------------------------------------*/

// this initDepthToRGBHandler() method need to be call once before using depthToRainbow or depthToGrayscale
extern "C" EXPORT void initRGBHandler();

// This function use to convert array of depth value to it's equivalent mapping color in RAINBOW spectrum
// * input  : depthArray[] holding array of items of depth value, each item use 2 byte for holding depth value
// * output : array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
extern "C" EXPORT Vec3 *depthToRainbow(unsigned short array_[], int length);

// This function use to convert array of depth value to it's equivalent mapping color in GRAYSCALE spectrum
// * input  : depthArray[] holding array of items of depth value, each item use 2 byte for holding depth value
// * output : array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
extern "C" EXPORT Vec3 *depthToGrayscale(unsigned short array_[], int length);

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
extern "C" EXPORT void releaseRGBHandler();

/*-----------------------------------------------------------------------------------------------------------------------------
* HEADER for file tflDepthToPoints.cpp

Integration pipeline:

Step 1: call initXYZHandler() once
Step 2: call depthZToXYZ(...) each time you want to have the point cloud from depth z[] data
Step 3: call releaseXYZHandler() once, after you done using the depthZToXYZ in your program
-----------------------------------------------------------------------------------------------------------------------------*/

// This initXYZHandler() method need to be call once before using depthZToXYZ
extern "C" EXPORT void initXYZHandler();

// This function for building point cloud from the input depth z[] data
// * input  : depthArray[] holding array of items of depth value
// * output : array of item of struct Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
extern "C" EXPORT Vec3* depthZToXYZ(unsigned short depthArray[], int size);

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
extern "C" EXPORT void releaseXYZHandler();