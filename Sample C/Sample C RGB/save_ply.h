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