// tfl_DepthToPoints.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"


#include <stdio.h> 
#include <stdlib.h> 
#include <float.h>  
#include <string.h>
#include <math.h>
#include "tfl_DepthToPoints.h"


Vec3* m_Mesh_XYZ = NULL;
int size = 307200;

double* __x_cal;
double* __y_cal;
double* __z_cal;

double _x, _y, _d;

double __x;
double __y;
double __z;

double r = 0.0056f;
double f = 2.16f;
int dy = 240;
int dx = 320;
int hw;

double f2 = 4.6656f;

void initXYZHandler()
{
	if (m_Mesh_XYZ == NULL)
	{
		m_Mesh_XYZ = (Vec3*)malloc(size * sizeof(Vec3));
	}

	__x_cal = (double*)malloc(size * sizeof(double));
	__y_cal = (double*)malloc(size * sizeof(double));
	__z_cal = (double*)malloc(size * sizeof(double));

	for (int h = 0; h < 480; h++)
	{
		for (int w = 0; w < 640; w++)
		{
			hw = h * 640 + w;
			_x = (w - dx) * r;
			_y = (h - dy) * r;

			double x2 = _x * _x;
			double y2 = _y * _y;
			_d = sqrt(x2 + y2 + f2);

			__x_cal[hw] = _x / _d;
			__y_cal[hw] = (-1) * _y / _d;
			__z_cal[hw] = f / _d;
		}
	}
}

Vec3* depthZToXYZ(unsigned short _buffDepthData[], int size)
{
	for (int i = 0; i < 307200; i++)
	{
		__x = _buffDepthData[i] * __x_cal[i];
		__y = _buffDepthData[i] * __y_cal[i];
		__z = _buffDepthData[i] * __z_cal[i];

		m_Mesh_XYZ[i].x = (float)__x;
		m_Mesh_XYZ[i].y = (float)__y;
		m_Mesh_XYZ[i].z = (float)__z;
	}
	return m_Mesh_XYZ;
}

void releaseXYZHandler()
{
	free(m_Mesh_XYZ);
	free(__x_cal);
	free(__y_cal);
	free(__z_cal);
}

