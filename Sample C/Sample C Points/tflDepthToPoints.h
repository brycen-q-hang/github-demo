#include <stdbool.h>
#define EXPORT extern "C" __declspec(dllexport) 

typedef struct Vector Vec3;  
struct Vector
{
    float x;
    float y;
    float z; 
};

void initXYZHandler();
Vec3* depthZToXYZ(unsigned short depthArray[], int size);
void releaseXYZHandler();
