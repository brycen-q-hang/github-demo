/* (C) 2020 by Brycen Group in international.
 */
#include "pch.h" 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc/imgproc.hpp>  
#include <opencv2/core/types.hpp>

#include "tflib_c.h"
#include "tflLicense.h"

using namespace cv;
using namespace TFL;

static bool			bFirstExec = true;
static TFL_RESULT	eRetExpiry = TFL_RESULT::TFL_ERROR;

static Mat			TED_cam_matrix;
static Mat			TED_distCoeff;

static Mat 			NewCameraMatrix;	

static Mat			Map1;				
static Mat			Map2;				

static void releaseUndistortHandler() {
	TED_cam_matrix.release();
	TED_distCoeff.release();
	Map1.release();
	Map2.release();
}

// This method need to be call once before using depthZToXYZ
static void initUndistorHandler()
{	
	TED_cam_matrix = (Mat1d(3, 3) <<
		3.5053614150161587e+02f, 0.0f, 3.1579134071223871e+02f,
		0, 3.5057707108015757e+02f, 1.9552750164723298e+02f,
		0.0f, 0.0f, 1.0f);

	TED_distCoeff = (Mat1d(1, 5) <<
		-2.4426975441401277e-01,
		9.9658626995523386e-02,
		-2.1129473041189171e-03,
		6.6627903393590778e-04,
		-2.2654325703365986e-02);
	
	cv::initUndistortRectifyMap(TED_cam_matrix, TED_distCoeff, Mat(), TED_cam_matrix, Size(TFL_FRAME_WIDTH, TFL_FRAME_HEIGHT), CV_16SC2, Map1, Map2);
}

/**
/// @brief This function for fixing the optical distortion from the raw depth image of TED ToF camera.
/// @param depthBuf [IN] Fixed-size array of uint16_t holding storing depth buffer.
/// @param depthBufUnDistorted [OUT] Fixed-size array of uint16_t holding storing depthBufUnDistorted which undistorted by Undistort function.
/// @return Unified processing result.
*/
TFL_RESULT TFL::Undistort(uint16_t depthBuf[TFL_FRAME_SIZE], uint16_t depthBufUnDistorted[TFL_FRAME_SIZE])
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

		initUndistorHandler();
	}

	if (eRetExpiry != TFL_RESULT::TFL_OK)
		return eRetExpiry;	// Return latched error code.

	// Main process is from here.
	Mat input(TFL_FRAME_HEIGHT, TFL_FRAME_WIDTH, CV_16U, depthBuf);
	Mat U_undistort(TFL_FRAME_HEIGHT, TFL_FRAME_WIDTH, CV_16U);
	
	cv::remap(input, U_undistort, Map1, Map2, INTER_LINEAR, BORDER_CONSTANT);

	memcpy(depthBufUnDistorted, U_undistort.data, TFL_FRAME_SIZE * 2);
	 
	return TFL_RESULT::TFL_OK;
}


