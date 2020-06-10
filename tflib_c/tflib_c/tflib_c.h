/* (C) 2020 by Brycen Group in international.
 */
#pragma once

 /*------------------------------------------------------------------------------------
				include files
 ------------------------------------------------------------------------------------*/
#include	 <stdint.h>

namespace TFL_Common
{
	/*------------------------------------------------------------------------------------
				Don't define "TFLIB_EXPORTS " in case of this Dll use.
	------------------------------------------------------------------------------------*/
#ifdef TFLIB_EXPORTS
#define TFL_DLL __declspec(dllexport)
#else
#define TFL_DLL __declspec(dllimport)
#endif

	/*------------------------------------------------------------------------------------
				definitions
	------------------------------------------------------------------------------------*/
#define	TFL_FRAME_W_TB_TOF_SQ930PU_IV		640
#define	TFL_FRAME_H_TB_TOF_SQ930PU_IV		480
#define	TFL_FRAME_SIZE_TB_TOF_SQ930PU_IV	(TFL_FRAME_W_TB_TOF_SQ930PU_IV * TFL_FRAME_H_TB_TOF_SQ930PU_IV)

#define TFL_FRAME_WIDTH						TFL_FRAME_W_TB_TOF_SQ930PU_IV
#define TFL_FRAME_HEIGHT					TFL_FRAME_H_TB_TOF_SQ930PU_IV
#define TFL_FRAME_SIZE						TFL_FRAME_SIZE_TB_TOF_SQ930PU_IV
#define TFL_LENGTH_COLOR                    5000
	/*------------------------------------------------------------------------------------
				enum, struct and class
	------------------------------------------------------------------------------------*/
	///This is used as execution result from Library API.
	enum struct TFL_RESULT
	{
		TFL_OK = 0,             ///< Value: 0  (No error from the the function execution)
		//Related to ExpiryDate
		TFL_ERROR = 1,          ///< Value: 1  (Unable to update the expiration date)
		TFL_EXPIRED = 2,        ///< Value: 2  (The library expired, the TFLib’s function halt)
		TFL_CHANGED = 3,        ///< Value: 3  (The expiration date value of the registry was changed)
		TFL_ZERODAY = 4,		///< Value: 4  (The last day to use the lib)

		//Related to Basic Function			(10-)
		//Related to Measure Cube			(100-)
		//Related to Detect People			(150-)
	};

	///This is used throughout this lib, for holding 3 float value
	struct TFL_PointXYZ
	{
		float x;
		float y;
		float z;
	};

	///This is used throughout this lib, for storing red green blue value of color in RGB space.
	struct TFL_Color
	{
		float r;
		float g;
		float b;
	};

	/*------------------------------------------------------------------------------------
				functions
	------------------------------------------------------------------------------------*/
	/**
	/// @brief This function for building point cloud from the input depth z[] data
	/// @param deptBuf [IN] holding array of items of depth value, item of the array use 2 bytes holding depth value for each
	/// @param pcdBuf [OUT] array of item of TFL_PointXYZ, each item holding 3 value of x y and z axis
	/// @return Unified processing result
	*/
	extern "C" TFL_RESULT TFL_DLL		DepthToPCD(uint16_t depthBuf[TFL_FRAME_SIZE], TFL_PointXYZ pcdBuf[TFL_FRAME_SIZE]);

	/**
	/// @brief This MarkNoise function can be call each time user want to detect outliner point (or noise) for the input organized-point-cloud
	/// @param pcdFullBuf [IN] Fixed-size TFL_PointXYZ array have TFL_FRAME_SIZE   number of item, holding point cloud data
	/// @param sensitiveFactor [IN] This input value ranging from 2 to 100 and Use small number for higher sensitive to noise detection
	/// @param noiseFlags [OUT Fixed-size bool array have TFL_FRAME_SIZE number of item. Item with false value reprepresent for the equivalent noisy point in pcdBuff
	/// @return Unified processing result
	*/
	extern "C" TFL_RESULT TFL_DLL		MarkPCDNoise(TFL_PointXYZ pcdFullBuf[TFL_FRAME_SIZE], uint16_t sensitiveFactor, bool noiseFlags[TFL_FRAME_SIZE], uint16_t &countNoise);

	/**
	/// @brief This function use to convert array of depth value to it's equivalent mapping color in RAINBOW spectrum
	/// @param depthBuf [IN] holding array of items of depth value, each item use 2 byte for holding depth value
	/// @param displayMin [IN] Minimum range value
	/// @param displayMax [IN] Maximum range value
	/// @param depthColor [OUT] array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
	/// @return Unified processing result
	*/
	extern "C" TFL_RESULT TFL_DLL       DepthToRainbow(uint16_t depthBuf[TFL_FRAME_SIZE], uint16_t displayMin, uint16_t displayMax, TFL_Color depthColor[TFL_FRAME_SIZE]);

	/**
	/// @brief This function use to convert array of depth value to it's equivalent mapping color in GRAYSCALE spectrum
	/// @param depthBuf [IN] holding array of items of depth value, each item use 2 byte for holding depth value
	/// @param displayMin [IN] Minimum range value
	/// @param displayMax [IN] Maximum range value
	/// @param depthColor [OUT] array of item of Vec3, each item containing 3 field holding 3 value of RED, GREEN, BLUE are the color component for the depth
	/// @return Unified processing result
	*/
	extern "C" TFL_RESULT TFL_DLL        DepthToGray(uint16_t depthBuf[TFL_FRAME_SIZE], uint16_t displayMin, uint16_t displayMax, TFL_Color depthColor[TFL_FRAME_SIZE]);

	/// @brief Checking if the library still allowing for trial use or not
	extern "C" bool       TFL_DLL       IsTrialExpired();

	extern "C" TFL_Color  TFL_DLL      *GetRGBSpect(int gameObjet_lenght, int value_start, int value_stop, float scale_up);
	extern "C" TFL_Color  TFL_DLL      *GetGrayScaleSpect(int gameObject_lenght, int value_start, float scale_up);

}
