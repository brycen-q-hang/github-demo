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

// slider for adjacent positions
static int _lut_WinSlider[8];

// lookup table for faster processing
static bool* _lut_left_640 = NULL;
static bool* _lut_top_480 = NULL;
static bool* _lut_right_640 = NULL;
static bool* _lut_bottom_480 = NULL;

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
static void releaseNoiseHandler() {
	// sensor: 640x480
	free(_lut_left_640);
	free(_lut_top_480);
	free(_lut_right_640);
	free(_lut_bottom_480);
}

// This method need to be call once before using depthZToXYZ
static void initNoiseHandler() {
	if (_lut_left_640 == NULL) {
		_lut_left_640 = (bool*)calloc(TFL_FRAME_SIZE, sizeof(bool));
		_lut_top_480 = (bool*)calloc(TFL_FRAME_SIZE, sizeof(bool));
		_lut_right_640 = (bool*)calloc(TFL_FRAME_SIZE, sizeof(bool));
		_lut_bottom_480 = (bool*)calloc(TFL_FRAME_SIZE, sizeof(bool));

		for (int i = 0; i < TFL_FRAME_SIZE; i++) {
			bool isTop;
			if (i < TFL_FRAME_WIDTH) {
				isTop = true;
			}
			else {
				isTop = false;
			}

			bool isBottom;
			if (i >= TFL_FRAME_SIZE - TFL_FRAME_WIDTH) {
				isBottom = true;
			}
			else {
				isBottom = false;
			}

			bool isLeft;
			if ((i + 1) % TFL_FRAME_WIDTH == 0) {
				isLeft = true;
			}
			else {
				isLeft = false;
			}

			isLeft = isLeft || (i) % TFL_FRAME_WIDTH == 0;

			bool isRight;
			if ((i + 2) % TFL_FRAME_WIDTH == 0) {
				isRight = true;
			}
			else {
				isRight = false;
			}

			isRight = isRight || (i + 1) % TFL_FRAME_WIDTH == 0;

			_lut_top_480[i] = isTop;
			_lut_bottom_480[i] = isBottom;
			_lut_left_640[i] = isLeft;
			_lut_right_640[i] = isRight;
		}

		_lut_WinSlider[0] = 1;
		_lut_WinSlider[1] = TFL_FRAME_WIDTH;
		_lut_WinSlider[2] = (TFL_FRAME_WIDTH + 1);
		_lut_WinSlider[3] = (TFL_FRAME_WIDTH - 1);
		_lut_WinSlider[4] = -1;
		_lut_WinSlider[5] = -TFL_FRAME_WIDTH;
		_lut_WinSlider[6] = -(TFL_FRAME_WIDTH + 1);
		_lut_WinSlider[7] = -(TFL_FRAME_WIDTH - 1);
	}
}

/**
/// @brief This MarkNoise function can be call each time user want to detect noisy points in an input point cloud data
/// @param pcdFullBuf [IN] Fixed-size TFL_PointXYZ array have TFL_FRAME_SIZE number of item, holding point cloud data
/// @param sensitiveFactor [IN] This input value ranging from 2 to 100 and Use small number for higher sensitive to noise detection
/// @param noiseFlags [OUT] Fixed-size bool array have TFL_FRAME_SIZE number of item. Item with false value reprepresent for the equivalent noisy point in pcdBuff
/// @param countNoise [OUT] Number of detected noisy points
/// @return Unified processing result
*/
TFL_RESULT  TFL::MarkPCDNoise(TFL_PointXYZ pcdFullBuf[TFL_FRAME_SIZE], uint16_t sensitiveFactor, bool noiseFlags[TFL_FRAME_SIZE], uint16_t &countNoise)
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
		initNoiseHandler();		
	}

	if (eRetExpiry != TFL_RESULT::TFL_OK)
		return eRetExpiry;	// Return latched error code.	

	countNoise = 0; 

	if (sensitiveFactor < 19)
	{
		sensitiveFactor = 19;// rule-of-thumb
	}

	// scan for neighbours
	for (int i = 0; i < TFL_FRAME_SIZE; i++)
	{
		// skip if current index is in the matrix's edge
		if (_lut_left_640[i] ||
			_lut_top_480[i] ||
			_lut_right_640[i] ||
			_lut_bottom_480[i]) {

			continue;
		}

		// current item to consider
		TFL_PointXYZ v = pcdFullBuf[i];

		// scan surrounding for neighbour
		int countNeighbour = 0;
		for (int j = 0; j < 8; j++)
		{
			int idx_now = _lut_WinSlider[j] + i;

			// skip if current neighbour is in the matrix's edge
			if (_lut_left_640[idx_now] ||
				_lut_top_480[idx_now] ||
				_lut_right_640[idx_now] ||
				_lut_bottom_480[idx_now])
			{
				continue;
			}

			// current adjacent
			TFL_PointXYZ v_now = pcdFullBuf[idx_now];

			// distance between v and v_now
			float z_d = 0;
			if (v_now.z > v.z)
			{
				z_d = v_now.z - v.z;
			}
			else
			{
				z_d = v.z - v_now.z;
			}

			if (z_d < sensitiveFactor)// adjacent will be considered as neighbour if there is only a small distance between them
			{
				countNeighbour++;

				if (countNeighbour >= 3)
				{
					break;
				}
			}
		}

		if (countNeighbour >= 3)
		{
			noiseFlags[i] = false;
		}
		else
		{
			// if not enough 3 neighbours, then current point is considered as outlier (or noise)			
			noiseFlags[i] = true;
			countNoise++;
		}

	}

	return TFL_RESULT::TFL_OK;
}