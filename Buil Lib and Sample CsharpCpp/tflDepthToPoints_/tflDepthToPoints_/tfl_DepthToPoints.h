#pragma once
#include <stdbool.h>
#define EXPORT extern "C" __declspec(dllexport) 

typedef struct Vector Vec3;
struct Vector
{
	float x;
	float y;
	float z;
};

extern "C" EXPORT void initXYZHandler();
extern "C" EXPORT Vec3* depthZToXYZ(unsigned short depthArray[], int size);
extern "C" EXPORT void releaseXYZHandler();
