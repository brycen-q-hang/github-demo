#include <stdbool.h>
#include <string.h>
#define EXPORT extern "C" __declspec(dllexport)

typedef struct struct_vector Vec3;
struct struct_vector
{
	float x;
	float y;
	float z;
};

// this initDepthToRGBHandler() method need to be call one before doing anything else
void initRGBHandler();

/* This function use to convert array of depth value to it's equivalent mapping color in RAINBOW spectrum
 * input  : depthArray[] holding array of items of depth value, each item use 2 byte for holding depth value
 * output : array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
 */
Vec3 *depthToRainbow(unsigned short array_[], int length);

/* This function use to convert array of depth value to it's equivalent mapping color in GRAYSCALE spectrum
 * input  : depthArray[] holding array of items of depth value, each item use 2 byte for holding depth value
 * output : array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
 */
Vec3 *depthToGrayscale(unsigned short array_[], int length);

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
void releaseRGBHandler();