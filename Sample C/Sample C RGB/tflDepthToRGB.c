#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tflDepthToRGB.h"

Vec3 *result = NULL;
unsigned short MIN, MAX;
float MAXMIN;

// this initDepthToRGBHandler() method need to be call one before doing anything else
void initRGBHandler() 
{
	MIN = 65525;
	MAX = 0;
}

// internal function: use inside this .c file only
void _getMaxMin(unsigned short depthArray[], int length) {
	MIN = 65535;
	MAX = 0;

	for (int i = 0; i < length; i++)
	{
		unsigned short value = depthArray[i];

		if (MIN > value)
		{
			MIN = value;
		}

		if (MAX < value)
		{
			MAX = value;
		}
	}

	if (MIN < 1)
	{
		MIN = 1;
	}

	MAXMIN = MAX - MIN;
}

// internal function: use inside this .c file only
void _allocateResultMemRGB(int length) 
{
	if (result != NULL)
		free(result);

	result = (Vec3 *)calloc(length, sizeof(Vec3));
}

/* This function use to convert array of depth value to it's equivalent mapping color in RAINBOW spectrum
 * input  : depthArray[] holding array of items of depth value, each item use 2 byte for holding depth value
 * output : array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
 */
Vec3 *depthToRainbow(unsigned short depthArray[], int length) 
{
	_allocateResultMemRGB(length);
	_getMaxMin(depthArray, length);

	for (int i = 0; i < length; i++)
	{
		float value_ = ((depthArray[i] - MIN) * 1.0) / MAXMIN;
		float  R, G, B;

		R = (value_ < 0.5f) ? 1 - (2 * value_) : 0;
		G = (value_ < 0.5f) ? 2 * value_ : 1 - ((value_ - 0.5f) * 2);
		B = (value_ >= 0.5f) ? (value_ - 0.5f) * 2 : 0;

		result[i].x = R;
		result[i].y = G;
		result[i].z = B;
	}

	return result;
}

/* This function use to convert array of depth value to it's equivalent mapping color in GRAYSCALE spectrum
 * input  : depthArray[] holding array of items of depth value, each item use 2 byte for holding depth value
 * output : array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
 */
Vec3 *depthToGrayscale(unsigned short depthArray[], int length) 
{
	_allocateResultMemRGB(length);
	_getMaxMin(depthArray, length);

	for (int i = 0; i < length; i++)
	{
		float W = 1.0 - (float)((depthArray[i] - MIN)*1.0 / MAXMIN) * 1.0;

		result[i].x = W;
		result[i].y = W;
		result[i].z = W;
	}

	return result;
}

//This method must be called to release all allocated memory used within this library, for the memory leak will not happen
void releaseRGBHandler() {
	free(result);
}

