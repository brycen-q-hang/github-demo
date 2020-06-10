/* (C) 2020 by Brycen Group in international.
 */
#include "pch.h"

#include <iostream>
#include "tflLicense.h"

using namespace TFL;

//HKEY_CURRENT_USERを使うと、ログインユーザーが変わった時点で「TFL_CHANGEDを戻すバグ」が出る。
//これを回避するため、以下defineを有効にし、HKEY_CLASSES_ROOTとHKEY_LOCAL_MACHINEの2ROOTを利用すること。
#define	USE_2REGISTORY_ROOT

wchar_t cRegiKey1[] = TEXT("TFLBRYCEN");
wchar_t cRegiKey2[] = TEXT("SOFTWARE\\TFLBRYCEN");

wchar_t cRegiName_First[] = TEXT("Date1");
wchar_t cRegiName_Expiry[] = TEXT("Date2");
wchar_t cRegiName_Previous[] = TEXT("Date3");

/*------------------------------------------------------------------------
 Public functions
-------------------------------------------------------------------------*/
/// @brief Clear all of registers. This function is NOT for end user, JUST for Brycen Test Program.
/// @param none
/// @return Unified processing result.
TFL_RESULT TFL::ClearExpiryDate()
{
	TFL_RESULT	tRet;

	ExpiryDate	cED = ExpiryDate();
	tRet = cED.Clear();

	if (tRet == TFL_RESULT::TFL_ERROR)
		cED.mLastError = GetLastError();

	return(tRet);
}

/*------------------------------------------------------------------------
 Public methods
-------------------------------------------------------------------------*/
ExpiryDate::ExpiryDate()
{
	this->mLastError = 0;
};

TFL_RESULT ExpiryDate::CheckExpiryDate(uint16_t days)
{
	time_t	timeNow = time(0);
	BOOL	bIs;

	if (days == 0)
		return TFL_RESULT::TFL_ZERODAY;

	// Check if First Use?
	if (IsFirstUsed(&bIs) != TRUE) {
		printf("TFLIB: IsFirstUsed() returned FALSE.");
		goto TFL_ERROR;
	}

	if (bIs) {
		if (InitRegistery(timeNow, days) != TRUE) {
			printf("TFLIB: InitRegistery() returned FALSE.");
			goto TFL_ERROR;
		}

		return TFL_RESULT::TFL_OK;
	}

	// Check if Reverse Engineered?
	if (IsChanged_1(&bIs) != TRUE) {
		printf("TFLIB: IsChanged_1() returned FALSE.");
		goto TFL_ERROR;
	}

	if (bIs)
		return TFL_RESULT::TFL_CHANGED;

	// Check if System Time was rewound?
	if (IsChanged_2(timeNow, &bIs) != TRUE) {
		printf("TFLIB: IsChanged_2() returned FALSE.");
		goto TFL_ERROR;
	}

	if (bIs)
		return TFL_RESULT::TFL_CHANGED;

	// Check if Expired?
	if (IsExpired(timeNow, &bIs) != TRUE) {
		printf("TFLIB: IsExpired() returned FALSE.");
		goto TFL_ERROR;
	}

	if (bIs)
		return TFL_RESULT::TFL_EXPIRED;


	// Record Current System Time as Previous Executed Time.
	if (SetPreviousDate(timeNow) != TRUE) {
		printf("TFLIB: SetPreviousDate() returned FALSE.");
		goto TFL_ERROR;
	}

	return TFL_RESULT::TFL_OK;

TFL_ERROR:
	mLastError = GetLastError();	//TBD: 0が設定される。
	return TFL_RESULT::TFL_ERROR;
}

/// KeyPoint: 途中でエラー発生しても全ての削除処理を行う。
TFL_RESULT ExpiryDate::Clear()
{
	TFL_RESULT	eResult;
	BOOL		bResult;

	eResult = TFL_RESULT::TFL_OK;

#ifndef USE_2REGISTORY_ROOT
	bResult = DeleteRegistryKey(HKEY_CURRENT_USER, cRegiKey1);
	if (bResult != TRUE)
		eResult = TFL_RESULT::TFL_ERROR;
#endif

	bResult = DeleteRegistryKey(HKEY_CLASSES_ROOT, cRegiKey1);
	if (bResult != TRUE)
		eResult = TFL_RESULT::TFL_ERROR;

	bResult = DeleteRegistryKey(HKEY_LOCAL_MACHINE, cRegiKey2);
	if (bResult != TRUE)
		eResult = TFL_RESULT::TFL_ERROR;

	return eResult;
}

/*------------------------------------------------------------------------
 Private methods
-------------------------------------------------------------------------*/
/// <summary>
/// Create all of registory keys and names(Values) newly
/// if any error is happened during processing, This function try to delete all of keys and names(values).
BOOL ExpiryDate::InitRegistery(time_t timeNow, uint16_t days)
{
	BOOL bResult;
	//Create all of registery keys.
#ifndef USE_2REGISTORY_ROOT
	bResult = CreateRegistryKey(HKEY_CURRENT_USER, cRegiKey1);
	if (bResult != TRUE)
		goto RET_FALSE;
#endif

	bResult = CreateRegistryKey(HKEY_CLASSES_ROOT, cRegiKey1);
	if (bResult != TRUE)
		goto RET_FALSE;

	bResult = CreateRegistryKey(HKEY_LOCAL_MACHINE, cRegiKey2);
	if (bResult != TRUE)
		goto RET_FALSE;

	//Create all of registery names(Value).
	bResult = SetFirstDate(timeNow);
	if (bResult != TRUE)
		goto RET_FALSE;

	bResult = SetExpiryDate(timeNow, days);
	if (bResult != TRUE)
		goto RET_FALSE;

	bResult = SetPreviousDate(timeNow);
	if (bResult != TRUE)
		goto RET_FALSE;

	return TRUE;

RET_FALSE:
	Clear();
	return FALSE;
}

/// <summary>
/// Read all Registorys in the specified key.
/// </summary>
///
BOOL ExpiryDate::ReadDate(HKEY hKeyParent, PWCHAR subkey, uint64_t* Date1, uint64_t* Date2, uint64_t* Date3)
{
	BOOL bResult = ReadQwordRegistry(hKeyParent, subkey, cRegiName_First, Date1); //read dword
	if (bResult != TRUE)
		return FALSE;

	bResult = ReadQwordRegistry(hKeyParent, subkey, cRegiName_Expiry, Date2); //read dword
	if (bResult != TRUE)
		return FALSE;

	bResult = ReadQwordRegistry(hKeyParent, subkey, cRegiName_Previous, Date3); //read dword
	if (bResult != TRUE)
		return FALSE;

	return TRUE;
}

/// <summary>
/// Read all of registory key to check if first use the software.
/// </summary>
///
BOOL ExpiryDate::IsFirstUsed(BOOL* bFirstUse)
{
	HKEY hKey;
	BOOL bRet;

#ifndef USE_2REGISTORY_ROOT
	//Open the key
	DWORD Result1 = RegOpenKeyEx(
		HKEY_CURRENT_USER,
		cRegiKey1
		0,
		KEY_ALL_ACCESS,
		&hKey
	);
	if (Result1 == ERROR_SUCCESS && hKey != NULL) {
		RegCloseKey(hKey);
	}
#endif

	//Open the key
	DWORD Result2 = RegOpenKeyEx(
		HKEY_CLASSES_ROOT,
		cRegiKey1,
		0,
		KEY_ALL_ACCESS,
		&hKey
	);
	if (Result2 == ERROR_SUCCESS && hKey != NULL) {
		RegCloseKey(hKey);
	}

	//Open the key
	DWORD Result3 = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE,
		cRegiKey2,
		0,
		KEY_ALL_ACCESS,
		&hKey
	);
	if (Result3 == ERROR_SUCCESS && hKey != NULL) {
		RegCloseKey(hKey);
	}

#ifndef USE_2REGISTORY_ROOT
	//User don't have administrator rights. 
	if ((Result1 == ERROR_ACCESS_DENIED) || (Result2 == ERROR_ACCESS_DENIED) || (Result3 == ERROR_ACCESS_DENIED)) {
		bRet = FALSE;
	}
	else {
		//３レジスタ・キー全てのOPENに失敗すれば Firest User　　 <- 正常ケース
		//全てのレジスタ・キーのOPENに成功すれば Not First User. <- 正常ケース
		//１～２レジスタ・キーのOPENに失敗すれば Not First User. <- ここが怪しいケース
		*bFirstUse = (
			(Result1 == ERROR_FILE_NOT_FOUND) && (Result2 == ERROR_FILE_NOT_FOUND) && (Result3 == ERROR_FILE_NOT_FOUND)
			) ? TRUE : FALSE;

		bRet = TRUE;
	}
#else
	//User don't have administrator rights. 
	if ((Result2 == ERROR_ACCESS_DENIED) || (Result3 == ERROR_ACCESS_DENIED)) {
		bRet = FALSE;
	}
	else {
		//２レジスタ・キー全てのOPENに失敗すれば Firest User　　 <- 正常ケース
		//全てのレジスタ・キーのOPENに成功すれば Not First User. <- 正常ケース
		//　　１レジスタ・キーのOPENに失敗すれば Not First User. <- ここが怪しいケース
		*bFirstUse = (
			(Result2 == ERROR_FILE_NOT_FOUND) && (Result3 == ERROR_FILE_NOT_FOUND)
			) ? TRUE : FALSE;

		bRet = TRUE;
	}
#endif

	return bRet;
}

/// <summary>
/// Check if All pairs of Regualar Registory Keys have same values or not.
/// </summary>
///
BOOL ExpiryDate::IsChanged_1(BOOL* bChanged)
{
	uint64_t Date1_2, Date2_2, Date3_2;
	uint64_t Date1_3, Date2_3, Date3_3;
	BOOL bResult;

#ifndef USE_2REGISTORY_ROOT
	uint64_t Date1_1, Date2_1, Date3_1;

	bResult = ReadDate(HKEY_CURRENT_USER, cRegiKey1, &Date1_1, &Date2_1, &Date3_1);
	if (bResult != TRUE) {
		Date1_1 = UINT64_MAX;
		Date2_1 = UINT64_MAX;
		Date3_1 = UINT64_MAX;
	}
#endif

	bResult = ReadDate(HKEY_CLASSES_ROOT, cRegiKey1, &Date1_2, &Date2_2, &Date3_2);
	if (bResult != TRUE) { //強制的に, *bChanged = TRUE にする。
		Date1_2 = UINT64_MAX - 1;
		Date2_2 = UINT64_MAX - 1;
		Date3_2 = UINT64_MAX - 1;
	}

	bResult = ReadDate(HKEY_LOCAL_MACHINE, cRegiKey2, &Date1_3, &Date2_3, &Date3_3);
	if (bResult != TRUE) {
		Date1_3 = UINT64_MAX - 2;
		Date2_3 = UINT64_MAX - 2;
		Date3_3 = UINT64_MAX - 2;
	}

#ifndef USE_2REGISTORY_ROOT
	// 1組でも値が異なれば、変更されたと判断する。
	* bChanged = (
		(Date1_1 != Date1_2) || (Date2_1 != Date2_2) || (Date3_1 != Date3_2) ||
		(Date1_1 != Date1_3) || (Date2_1 != Date2_3) || (Date3_1 != Date3_3)
		) ? TRUE : FALSE;
#else
	// 1組でも値が異なれば、変更されたと判断する。
	* bChanged = (
		(Date1_2 != Date1_3) || (Date2_2 != Date2_3) || (Date3_2 != Date3_3)
		) ? TRUE : FALSE;
#endif

	return TRUE;
}

/// <summary>
/// Check if Current System Time was rewound.
/// </summary>
///
BOOL ExpiryDate::IsChanged_2(time_t timeNow, BOOL* bChanged)
{
	uint64_t	Date3;

	BOOL bResult = ReadQwordRegistry(HKEY_CLASSES_ROOT, cRegiKey1, cRegiName_Previous, &Date3); //read dword
	if (bResult != TRUE)
		return FALSE;

	*bChanged = (Date3 > (uint64_t)timeNow) ? TRUE : FALSE;

	return TRUE;
}

/// <summary>
/// Check if expired.
/// </summary>
///
BOOL ExpiryDate::IsExpired(time_t timeNow, BOOL* bChanged)
{
	uint64_t	expiryDay;

	BOOL bResult = ReadQwordRegistry(HKEY_CLASSES_ROOT, cRegiKey1, cRegiName_Expiry, &expiryDay); //read dword
	if (bResult != TRUE)
		return FALSE;

	*bChanged = (expiryDay <= (uint64_t)timeNow) ? TRUE : FALSE;

	return TRUE;
}

/// <summary>
/// Set time of now as First Use Day.
/// </summary>
///
BOOL ExpiryDate::SetFirstDate(time_t timeNow)
{
	BOOL bResult;

#ifndef USE_2REGISTORY_ROOT
	bResult = WriteQwordInRegistry(HKEY_CURRENT_USER, cRegiKey1, cRegiName_First, timeNow);
	if (!bResult)
		return FALSE;
#endif

	bResult = WriteQwordInRegistry(HKEY_CLASSES_ROOT, cRegiKey1, cRegiName_First, timeNow);
	if (!bResult)
		return FALSE;

	bResult = WriteQwordInRegistry(HKEY_LOCAL_MACHINE, cRegiKey2, cRegiName_First, timeNow);
	if (!bResult)
		return FALSE;

	return TRUE;
}

/// <summary>
/// Caluculate time_t following parametarts.
/// </summary>
///
time_t ExpiryDate::CalcExpiryDate(time_t now, uint16_t days) {
	int secs = days * (60 * 60 * 24);	//1day = 86400 seconds
	time_t ExpiryDay = now + secs;

	return ExpiryDay;
}

/// <summary>
/// Record Expiry Date to Regular Registory Keys.
/// </summary>
///
BOOL ExpiryDate::SetExpiryDate(time_t timeNow, uint16_t days)
{
	time_t	expiryDay = CalcExpiryDate(timeNow, days);
	BOOL	bResult;

#ifndef USE_2REGISTORY_ROOT
	bResult = WriteQwordInRegistry(HKEY_CURRENT_USER, cRegiKey1, cRegiName_Expiry, expiryDay);
	if (!bResult)
		return FALSE;
#endif

	bResult = WriteQwordInRegistry(HKEY_CLASSES_ROOT, cRegiKey1, cRegiName_Expiry, expiryDay);
	if (!bResult)
		return FALSE;

	bResult = WriteQwordInRegistry(HKEY_LOCAL_MACHINE, cRegiKey2, cRegiName_Expiry, expiryDay);
	if (!bResult)
		return FALSE;

	return TRUE;
}

/// <summary>
/// Update Previous Run Date to Regular Registory Keys.
/// </summary>
///
BOOL ExpiryDate::SetPreviousDate(time_t timeNow)
{
	BOOL bResult;

#ifndef USE_2REGISTORY_ROOT
	bResult = WriteQwordInRegistry(HKEY_CURRENT_USER, cRegiKey1, cRegiName_Previous, timeNow);
	if (!bResult)
		return FALSE;
#endif

	bResult = WriteQwordInRegistry(HKEY_CLASSES_ROOT, cRegiKey1, cRegiName_Previous, timeNow);
	if (!bResult)
		return FALSE;

	bResult = WriteQwordInRegistry(HKEY_LOCAL_MACHINE, cRegiKey2, cRegiName_Previous, timeNow);
	if (!bResult)
		return FALSE;

	return TRUE;
}

///// <summary>
///// Record Previous Run Date to Regular Registory Keys.
///// </summary>
/////
//BOOL ExpiryDate::SetPreviousDateDefault()
//{
//	BOOL bResult = WriteDwordInRegistry(HKEY_CURRENT_USER, cRegiKey1, cRegiName_Previous, 0);
//	if (!bResult)
//		return FALSE;
//
//	bResult = WriteDwordInRegistry(HKEY_CLASSES_ROOT, cRegiKey1, cRegiName_Previous, 0);
//	if (!bResult)
//		return FALSE;
//
//	bResult = WriteDwordInRegistry(HKEY_LOCAL_MACHINE, cRegiKey2, cRegiName_Previous, 0);
//	if (!bResult)
//		return FALSE;
//
//	return TRUE;
//}

/// <summary>
/// Create key in registry
/// </summary>
///
BOOL ExpiryDate::CreateRegistryKey(HKEY hKeyParent, PWCHAR subkey)
{
	HKEY  hKey;
	DWORD dwDisposition; //It verify new key is created or open existing key
	DWORD dwRet;

	dwRet =
		RegCreateKeyEx(
			hKeyParent,
			subkey,
			0,
			NULL,
			REG_OPTION_NON_VOLATILE,
			KEY_ALL_ACCESS,
			NULL,
			&hKey,
			&dwDisposition);

	if (dwRet != ERROR_SUCCESS)
	{
		//		printf("Error opening or creating key.\n");
		return FALSE;
	}

	RegCloseKey(hKey);
	return TRUE;
}

/// <summary>
/// Write data in registry
/// </summary>
///
BOOL ExpiryDate::WriteQwordInRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, uint64_t data)
{
	DWORD dwRet;
	HKEY hKey;

	//Open the key
	dwRet = RegOpenKeyEx(
		hKeyParent,
		subkey,
		0,
		KEY_WRITE,
		&hKey
	);

	if (dwRet != ERROR_SUCCESS)
	{
		//		printf("Error opening or creating key.\n");
		return FALSE;
	}

	//Set the value in key
	dwRet = RegSetValueEx(
		hKey,
		valueName,
		0,
		REG_QWORD,
		reinterpret_cast<BYTE*>(&data),
		sizeof(data));

	if (dwRet != ERROR_SUCCESS)
	{
		RegCloseKey(hKey);
		return FALSE;
	}

	//close the key
	RegCloseKey(hKey);
	return TRUE;
}

/// <summary>
/// Read data from registry
/// </summary>
///
BOOL ExpiryDate::ReadQwordRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, uint64_t* readData)
{
	HKEY hKey;
	DWORD dwRet;

	//Check if the registry exists
	dwRet = RegOpenKeyEx(
		hKeyParent,
		subkey,
		0,
		KEY_READ,
		&hKey
	);

	if (dwRet != ERROR_SUCCESS)
	{
		//		printf("Error opening or creating key.\n");
		return FALSE;
	}

	DWORD len = sizeof(uint64_t);//size of data

	dwRet = RegQueryValueEx(
		hKey,
		valueName,
		NULL,
		NULL,
		(LPBYTE)readData,
		&len
	);

	if (dwRet != ERROR_SUCCESS)
	{
		RegCloseKey(hKey);
		return FALSE;
	}

	RegCloseKey(hKey);
	return TRUE;
}

/// <summary>
/// Write range and type into the registry
/// </summary>
///
BOOL ExpiryDate::WriteStringInRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, PWCHAR strData)
{
	HKEY hKey;
	DWORD dwRet;

	//Check if the registry exists
	dwRet = RegOpenKeyEx(
		hKeyParent,
		subkey,
		0,
		KEY_WRITE,
		&hKey
	);

	if (dwRet != ERROR_SUCCESS)
	{
		//		printf("Error opening or creating key.\n");
		return FALSE;
	}

	dwRet = RegSetValueEx(
		hKey,
		valueName,
		0,
		REG_SZ,
		(LPBYTE)(strData),
		((((DWORD)lstrlen(strData) + 1)) * 2));

	if (dwRet != ERROR_SUCCESS)
	{
		RegCloseKey(hKey);
		return FALSE;
	}

	RegCloseKey(hKey);
	return TRUE;
}

#if 0
/// <summary>
/// Read customer infromation from the registry
/// </summary>
///
BOOL ExpiryDate::ReadUserInfoFromRegistry(HKEY hKeyParent, PWCHAR subkey, PWCHAR valueName, PWCHAR* readData)
{
	HKEY hKey;
	DWORD len = TOTAL_BYTES_READ;
	DWORD dwRet;

	DWORD readDataLen = len;

	PWCHAR readBuffer = (PWCHAR)malloc(sizeof(PWCHAR) * len);
	if (readBuffer == NULL)
		return FALSE;

	//Check if the registry exists
	dwRet = RegOpenKeyEx(
		hKeyParent,
		subkey,
		0,
		KEY_READ,
		&hKey
	);

	if (dwRet != ERROR_SUCCESS)
	{
		//		printf("Error opening or creating key.\n");
		return FALSE;
	}

	dwRet = RegQueryValueEx(
		hKey,
		valueName,
		NULL,
		NULL,
		(BYTE*)readBuffer,
		&readDataLen
	);

	while (dwRet == ERROR_MORE_DATA)
	{
		// Get a buffer that is big enough.

		len += OFFSET_BYTES;
		readBuffer = (PWCHAR)realloc(readBuffer, len);
		if (readBuffer = NULL) {
			dwRet = ERROR_NOT_ENOUGH_MEMORY;
			break;
		}

		readDataLen = len;
		dwRet = RegQueryValueEx(
			hKey,
			valueName,
			NULL,
			NULL,
			(BYTE*)readBuffer,
			&readDataLen
		);
	}

	if (dwRet != ERROR_SUCCESS)
	{
		RegCloseKey(hKey);
		return FALSE;
	}

	*readData = readBuffer;

	RegCloseKey(hKey);
	return TRUE;
}
#endif

BOOL ExpiryDate::RegDelnodeRecurse(HKEY hKeyRoot, PWCHAR subkey)
{
	FILETIME ftWrite;
	HKEY	hKey;
	LPWSTR	lpEnd;
	LONG	lResult;
	DWORD	dwSize;
	TCHAR	szName[MAX_PATH];

	// First, see if we can delete the key without having to recurse.
	lResult = RegDeleteKey(hKeyRoot, subkey);
	if (lResult == ERROR_SUCCESS)
		return TRUE;

	lResult = RegOpenKeyEx(hKeyRoot, subkey, 0, KEY_READ, &hKey);
	if (lResult != ERROR_SUCCESS)
	{
		if (lResult == ERROR_FILE_NOT_FOUND) {
			//			printf("Key not found.\n");
			return TRUE;
		}
		else {
			//			printf("Error opening key.\n");
			return FALSE;
		}
	}

	// Check for an ending slash and add one if it is missing.
	lpEnd = subkey + lstrlen(subkey);

	if (*(lpEnd - 1) != TEXT('\\'))
	{
		*lpEnd = TEXT('\\');
		lpEnd++;
		*lpEnd = TEXT('\0');
	}

	// Enumerate the keys
	dwSize = MAX_PATH;
	lResult = RegEnumKeyEx(hKey, 0, szName, &dwSize, NULL, NULL, NULL, &ftWrite);

	if (lResult == ERROR_SUCCESS)
	{
		do {

			*lpEnd = TEXT('\0');
			StringCchCat(subkey, MAX_PATH * 2, szName);

			if (!RegDelnodeRecurse(hKeyRoot, subkey)) {
				break;
			}

			dwSize = MAX_PATH;

			lResult = RegEnumKeyEx(hKey, 0, szName, &dwSize, NULL,
				NULL, NULL, &ftWrite);

		} while (lResult == ERROR_SUCCESS);
	}

	lpEnd--;
	*lpEnd = TEXT('\0');

	RegCloseKey(hKey);

	// Try again to delete the key.
	lResult = RegDeleteKey(hKeyRoot, subkey);
	if (lResult == ERROR_SUCCESS)
		return TRUE;

	return FALSE;
}

BOOL ExpiryDate::DeleteRegistryKey(HKEY hKeyParent, PWCHAR subkey)
{
	TCHAR szDelKey[MAX_PATH * 2];

	StringCchCopy(szDelKey, MAX_PATH * 2, subkey);
	return RegDelnodeRecurse(hKeyParent, szDelKey);
}
