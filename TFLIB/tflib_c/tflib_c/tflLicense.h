/* (C) 2020 by Brycen Group in international.
 */
#pragma once

#include <Windows.h>
#include <stdio.h>
#include <iostream>
#include <cstdint>
#include <ctime>
#include <strsafe.h>
#include "tflib_c.h"

 //ExpiryDate is not for DLL module, Just subroutines for TFL. So comment out below.
#ifndef TFLIB_EXPORTS
#ifdef TFLIB_EXPORTS
#define TFLIB_EXPORTS __declspec(dllexport)
#else
#define TFLIB_EXPORTS __declspec(dllimport)
#endif
#endif

#if 0
#define	TFL_DEFAULT_EXPIRYDAYS	30
#else
#define	TFL_DEFAULT_EXPIRYDAYS	90		// 3 months for Star Seiki Co.Ltd.
#endif

namespace TFL
{
#define TOTAL_BYTES_READ 1024
#define OFFSET_BYTES 1024
	typedef uint16_t UINT16;

	/*------------------------------------------------------------------------------------
				class for tflib internal
	------------------------------------------------------------------------------------*/
	class ExpiryDate
	{
	private:
		BOOL InitRegistery(time_t timeNow, uint16_t days);
		time_t CalcExpiryDate(time_t, uint16_t);

		BOOL IsFirstUsed(BOOL* bFirstUse);
		BOOL IsChanged_1(BOOL* bChanged);
		BOOL IsChanged_2(time_t timeNow, BOOL* bChanged);
		BOOL IsExpired(time_t timeNow, BOOL* bExpired);

		BOOL ReadDate(HKEY hKeyParent, PWCHAR subkey, uint64_t* Date1, uint64_t* Date2, uint64_t* Date3);

		BOOL SetFirstDate(time_t timeNow);
		BOOL SetExpiryDate(time_t timeNow, uint16_t days);
		BOOL SetPreviousDate(time_t timeNow);

		//Create key in registry
		BOOL CreateRegistryKey(HKEY hKeyParent, PWCHAR subkey);
		//Write data in registry
		BOOL WriteQwordInRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, uint64_t data);
		//Read data from registry
		BOOL ReadQwordRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, uint64_t* readData);
		//Write range and type into the registry
		BOOL WriteStringInRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, PWCHAR strData);
		//		//read customer infromation from the registry
		//		BOOL ReadUserInfoFromRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, PWCHAR* readData);
				//delete registry key
		BOOL DeleteRegistryKey(HKEY hKeyParent, PWCHAR subkey);
		BOOL RegDelnodeRecurse(HKEY hKeyRoot, PWCHAR subkey);

	public:
		ExpiryDate();
		TFL_RESULT	CheckExpiryDate(uint16_t);
		TFL_RESULT	Clear();

		uint64_t	mLastError;
	};

	/*------------------------------------------------------------------------------------
				functions for tflib external (but NOT for end user, JUST for Brycen Test Program)
	------------------------------------------------------------------------------------*/
	TFL_RESULT TFL_DLL		ClearExpiryDate();
}
