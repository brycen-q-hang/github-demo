#include <stdbool.h>
#define EXPORT extern "C" __declspec(dllexport) 
#define MAXCHAR 1024
#define max_point 307200

typedef struct struct_vec Vec3;
struct struct_vec
{
	float X;
	float Y;
	float Z;
};

// this InitNoiseHandler() method need to be call one before doing anything else
void initNoiseHandler();

// This MarkNoise function can be call each time user want to detect outliner for the input organized point cloud
//
// input 1: Vector3 *data array represent for input point clouds. Each item of the array holding x y z of the points
// input 2: threshold ranging from 19..100. The smaller the threshold, the more sensitive to the noise detection
// input 3: sensor_w number of sensor pixel in width
// input 4: sensor_h number of sensor pixel in heigh
// 
// Output : bool array represent for noise of the input Vector3 *data. Each item of the array holding bool value, 
// 'true' for outlier/noise and 'false' for non-noise
bool* markNoise(Vec3 *data, float threshold, int sensor_w, int sensor_h);

// This function should be call after MarkNoise(..)
// Output: number of noise detected from the last call of MarkNoise
int GetLastNoiseCount();

// This method should be call to release all allocated memory used within this library, for the memory leak will not happen
void releaseNoiseHandler();