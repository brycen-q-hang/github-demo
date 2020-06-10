/* (C) 2020 by Brycen Group in international.
 */
#include "pch.h"

#include <iostream>
#include "tflLicense.h"

using namespace TFL;

static bool			bFirstExec = true;
static TFL_RESULT	eRetExpiry = TFL_RESULT::TFL_OK;

/// @brief Checking if the library still allowing for trial use or not
bool TFL::IsTrialExpired()
{
	//Check of Expiry Date.
	bool IsExpired = false;
	if (bFirstExec) {
		bFirstExec = false;
		ExpiryDate cED = ExpiryDate();
		eRetExpiry = cED.CheckExpiryDate(TFL_DEFAULT_EXPIRYDAYS);

		if (eRetExpiry != TFL_RESULT::TFL_OK)
		{
			IsExpired = true;
			return IsExpired;
		}
	}

	if (eRetExpiry != TFL_RESULT::TFL_OK)
	{
		IsExpired = true;
		return true;	// Return latched error code.
	}

	return IsExpired;
}