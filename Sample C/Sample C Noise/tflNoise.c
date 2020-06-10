#include "tflNoise.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


int _countLastNoise = 0;
bool* _outlier_flags;

// slider for adjacent positions
int _lut_WinSlider[8];

// lookup table for faster processing
bool* _lut_left_640 = NULL;
bool* _lut_top_480 = NULL;
bool* _lut_right_640 = NULL;
bool* _lut_bottom_480 = NULL;

// this InitNoiseHandler() method need to be call one before doing anything else
void initNoiseHandler() {
	if (_lut_left_640 == NULL) {
		int sensor_w = 640;
		int sensor_h = 480;

		int s = sensor_w * sensor_h;  //sensor of tof start run from 0 to 307199

		_lut_left_640 = (bool*)calloc(s, sizeof(bool));
		_lut_top_480 = (bool*)calloc(s, sizeof(bool));
		_lut_right_640 = (bool*)calloc(s, sizeof(bool));
		_lut_bottom_480 = (bool*)calloc(s, sizeof(bool));

		for (int i = 0; i < s; i++) {
			bool isTop;
			if (i < sensor_w) {
				isTop = true;
			}
			else {
				isTop = false;
			}

			bool isBottom;
			if (i >= s - sensor_w) {
				isBottom = true;
			}
			else {
				isBottom = false;
			}

			bool isLeft;
			if ((i + 1) % sensor_w == 0) {
				isLeft = true;
			}
			else {
				isLeft = false;
			}

			isLeft = isLeft || (i) % sensor_w == 0;

			bool isRight;
			if ((i + 2) % sensor_w == 0) {
				isRight = true;
			}
			else {
				isRight = false;
			}

			isRight = isRight || (i + 1) % sensor_w == 0;

			_lut_top_480[i] = isTop;
			_lut_bottom_480[i] = isBottom;
			_lut_left_640[i] = isLeft;
			_lut_right_640[i] = isRight;
		}

		_lut_WinSlider[0] = 1;
		_lut_WinSlider[1] = sensor_w;
		_lut_WinSlider[2] = (sensor_w + 1);
		_lut_WinSlider[3] = (sensor_w - 1);
		_lut_WinSlider[4] = -1;
		_lut_WinSlider[5] = -sensor_w;
		_lut_WinSlider[6] = -(sensor_w + 1);
		_lut_WinSlider[7] = -(sensor_w - 1);
	}
}

// This MarkNoise function can be call each time user want to detect outliner point (or noise) for the input organized-point-cloud
//
// input 1: Vector3 *data array represent for input point clouds. Each item of the array holding x y z of the points
// input 2: threshold ranging from 19..100. The smaller the threshold, the more sensitive to the noise detection
// input 3: sensor_w number of sensor pixel in width
// input 4: sensor_h number of sensor pixel in heigh
// 
// Output : bool array represent for noise of the input Vector3 *data. Each item of the array holding bool value, 
// 'true' for outlier/noise and 'false' for non-noise
bool* markNoise(Vec3 *data, float threshold, int sensor_w, int sensor_h) 
{
	if (threshold < 19)
	{
		threshold = 19;// rule-of-thumb
	}

	// sensor size
	int size = sensor_w * sensor_h;

	// init noise list for later use
	free(_outlier_flags);
	_outlier_flags = (bool*)calloc(size, sizeof(bool)); //NoiseList == flgNoise thay thế cho mảng Bool ở C#

	// scan for neighbours
	_countLastNoise = size;
	for (int i = 0; i < size; i++)
	{
		// skip if current index is in the matrix's edge
		if (_lut_left_640[i] || 
			_lut_top_480[i] || 
			_lut_right_640[i] || 
			_lut_bottom_480[i]) {

			continue;
		}

		// current item to consider
		Vec3 v = data[i];

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
			Vec3 v_now = data[idx_now];

			// distance between v and v_now
			float z_d = 0;
			if (v_now.Z > v.Z)
			{
				z_d = v_now.Z - v.Z;
			}
			else
			{
				z_d = v.Z - v_now.Z;
			}

			if (z_d < threshold)// adjacent is neighbour if there is only a small distance between them
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
			_outlier_flags[i] = false;
			_countLastNoise = _countLastNoise - 1;
		}
		else
		{
			// if not enough 3 neighbours, then current point is considered as outlier (or noise)
			_outlier_flags[i] = true;
		}
	}

	return _outlier_flags;
}

// This function should be call after MarkNoise(..)
// Output: number of noise detected from the last call of MarkNoise
int GetLastNoiseCount() {
	return _countLastNoise;
}

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
void releaseNoiseHandler() {
	free(_outlier_flags);
	_countLastNoise = 0;

	// sensor: 640x480
	free(_lut_left_640);
	free(_lut_top_480);
	free(_lut_right_640);
	free(_lut_bottom_480);
}
