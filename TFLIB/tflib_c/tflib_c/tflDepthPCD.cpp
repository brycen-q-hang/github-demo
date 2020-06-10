/* (C) 2020 by Brycen Group in international.
 */
#include "pch.h"

#include <stdio.h> 
#include <stdlib.h> 
#include <float.h>  
#include <string.h>
#include <math.h>
#include "tflib_c.h"
#include "tflLicense.h"

using namespace TFL;
static bool			bFirstExec = true;
static TFL_RESULT	eRetExpiry = TFL_RESULT::TFL_ERROR;

static float* __x_cal = NULL;
static float* __y_cal = NULL;
static float* __z_cal = NULL;

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
static void releaseXYZHandler()
{
	if (__x_cal != NULL) {
		free(__x_cal);
		__x_cal = NULL;
	}

	if (__y_cal != NULL) {
		free(__y_cal);
		__y_cal = NULL;
	}

	if (__z_cal != NULL) {
		free(__z_cal);
		__z_cal = NULL;
	}
}

// This method need to be call once before using depthZToXYZ
static void initXYZHandler()
{
	if (__x_cal == NULL)
	{
		const double	r = 0.0056f;
		const double	f = 2.16f;
		const double	f2 = 4.6656f;
		const int	dy = 240;
		const int	dx = 320;

		double _x, _y, _d;
		double x2, y2;

		int hw;

		releaseXYZHandler();

		__x_cal = (float*)malloc(TFL_FRAME_SIZE * sizeof(float));
		__y_cal = (float*)malloc(TFL_FRAME_SIZE * sizeof(float));
		__z_cal = (float*)malloc(TFL_FRAME_SIZE * sizeof(float));

		hw = 0;
		for (int h = 0; h < TFL_FRAME_HEIGHT; h++)
		{
			for (int w = 0; w < TFL_FRAME_WIDTH; w++)
			{
				//hw = h * TFL_FRAME_WIDTH + w;
				_x = (w - dx) * r;
				_y = (h - dy) * r;

				x2 = _x * _x;
				y2 = _y * _y;
				_d = sqrt(x2 + y2 + f2);

				__x_cal[hw] = (float)(_x / _d);
				__y_cal[hw] = (float)((-1) * _y / _d);
				__z_cal[hw] = (float)(f / _d);

				hw++;
			}
		}
	}
}

/**
/// @brief This function for building point cloud from the input depth data
/// @param deptBuf [IN] Fixed-size array of uint16_t holding storing depth buffer
/// @param pcdBuf [OUT] Fixed-size TFL_PointXYZ array of TFL_FRAME_SIZE number item. Each item hold X Y Z value in Cartesian coordinate system for all input depth value.
/// @return Unified processing result
*/
TFL_RESULT  TFL::DepthToPCD(uint16_t depthBuf[TFL_FRAME_SIZE], TFL_PointXYZ pcdBuf[TFL_FRAME_SIZE])
{
	// Check of Expiry Date.
	if (bFirstExec) {
		bFirstExec = false;

		ExpiryDate cED = ExpiryDate();
		eRetExpiry = cED.CheckExpiryDate(TFL_DEFAULT_EXPIRYDAYS);
		if (eRetExpiry != TFL_RESULT::TFL_OK)
		{
			return eRetExpiry;
		}

		// This method need to be call one before doing anything else
		initXYZHandler();
	}

	if (eRetExpiry != TFL_RESULT::TFL_OK)
		return eRetExpiry;	// Return latched error code.	

	// Main process is from here.
	for (int i = 0; i < TFL_FRAME_SIZE; i++)
	{
		pcdBuf->x = *depthBuf * __x_cal[i];
		pcdBuf->y = *depthBuf * __y_cal[i];
		pcdBuf->z = *depthBuf * __z_cal[i];

		depthBuf++;
		pcdBuf++;
	}

	return TFL_RESULT::TFL_OK;
}
