#pragma once

#define EXPORT __declspec(dllexport)

typedef struct Vector Vec3;  
struct Vector
{
    float x;
    float y;
    float z; 
};

extern "C" EXPORT void initDepthToPointXYZHandler();
extern "C" EXPORT Vec3* depthToPointsXYZ(unsigned short depthArray[], int size);
extern "C" EXPORT void ReleaseDepthToPointXYZHandler();
