#include <stdbool.h>
#define EXPORT extern "C" __declspec(dllexport) 
#define MAXCHAR 1024
#define max_point 307200
#define	TFL_SIZE 
#define SiZE 3


typedef struct TFL_PointXYZ TFL_PointXYZ;
struct TFL_PointXYZ
{
	float x;
	float y;
	float z;
};

int Get_value_of_arr(int a[SiZE]);
int Get_value_of_struct(TFL_PointXYZ str[SiZE]);