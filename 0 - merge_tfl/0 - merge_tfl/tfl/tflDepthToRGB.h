#pragma once

#include <stdbool.h>
#include <string.h>
#define EXPORT __declspec(dllexport)

typedef struct struct_vector Vec3;
struct struct_vector
{
	float X;
	float Y;
	float Z;
};

