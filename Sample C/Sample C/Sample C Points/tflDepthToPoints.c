#include <stdio.h> 
#include <stdlib.h> 
#include <float.h>  
#include <string.h>
#include <math.h>
#include "tflDepthToPoints.h"


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































/*
Vec3* vec3_points = NULL;
float *_lut_x = NULL;
float *_lut_y = NULL;
float *_lut_zp_t_c = NULL;

const float INF_FLOAT = 3.402823e+38;
const unsigned short INF_USHORT = 65535;

const float TED_SENSOR_PIXEL_SIZE = 0.0056f;
const float TED_FOCAL_LENGTH = 2.16f;
const float TED_LENS_X_CENTER = 1.7892f;
const float TED_LENS_Y_CENTER = 1.3412f;

const unsigned short TED_SENSOR_RES_W = 640;
const unsigned short TED_SENSOR_RES_H = 480;

const int __EDGE_X = TED_SENSOR_RES_W - 1;
const int __EDGE_Y = TED_SENSOR_RES_H - 1;
*/
/*
void initXYZHandler()
{
	// init _lut_x
	if (_lut_x == NULL)
	{
		_lut_x = (float *)malloc(TED_SENSOR_RES_W * sizeof(float));
		for (int i = 0; i < TED_SENSOR_RES_W; i++)
		{
			_lut_x[i] = INF_FLOAT;
		}
	}

	// init _lut_y
	if (_lut_y == NULL)
	{
		_lut_y = (float *)malloc(TED_SENSOR_RES_H * sizeof(float));
		for (int i = 0; i < TED_SENSOR_RES_H; i++)
		{
			_lut_y[i] = INF_FLOAT;
		}
	}
	
	// init _lut_zp_t_c
	if (_lut_zp_t_c == NULL)
	{
		_lut_zp_t_c = (float *)malloc(INF_USHORT * sizeof(float));
		for (int i = 0; i < INF_USHORT; i++)
		{
			_lut_zp_t_c[i] = INF_USHORT;
		}
	}

	// build lookup table for sensor x and y
	float ___mx_t_x0;
	float ___my_t_y0;
	int __x_axis = 0;
	int __y_axis = 0;

	int sensor_size = TED_SENSOR_RES_W * TED_SENSOR_RES_H;
	for (int i = 0; i < sensor_size; i++)
	{
		___mx_t_x0 = ((__x_axis * TED_SENSOR_PIXEL_SIZE) - TED_LENS_X_CENTER) / 2;
		_lut_x[__x_axis] = ___mx_t_x0;

		___my_t_y0 = ((__y_axis * TED_SENSOR_PIXEL_SIZE) - TED_LENS_Y_CENTER) / 2;
		_lut_y[__y_axis] = ___my_t_y0;

		if (__EDGE_X == __x_axis)
		{
			__x_axis = 0;
			__y_axis++;

			continue;
		}

		__x_axis++;
	}

	// build lookup table for zp_t_c
	for (unsigned short z_p = 0; z_p < INF_USHORT; z_p++) {
		float zp_t_c = (z_p - TED_FOCAL_LENGTH) / 2;
		_lut_zp_t_c[z_p] = zp_t_c;
	}
}
*/

// internal function: use inside this .c file only
/*
void _allocateResultMem(int length)
{
	if (vec3_points == NULL) {
		vec3_points = (Vec3 *)malloc(length * sizeof(Vec3));
	}
}*/
/*
Vec3 *depthToPointsXYZ(unsigned short depthArray[], int size)
{
	_allocateResultMem(size);

	int __x_axis = 0;
	int __y_axis = 0;

	float ___mx_t_x0;
	float ___my_t_y0;

	float zp_t_c = 0;
	for (int i = 0; i < size; i++)
	{
		unsigned short z_p = depthArray[i];

		___mx_t_x0 = _lut_x[__x_axis];
		___my_t_y0 = _lut_y[__y_axis];

		zp_t_c = _lut_zp_t_c[z_p];

		vec3_points[i].x = TED_LENS_X_CENTER - (___mx_t_x0  * zp_t_c);
		vec3_points[i].y = TED_LENS_Y_CENTER - (___my_t_y0  * zp_t_c);
		vec3_points[i].z = z_p;

		if (__EDGE_X == __x_axis)
		{
			__x_axis = 0;
			__y_axis++;

			continue;
		}

		__x_axis++;
	}

	return vec3_points;
}

void releaseXYZHandler() 
{	
	free(_lut_x);
	free(_lut_y);
	free(_lut_zp_t_c);

	free(vec3_points);
}*/
